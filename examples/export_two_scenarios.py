import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel
from examples.export_images_only import save_images_only


def run_scenario(path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = load_from_file(path)
    max_age = data['max_age']
    model = CohortComponentModel(max_age=max_age)

    proj_kwargs = dict(
        years=50,
        pop_female=data['pop_female'],
        fertility=data['fertility'],
        pop_male=data.get('pop_male'),
        mig_female=data.get('mig_female'),
        mig_male=data.get('mig_male'),
    )

    # survival or death_prob
    if 'death_prob_female' in data:
        proj_kwargs['death_prob_female'] = data['death_prob_female']
        proj_kwargs['death_prob_male'] = data['death_prob_male']
    else:
        proj_kwargs['survival_female'] = data['survival_female']
        proj_kwargs['survival_male'] = data['survival_male']

    # optional fertility metadata
    if 'fertility_annual_factor' in data and data.get('fertility_annual_factor') is not None:
        proj_kwargs['fertility_annual_factor'] = data['fertility_annual_factor']
    if 'fertility_decline_years' in data and data.get('fertility_decline_years') is not None:
        proj_kwargs['fertility_decline_years'] = data['fertility_decline_years']

    out = model.project(**proj_kwargs)

    # reuse save_images_only to write outputs to out_dir
    total_png, pyramids_dir = save_images_only(data, out, out_dir=out_dir)
    print(f'Saved total population plot: {total_png}')
    print(f'Saved pyramids in: {pyramids_dir}')


def main():
    # assume CSV files placed in data/ and suffixed .csv
    pos_csv = 'data/example_population_positive.csv'
    neg_csv = 'data/example_population_negative.csv'

    if not os.path.exists(pos_csv):
        raise FileNotFoundError(f'Positive scenario file not found: {pos_csv}')
    if not os.path.exists(neg_csv):
        raise FileNotFoundError(f'Negative scenario file not found: {neg_csv}')

    run_scenario(pos_csv, out_dir='outputs_images/positive')
    run_scenario(neg_csv, out_dir='outputs_images/negative')


if __name__ == '__main__':
    main()
