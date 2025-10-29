"""Simple data loader to read population/ASFR/survival/migration from CSV/Excel.

This file is copied from io/data_loader.py to avoid conflict with stdlib 'io' package.
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
    surv_f = get_array('surv_female', default=None)
    surv_m = get_array('surv_male', default=None)
    # attempt to read death probability columns if present (common names)
    def find_death_prob():
        if 'death_prob_female' in df.columns:
            return df['death_prob_female'].to_numpy(dtype=float), df.get('death_prob_male', df['death_prob_female']).to_numpy(dtype=float)
        if 'q_female' in df.columns:
            return df['q_female'].to_numpy(dtype=float), df.get('q_male', df['q_female']).to_numpy(dtype=float)
        return None, None

    death_prob_f, death_prob_m = find_death_prob()

    # If survival not provided but death_prob provided, keep death_prob and leave surv as None
    if surv_f is None and death_prob_f is not None:
        surv_f = None
    else:
        # default survival to 1.0 if completely missing
        if surv_f is None:
            surv_f = np.full_like(ages, fill_value=1.0, dtype=float)
    if surv_m is None and death_prob_m is not None:
        surv_m = None
    else:
        if surv_m is None:
            surv_m = surv_f.copy()

    mig_f = get_array('mig_female', default=0.0)
    mig_m = get_array('mig_male', default=0.0)

    # Optional metadata fields: read first non-null value if present
    def read_scalar_column(col_name, cast_func=float):
        if col_name in df.columns:
            series = df[col_name].dropna()
            if not series.empty:
                try:
                    return cast_func(series.iloc[0])
                except Exception:
                    # fallback: try converting via float then to int if needed
                    if cast_func is int:
                        return int(float(series.iloc[0]))
                    return float(series.iloc[0])
        return None

    fertility_annual_factor = read_scalar_column('fertility_annual_factor', float)
    fertility_decline_years = read_scalar_column('fertility_decline_years', int)

    # Validate lengths are max_age+1 and ages are contiguous 0..max_age
    expected_ages = np.arange(0, max_age + 1)
    if not np.array_equal(ages, expected_ages):
        raise ValueError(f"Ages must be contiguous 0..max_age. Found ages: {ages}")

    out = {
        'max_age': max_age,
        'pop_female': female_pop,
        'pop_male': male_pop,
        'fertility': asfr,
        'survival_female': surv_f,
        'survival_male': surv_m,
        'mig_female': mig_f,
        'mig_male': mig_m,
    }
    # attach optional fertility trend metadata if present
    if fertility_annual_factor is not None:
        out['fertility_annual_factor'] = float(fertility_annual_factor)
    if fertility_decline_years is not None:
        out['fertility_decline_years'] = int(fertility_decline_years)
    if death_prob_f is not None:
        out['death_prob_female'] = np.asarray(death_prob_f, dtype=float)
        out['death_prob_male'] = np.asarray(death_prob_m, dtype=float)

    return out
