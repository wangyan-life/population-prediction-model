import numpy as np
from models.cohort_component import CohortComponentModel, make_simple_example


def test_deathprob_conversion_equivalence():
    max_age = 30
    pop_f, pop_m, fertility, survival = make_simple_example(max_age=max_age)
    # create death_prob as q = 1 - survival
    death_prob = 1.0 - survival

    model = CohortComponentModel(max_age=max_age)

    out_surv = model.project(years=5, pop_female=pop_f, fertility=fertility, survival_female=survival, pop_male=pop_m, survival_male=survival)
    out_q = model.project(years=5, pop_female=pop_f, fertility=fertility, death_prob_female=death_prob, death_prob_male=death_prob, pop_male=pop_m)

    # totals should be equal
    assert np.allclose(out_surv['total'], out_q['total'])
    assert np.allclose(out_surv['births'], out_q['births'])
