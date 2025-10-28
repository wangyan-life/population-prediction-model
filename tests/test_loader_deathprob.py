import numpy as np
import pandas as pd
import tempfile
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel, make_simple_example


def test_loader_reads_death_prob_and_model_accepts(tmp_path):
    max_age = 10
    ages = np.arange(0, max_age + 1)
    pop_f = np.linspace(1000, 500, len(ages))
    pop_m = pop_f * 1.02
    # make survival and death_prob
    surv = np.clip(1.0 - (ages / 100.0) * 0.01, 0.5, 1.0)
    death_prob = 1.0 - surv

    df = pd.DataFrame({
        'age': ages,
        'female_pop': pop_f,
        'male_pop': pop_m,
        'asfr': np.zeros_like(ages, dtype=float),
        'death_prob_female': death_prob,
        'death_prob_male': death_prob,
    })

    p = tmp_path / "tmp_deathprob.csv"
    df.to_csv(p, index=False)

    data = load_from_file(str(p))
    model = CohortComponentModel(max_age=max_age)
    out_q = model.project(years=3, pop_female=data['pop_female'], fertility=data['fertility'], death_prob_female=data['death_prob_female'], death_prob_male=data['death_prob_male'], pop_male=data['pop_male'])

    # Now run with survival directly
    out_s = model.project(years=3, pop_female=data['pop_female'], fertility=data['fertility'], survival_female=surv, survival_male=surv, pop_male=data['pop_male'])

    assert np.allclose(out_q['total'], out_s['total'])
