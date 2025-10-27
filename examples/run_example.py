"""
Small example to run the cohort-component model and print summary outputs.
一个运行 Cohort-component 模型并打印摘要输出的小示例。
"""
from models.cohort_component import CohortComponentModel, make_simple_example


def main():
    max_age = 100
    pop_f, pop_m, fertility, survival = make_simple_example(max_age=max_age)
    model = CohortComponentModel(max_age=max_age, sex_ratio_at_birth=1.05)
    out = model.project(years=50, pop_female=pop_f, fertility=fertility, survival_female=survival, pop_male=pop_m, survival_male=survival)

    print(f"Years: {len(out['years'])}")
    print(f"Initial total: {out['total'][0]:.1f}")
    print(f"Final total: {out['total'][-1]:.1f}")
    print(f"Total births (sum): {out['births'].sum():.1f}")


if __name__ == '__main__':
    main()
