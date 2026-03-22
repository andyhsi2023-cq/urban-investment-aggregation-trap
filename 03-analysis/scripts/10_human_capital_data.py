"""
10_human_capital_data.py
========================
目的：构建四国（中国、日本、美国、英国）的人力资本指数 H(t) 时序，
     以及劳动年龄人口占比时序，为 K* 估计做准备。

方法：
  - 平均受教育年限数据来源：UNDP HDR / Barro-Lee 数据集（硬编码关键年份）
  - 五年间隔数据线性插值为年度数据
  - H(t) = exp(phi * s(t))，phi = 0.10（Mincer 回报率）
  - 劳动年龄人口占比（15-64岁）：硬编码关键年份 + 线性插值

输出：
  - four_country_human_capital.csv — 四国人力资本面板数据
  - fig08_human_capital.png — 2子图: H(t)时序 + 劳动年龄人口占比

依赖包：pandas, numpy, matplotlib, scipy
"""

import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 0. 路径设置
# ============================================================

PROJECT_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
OUTPUT_CSV = PROJECT_DIR / "02-data/processed/four_country_human_capital.csv"
OUTPUT_FIG = PROJECT_DIR / "04-figures/drafts/fig08_human_capital.png"
MODELS_DIR = PROJECT_DIR / "03-analysis/models"
SIX_CURVES_DIR = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition")

# ============================================================
# 1. 平均受教育年限原始数据（硬编码，基于 UNDP HDR / Barro-Lee）
# ============================================================

# 单位：年
MYS_DATA = {
    "China": {
        1970: 3.0, 1975: 3.8, 1980: 4.7, 1985: 5.2,
        1990: 5.8, 1995: 6.4, 2000: 7.1, 2005: 7.7,
        2010: 8.2, 2015: 8.8, 2020: 9.4, 2024: 9.9,
    },
    "Japan": {
        1970: 8.2, 1975: 8.8, 1980: 9.5, 1985: 10.1,
        1990: 10.6, 1995: 11.1, 2000: 11.5, 2005: 11.8,
        2010: 12.1, 2015: 12.4, 2020: 12.8, 2024: 13.0,
    },
    "USA": {
        1970: 10.5, 1975: 11.0, 1980: 11.9, 1985: 12.2,
        1990: 12.4, 1995: 12.7, 2000: 13.0, 2005: 13.2,
        2010: 13.4, 2015: 13.6, 2020: 13.7, 2024: 13.8,
    },
    "UK": {
        1970: 8.5, 1975: 9.0, 1980: 9.8, 1985: 10.5,
        1990: 11.0, 1995: 11.6, 2000: 12.0, 2005: 12.3,
        2010: 12.8, 2015: 13.1, 2020: 13.4, 2024: 13.5,
    },
}

# ============================================================
# 2. 劳动年龄人口占比（15-64岁）原始数据（硬编码，粗略估计）
# ============================================================

LABOR_AGE_DATA = {
    "China": {
        1970: 56.0, 1975: 57.0, 1980: 60.0, 1985: 64.0,
        1990: 67.0, 1995: 68.5, 2000: 70.0, 2005: 72.0,
        2010: 74.0, 2015: 73.0, 2020: 70.0, 2024: 68.0,
    },
    "Japan": {
        1970: 69.0, 1975: 68.0, 1980: 68.0, 1985: 69.0,
        1990: 70.0, 1995: 69.5, 2000: 68.0, 2005: 66.0,
        2010: 64.0, 2015: 61.0, 2020: 59.0, 2024: 58.0,
    },
    "USA": {
        1970: 62.0, 1975: 63.0, 1980: 64.0, 1985: 65.0,
        1990: 66.0, 1995: 65.5, 2000: 66.0, 2005: 67.0,
        2010: 67.0, 2015: 66.0, 2020: 65.0, 2024: 65.0,
    },
    "UK": {
        1970: 63.0, 1975: 63.0, 1980: 64.0, 1985: 65.0,
        1990: 65.0, 1995: 65.0, 2000: 65.0, 2005: 66.0,
        2010: 66.0, 2015: 65.0, 2020: 64.0, 2024: 63.0,
    },
}

# Mincer 回报率
PHI = 0.10

# ============================================================
# 3. 线性插值函数
# ============================================================

def interpolate_to_annual(data_dict, year_min=1960, year_max=2024):
    """将稀疏年份数据线性插值为年度数据"""
    years = sorted(data_dict.keys())
    values = [data_dict[y] for y in years]

    # 使用 scipy 线性插值，允许外推到数据范围外（但我们会裁剪）
    f = interp1d(years, values, kind='linear', fill_value='extrapolate')

    # 生成年度序列（仅在数据范围内）
    actual_min = max(year_min, min(years))
    actual_max = min(year_max, max(years))
    annual_years = np.arange(actual_min, actual_max + 1)
    annual_values = f(annual_years)

    return annual_years, annual_values


# ============================================================
# 4. 构建年度面板
# ============================================================

all_rows = []

for country in ["China", "Japan", "USA", "UK"]:
    # 受教育年限插值
    mys_years, mys_vals = interpolate_to_annual(MYS_DATA[country])

    # 劳动年龄人口占比插值
    lab_years, lab_vals = interpolate_to_annual(LABOR_AGE_DATA[country])

    # 取两者共同的年份范围
    yr_min = max(mys_years.min(), lab_years.min())
    yr_max = min(mys_years.max(), lab_years.max())

    for yr in range(int(yr_min), int(yr_max) + 1):
        mys_idx = yr - int(mys_years.min())
        lab_idx = yr - int(lab_years.min())

        s = mys_vals[mys_idx]
        H = np.exp(PHI * s)
        labor_ratio = lab_vals[lab_idx]

        all_rows.append({
            'year': yr,
            'country': country,
            'mean_years_schooling': round(s, 2),
            'H_index': round(H, 4),
            'labor_age_ratio': round(labor_ratio, 2),
        })

df_hc = pd.DataFrame(all_rows)

# ============================================================
# 5. 提取城镇人口 Pu(t)（从各国 urban_q CSV + six-curves 主数据）
# ============================================================

print("=" * 60)
print("提取各国城镇人口数据...")
print("=" * 60)

# --- 中国：从 six-curves 主数据集提取 ---
china_master = pd.read_csv(
    SIX_CURVES_DIR / "02-data/processed/six_curves_master_dataset_processed.csv"
)
china_pop = china_master[['year', 'urban_population_10k', 'total_population_10k']].copy()
china_pop['urban_pop_mil'] = china_pop['urban_population_10k'] / 100  # 万人 -> 百万人
china_pop['country'] = 'China'
china_pop = china_pop[['year', 'country', 'urban_pop_mil']].dropna()
print(f"  中国: {china_pop.year.min()}-{china_pop.year.max()}, {len(china_pop)} 年")

# --- 日本：从 urban_q CSV 提取城镇化率，硬编码总人口，计算城镇人口 ---
japan_uq = pd.read_csv(MODELS_DIR / "japan_urban_q_timeseries.csv")
# 日本总人口（百万人，硬编码关键年份）
japan_total_pop = {
    1960: 93.4, 1965: 98.3, 1970: 104.3, 1975: 111.9, 1980: 117.1,
    1985: 121.0, 1990: 123.6, 1995: 125.6, 2000: 126.9, 2005: 127.8,
    2010: 128.1, 2015: 127.1, 2020: 125.8, 2023: 124.5,
}
jp_pop_years, jp_pop_vals = interpolate_to_annual(japan_total_pop, 1960, 2023)
jp_pop_series = pd.Series(jp_pop_vals, index=jp_pop_years.astype(int))

japan_pop = japan_uq[['year', 'urbanization_rate']].copy()
japan_pop['total_pop_mil'] = japan_pop['year'].map(jp_pop_series)
japan_pop['urban_pop_mil'] = japan_pop['total_pop_mil'] * japan_pop['urbanization_rate'] / 100
japan_pop['country'] = 'Japan'
japan_pop = japan_pop[['year', 'country', 'urban_pop_mil']].dropna()
print(f"  日本: {japan_pop.year.min()}-{japan_pop.year.max()}, {len(japan_pop)} 年")

# --- 美国：population_million 已在 CSV 中 ---
us_uq = pd.read_csv(MODELS_DIR / "us_urban_q_timeseries.csv")
us_pop = us_uq[['year', 'urbanization_rate', 'population_million']].copy()
us_pop['urban_pop_mil'] = us_pop['population_million'] * us_pop['urbanization_rate'] / 100
us_pop['country'] = 'USA'
us_pop = us_pop[['year', 'country', 'urban_pop_mil']].dropna()
print(f"  美国: {us_pop.year.min()}-{us_pop.year.max()}, {len(us_pop)} 年")

# --- 英国：population_million 已在 CSV 中 ---
uk_uq = pd.read_csv(MODELS_DIR / "uk_urban_q_timeseries.csv")
uk_pop = uk_uq[['year', 'urbanization_rate', 'population_million']].copy()
uk_pop['urban_pop_mil'] = uk_pop['population_million'] * uk_pop['urbanization_rate'] / 100
uk_pop['country'] = 'UK'
uk_pop = uk_pop[['year', 'country', 'urban_pop_mil']].dropna()
print(f"  英国: {uk_pop.year.min()}-{uk_pop.year.max()}, {len(uk_pop)} 年")

# 合并城镇人口到主数据框
pop_all = pd.concat([china_pop, japan_pop, us_pop, uk_pop], ignore_index=True)
df_hc = df_hc.merge(pop_all, on=['year', 'country'], how='left')

# 重排列顺序
df_hc = df_hc[['year', 'country', 'mean_years_schooling', 'H_index',
               'urban_pop_mil', 'labor_age_ratio']]

# ============================================================
# 6. 输出 CSV
# ============================================================

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df_hc.to_csv(OUTPUT_CSV, index=False)
print(f"\n已保存: {OUTPUT_CSV}")
print(f"总行数: {len(df_hc)}")
print(f"\n各国数据概览:")
for c in ["China", "Japan", "USA", "UK"]:
    sub = df_hc[df_hc.country == c]
    print(f"  {c}: {sub.year.min()}-{sub.year.max()}, "
          f"H: {sub.H_index.min():.3f}-{sub.H_index.max():.3f}, "
          f"urban_pop: {sub.urban_pop_mil.min():.1f}-{sub.urban_pop_mil.max():.1f} M (non-null: {sub.urban_pop_mil.notna().sum()})")

# ============================================================
# 7. 可视化：2 个子图
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# 颜色和样式定义
COLORS = {"China": "#E63946", "Japan": "#457B9D", "USA": "#2A9D8F", "UK": "#E9C46A"}
MARKERS = {"China": "o", "Japan": "s", "USA": "^", "UK": "D"}

# --- 子图 A: H(t) 时序对比 ---
ax = axes[0]
for country in ["China", "Japan", "USA", "UK"]:
    sub = df_hc[df_hc.country == country]
    ax.plot(sub.year, sub.H_index, color=COLORS[country],
            marker=MARKERS[country], markevery=5, markersize=5,
            linewidth=1.8, label=country)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Human Capital Index  H(t) = exp(0.10 * s)", fontsize=11)
ax.set_title("A. Human Capital Index by Country", fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(1970, 2025)

# 添加注释：中国的快速追赶
ax.annotate("China: rapid\ncatch-up phase",
            xy=(2005, df_hc[(df_hc.country == "China") & (df_hc.year == 2005)].H_index.values[0]),
            xytext=(1985, 2.0),
            arrowprops=dict(arrowstyle='->', color='gray', lw=1.2),
            fontsize=9, color='gray')

# --- 子图 B: 劳动年龄人口占比时序对比 ---
ax = axes[1]
for country in ["China", "Japan", "USA", "UK"]:
    sub = df_hc[df_hc.country == country]
    # 劳动年龄人口占比数据范围（取有数据的部分）
    sub_valid = sub[sub.labor_age_ratio.notna()]
    ax.plot(sub_valid.year, sub_valid.labor_age_ratio, color=COLORS[country],
            marker=MARKERS[country], markevery=5, markersize=5,
            linewidth=1.8, label=country)

ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Working-age Population Share (%)", fontsize=11)
ax.set_title("B. Working-age Population (15-64) Share", fontsize=12, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(1970, 2025)
ax.set_ylim(50, 80)

# 添加注释：中国人口红利窗口
ax.axvspan(1990, 2015, alpha=0.08, color='red', label='_nolegend_')
ax.text(2002, 76, "China's\ndemographic\ndividend", fontsize=8, color='#E63946',
        ha='center', style='italic')

# 添加注释：日本老龄化
ax.annotate("Japan: rapid\naging since 1990s",
            xy=(2005, 66), xytext=(2010, 75),
            arrowprops=dict(arrowstyle='->', color='gray', lw=1.2),
            fontsize=9, color='gray')

plt.tight_layout()
plt.savefig(OUTPUT_FIG, dpi=200, bbox_inches='tight')
plt.close()
print(f"\n图表已保存: {OUTPUT_FIG}")

# ============================================================
# 8. 数据质量检查
# ============================================================

print("\n" + "=" * 60)
print("数据质量检查")
print("=" * 60)
print(f"\n缺失值统计:")
print(df_hc.isnull().sum())
print(f"\n描述性统计:")
print(df_hc.groupby('country')[['mean_years_schooling', 'H_index', 'urban_pop_mil', 'labor_age_ratio']].describe().round(2))
