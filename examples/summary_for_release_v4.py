import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel


def summarize(path, label):
    data = load_from_file(path)
    model = CohortComponentModel(max_age=data['max_age'])
    proj_kwargs = dict(
        years=50,
        pop_female=data['pop_female'],
        fertility=data['fertility'],
        pop_male=data.get('pop_male'),
        mig_female=data.get('mig_female'),
        mig_male=data.get('mig_male'),
    )
    if 'death_prob_female' in data:
        proj_kwargs['death_prob_female'] = data['death_prob_female']
        proj_kwargs['death_prob_male'] = data['death_prob_male']
    else:
        proj_kwargs['survival_female'] = data['survival_female']
        proj_kwargs['survival_male'] = data['survival_male']
    if 'fertility_annual_factor' in data and data.get('fertility_annual_factor') is not None:
        proj_kwargs['fertility_annual_factor'] = data['fertility_annual_factor']
    if 'fertility_decline_years' in data and data.get('fertility_decline_years') is not None:
        proj_kwargs['fertility_decline_years'] = data['fertility_decline_years']

    out = model.project(**proj_kwargs)
    births = out['births']
    total = out['total']
    years = out['years']
    age_female = out['age_female']
    age_male = out['age_male']

    base_year = 2020
    # 2025..2030 inclusive
    y0 = 2025
    y1 = 2030
    idx0 = y0 - base_year
    idx1 = y1 - base_year
    births_slice = births[idx0:idx1+1]

    summary = {}
    summary['label'] = label
    summary['base_year'] = base_year
    summary['births_2025_2030'] = [int(round(float(b))) for b in births_slice]
    summary['births_2025_2030_total'] = int(round(float(np.sum(births_slice))))
    summary['pop_2020'] = int(round(float(total[0])))
    summary['pop_2070'] = int(round(float(total[-1])))
    summary['pop_change_abs'] = summary['pop_2070'] - summary['pop_2020']
    summary['pop_change_pct'] = round(100.0 * summary['pop_change_abs'] / max(1, summary['pop_2020']), 2)

    # peak population year
    peak_idx = int(np.argmax(total))
    summary['peak_year'] = base_year + peak_idx
    summary['peak_pop'] = int(round(float(np.max(total))))

    # compute median age per year (simple integer median from age distribution)
    medians = []
    for af, am in zip(age_female, age_male):
        pop = np.asarray(af) + np.asarray(am)
        cum = np.cumsum(pop)
        half = cum[-1] / 2.0
        median_age = int(np.searchsorted(cum, half))
        medians.append(int(median_age))
    summary['median_age_2020'] = medians[0]
    summary['median_age_2070'] = medians[-1]

    # dependency ratios: youth 0-14, working 15-64, elderly 65+
    def dependency_indices(max_age):
        ages = np.arange(0, max_age + 1)
        youth_mask = (ages <= 14)
        working_mask = (ages >= 15) & (ages <= 64)
        elderly_mask = (ages >= 65)
        return youth_mask, working_mask, elderly_mask

    max_age = data['max_age']
    youth_mask, working_mask, elderly_mask = dependency_indices(max_age)
    # compute dependency ratios for first and last year
    def compute_dependency(af, am):
        pop = np.asarray(af) + np.asarray(am)
        youth = float(np.sum(pop[youth_mask]))
        working = float(np.sum(pop[working_mask]))
        elderly = float(np.sum(pop[elderly_mask]))
        # avoid division by zero
        working = working if working > 0 else 1.0
        youth_dep = 100.0 * youth / working
        elderly_dep = 100.0 * elderly / working
        total_dep = 100.0 * (youth + elderly) / working
        return youth_dep, elderly_dep, total_dep

    y_dep0, e_dep0, t_dep0 = compute_dependency(age_female[0], age_male[0])
    y_dep1, e_dep1, t_dep1 = compute_dependency(age_female[-1], age_male[-1])
    summary['dependency_2020'] = {'youth_pct': round(y_dep0, 2), 'elderly_pct': round(e_dep0, 2), 'total_pct': round(t_dep0, 2)}
    summary['dependency_2070'] = {'youth_pct': round(y_dep1, 2), 'elderly_pct': round(e_dep1, 2), 'total_pct': round(t_dep1, 2)}

    # compute TFR per year: sum ASFR across reproductive ages (15-49) with fertility trend if present
    fert = np.asarray(data['fertility'])
    fert_ages = np.arange(0, len(fert))
    fert_mask = (fert_ages >= 15) & (fert_ages <= 49)
    tfrs = []
    factor = data.get('fertility_annual_factor', None)
    decline_years = data.get('fertility_decline_years', 0) or 0
    for i, yr in enumerate(years):
        # year 0 uses base fertility; subsequent years scale by factor ** min(year_index, decline_years)
        if factor is not None and i > 0:
            exp = min(i, int(decline_years))
            scale = float(factor) ** exp
        else:
            scale = 1.0
        tfr = float(np.sum(fert[fert_mask] * scale))
        tfrs.append(round(tfr, 4))
    # attach a few TFR values
    summary['tfr_2020'] = tfrs[0]
    summary['tfr_2025'] = tfrs[5] if len(tfrs) > 5 else None
    summary['tfr_2030'] = tfrs[10] if len(tfrs) > 10 else None
    summary['tfr_series'] = tfrs

    return summary


def make_markdown(pos, neg):
    md = []
    md.append('# Release summary: v4.0.0')
    md.append('Generated statistics for positive and negative scenarios (base year 2020).')
    md.append('')
    for s in (pos, neg):
        md.append(f"## {s['label'].capitalize()} scenario")
        md.append(f"- Population 2020: {s['pop_2020']:,}")
        md.append(f"- Population 2070: {s['pop_2070']:,} ({s['pop_change_abs']:+,} / {s['pop_change_pct']}% change)")
        md.append(f"- Peak population: {s['peak_pop']:,} in {s['peak_year']}")
        md.append('- Births by year (2025–2030):')
        for y, b in zip(range(2025, 2031), s['births_2025_2030']):
            md.append(f"  - {y}: {b:,}")
        md.append(f"- Total births 2025–2030: {s['births_2025_2030_total']:,}")
        md.append('')

    # comparison snippet
    md.append('## Comparison notes')
    diff = neg['pop_2070'] - pos['pop_2070']
    md.append(f"- Difference in 2070 population (negative - positive): {diff:,}")
    md.append('')
    return '\n'.join(md)


def main():
    pos_csv = os.path.join('data', 'example_population_positive.csv')
    neg_csv = os.path.join('data', 'example_population_negative.csv')
    pos = summarize(pos_csv, 'positive')
    neg = summarize(neg_csv, 'negative')
    md = make_markdown(pos, neg)
    out_file = os.path.join(os.path.dirname(__file__), '..', 'release_notes_v4.md')
    out_file = os.path.abspath(out_file)
    with open(out_file, 'w', encoding='utf8') as f:
        f.write(md)
    print('Wrote release notes to', out_file)
    print('\n---\n')
    print(md)


if __name__ == '__main__':
    main()
