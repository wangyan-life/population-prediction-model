import os
import numpy as np
import pandas as pd
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel


def save_outputs(data, out, out_dir='outputs'):
    os.makedirs(out_dir, exist_ok=True)
    pyramids_dir = os.path.join(out_dir, 'pyramids')
    os.makedirs(pyramids_dir, exist_ok=True)

    years = out['years']
    max_age = data['max_age']
    ages = np.arange(0, max_age + 1)

    # Build pop_by_age_year dataframe
    rows = []
    for i, y in enumerate(years):
        f = out['age_female'][i]
        m = out['age_male'][i]
        for a in ages:
            rows.append({'year': y, 'age': int(a), 'female': float(f[a]), 'male': float(m[a]), 'total': float(f[a] + m[a])})
    df_pop = pd.DataFrame(rows)
    pop_csv = os.path.join(out_dir, 'pop_by_age_year.csv')
    df_pop.to_csv(pop_csv, index=False)

    # Build deaths_by_age_year dataframe
    rows = []
    for i, y in enumerate(years):
        df_age_f = out['deaths_by_age_f'][i]
        df_age_m = out['deaths_by_age_m'][i]
        for a in ages:
            rows.append({'year': y, 'age': int(a), 'deaths_f': float(df_age_f[a]), 'deaths_m': float(df_age_m[a]), 'deaths_total': float(df_age_f[a] + df_age_m[a])})
    df_deaths = pd.DataFrame(rows)
    deaths_csv = os.path.join(out_dir, 'deaths_by_age_year.csv')
    df_deaths.to_csv(deaths_csv, index=False)

    # Create pyramids per year
    try:
        import matplotlib.pyplot as plt

        for i, y in enumerate(years):
            f = out['age_female'][i]
            m = out['age_male'][i]
            # plot pyramid
            fig, ax = plt.subplots(figsize=(6, 8))
            # plot males to left (negative)
            ax.barh(ages, -m, color='steelblue', label='male')
            ax.barh(ages, f, color='lightcoral', label='female')
            ax.set_xlabel('Population')
            ax.set_ylabel('Age')
            ax.set_title(f'Population pyramid year {y}')
            ax.legend()
            ax.grid(axis='x', linestyle='--', alpha=0.3)
            plt.tight_layout()
            fname = os.path.join(pyramids_dir, f'year_{y}.png')
            fig.savefig(fname)
            plt.close(fig)
    except Exception as e:
        print('Matplotlib not available or failed to plot:', e)

    return pop_csv, deaths_csv, pyramids_dir


def main():
    path = 'data/example_population_full.csv'
    data = load_from_file(path)
    max_age = data['max_age']
    model = CohortComponentModel(max_age=max_age)

    proj_kwargs = dict(
        years=5,
        pop_female=data['pop_female'],
        fertility=data['fertility'],
        pop_male=data['pop_male'],
        mig_female=data['mig_female'],
        mig_male=data['mig_male'],
    )

    # prefer death_prob if present
    if 'death_prob_female' in data:
        proj_kwargs['death_prob_female'] = data['death_prob_female']
        proj_kwargs['death_prob_male'] = data['death_prob_male']
    else:
        proj_kwargs['survival_female'] = data['survival_female']
        proj_kwargs['survival_male'] = data['survival_male']

    out = model.project(**proj_kwargs)

    pop_csv, deaths_csv, pyramids_dir = save_outputs(data, out, out_dir='outputs')
    print('Saved:', pop_csv)
    print('Saved:', deaths_csv)
    print('Pyramids saved in:', pyramids_dir)


if __name__ == '__main__':
    main()
