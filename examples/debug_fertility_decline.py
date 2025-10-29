import sys
sys.path.insert(0, r'D:/Codes/git/population-prediction-model')
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel
import numpy as np

path = 'data/example_population_full.csv'
data = load_from_file(path)
max_age = data['max_age']
print('max_age', max_age)
print('fertility has NaN?', np.isnan(data['fertility']).any())
print('fertility sum:', np.nansum(data['fertility']))
print('survival_female has NaN?', np.isnan(data.get('survival_female', np.array([]))).any())
print('survival_male has NaN?', np.isnan(data.get('survival_male', np.array([]))).any())

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
print('births array:', out['births'])
