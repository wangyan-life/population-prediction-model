"""
Cohort-component population projection (single-sex fertility model).

This module implements a simple age-structured cohort-component model where
fertility is modeled only for females (age-specific fertility rates). Births
are produced from the female age distribution and then split by sex using a
sex-ratio-at-birth. Mortality/survival can be provided separately for males
and females.

The implementation is intentionally small and well-documented so it can be
adapted to real data inputs later.

Cohort-component population projection（单性别生育模型）。

该模块实现了一个简单的按年龄结构划分的 Cohort-component 模型，其中生育仅针对女性
建模（按年龄划分的生育率）。出生人口由女性年龄分布产生，然后根据出生性别比进行性别
分配。死亡/出生率可以分别为男性和女性提供。

该实现故意保持简洁且有良好的文档记录，以便以后能够适配真实的数据输入。
"""
from typing import Optional, Dict, Any
import numpy as np


class CohortComponentModel:
    """
    一个轻量级的 Cohort-component 预测引擎。

    Contract (inputs/outputs):
    - Inputs:
    * max_age: maximum age (ages 0...max_age, inclusive)
      * initial female/male population arrays of shape (max_age+1,)
      * fertility: age-specific fertility rates (ASFR) for female ages
      * survival_female / survival_male: annual survival probabilities by age
    - Outputs: dict with yearly totals, births, deaths, and age distributions

    Error modes: raises ValueError for shape mismatches.
    """

    def __init__(self, max_age: int, sex_ratio_at_birth: float = 1.05) -> None:
        self.max_age = int(max_age)
        self.srb = float(sex_ratio_at_birth)

    def _check_shapes(self, arr: np.ndarray) -> None:
        expected = self.max_age + 1
        if arr.shape[0] != expected:
            raise ValueError(f"array length must be {expected}, got {arr.shape}")

    def project(
        self,
        years: int,
        pop_female: np.ndarray,
        fertility: np.ndarray,
        survival_female: np.ndarray,
        pop_male: Optional[np.ndarray] = None,
        survival_male: Optional[np.ndarray] = None,
        mig_female: Optional[np.ndarray] = None,
        mig_male: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """Run a multi-year projection.

        Args:
            years: number of projection years (integer)
            pop_female: initial female population by age (ages 0...max_age, inclusive)
            fertility: ASFR (births per woman per year) for female ages
            survival_female: annual survival probabilities for females by age
            pop_male: optional initial male population by age; if None, mirrored
            survival_male: optional male survival; if None, uses female survival

        Returns:
            dict with keys:
              - 'years': list of year indices (0...years, inclusive)
              - 'total': total population per year
              - 'births': births per year (number of newborns)
              - 'deaths': deaths per year (total deaths)
              - 'age_female' / 'age_male': list of arrays for each year
        """
        years = int(years)
        pop_female = np.asarray(pop_female, dtype=float).copy()
        fertility = np.asarray(fertility, dtype=float)
        survival_female = np.asarray(survival_female, dtype=float)

        self._check_shapes(pop_female)
        self._check_shapes(fertility)
        self._check_shapes(survival_female)

        if pop_male is None:
            pop_male = pop_female.copy()
        else:
            pop_male = np.asarray(pop_male, dtype=float).copy()
            self._check_shapes(pop_male)

        if survival_male is None:
            survival_male = survival_female.copy()
        else:
            survival_male = np.asarray(survival_male, dtype=float)
            self._check_shapes(survival_male)

        # Pre-allocate storage
        yrs = list(range(years + 1))
        age_female = [pop_female.copy()]
        age_male = [pop_male.copy()]
        births = [0.0]
        deaths = [0.0]
        deaths_by_age_f = [np.zeros_like(pop_female)]
        deaths_by_age_m = [np.zeros_like(pop_male)]

        # migration defaults
        if mig_female is None:
            mig_female = np.zeros_like(pop_female)
        else:
            mig_female = np.asarray(mig_female, dtype=float)
            self._check_shapes(mig_female)

        if mig_male is None:
            mig_male = np.zeros_like(pop_male)
        else:
            mig_male = np.asarray(mig_male, dtype=float)
            self._check_shapes(mig_male)

        for y in range(1, years + 1):
            prev_f = age_female[-1]
            prev_m = age_male[-1]

            # Births produced by females: sum ASFR * women_at_age
            yearly_births = float(np.sum(fertility * prev_f))

            # Allocate births by sex using sex-ratio-at-birth (SRB = males/females)
            male_prop = self.srb / (1.0 + self.srb)
            female_prop = 1.0 - male_prop
            newborns_m = yearly_births * male_prop
            newborns_f = yearly_births * female_prop

            # Compute newborn survival within the year (explicit infant deaths)
            # newborns_alive = newborns * survival[0]
            newborns_alive_f = newborns_f * survival_female[0]
            newborns_alive_m = newborns_m * survival_male[0]
            infant_deaths_f = newborns_f - newborns_alive_f
            infant_deaths_m = newborns_m - newborns_alive_m

            # Ageing + survival: build new arrays
            new_f = np.zeros_like(prev_f)
            new_m = np.zeros_like(prev_m)

            # Age 0 at period end: newborns who survived within year
            new_f[0] = newborns_alive_f
            new_m[0] = newborns_alive_m

            # For ages 1..max_age-1: those who were age a-1 survive to a
            for a in range(1, self.max_age):
                new_f[a] = prev_f[a - 1] * survival_female[a - 1]
                new_m[a] = prev_m[a - 1] * survival_male[a - 1]

            # max_age (open group): survivors from prev[max_age-1] aging in
            new_f[self.max_age] = prev_f[self.max_age - 1] * survival_female[self.max_age - 1]
            new_m[self.max_age] = prev_m[self.max_age - 1] * survival_male[self.max_age - 1]

            # plus survivors who were already in max_age and remain there
            new_f[self.max_age] += prev_f[self.max_age] * survival_female[self.max_age]
            new_m[self.max_age] += prev_m[self.max_age] * survival_male[self.max_age]

            # Age-specific deaths among previous cohorts (excluding newborns of this year)
            deaths_prev_f = prev_f * (1.0 - survival_female)
            deaths_prev_m = prev_m * (1.0 - survival_male)

            # Combine newborn deaths into age 0 deaths
            deaths_by_age_f_this = deaths_prev_f.copy()
            deaths_by_age_m_this = deaths_prev_m.copy()
            deaths_by_age_f_this[0] += infant_deaths_f
            deaths_by_age_m_this[0] += infant_deaths_m

            # Total deaths this year is sum of previous-cohort deaths + infant deaths
            deaths_this_year = float(np.sum(deaths_by_age_f_this) + np.sum(deaths_by_age_m_this))

            # Apply net migration at period end (after deaths). Migration vectors are counts to add.
            new_f = new_f + mig_female
            new_m = new_m + mig_male

            age_female.append(new_f)
            age_male.append(new_m)
            births.append(yearly_births)
            deaths.append(deaths_this_year)
            deaths_by_age_f.append(deaths_by_age_f_this)
            deaths_by_age_m.append(deaths_by_age_m_this)

        total = [float(np.sum(age_female[i]) + np.sum(age_male[i])) for i in range(len(age_female))]

        return {
            "years": yrs,
            "total": np.array(total),
            "births": np.array(births),
            "deaths": np.array(deaths),
            "age_female": age_female,
            "age_male": age_male,
            "deaths_by_age_f": deaths_by_age_f,
            "deaths_by_age_m": deaths_by_age_m,
        }


def make_simple_example(max_age: int = 100):
    """Create a tiny synthetic example suitable for quick runs and tests.

    - initial population: triangular age distribution
    - fertility: simple hump for ages 15-49
    - survival: high survival with slight decrease by age
    """
    ages = np.arange(0, max_age + 1)
    # initial female population: decreasing with age
    base = np.maximum(0, (max_age + 1 - ages))
    pop_f = base * 1000.0
    pop_m = pop_f * 1.02

    fertility = np.zeros_like(ages, dtype=float)
    fert_mask = (ages >= 15) & (ages <= 49)
    fertility[fert_mask] = 0.05 * np.exp(-((ages[fert_mask] - 28) ** 2) / (2 * 7.0 ** 2))

    # survival probabilities by age (probability to survive one year)
    survival = 1.0 - (ages / (max_age + 200.0)) * 0.02
    survival = np.clip(survival, 0.4, 1.0)

    return pop_f, pop_m, fertility, survival
