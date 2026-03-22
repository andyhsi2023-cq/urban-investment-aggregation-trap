#!/usr/bin/env python3
"""
83_us_msa_scaling.py — 美国 MSA 级标度律检验
=============================================
目的: 验证 OCR ~ Pop^(-alpha) 标度律在美国 MSA 是否成立
      核心假说: 大城市 Q 高 / 小城市 Q 低 (即 V/GDP ~ Pop^alpha)

数据来源:
  - Census ACS 5-Year 2022: 人口、住房单元数、房屋中位价、建筑中位年份
  - BEA CAGDP1: MSA GDP (current dollars)

输入: 从 API 直接下载
输出:
  - 02-data/raw/us_msa_data.csv             (合并后原始数据)
  - 03-analysis/models/us_msa_scaling_report.txt (回归报告)
  - 04-figures/drafts/fig_us_msa_scaling.png     (标度律图)
依赖: pandas, numpy, requests, statsmodels, scipy, matplotlib, zipfile, io
"""

import os
import sys
import io
import zipfile
import warnings
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

warnings.filterwarnings('ignore')

# ============================================================
# 路径配置
# ============================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
DATA_RAW = os.path.join(BASE, '02-data', 'raw')
DATA_PROC = os.path.join(BASE, '02-data', 'processed')
MODELS = os.path.join(BASE, '03-analysis', 'models')
FIGS = os.path.join(BASE, '04-figures', 'drafts')
SOURCE_DIR = os.path.join(BASE, '04-figures', 'source-data')

for d in [DATA_RAW, DATA_PROC, MODELS, FIGS, SOURCE_DIR]:
    os.makedirs(d, exist_ok=True)

report_lines = []
def rpt(s=''):
    report_lines.append(s)
    print(s)

# ============================================================
# 步骤 1: 下载 Census ACS 数据
# ============================================================
rpt('=' * 72)
rpt('步骤 1: 下载 Census ACS 5-Year 2022 数据')
rpt('=' * 72)

# 获取人口、住房单元数、房屋中位价
census_url_1 = (
    'https://api.census.gov/data/2022/acs/acs5'
    '?get=B25077_001E,B01003_001E,B25001_001E,NAME'
    '&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*'
)
# 获取建筑中位年份
census_url_2 = (
    'https://api.census.gov/data/2022/acs/acs5'
    '?get=B25035_001E'
    '&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*'
)

rpt('正在请求 Census ACS API...')
try:
    r1 = requests.get(census_url_1, timeout=60)
    r1.raise_for_status()
    data1 = r1.json()
    census_df = pd.DataFrame(data1[1:], columns=data1[0])
    census_df.rename(columns={
        'B25077_001E': 'median_home_value',
        'B01003_001E': 'population',
        'B25001_001E': 'housing_units',
        'metropolitan statistical area/micropolitan statistical area': 'cbsa_code',
        'NAME': 'msa_name'
    }, inplace=True)
    rpt(f'  Census 主表: {len(census_df)} 条记录')

    r2 = requests.get(census_url_2, timeout=60)
    r2.raise_for_status()
    data2 = r2.json()
    yr_df = pd.DataFrame(data2[1:], columns=data2[0])
    yr_df.rename(columns={
        'B25035_001E': 'median_year_built',
        'metropolitan statistical area/micropolitan statistical area': 'cbsa_code'
    }, inplace=True)
    yr_df = yr_df[['cbsa_code', 'median_year_built']]

    census_df = census_df.merge(yr_df, on='cbsa_code', how='left')
    rpt(f'  合并建筑年份后: {len(census_df)} 条记录')

except Exception as e:
    rpt(f'[ERROR] Census API 请求失败: {e}')
    sys.exit(1)

# 转换数值列
for col in ['median_home_value', 'population', 'housing_units', 'median_year_built']:
    census_df[col] = pd.to_numeric(census_df[col], errors='coerce')

# 区分 Metro 和 Micro
census_df['is_metro'] = census_df['msa_name'].str.contains('Metro Area', na=False)
n_metro = census_df['is_metro'].sum()
n_micro = (~census_df['is_metro']).sum()
rpt(f'  Metro Areas: {n_metro}, Micro Areas: {n_micro}')
rpt()

# ============================================================
# 步骤 2: 下载 BEA MSA GDP 数据
# ============================================================
rpt('=' * 72)
rpt('步骤 2: 下载 BEA CAGDP1 (GDP by MSA) 数据')
rpt('=' * 72)

bea_zip_url = 'https://apps.bea.gov/regional/zip/CAGDP1.zip'
rpt('正在下载 BEA CAGDP1.zip (县级 GDP)...')

bea_county_gdp = None
try:
    r_bea = requests.get(bea_zip_url, timeout=120)
    r_bea.raise_for_status()
    rpt(f'  下载完成: {len(r_bea.content) / 1e6:.1f} MB')

    with zipfile.ZipFile(io.BytesIO(r_bea.content)) as zf:
        csv_names = [n for n in zf.namelist() if n.endswith('.csv')]
        target_csv = [n for n in csv_names if 'ALL_AREAS' in n.upper()]
        if not target_csv:
            target_csv = csv_names
        fname = target_csv[0]
        rpt(f'  读取: {fname}')

        with zf.open(fname) as f:
            raw_bytes = f.read()
        for enc in ['utf-8-sig', 'latin-1', 'cp1252']:
            try:
                bea_df = pd.read_csv(io.BytesIO(raw_bytes), encoding=enc, low_memory=False)
                rpt(f'  成功以 {enc} 编码读取')
                break
            except Exception:
                continue

    rpt(f'  BEA 原始表: {bea_df.shape[0]} 行 x {bea_df.shape[1]} 列')

    # 筛选 LineCode=3 (Current-dollar GDP, thousands of current dollars) 的县级数据
    # LineCode=1 是 Real GDP (chained 2017 dollars), 不适合与当期房价比较
    gdp_rows = bea_df[bea_df['LineCode'] == 3].copy()
    rpt(f'  使用 LineCode=3: Current-dollar GDP (thousands of current dollars)')
    gdp_rows['county_fips'] = gdp_rows['GeoFIPS'].astype(str).str.strip().str.replace('"', '').str.strip()

    # 县级 FIPS = 5位 (州2位+县3位), 排除州级(xx000)和国家级(00000)
    gdp_rows = gdp_rows[gdp_rows['county_fips'].str.match(r'^\d{5}$')]
    gdp_rows = gdp_rows[~gdp_rows['county_fips'].str.endswith('000')]
    rpt(f'  县级 GDP 行数: {len(gdp_rows)}')

    # 取 2022 年 GDP
    year_cols = [c for c in gdp_rows.columns if str(c).isdigit() and int(c) >= 2000]
    target_year = '2022' if '2022' in year_cols else year_cols[-1]
    bea_county_gdp = gdp_rows[['county_fips', 'GeoName', target_year]].copy()
    bea_county_gdp.rename(columns={target_year: 'county_gdp_thousands'}, inplace=True)
    bea_county_gdp['county_gdp_thousands'] = pd.to_numeric(
        bea_county_gdp['county_gdp_thousands'].astype(str).str.replace(',', '').str.strip(),
        errors='coerce'
    )
    bea_county_gdp.dropna(subset=['county_gdp_thousands'], inplace=True)
    # 转为百万美元 (原始单位是千美元)
    bea_county_gdp['county_gdp_millions'] = bea_county_gdp['county_gdp_thousands'] / 1000.0
    rpt(f'  有效县级 GDP: {len(bea_county_gdp)} 县 (年份={target_year})')

except Exception as e:
    rpt(f'[ERROR] BEA 下载失败: {e}')

# ============================================================
# 步骤 2b: 下载 Census CBSA 划界文件 (县->MSA 映射)
# ============================================================
rpt()
rpt('下载 Census CBSA Delineation (县->MSA 交叉表)...')
cbsa_xwalk = None
try:
    delin_url = ('https://www2.census.gov/programs-surveys/metro-micro/'
                 'geographies/reference-files/2020/delineation-files/list1_2020.xls')
    r_delin = requests.get(delin_url, timeout=30)
    r_delin.raise_for_status()
    xw = pd.read_excel(io.BytesIO(r_delin.content), header=2)
    # 去掉含 NA 的行
    xw = xw.dropna(subset=['FIPS State Code', 'FIPS County Code', 'CBSA Code'])
    # 构建 5位县 FIPS
    xw['state_fips'] = xw['FIPS State Code'].astype(int).astype(str).str.zfill(2)
    xw['county_fips_num'] = xw['FIPS County Code'].astype(int).astype(str).str.zfill(3)
    xw['county_fips'] = xw['state_fips'] + xw['county_fips_num']
    xw['cbsa_code'] = xw['CBSA Code'].astype(int).astype(str).str.zfill(5)
    cbsa_xwalk = xw[['county_fips', 'cbsa_code', 'CBSA Title']].copy()
    rpt(f'  CBSA 交叉表: {len(cbsa_xwalk)} 县->MSA 映射, {cbsa_xwalk["cbsa_code"].nunique()} 个 CBSA')
except Exception as e:
    rpt(f'[ERROR] CBSA 交叉表下载失败: {e}')

# ============================================================
# 步骤 3: 县级 GDP 聚合为 MSA 级 GDP
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 3: 县级 GDP 聚合为 MSA 级')
rpt('=' * 72)

gdp_msa = None

if bea_county_gdp is not None and cbsa_xwalk is not None:
    # 合并县级 GDP 与 CBSA 交叉表
    merged = bea_county_gdp.merge(cbsa_xwalk, on='county_fips', how='inner')
    rpt(f'  县-CBSA 匹配: {len(merged)} 条 (覆盖 {merged["cbsa_code"].nunique()} 个 CBSA)')

    # 按 CBSA 汇总 GDP
    gdp_msa = merged.groupby('cbsa_code').agg(
        gdp_millions=('county_gdp_millions', 'sum'),
        n_counties=('county_fips', 'count')
    ).reset_index()
    rpt(f'  MSA 级 GDP: {len(gdp_msa)} 个 CBSA')
    rpt(f'  GDP 范围: {gdp_msa["gdp_millions"].min():.0f} - {gdp_msa["gdp_millions"].max():.0f} 百万美元')
else:
    rpt('  [WARNING] 无法构建 MSA GDP, 缺少县级 GDP 或 CBSA 交叉表')

# ============================================================
# 步骤 4: 合并 Census + BEA 数据
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 4: 合并 Census 与 BEA 数据')
rpt('=' * 72)

# 确保 cbsa_code 格式一致
census_df['cbsa_code'] = census_df['cbsa_code'].astype(str).str.strip().str.zfill(5)

if gdp_msa is not None:
    gdp_msa['cbsa_code'] = gdp_msa['cbsa_code'].astype(str).str.strip().str.zfill(5)
    df = census_df.merge(gdp_msa[['cbsa_code', 'gdp_millions']], on='cbsa_code', how='inner')
    rpt(f'  合并后 (inner join): {len(df)} MSAs')
else:
    df = census_df.copy()
    df['gdp_millions'] = np.nan
    rpt('  [WARNING] 无 BEA GDP 数据, 仅用 Census 数据')

# 基本过滤: 去除数据不完整的行
df = df.dropna(subset=['population', 'housing_units', 'median_home_value'])
df = df[df['population'] > 0]
df = df[df['housing_units'] > 0]
df = df[df['median_home_value'] > 0]
rpt(f'  有效记录 (非缺失): {len(df)}')

# ============================================================
# 步骤 5: 构造分析变量
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 5: 构造分析变量')
rpt('=' * 72)

# V = Median home value * Housing units (总住房价值近似, 单位: 美元)
df['V_total'] = df['median_home_value'] * df['housing_units']
# V 转为百万美元
df['V_millions'] = df['V_total'] / 1e6

# 人均住房单元 (Housing units per capita ~ OCR 近似)
df['hu_per_capita'] = df['housing_units'] / df['population']

# 人均住房价值
df['V_per_capita'] = df['V_total'] / df['population']

# 住房年龄 (2022 - median year built)
df['housing_age'] = 2022 - df['median_year_built']

# 如果有 GDP
if df['gdp_millions'].notna().sum() > 50:
    df['V_GDP_ratio'] = df['V_millions'] / df['gdp_millions']  # Q 的粗略近似
    df['gdp_per_capita'] = df['gdp_millions'] * 1e6 / df['population']
    has_gdp = True
    rpt(f'  有 GDP 数据的 MSA: {df["gdp_millions"].notna().sum()}')
else:
    has_gdp = False
    rpt('  [WARNING] GDP 数据不足, 仅做人口-住房分析')

# 对数变换
df['ln_pop'] = np.log(df['population'])
df['ln_hu'] = np.log(df['housing_units'])
df['ln_hu_pc'] = np.log(df['hu_per_capita'])
df['ln_V'] = np.log(df['V_millions'])
df['ln_median_hv'] = np.log(df['median_home_value'])
df['ln_V_pc'] = np.log(df['V_per_capita'])

if has_gdp:
    mask_gdp = df['gdp_millions'].notna() & (df['gdp_millions'] > 0)
    df.loc[mask_gdp, 'ln_gdp'] = np.log(df.loc[mask_gdp, 'gdp_millions'])
    df.loc[mask_gdp, 'ln_V_GDP'] = np.log(df.loc[mask_gdp, 'V_GDP_ratio'])
    df.loc[mask_gdp, 'ln_gdp_pc'] = np.log(df.loc[mask_gdp, 'gdp_per_capita'])

# 区域分类 (基于州名)
# 从 MSA 名称提取州名缩写
def extract_state(name):
    """从 MSA 名称提取主要州名"""
    if pd.isna(name):
        return None
    # 格式: "Name, ST Metro/Micro Area" 或 "Name, ST-ST Metro/Micro Area"
    parts = name.split(',')
    if len(parts) >= 2:
        state_part = parts[-1].strip()
        # 去掉 "Metro Area" / "Micro Area"
        state_part = state_part.replace('Metro Area', '').replace('Micro Area', '').strip()
        # 取第一个州
        state = state_part.split('-')[0].strip()
        return state
    return None

df['state'] = df['msa_name'].apply(extract_state)

# Census 区域映射
NORTHEAST = {'CT', 'ME', 'MA', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT'}
MIDWEST = {'IL', 'IN', 'IA', 'KS', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'SD', 'WI'}
SOUTH = {'AL', 'AR', 'DE', 'FL', 'GA', 'KY', 'LA', 'MD', 'MS', 'NC', 'OK', 'SC',
         'TN', 'TX', 'VA', 'WV', 'DC'}
WEST = {'AK', 'AZ', 'CA', 'CO', 'HI', 'ID', 'MT', 'NV', 'NM', 'OR', 'UT', 'WA', 'WY'}

def assign_region(st):
    if st in NORTHEAST: return 'Northeast'
    if st in MIDWEST: return 'Midwest'
    if st in SOUTH: return 'South'
    if st in WEST: return 'West'
    return 'Other'  # PR, territories

df['region'] = df['state'].apply(assign_region)

rpt(f'  区域分布:')
for reg in ['Northeast', 'Midwest', 'South', 'West', 'Other']:
    n = (df['region'] == reg).sum()
    rpt(f'    {reg}: {n}')

# 仅保留 50 州 + DC (排除 PR 等领地)
df_us = df[df['region'] != 'Other'].copy()
rpt(f'  排除领地后: {len(df_us)} MSAs')

# 保存原始数据
df_us.to_csv(os.path.join(DATA_RAW, 'us_msa_data.csv'), index=False)
rpt(f'  数据已保存: us_msa_data.csv')

# ============================================================
# 步骤 6: 描述性统计
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 6: 描述性统计')
rpt('=' * 72)

desc_cols = ['population', 'housing_units', 'median_home_value', 'hu_per_capita']
if has_gdp:
    desc_cols += ['gdp_millions', 'V_GDP_ratio', 'gdp_per_capita']

# Metro vs Micro 对比
for subset_name, subset_mask in [('All MSAs', pd.Series(True, index=df_us.index)),
                                   ('Metro only', df_us['is_metro']),
                                   ('Micro only', ~df_us['is_metro'])]:
    sub = df_us[subset_mask]
    rpt(f'\n--- {subset_name} (N={len(sub)}) ---')
    for col in desc_cols:
        if col in sub.columns and sub[col].notna().sum() > 0:
            vals = sub[col].dropna()
            rpt(f'  {col:25s}: mean={vals.mean():>12,.1f}  median={vals.median():>12,.1f}  '
                f'sd={vals.std():>12,.1f}  min={vals.min():>12,.1f}  max={vals.max():>12,.1f}')

# ============================================================
# 步骤 7: 核心标度律回归
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 7: 核心标度律回归')
rpt('=' * 72)

def run_ols(y, x, label, data):
    """运行 OLS 回归并报告结果"""
    mask = data[y].notna() & data[x].notna() & np.isfinite(data[y]) & np.isfinite(data[x])
    d = data[mask]
    Y = d[y]
    X = sm.add_constant(d[x])
    model = sm.OLS(Y, X).fit(cov_type='HC1')
    b = model.params.iloc[1]
    se = model.bse.iloc[1]
    ci = model.conf_int().iloc[1]
    rpt(f'\n  [{label}]')
    rpt(f'  {y} = a + b * {x}')
    rpt(f'  N = {len(d)}')
    rpt(f'  b = {b:.4f} (SE = {se:.4f})')
    rpt(f'  95% CI = [{ci[0]:.4f}, {ci[1]:.4f}]')
    rpt(f'  t = {model.tvalues.iloc[1]:.3f}, p = {model.pvalues.iloc[1]:.2e}')
    rpt(f'  R-squared = {model.rsquared:.4f}')
    return model, d

# --- 回归 A: ln(median_home_value) ~ ln(pop) ---
# 大城市房价更高? (基础 Bettencourt 型标度)
rpt('\n--- A. 房价-人口标度律 ---')
mA, dA = run_ols('ln_median_hv', 'ln_pop', 'All MSAs: ln(MedianHomeValue) ~ ln(Pop)', df_us)
mA_metro, dA_metro = run_ols('ln_median_hv', 'ln_pop', 'Metro only: ln(MedianHomeValue) ~ ln(Pop)',
                              df_us[df_us['is_metro']])

# --- 回归 B: ln(hu_per_capita) ~ ln(pop) ---
# 类似中国的 OCR ~ Pop^(-alpha)
rpt('\n--- B. 人均住房-人口标度律 (类似 OCR) ---')
mB, dB = run_ols('ln_hu_pc', 'ln_pop', 'All MSAs: ln(HU_per_capita) ~ ln(Pop)', df_us)
mB_metro, dB_metro = run_ols('ln_hu_pc', 'ln_pop', 'Metro only: ln(HU_per_capita) ~ ln(Pop)',
                              df_us[df_us['is_metro']])

# --- 回归 C: ln(V/GDP) ~ ln(pop) --- (如果有 GDP)
if has_gdp:
    rpt('\n--- C. V/GDP (Q近似) - 人口标度律 ---')
    df_gdp = df_us[df_us['ln_V_GDP'].notna() & np.isfinite(df_us['ln_V_GDP'])].copy()
    mC, dC = run_ols('ln_V_GDP', 'ln_pop', 'All MSAs: ln(V/GDP) ~ ln(Pop)', df_gdp)
    mC_metro, dC_metro = run_ols('ln_V_GDP', 'ln_pop', 'Metro only: ln(V/GDP) ~ ln(Pop)',
                                  df_gdp[df_gdp['is_metro']])

    # --- 回归 D: ln(V_per_capita) ~ ln(pop) ---
    rpt('\n--- D. 人均住房价值-人口标度律 ---')
    mD, dD = run_ols('ln_V_pc', 'ln_pop', 'All MSAs: ln(V_per_capita) ~ ln(Pop)', df_us)

# ============================================================
# 步骤 8: 分区域稳健性
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 8: 分区域稳健性检验')
rpt('=' * 72)

for reg in ['Northeast', 'Midwest', 'South', 'West']:
    sub = df_us[df_us['region'] == reg]
    if len(sub) < 20:
        rpt(f'\n  [{reg}] 样本不足 (N={len(sub)}), 跳过')
        continue
    rpt(f'\n--- 区域: {reg} (N={len(sub)}) ---')
    run_ols('ln_median_hv', 'ln_pop', f'{reg}: ln(MedianHV) ~ ln(Pop)', sub)
    run_ols('ln_hu_pc', 'ln_pop', f'{reg}: ln(HU_pc) ~ ln(Pop)', sub)
    if has_gdp:
        sub_gdp = sub[sub['ln_V_GDP'].notna() & np.isfinite(sub['ln_V_GDP'])]
        if len(sub_gdp) >= 20:
            run_ols('ln_V_GDP', 'ln_pop', f'{reg}: ln(V/GDP) ~ ln(Pop)', sub_gdp)

# ============================================================
# 步骤 9: 仅 Metro 的 Rank-Size 检验
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 9: Metro Areas Rank-Size 分析')
rpt('=' * 72)

metro = df_us[df_us['is_metro']].sort_values('population', ascending=False).copy()
metro['rank'] = range(1, len(metro) + 1)
metro['ln_rank'] = np.log(metro['rank'])

rpt(f'  Metro Areas 数量: {len(metro)}')
rpt(f'  Top 10 MSAs:')
for _, row in metro.head(10).iterrows():
    gdp_str = f'GDP={row["gdp_millions"]:,.0f}M' if pd.notna(row.get('gdp_millions')) else 'GDP=N/A'
    rpt(f'    {row["msa_name"][:50]:50s} Pop={row["population"]:>10,d}  '
        f'MedianHV=${row["median_home_value"]:>8,.0f}  {gdp_str}')

# Zipf's law: ln(rank) ~ -beta * ln(pop)
run_ols('ln_rank', 'ln_pop', 'Zipf: ln(Rank) ~ ln(Pop)', metro)

# ============================================================
# 步骤 10: 可视化
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 10: 生成图表')
rpt('=' * 72)

REGION_COLORS = {
    'Northeast': '#0072B2',   # 蓝
    'Midwest': '#D55E00',     # 橙红
    'South': '#009E73',       # 绿
    'West': '#CC79A7',        # 粉紫
}

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Scaling Laws in U.S. Metropolitan/Micropolitan Areas (2022)',
             fontsize=14, fontweight='bold', y=0.98)

# --- Panel A: ln(MedianHomeValue) ~ ln(Pop) ---
ax = axes[0, 0]
for reg in ['Northeast', 'Midwest', 'South', 'West']:
    sub = df_us[df_us['region'] == reg]
    metro_sub = sub[sub['is_metro']]
    micro_sub = sub[~sub['is_metro']]
    ax.scatter(metro_sub['ln_pop'], metro_sub['ln_median_hv'],
              c=REGION_COLORS[reg], alpha=0.5, s=20, edgecolors='none')
    ax.scatter(micro_sub['ln_pop'], micro_sub['ln_median_hv'],
              c=REGION_COLORS[reg], alpha=0.2, s=10, marker='x')

# OLS 拟合线
x_fit = np.linspace(df_us['ln_pop'].min(), df_us['ln_pop'].max(), 100)
y_fit = mA.params.iloc[0] + mA.params.iloc[1] * x_fit
ax.plot(x_fit, y_fit, 'k-', linewidth=2, label=f'b = {mA.params.iloc[1]:.3f}')
b_a = mA.params.iloc[1]
ci_a = mA.conf_int().iloc[1]
ax.set_xlabel('ln(Population)', fontsize=11)
ax.set_ylabel('ln(Median Home Value)', fontsize=11)
ax.set_title(f'A. Home Value ~ Population\n'
             f'b = {b_a:.3f} [{ci_a[0]:.3f}, {ci_a[1]:.3f}], '
             f'R² = {mA.rsquared:.3f}', fontsize=10)
ax.legend(fontsize=9)

# --- Panel B: ln(HU_per_capita) ~ ln(Pop) ---
ax = axes[0, 1]
for reg in ['Northeast', 'Midwest', 'South', 'West']:
    sub = df_us[df_us['region'] == reg]
    metro_sub = sub[sub['is_metro']]
    micro_sub = sub[~sub['is_metro']]
    ax.scatter(metro_sub['ln_pop'], metro_sub['ln_hu_pc'],
              c=REGION_COLORS[reg], alpha=0.5, s=20, edgecolors='none')
    ax.scatter(micro_sub['ln_pop'], micro_sub['ln_hu_pc'],
              c=REGION_COLORS[reg], alpha=0.2, s=10, marker='x')

y_fit = mB.params.iloc[0] + mB.params.iloc[1] * x_fit
ax.plot(x_fit, y_fit, 'k-', linewidth=2, label=f'b = {mB.params.iloc[1]:.3f}')
b_b = mB.params.iloc[1]
ci_b = mB.conf_int().iloc[1]
ax.set_xlabel('ln(Population)', fontsize=11)
ax.set_ylabel('ln(Housing Units per Capita)', fontsize=11)
ax.set_title(f'B. Housing Density ~ Population (OCR proxy)\n'
             f'b = {b_b:.3f} [{ci_b[0]:.3f}, {ci_b[1]:.3f}], '
             f'R² = {mB.rsquared:.3f}', fontsize=10)
ax.legend(fontsize=9)

# --- Panel C: ln(V/GDP) ~ ln(Pop) ---
ax = axes[1, 0]
if has_gdp:
    df_plot = df_us[df_us['ln_V_GDP'].notna() & np.isfinite(df_us['ln_V_GDP'])]
    for reg in ['Northeast', 'Midwest', 'South', 'West']:
        sub = df_plot[df_plot['region'] == reg]
        metro_sub = sub[sub['is_metro']]
        micro_sub = sub[~sub['is_metro']]
        ax.scatter(metro_sub['ln_pop'], metro_sub['ln_V_GDP'],
                  c=REGION_COLORS[reg], alpha=0.5, s=20, edgecolors='none')
        ax.scatter(micro_sub['ln_pop'], micro_sub['ln_V_GDP'],
                  c=REGION_COLORS[reg], alpha=0.2, s=10, marker='x')

    x_fit_c = np.linspace(df_plot['ln_pop'].min(), df_plot['ln_pop'].max(), 100)
    y_fit = mC.params.iloc[0] + mC.params.iloc[1] * x_fit_c
    ax.plot(x_fit_c, y_fit, 'k-', linewidth=2, label=f'b = {mC.params.iloc[1]:.3f}')
    b_c = mC.params.iloc[1]
    ci_c = mC.conf_int().iloc[1]
    ax.set_title(f'C. V/GDP (Q proxy) ~ Population\n'
                 f'b = {b_c:.3f} [{ci_c[0]:.3f}, {ci_c[1]:.3f}], '
                 f'R² = {mC.rsquared:.3f}', fontsize=10)
    ax.legend(fontsize=9)
else:
    ax.text(0.5, 0.5, 'GDP data unavailable', transform=ax.transAxes,
            ha='center', va='center', fontsize=12)
ax.set_xlabel('ln(Population)', fontsize=11)
ax.set_ylabel('ln(V/GDP)', fontsize=11)

# --- Panel D: 分区域系数对比 ---
ax = axes[1, 1]
regions = ['Northeast', 'Midwest', 'South', 'West']
coefs = []
cis_lo = []
cis_hi = []
for reg in regions:
    sub = df_us[df_us['region'] == reg]
    if len(sub) < 20:
        coefs.append(np.nan)
        cis_lo.append(np.nan)
        cis_hi.append(np.nan)
        continue
    mask = sub['ln_median_hv'].notna() & sub['ln_pop'].notna()
    d = sub[mask]
    Y = d['ln_median_hv']
    X = sm.add_constant(d['ln_pop'])
    m = sm.OLS(Y, X).fit(cov_type='HC1')
    coefs.append(m.params.iloc[1])
    ci = m.conf_int().iloc[1]
    cis_lo.append(ci[0])
    cis_hi.append(ci[1])

# 加上全样本
coefs.append(mA.params.iloc[1])
ci_all = mA.conf_int().iloc[1]
cis_lo.append(ci_all[0])
cis_hi.append(ci_all[1])
labels = regions + ['All U.S.']
colors = [REGION_COLORS[r] for r in regions] + ['black']

y_pos = range(len(labels))
ax.barh(y_pos, coefs, color=colors, alpha=0.7, height=0.6)
for i, (c, lo, hi) in enumerate(zip(coefs, cis_lo, cis_hi)):
    if not np.isnan(c):
        ax.plot([lo, hi], [i, i], 'k-', linewidth=2)
        ax.plot([lo, lo], [i-0.1, i+0.1], 'k-', linewidth=1.5)
        ax.plot([hi, hi], [i-0.1, i+0.1], 'k-', linewidth=1.5)
        ax.text(hi + 0.005, i, f'{c:.3f}', va='center', fontsize=9)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.set_xlabel('Scaling exponent (b)', fontsize=11)
ax.set_title('D. Regional scaling exponents\nln(MedianHV) ~ b * ln(Pop)', fontsize=10)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# 区域图例
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=REGION_COLORS[r],
                           label=r, markersize=8) for r in regions]
legend_elements += [Line2D([0], [0], marker='x', color='gray', label='Micro Areas',
                            markersize=6, linestyle='None')]
fig.legend(handles=legend_elements, loc='lower center', ncol=5, fontsize=9,
           bbox_to_anchor=(0.5, 0.0))

plt.savefig(os.path.join(FIGS, 'fig_us_msa_scaling.png'), dpi=200, bbox_inches='tight',
            facecolor='white')
rpt(f'  图表已保存: fig_us_msa_scaling.png')

# 保存 source data
df_us.to_csv(os.path.join(SOURCE_DIR, 'fig_us_msa_scaling_source.csv'), index=False)

# ============================================================
# 步骤 11: 与中国标度律对比
# ============================================================
rpt()
rpt('=' * 72)
rpt('步骤 11: 与中国标度律对比')
rpt('=' * 72)

rpt(f'\n  中国 (275城市, 2015-2016):')
rpt(f'    OCR ~ Pop^(-0.319)   [alpha = 0.319]')
rpt(f'    (来源: 80_scaling_law_ocr.py)')
rpt(f'\n  美国 (MSA/Micro, 2022):')
rpt(f'    ln(MedianHV) ~ {mA.params.iloc[1]:.3f} * ln(Pop)')
rpt(f'    ln(HU_pc) ~ {mB.params.iloc[1]:.3f} * ln(Pop)')
if has_gdp:
    rpt(f'    ln(V/GDP) ~ {mC.params.iloc[1]:.3f} * ln(Pop)')

rpt(f'\n  解读:')
if has_gdp:
    b_vgdp = mC.params.iloc[1]
    if b_vgdp > 0:
        rpt(f'    V/GDP (Q 近似) 的标度指数为正 ({b_vgdp:.3f}), 说明大城市 Q 更高')
        rpt(f'    这与中国的模式一致: 大城市资产相对于经济基本面被"高估"')
    else:
        rpt(f'    V/GDP (Q 近似) 的标度指数为负 ({b_vgdp:.3f}), 说明大城市 Q 更低')
        rpt(f'    这与中国的模式相反, 值得深入探讨')

b_hu = mB.params.iloc[1]
if b_hu < 0:
    rpt(f'    HU_per_capita 的标度指数为负 ({b_hu:.3f}), 说明大城市人均住房更少')
    rpt(f'    类似于中国 OCR < 1 的"建设不足"模式')
else:
    rpt(f'    HU_per_capita 的标度指数为正 ({b_hu:.3f}), 大城市人均住房更多')
    rpt(f'    与中国 OCR 标度律方向不同')

# ============================================================
# 保存报告
# ============================================================
rpt()
rpt('=' * 72)
rpt('分析完成')
rpt('=' * 72)

report_path = os.path.join(MODELS, 'us_msa_scaling_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rpt(f'报告已保存: {report_path}')

print('\n[DONE] 所有输出文件:')
print(f'  数据: {os.path.join(DATA_RAW, "us_msa_data.csv")}')
print(f'  报告: {report_path}')
print(f'  图表: {os.path.join(FIGS, "fig_us_msa_scaling.png")}')
