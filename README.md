# population-prediction-model
人口预测模型，预测人口数量、性别比例、年龄结构等变化

# 数据来源
1. 第七次人口普查主要数据：https://www.stats.gov.cn/sj/pcsj/rkpc/d7c/202303/P020230301403217959330.pdf
2. 中国人口普查年鉴2020（第七次人口普查全数据）：https://www.stats.gov.cn/sj/pcsj/rkpc/7rp/zk/indexch.htm
3. 中国历年净移民人口数量统计（World Bank）：https://data.worldbank.org.cn/indicator/SM.POP.NETM?end=2024&locations=CN&start=2008

## 模型说明（中文）

### 模型功能概述
- 本仓库实现了一个按年龄分组的 Cohort-component（队列成分）人口预测模型。
- 主要产出：按年的人口总量、按年龄的性别结构、年度出生数、年度死亡数、按年龄的死亡人数等。

### 主要参数与含义
- `max_age`：最大年龄（模型在 0...max_age 的单岁年龄组上运行，max_age 为开龄组的上限）。
- `pop_female` / `pop_male`：基年按年龄的人口向量（长度为 `max_age+1`）。
- `fertility`：按年龄的年龄别生育率（ASFR，单位：每名妇女每年出生数）。用于计算年度出生数（ASFR * 女性人数）。
- `sex_ratio_at_birth`（模型构造器参数）：出生性别比（默认 1.05，表示男/女 = 1.05）。
- `survival_female` / `survival_male`：按年龄的年存活概率（s_x，0-1）。
- `death_prob_female` / `death_prob_male`：按年龄的年死亡概率 q_x（模型内部会转换为 s_x = 1 - q_x）。
- `mig_female` / `mig_male`：按年龄的净迁移人数（可为负值，表示净流出），默认 0。
- `years`：投影年份数（整数，模型会返回长度为 `years+1` 的年份序列，包含基年）。
- `fertility_annual_factor`（可选）：用于模拟前若干年生育率逐年按常数比例下降的乘数，例如 0.9 表示下一年为上一年的 0.9 倍。
- `fertility_decline_years`（可选）：配合 `fertility_annual_factor`，表示生育率下降持续的年数（例如 5 表示前 5 年按因子衰减，第 6 年起固定）。

### 输出形式（主要字段）
- `years`：年份索引（0=基年）。
- `total`：每年总人口数（数值数组）。
- `births`：每年出生数（数值数组）。
- `deaths`：每年死亡数（数值数组）。
- `age_female` / `age_male`：每年按年龄的人口数组列表。
- `deaths_by_age_f` / `deaths_by_age_m`：每年按年龄的死亡人数数组列表。

## 快速使用（命令示例，PowerShell）
- 运行单个示例并打印简要摘要：
```powershell
python -c "import sys; sys.path.insert(0, r'D:/Codes/git/population-prediction-model'); from examples.run_from_csv import main; main()"
```
- 导出 50 年仅图片（默认读取 `data/example_population_full.csv`）：
```powershell
python -c "import sys; sys.path.insert(0, r'D:/Codes/git/population-prediction-model'); from examples.export_images_only import main; main()"
```
- 对比正/负两个场景并生成图片：
```powershell
python -c "import sys; sys.path.insert(0, r'D:/Codes/git/population-prediction-model'); from examples.export_two_scenarios import main; main()"
```
- 生成动画与总人口对比图（在 `outputs_images/` 生成 GIF 与 PNG）：
```powershell
python -c "import sys; sys.path.insert(0, r'D:/Codes/git/population-prediction-model'); from examples.create_animations_and_comparison import main; main()"
```
- 生成并更新 release 用的统计摘要（会写入 `release_notes_v4.md`）：
```powershell
python -c "import sys; sys.path.insert(0, r'D:/Codes/git/population-prediction-model'); from examples.summary_for_release_v4 import main; main()"
```

## v4.0.0 Release 预测摘要（基于仓库的 `example_population_positive.csv` 与 `example_population_negative.csv`，基年 2020，投影至 2070）
以下数值来源于仓库自动生成的 release 说明（已同步到 Release v4.0.0）：

### Positive 场景
- 基年人口（2020）：1,443,555,766
- 2070 年人口：636,885,855（绝对变化 -806,669,911，下降 -55.88%）
- 峰值人口：1,443,555,766（发生在 2020 年）
- 2025–2030 年每年出生数：
	- 2025: 7,205,670
	- 2026: 6,898,649
	- 2027: 6,602,774
	- 2028: 6,327,213
	- 2029: 6,075,767
	- 2030: 5,852,165
- 2025–2030 年累计出生：38,962,239

### Negative 场景
- 基年人口（2020）：1,254,013,417
- 2070 年人口：536,466,397（绝对变化 -717,547,020，下降 -57.22%）
- 峰值人口：1,254,013,417（发生在 2020 年）
- 2025–2030 年每年出生数：
	- 2025: 5,797,391
	- 2026: 5,549,788
	- 2027: 5,311,178
	- 2028: 5,088,944
	- 2029: 4,886,148
	- 2030: 4,705,794
- 2025–2030 年累计出生：31,339,242

（更多指标与完整表格见仓库根目录 `release_notes_v4.md` 与 Release 页面）

## 后续建议
- 若需对比更多情景或做不确定性分析，可把不同情景的 CSV 放到 `data/` 并使用 `examples/export_two_scenarios.py` 或自行编写批处理脚本。
- 若需把生成的图像发布到 Release，我可以替你打包并上传（已支持自动化流程）。
