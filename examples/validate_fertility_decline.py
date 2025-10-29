import sys
sys.path.insert(0, r'D:/Codes/git/population-prediction-model')
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel

path = 'data/example_population_full.csv'
data = load_from_file(path)
max_age = data['max_age']
model = CohortComponentModel(max_age=max_age)

proj_kwargs = dict(
    years=10,
    pop_female=data['pop_female'],
    fertility=data['fertility'],
    pop_male=data.get('pop_male'),
    mig_female=data.get('mig_female'),
    mig_male=data.get('mig_male'),
    survival_female=data.get('survival_female'),
    survival_male=data.get('survival_male'),
    fertility_annual_factor=0.9,
    fertility_decline_years=5,
)

out = model.project(**proj_kwargs)

births = out['births']
base_year = 2020
print('Requested years 2025-2030 (with 0.9 annual factor for first 5 years):')
for y in range(2025, 2031):
    idx = y - base_year
    if 0 <= idx < len(births):
        print(f'{y}: {int(round(births[idx]))}')
    else:
        print(f'{y}: out of range')
