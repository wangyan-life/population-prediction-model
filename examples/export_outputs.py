import os
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel
import numpy as np
import matplotlib.pyplot as plt


def save_csv_pop_age_year(out, path):
    # out['age_female'] is list of arrays per year
    years = out['years']
    ages = np.arange(len(out['age_female'][0]))
    rows = []
    for i, y in enumerate(years):
        f = out['age_female'][i]
        m = out['age_male'][i]
        for a in ages:
            rows.append((y, a, f[a], m[a]))
    import csv
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['year', 'age', 'female_pop', 'male_pop'])
        writer.writerows(rows)


def save_csv_deaths_age_year(out, path):
    years = out['years']
    ages = np.arange(len(out['deaths_by_age_f'][0]))
    rows = []
    for i, y in enumerate(years):
        df = out['deaths_by_age_f'][i]
        dm = out['deaths_by_age_m'][i]
        for a in ages:
            rows.append((y, a, df[a], dm[a]))
    import csv
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['year', 'age', 'deaths_female', 'deaths_male'])
        writer.writerows(rows)


def plot_age_pyramid(year_index, out, outdir):
    f = out['age_female'][year_index]
    m = out['age_male'][year_index]
    ages = np.arange(len(f))
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.barh(ages, -m, color='steelblue', label='male')
    ax.barh(ages, f, color='salmon', label='female')
    ax.set_xlabel('Population')
    ax.set_ylabel('Age')
    ax.set_yticks(ages[::5])
    ax.legend()
    ax.set_title(f'Age pyramid year {out["years"][year_index]}')
    path = os.path.join(outdir, f'pyramid_year_{out["years"][year_index]}.png')
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    path = 'data/example_population_full.csv'
    data = load_from_file(path)
    max_age = data['max_age']
    model = CohortComponentModel(max_age=max_age)

    out = model.project(
        years=5,
        pop_female=data['pop_female'],
        fertility=data['fertility'],
        death_prob_female=data.get('death_prob_female'),
        death_prob_male=data.get('death_prob_male'),
        pop_male=data['pop_male'],
        mig_female=data['mig_female'],
        mig_male=data['mig_male'],
    )

    os.makedirs('outputs', exist_ok=True)
    pop_csv = 'outputs/pop_by_age_year.csv'
    deaths_csv = 'outputs/deaths_by_age_year.csv'
    save_csv_pop_age_year(out, pop_csv)
    save_csv_deaths_age_year(out, deaths_csv)

    # generate pyramids for each year
    for i in range(len(out['years'])):
        plot_age_pyramid(i, out, 'outputs')

    print('Wrote:', pop_csv, deaths_csv)


if __name__ == '__main__':
    main()
