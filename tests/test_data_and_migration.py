import numpy as np
from models.cohort_component import CohortComponentModel


def test_deaths_and_migration_behavior():
    max_age = 5
    ages = np.arange(0, max_age + 1)
    # simple populations
    pop_f = np.array([100.0, 80.0, 60.0, 40.0, 20.0, 10.0])
    pop_m = pop_f * 1.0
    # no fertility to simplify
    fert = np.zeros_like(ages, dtype=float)
    # survival: everyone survives except age 0 has 0.5 survival
    surv = np.ones_like(ages, dtype=float)
    surv[0] = 0.5
    # migration: add 10 people to age 2 female, remove 5 from male age 3
    mig_f = np.zeros_like(ages, dtype=float)
    mig_m = np.zeros_like(ages, dtype=float)
    mig_f[2] = 10.0
    mig_m[3] = -5.0

    model = CohortComponentModel(max_age=max_age)
    out = model.project(years=1, pop_female=pop_f, fertility=fert, survival_female=surv, pop_male=pop_m, survival_male=surv, mig_female=mig_f, mig_male=mig_m)

    # births zero
    assert out['births'][1] == 0.0
    # check migration applied: age 2 female in year1 should equal survivors from age1 + mig_f[2]
    expected_age2_f = pop_f[1] * surv[1] + mig_f[2]
    assert abs(out['age_female'][1][2] - expected_age2_f) < 1e-6
    # check male age3 migration
    expected_age3_m = pop_m[2] * surv[2] + mig_m[3]
    assert abs(out['age_male'][1][3] - expected_age3_m) < 1e-6
