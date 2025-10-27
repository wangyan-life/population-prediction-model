import numpy as np
from models.cohort_component import CohortComponentModel, make_simple_example


def test_projection_basic():
    max_age = 80
    pop_f, pop_m, fertility, survival = make_simple_example(max_age=max_age)
    model = CohortComponentModel(max_age=max_age, sex_ratio_at_birth=1.05)
    out = model.project(years=10, pop_female=pop_f, fertility=fertility, survival_female=survival, pop_male=pop_m, survival_male=survival)

    # basic checks
    assert len(out['years']) == 11
    assert out['total'][0] > 0
    assert out['births'].shape[0] == 11
    # births should be non-negative
    assert np.all(out['births'] >= 0)


def test_shape_mismatch_raises():
    max_age = 50
    pop_f, pop_m, fertility, survival = make_simple_example(max_age=100)
    model = CohortComponentModel(max_age=max_age)
    try:
        model.project(years=1, pop_female=pop_f, fertility=fertility, survival_female=survival)
        raised = False
    except ValueError:
        raised = True
    assert raised, "Expected ValueError for shape mismatch"
