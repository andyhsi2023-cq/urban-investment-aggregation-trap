"""
11_unified_panel.py
===================
目的：将所有已有数据合并为四国统一面板数据集，为 K* 估计和倒 U 型跨国回归做准备。

输入：
  - 各国 urban_q_timeseries.csv（日本、美国、英国）
  - china_urban_q_timeseries.csv + six-curves 主数据集（中国）
  - china_ratio_curves.csv（中国产业结构）
  - four_country_human_capital.csv（人力资本指数）

输出：
  - four_country_panel.csv — 统一面板数据集

列定义：
  year, country, V (资产价值), K (资本存量), I (投资), GDP,
  urban_q, muq, urbanization_rate, g3_ratio (三产占比),
  H_index, labor_age_ratio, CI_GDP_ratio, delta_V_ratio (dV/V)

依赖包：pandas, numpy
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 0. 路径设置
# ============================================================

PROJECT_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
MODELS_DIR = PROJECT_DIR / "03-analysis/models"
PROCESSED_DIR = PROJECT_DIR / "02-data/processed"
SIX_CURVES_DIR = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition")

OUTPUT_CSV = PROCESSED_DIR / "four_country_panel.csv"

# ============================================================
# 1. 读取人力资本数据
# ============================================================

hc = pd.read_csv(PROCESSED_DIR / "four_country_human_capital.csv")
print(f"人力资本数据: {len(hc)} 行, 国家: {hc.country.unique()}")

# ============================================================
# 2. 构建中国面板
# ============================================================

print("\n--- 中国 ---")

# 主 Urban Q 数据
china_uq = pd.read_csv(MODELS_DIR / "china_urban_q_timeseries.csv")

# six-curves 主数据集（GDP、人口等）
china_master = pd.read_csv(
    SIX_CURVES_DIR / "02-data/processed/six_curves_master_dataset_processed.csv"
)

# 产业结构
china_ratio = pd.read_csv(MODELS_DIR / "china_ratio_curves.csv")

# 合并
china = china_uq[['year', 'urbanization_rate_pct',
                   'V2_total_urban_value_100m',  # 使用 V2 作为总资产价值
                   'K2_pim_capital_stock_100m',   # 使用 K2 (PIM) 作为资本存量
                   'total_construction_inv',
                   'Q_V2K2', 'MUQ_V2']].copy()

china.columns = ['year', 'urbanization_rate', 'V', 'K', 'I', 'urban_q', 'muq']

# 合并 GDP
gdp_cols = china_master[['year', 'gdp_100m_current']].copy()
china = china.merge(gdp_cols, on='year', how='left')
china.rename(columns={'gdp_100m_current': 'GDP'}, inplace=True)

# 合并三产占比
g3 = china_ratio[['year', 'tertiary_pct']].copy()
china = china.merge(g3, on='year', how='left')
china.rename(columns={'tertiary_pct': 'g3_ratio'}, inplace=True)

# 计算 CI/GDP ratio（投资/GDP）
china['CI_GDP_ratio'] = china['I'] / china['GDP']

# 计算 delta_V_ratio (dV/V)
china = china.sort_values('year').reset_index(drop=True)
china['delta_V_ratio'] = china['V'].pct_change()

china['country'] = 'China'

# 单位说明：V, K, I, GDP 均为亿元（100m RMB）
print(f"  年份: {china.year.min()}-{china.year.max()}, {len(china)} 年")
print(f"  GDP范围: {china.GDP.min():.0f}-{china.GDP.max():.0f} 亿元")

# ============================================================
# 3. 构建日本面板
# ============================================================

print("\n--- 日本 ---")

japan = pd.read_csv(MODELS_DIR / "japan_urban_q_timeseries.csv")

japan_panel = pd.DataFrame({
    'year': japan['year'],
    'urbanization_rate': japan['urbanization_rate'],
    'V': japan['asset_value_V'],                       # 万亿日元
    'K': japan['capital_stock_K'],                     # 万亿日元
    'I': japan['construction_investment_trillion_yen'], # 万亿日元
    'GDP': japan['gdp_trillion_yen'],                  # 万亿日元
    'urban_q': japan['urban_Q'],
    'muq': japan['MUQ'],
    'g3_ratio': japan['tertiary_share_pct'],
    'country': 'Japan',
})

# 计算 CI/GDP ratio
japan_panel['CI_GDP_ratio'] = japan_panel['I'] / japan_panel['GDP']

# 计算 delta_V_ratio
japan_panel = japan_panel.sort_values('year').reset_index(drop=True)
japan_panel['delta_V_ratio'] = japan_panel['V'].pct_change()

print(f"  年份: {japan_panel.year.min()}-{japan_panel.year.max()}, {len(japan_panel)} 年")

# ============================================================
# 4. 构建美国面板
# ============================================================

print("\n--- 美国 ---")

us = pd.read_csv(MODELS_DIR / "us_urban_q_timeseries.csv")

us_panel = pd.DataFrame({
    'year': us['year'],
    'urbanization_rate': us['urbanization_rate'],
    'V': us['V_total'],                        # 万亿美元
    'K': us['capital_stock_K'],                 # 万亿美元
    'I': us['construction_investment_trillion'], # 万亿美元
    'GDP': us['gdp_trillion_usd'],              # 万亿美元
    'urban_q': us['urban_Q'],
    'muq': us['MUQ'],
    'g3_ratio': us['tertiary_share_pct'],
    'country': 'USA',
})

us_panel['CI_GDP_ratio'] = us_panel['I'] / us_panel['GDP']
us_panel = us_panel.sort_values('year').reset_index(drop=True)
us_panel['delta_V_ratio'] = us_panel['V'].pct_change()

print(f"  年份: {us_panel.year.min()}-{us_panel.year.max()}, {len(us_panel)} 年")

# ============================================================
# 5. 构建英国面板
# ============================================================

print("\n--- 英国 ---")

uk = pd.read_csv(MODELS_DIR / "uk_urban_q_timeseries.csv")

uk_panel = pd.DataFrame({
    'year': uk['year'],
    'urbanization_rate': uk['urbanization_rate'],
    'V': uk['V_total'],                        # 万亿英镑
    'K': uk['capital_stock_K'],                 # 万亿英镑
    'I': uk['construction_investment_trillion'], # 万亿英镑
    'GDP': uk['gdp_trillion_gbp'],              # 万亿英镑
    'urban_q': uk['urban_Q'],
    'muq': uk['MUQ'],
    'g3_ratio': uk['tertiary_share_pct'],
    'country': 'UK',
})

uk_panel['CI_GDP_ratio'] = uk_panel['I'] / uk_panel['GDP']
uk_panel = uk_panel.sort_values('year').reset_index(drop=True)
uk_panel['delta_V_ratio'] = uk_panel['V'].pct_change()

print(f"  年份: {uk_panel.year.min()}-{uk_panel.year.max()}, {len(uk_panel)} 年")

# ============================================================
# 6. 合并四国面板
# ============================================================

print("\n" + "=" * 60)
print("合并四国面板...")
print("=" * 60)

# 统一列
common_cols = ['year', 'country', 'V', 'K', 'I', 'GDP', 'urban_q', 'muq',
               'urbanization_rate', 'g3_ratio', 'CI_GDP_ratio', 'delta_V_ratio']

panel = pd.concat([
    china[common_cols],
    japan_panel[common_cols],
    us_panel[common_cols],
    uk_panel[common_cols],
], ignore_index=True)

# 合并人力资本数据
panel = panel.merge(
    hc[['year', 'country', 'H_index', 'labor_age_ratio', 'urban_pop_mil']],
    on=['year', 'country'],
    how='left'
)

# 最终列顺序
final_cols = ['year', 'country', 'V', 'K', 'I', 'GDP', 'urban_q', 'muq',
              'urbanization_rate', 'g3_ratio', 'H_index', 'labor_age_ratio',
              'urban_pop_mil', 'CI_GDP_ratio', 'delta_V_ratio']
panel = panel[final_cols].sort_values(['country', 'year']).reset_index(drop=True)

# ============================================================
# 7. 输出 CSV
# ============================================================

panel.to_csv(OUTPUT_CSV, index=False)
print(f"\n已保存: {OUTPUT_CSV}")
print(f"总行数: {len(panel)}")

# ============================================================
# 8. 面板基本统计量
# ============================================================

print("\n" + "=" * 60)
print("面板基本统计量")
print("=" * 60)

# 各国年份范围
print("\n各国年份范围与观测数:")
for c in ['China', 'Japan', 'USA', 'UK']:
    sub = panel[panel.country == c]
    print(f"  {c}: {sub.year.min()}-{sub.year.max()}, N={len(sub)}")

# 各变量的基本统计
print("\n变量统计描述（全样本）:")
numeric_cols = ['V', 'K', 'I', 'GDP', 'urban_q', 'muq', 'urbanization_rate',
                'g3_ratio', 'H_index', 'labor_age_ratio', 'urban_pop_mil',
                'CI_GDP_ratio', 'delta_V_ratio']
desc = panel[numeric_cols].describe().round(4)
print(desc.to_string())

# 缺失值统计
print("\n缺失值统计:")
miss = panel.isnull().sum()
miss_pct = (panel.isnull().sum() / len(panel) * 100).round(1)
miss_df = pd.DataFrame({'missing': miss, 'pct': miss_pct})
print(miss_df[miss_df.missing > 0].to_string())

# 各国分别统计核心变量
print("\n各国核心变量均值:")
core_stats = panel.groupby('country')[['urban_q', 'CI_GDP_ratio', 'H_index',
                                        'urbanization_rate', 'g3_ratio']].mean().round(4)
print(core_stats.to_string())

# K* 估计相关变量的可用性检查
print("\n\nK* 估计所需变量的可用性（非空计数）:")
k_star_vars = ['K', 'urban_pop_mil', 'H_index', 'GDP']
for c in ['China', 'Japan', 'USA', 'UK']:
    sub = panel[panel.country == c]
    avail = {v: sub[v].notna().sum() for v in k_star_vars}
    print(f"  {c}: " + ", ".join(f"{v}={n}" for v, n in avail.items()))
