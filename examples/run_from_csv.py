from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel


def main():
    path = 'data/example_population_full.csv'
    data = load_from_file(path)
    max_age = data['max_age']
    model = CohortComponentModel(max_age=max_age)

    out = model.project(
        years=10,
        pop_female=data['pop_female'],
        fertility=data['fertility'],
        death_prob_female=data.get('death_prob_female'),
        death_prob_male=data.get('death_prob_male'),
        pop_male=data['pop_male'],
        mig_female=data['mig_female'],
        mig_male=data['mig_male'],
    )

    print(f"Years simulated: {len(out['years']) - 1}")
    print(f"Initial total population: {out['total'][0]:,.1f}")
    print(f"Final total population: {out['total'][-1]:,.1f}")
    print(f"Total births over period: {out['births'].sum():,.1f}")
    print(f"Total deaths over period: {out['deaths'].sum():,.1f}")
    # show deaths by age for final year (sum female+male)
    deaths_f_last = out['deaths_by_age_f'][-1]
    deaths_m_last = out['deaths_by_age_m'][-1]
    print(f"Deaths by age (final year) total: {deaths_f_last.sum() + deaths_m_last.sum():,.1f}")


if __name__ == '__main__':
    main()
