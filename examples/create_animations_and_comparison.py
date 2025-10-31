import os
import sys
from PIL import Image
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_io.data_loader import load_from_file
from models.cohort_component import CohortComponentModel


def make_gif_from_pngs(png_dir, out_path, duration=200):
    # sort files by numeric index extracted from filename (e.g. year_0.png -> 0)
    import re
    def extract_index(name):
        m = re.search(r"(\d+)", name)
        return int(m.group(1)) if m else -1

    files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
    files.sort(key=extract_index)
    files = [os.path.join(png_dir, f) for f in files]
    if not files:
        raise FileNotFoundError(f'No PNG files found in {png_dir}')
    frames = []
    for f in files:
        img = Image.open(f).convert('RGBA')
        frames.append(img)
    # save as GIF
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    return out_path


def run_projection_totals(csv_path):
    data = load_from_file(csv_path)
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
    return out['years'], out['total']


def main():
    base_out = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs_images'))
    pos_pyr_dir = os.path.join(base_out, 'positive', 'pyramids')
    neg_pyr_dir = os.path.join(base_out, 'negative', 'pyramids')
    os.makedirs(base_out, exist_ok=True)

    # Create GIFs
    pos_gif = os.path.join(base_out, 'positive_pyramids.gif')
    neg_gif = os.path.join(base_out, 'negative_pyramids.gif')
    if os.path.isdir(pos_pyr_dir):
        make_gif_from_pngs(pos_pyr_dir, pos_gif)
        print('Saved', pos_gif)
    else:
        print('Positive pyramids directory not found:', pos_pyr_dir)

    if os.path.isdir(neg_pyr_dir):
        make_gif_from_pngs(neg_pyr_dir, neg_gif)
        print('Saved', neg_gif)
    else:
        print('Negative pyramids directory not found:', neg_pyr_dir)

    # Plot combined total population comparison by re-running projections
    pos_csv = os.path.join('data', 'example_population_positive.csv')
    neg_csv = os.path.join('data', 'example_population_negative.csv')
    years_pos, total_pos = run_projection_totals(pos_csv)
    years_neg, total_neg = run_projection_totals(neg_csv)

    # assume years align
    plt.figure(figsize=(8, 4))
    plt.plot(years_pos, total_pos, label='positive', marker='o')
    plt.plot(years_neg, total_neg, label='negative', marker='o')
    plt.xlabel('Year index (0=base 2020)')
    plt.ylabel('Total population')
    plt.title('Total population comparison: positive vs negative (50 years)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.4)
    out_cmp = os.path.join(base_out, 'total_population_comparison.png')
    plt.tight_layout()
    plt.savefig(out_cmp)
    plt.close()
    print('Saved', out_cmp)


if __name__ == '__main__':
    main()
