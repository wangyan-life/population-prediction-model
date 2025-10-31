import os
import numpy as np
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel


def save_images_only(data, out, out_dir='outputs_images'):
    os.makedirs(out_dir, exist_ok=True)
    pyramids_dir = os.path.join(out_dir, 'pyramids')
    os.makedirs(pyramids_dir, exist_ok=True)

    years = out['years']
    max_age = data['max_age']
    ages = np.arange(0, max_age + 1)

    # Total population over time plot
    total = out['total']
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(years, total, marker='o')
        ax.set_xlabel('Year index (0=base)')
        ax.set_ylabel('Total population')
        ax.set_title('Total population over time (50-year projection)')
        ax.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()
        total_png = os.path.join(out_dir, 'total_population_50yr.png')
        fig.savefig(total_png)
        plt.close(fig)
    except Exception as e:
        raise RuntimeError(f'Failed to plot total population: {e}')

    # Age pyramids per year
    try:
        import matplotlib.pyplot as plt
        # compute a global maximum for the x-axis so all frames use identical scale
        all_max = 0.0
        for i in range(len(years)):
            f = out['age_female'][i]
            m = out['age_male'][i]
            all_max = max(all_max, float(np.max(f)), float(np.max(m)))
        xlim = ( -all_max * 1.2, all_max * 1.2 )

        for i, y in enumerate(years):
            f = out['age_female'][i]
            m = out['age_male'][i]
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(ages, -m, color='steelblue')
            ax.barh(ages, f, color='lightcoral')
            ax.set_xlabel('Population')
            ax.set_ylabel('Age')
            ax.set_title(f'Population pyramid year {y}')
            ax.set_xlim(xlim)
            xt = ax.get_xticks()
            # ensure ticks are fixed before setting custom labels to avoid Matplotlib warnings
            ax.set_xticks(xt)
            ax.set_xticklabels([str(int(abs(x))) for x in xt])
            ax.grid(axis='x', linestyle='--', alpha=0.3)
            plt.tight_layout()
            fname = os.path.join(pyramids_dir, f'year_{y}.png')
            fig.savefig(fname)
            plt.close(fig)
    except Exception as e:
        raise RuntimeError(f'Failed to create pyramid images: {e}')

    return total_png, pyramids_dir


def main():
    path = 'data/example_population_full.csv'
    data = load_from_file(path)
    max_age = data['max_age']
    model = CohortComponentModel(max_age=max_age)

    proj_kwargs = dict(
        years=50,
        pop_female=data['pop_female'],
        fertility=data['fertility'],
        pop_male=data['pop_male'],
        mig_female=data['mig_female'],
        mig_male=data['mig_male'],
    )

    if 'death_prob_female' in data:
        proj_kwargs['death_prob_female'] = data['death_prob_female']
        proj_kwargs['death_prob_male'] = data['death_prob_male']
    else:
        proj_kwargs['survival_female'] = data['survival_female']
        proj_kwargs['survival_male'] = data['survival_male']

    # Pass optional fertility trend metadata from loader if present
    if 'fertility_annual_factor' in data and data.get('fertility_annual_factor') is not None:
        proj_kwargs['fertility_annual_factor'] = data['fertility_annual_factor']
    if 'fertility_decline_years' in data and data.get('fertility_decline_years') is not None:
        proj_kwargs['fertility_decline_years'] = data['fertility_decline_years']

    out = model.project(**proj_kwargs)

    total_png, pyramids_dir = save_images_only(data, out, out_dir='outputs_images')
    print('Saved total population plot:', total_png)
    print('Saved pyramids in:', pyramids_dir)


if __name__ == '__main__':
    main()
