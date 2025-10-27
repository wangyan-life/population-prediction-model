"""Simple data loader to read population/ASFR/survival/migration from CSV/Excel.

Expected minimal input format (CSV or Excel sheet with columns):
 - age: integer ages 0..max_age
 - female_pop, male_pop (optional)
 - asfr (optional)  -- age-specific fertility rate for females
 - surv_female, surv_male (optional) -- annual survival probability by age
 - mig_female, mig_male (optional) -- net migration counts by age for a single year

The loader returns a dict with numpy arrays keyed to feed into CohortComponentModel.project.
"""
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np


def load_from_file(path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    df = pd.read_excel(path, sheet_name=sheet_name) if path.lower().endswith(('.xls', '.xlsx')) else pd.read_csv(path)

    if 'age' not in df.columns:
        raise ValueError("Input file must contain 'age' column with integer ages.")

    df = df.sort_values('age')
    ages = df['age'].astype(int).to_numpy()
    max_age = int(ages.max())

    def get_array(col, default=0.0):
        if col in df.columns:
            return df[col].to_numpy(dtype=float)
        else:
            return np.full_like(ages, fill_value=default, dtype=float)

    female_pop = get_array('female_pop', default=0.0)
    male_pop = get_array('male_pop', default=female_pop * 1.0)
    asfr = get_array('asfr', default=0.0)
    surv_f = get_array('surv_female', default=1.0)
    surv_m = get_array('surv_male', default=surv_f)
    mig_f = get_array('mig_female', default=0.0)
    mig_m = get_array('mig_male', default=0.0)

    # Validate lengths are max_age+1 and ages are contiguous 0..max_age
    expected_ages = np.arange(0, max_age + 1)
    if not np.array_equal(ages, expected_ages):
        raise ValueError(f"Ages must be contiguous 0..max_age. Found ages: {ages}")

    return {
        'max_age': max_age,
        'pop_female': female_pop,
        'pop_male': male_pop,
        'fertility': asfr,
        'survival_female': surv_f,
        'survival_male': surv_m,
        'mig_female': mig_f,
        'mig_male': mig_m,
    }
