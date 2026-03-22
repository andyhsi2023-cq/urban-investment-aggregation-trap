#!/usr/bin/env python3
"""
92_us_msa_muq.py — 美国 MSA 级 MUQ 面板构建与分析
====================================================
目的: 构建 2010-2022 MSA 面板, 计算 MUQ, 检验"投资强度 vs MUQ 负相关"
      的跨国一致性 (与中国 290 城市结果对比)

数据来源:
  A. Census ACS 5-Year (2010-2022): 人口、住房单元数、房屋中位价
  B. BEA CAGDP1 bulk CSV: MSA 级 GDP (多年)
  C. Census CBSA Delineation: 县->MSA 映射

输入: 从 API / bulk download 获取
输出:
  - 02-data/processed/us_msa_muq_panel.csv      (MSA 面板)
  - 03-analysis/models/us_msa_muq_report.txt     (分析报告)
  - 04-figures/drafts/fig_us_msa_muq.png         (可视化)

依赖: pandas, numpy, requests, statsmodels, scipy, matplotlib, zipfile, io
"""

import os
import sys
import io
import time
import zipfile
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 随机种子
np.random.seed(42)

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
    report_lines.append(str(s))
    print(s)

def winsorize(s, lower=0.01, upper=0.99):
    """Winsorize at given percentiles"""
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lo, hi)

# ============================================================
# 步骤 1: 从 Census ACS 下载多年住房数据 (2010-2022)
# ============================================================
rpt('=' * 72)
rpt('步骤 1: 下载 Census ACS 5-Year 多年面板数据 (2010-2022)')
rpt('=' * 72)

YEARS = list(range(2010, 2023))  # 2010-2022

# 尝试 API 下载
census_panels = []
api_success = True

for yr in YEARS:
    url = (
        f'https://api.census.gov/data/{yr}/acs/acs5'
        '?get=B25077_001E,B01003_001E,B25001_001E,NAME'
        '&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*'
    )
    try:
        rpt(f'  请求 {yr} 年数据...')
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        df_yr = pd.DataFrame(data[1:], columns=data[0])
        df_yr.rename(columns={
            'B25077_001E': 'median_home_value',
            'B01003_001E': 'population',
            'B25001_001E': 'housing_units',
            'metropolitan statistical area/micropolitan statistical area': 'cbsa_code',
            'NAME': 'msa_name'
        }, inplace=True)
        df_yr['year'] = yr
        for col in ['median_home_value', 'population', 'housing_units']:
            df_yr[col] = pd.to_numeric(df_yr[col], errors='coerce')
        census_panels.append(df_yr)
        rpt(f'    -> {len(df_yr)} MSAs')
        time.sleep(1.0)  # 速率限制
    except Exception as e:
        rpt(f'    [WARN] {yr} 年请求失败: {e}')
        api_success = False
        break

if len(census_panels) >= 3:
    census_panel = pd.concat(census_panels, ignore_index=True)
    rpt(f'\n  Census 面板: {len(census_panel)} 行, 覆盖 {census_panel["year"].nunique()} 年')
    rpt(f'  年份范围: {census_panel["year"].min()}-{census_panel["year"].max()}')
    PANEL_MODE = True
else:
    rpt('\n  [INFO] Census API 面板构建失败, 退回到截面分析模式')
    PANEL_MODE = False

# ============================================================
# 步骤 1b: 如果面板失败, 用已有 2022 截面数据
# ============================================================
if not PANEL_MODE:
    rpt('\n  加载已有 2022 截面数据...')
    cross_path = os.path.join(DATA_RAW, 'us_msa_data.csv')
    df_cross = pd.read_csv(cross_path)
    rpt(f'  截面数据: {len(df_cross)} MSAs')

# ============================================================
# 步骤 2: 下载 BEA GDP 面板 (多年)
# ============================================================
rpt('\n' + '=' * 72)
rpt('步骤 2: 下载 BEA CAGDP1 (县级 GDP, 多年)')
rpt('=' * 72)

bea_zip_url = 'https://apps.bea.gov/regional/zip/CAGDP1.zip'
rpt('正在下载 BEA CAGDP1.zip...')

bea_msa_panel = None
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
                rpt(f'  编码: {enc}, 原始行数: {len(bea_df)}')
                break
            except Exception:
                continue

    # LineCode=3: Current-dollar GDP (thousands)
    gdp_rows = bea_df[bea_df['LineCode'] == 3].copy()
    gdp_rows['county_fips'] = (gdp_rows['GeoFIPS'].astype(str)
                                .str.strip().str.replace('"', '').str.strip())
    # 县级: 5位 FIPS, 非 xx000
    gdp_rows = gdp_rows[gdp_rows['county_fips'].str.match(r'^\d{5}$')]
    gdp_rows = gdp_rows[~gdp_rows['county_fips'].str.endswith('000')]
    rpt(f'  县级 GDP 行数: {len(gdp_rows)}')

    # 识别可用年份列
    year_cols = sorted([c for c in gdp_rows.columns if str(c).isdigit() and 2005 <= int(c) <= 2025])
    rpt(f'  可用年份列: {year_cols[0]}-{year_cols[-1]}')

    # 下载 CBSA 交叉表
    rpt('\n  下载 CBSA Delineation (县->MSA 映射)...')
    delin_url = ('https://www2.census.gov/programs-surveys/metro-micro/'
                 'geographies/reference-files/2020/delineation-files/list1_2020.xls')
    r_delin = requests.get(delin_url, timeout=30)
    r_delin.raise_for_status()
    xw = pd.read_excel(io.BytesIO(r_delin.content), header=2)
    xw = xw.dropna(subset=['FIPS State Code', 'FIPS County Code', 'CBSA Code'])
    xw['state_fips'] = xw['FIPS State Code'].astype(int).astype(str).str.zfill(2)
    xw['county_fips_num'] = xw['FIPS County Code'].astype(int).astype(str).str.zfill(3)
    xw['county_fips'] = xw['state_fips'] + xw['county_fips_num']
    xw['cbsa_code'] = xw['CBSA Code'].astype(int).astype(str).str.zfill(5)
    rpt(f'  CBSA 交叉表: {xw["cbsa_code"].nunique()} 个 CBSA')

    # 构建县级 GDP 面板 (长格式)
    # 使用 Census panel 年份范围
    target_years = [str(y) for y in YEARS if str(y) in year_cols]
    rpt(f'  目标年份: {target_years}')

    county_long = []
    for yr_str in target_years:
        tmp = gdp_rows[['county_fips', yr_str]].copy()
        tmp['year'] = int(yr_str)
        tmp.rename(columns={yr_str: 'county_gdp_thousands'}, inplace=True)
        tmp['county_gdp_thousands'] = pd.to_numeric(
            tmp['county_gdp_thousands'].astype(str).str.replace(',', '').str.strip(),
            errors='coerce'
        )
        county_long.append(tmp)

    county_long = pd.concat(county_long, ignore_index=True)
    county_long.dropna(subset=['county_gdp_thousands'], inplace=True)
    county_long['county_gdp_millions'] = county_long['county_gdp_thousands'] / 1000.0

    # 县->MSA 映射
    merged_gdp = county_long.merge(xw[['county_fips', 'cbsa_code']], on='county_fips', how='inner')

    # 按 MSA-year 聚合
    bea_msa_panel = merged_gdp.groupby(['cbsa_code', 'year']).agg(
        gdp_millions=('county_gdp_millions', 'sum')
    ).reset_index()
    rpt(f'  MSA 级 GDP 面板: {len(bea_msa_panel)} 行, '
        f'{bea_msa_panel["cbsa_code"].nunique()} MSAs, '
        f'{bea_msa_panel["year"].nunique()} 年')

except Exception as e:
    rpt(f'[ERROR] BEA 下载/处理失败: {e}')
    import traceback
    traceback.print_exc()

# ============================================================
# 步骤 3: 合并 Census + BEA, 构建面板
# ============================================================
rpt('\n' + '=' * 72)
rpt('步骤 3: 合并 Census + BEA, 构建完整面板')
rpt('=' * 72)

if PANEL_MODE:
    census_panel['cbsa_code'] = census_panel['cbsa_code'].astype(str).str.strip().str.zfill(5)
    census_panel['is_metro'] = census_panel['msa_name'].str.contains('Metro Area', na=False)

    if bea_msa_panel is not None:
        bea_msa_panel['cbsa_code'] = bea_msa_panel['cbsa_code'].astype(str).str.strip().str.zfill(5)
        panel = census_panel.merge(bea_msa_panel, on=['cbsa_code', 'year'], how='inner')
        rpt(f'  合并后面板: {len(panel)} 行')
    else:
        panel = census_panel.copy()
        panel['gdp_millions'] = np.nan
        rpt(f'  [WARN] 无 GDP, 面板仅含 Census 数据: {len(panel)} 行')

    # 基本清洗
    panel = panel.dropna(subset=['population', 'housing_units', 'median_home_value'])
    panel = panel[(panel['population'] > 0) &
                  (panel['housing_units'] > 0) &
                  (panel['median_home_value'] > 0)]
    rpt(f'  清洗后: {len(panel)} 行, {panel["cbsa_code"].nunique()} MSAs, '
        f'{panel["year"].nunique()} 年')

    # 构造分析变量
    panel['V_total'] = panel['median_home_value'] * panel['housing_units']
    panel['V_millions'] = panel['V_total'] / 1e6
    panel['hu_per_capita'] = panel['housing_units'] / panel['population']
    panel['V_per_capita'] = panel['V_total'] / panel['population']

    if panel['gdp_millions'].notna().sum() > 100:
        panel['V_GDP_ratio'] = panel['V_millions'] / panel['gdp_millions']
        panel['gdp_per_capita'] = panel['gdp_millions'] * 1e6 / panel['population']
        has_gdp = True
    else:
        has_gdp = False

    panel['ln_pop'] = np.log(panel['population'])
    panel['ln_hu'] = np.log(panel['housing_units'])
    panel['ln_V'] = np.log(panel['V_millions'])

    # 添加区域标识 (基于 MSA 名称中的州缩写)
    # 使用 2022 截面数据的 state/region 映射
    cross_path = os.path.join(DATA_RAW, 'us_msa_data.csv')
    if os.path.exists(cross_path):
        df_ref = pd.read_csv(cross_path, usecols=['cbsa_code', 'state', 'region'])
        df_ref['cbsa_code'] = df_ref['cbsa_code'].astype(str).str.strip().str.zfill(5)
        panel = panel.merge(df_ref[['cbsa_code', 'state', 'region']].drop_duplicates('cbsa_code'),
                           on='cbsa_code', how='left')

    # 排序
    panel = panel.sort_values(['cbsa_code', 'year']).reset_index(drop=True)

else:
    # 截面模式: 使用已有数据
    panel = df_cross.copy()
    panel['year'] = 2022
    panel['cbsa_code'] = panel['cbsa_code'].astype(str).str.strip().str.zfill(5)
    has_gdp = panel['gdp_millions'].notna().sum() > 50
    rpt(f'  截面模式: {len(panel)} MSAs, 年份=2022')

rpt(f'  has_gdp = {has_gdp}')
rpt(f'  面板维度: {panel.shape}')

# ============================================================
# 步骤 4: 构建 MUQ
# ============================================================
rpt('\n' + '=' * 72)
rpt('步骤 4: 构建 MUQ (Marginal Urban Q)')
rpt('=' * 72)

if PANEL_MODE:
    # 面板模式: 计算 ΔV 和 ΔHU
    panel = panel.sort_values(['cbsa_code', 'year'])

    # 一阶差分
    panel['V_total_lag'] = panel.groupby('cbsa_code')['V_total'].shift(1)
    panel['hu_lag'] = panel.groupby('cbsa_code')['housing_units'].shift(1)
    panel['pop_lag'] = panel.groupby('cbsa_code')['population'].shift(1)
    panel['gdp_lag'] = panel.groupby('cbsa_code')['gdp_millions'].shift(1)

    panel['dV'] = panel['V_total'] - panel['V_total_lag']
    panel['dHU'] = panel['housing_units'] - panel['hu_lag']

    # MUQ 定义 1: ΔV / I, 其中 I = ΔHU × median_home_value
    panel['I_hu'] = panel['dHU'] * panel['median_home_value']
    panel['MUQ_basic'] = np.where(
        (panel['I_hu'].notna()) & (panel['I_hu'] > 0),
        panel['dV'] / panel['I_hu'],
        np.nan
    )

    # MUQ 定义 2 (更稳定): ΔV / GDP — 边际效率相对于经济规模
    if has_gdp:
        panel['MUQ_gdp'] = panel['dV'] / (panel['gdp_millions'] * 1e6)

    # 投资强度指标
    panel['hu_growth'] = panel['dHU'] / panel['hu_lag']  # 住房单元增长率
    panel['hu_growth_pop'] = panel['dHU'] / panel['pop_lag']  # 人均新增住房
    if has_gdp:
        # V/GDP 变化率 (类似 OCR 的变化)
        panel['V_GDP_ratio_lag'] = panel.groupby('cbsa_code')['V_GDP_ratio'].shift(1)
        panel['dV_GDP'] = panel['V_GDP_ratio'] - panel['V_GDP_ratio_lag']

        # 投资强度: 新增住房价值 / GDP
        panel['invest_intensity'] = panel['I_hu'] / (panel['gdp_millions'] * 1e6)

    # 去掉第一年 (无差分)
    panel_diff = panel[panel['V_total_lag'].notna()].copy()
    rpt(f'  差分后面板: {len(panel_diff)} 行')

    # Winsorize 极端值
    for col in ['MUQ_basic', 'MUQ_gdp', 'hu_growth', 'invest_intensity']:
        if col in panel_diff.columns and panel_diff[col].notna().sum() > 10:
            panel_diff[col + '_w'] = winsorize(panel_diff[col].dropna())
            # 回填
            mask = panel_diff[col].notna()
            panel_diff.loc[mask, col + '_w'] = winsorize(panel_diff.loc[mask, col])

else:
    # 截面模式: 用 housing_age 和 hu_per_capita 构建截面近似
    rpt('  截面模式: 使用 housing_age 和 hu_per_capita 构建截面 MUQ 近似')
    panel['housing_age'] = 2022 - panel['median_year_built']
    # 截面 "投资强度" 近似: hu_per_capita (高 = 历史上建了很多房)
    # 截面 "MUQ" 近似: V_GDP_ratio (高 = 住房价值相对经济规模大)
    panel_diff = panel.copy()

# ============================================================
# 步骤 5: 保存面板数据
# ============================================================
rpt('\n' + '=' * 72)
rpt('步骤 5: 保存面板数据')
rpt('=' * 72)

panel_path = os.path.join(DATA_PROC, 'us_msa_muq_panel.csv')
if PANEL_MODE:
    panel.to_csv(panel_path, index=False)
    rpt(f'  完整面板已保存: {panel_path}')
    rpt(f'  维度: {panel.shape}')
else:
    panel_diff.to_csv(panel_path, index=False)
    rpt(f'  截面数据已保存: {panel_path}')

# ============================================================
# 步骤 6: 描述性统计
# ============================================================
rpt('\n' + '=' * 72)
rpt('Part A: 描述性统计')
rpt('=' * 72)

if PANEL_MODE:
    df_a = panel_diff.copy()

    # MUQ 分布
    for muq_col in ['MUQ_basic', 'MUQ_gdp']:
        if muq_col not in df_a.columns:
            continue
        vals = df_a[muq_col].dropna()
        if len(vals) < 10:
            continue
        # Winsorize for reporting
        vals_w = winsorize(vals)
        rpt(f'\n  {muq_col} 分布 (winsorized 1%/99%):')
        rpt(f'    N = {len(vals_w)}')
        rpt(f'    Mean = {vals_w.mean():.4f}')
        rpt(f'    Median = {vals_w.median():.4f}')
        rpt(f'    Std = {vals_w.std():.4f}')
        rpt(f'    Q25 = {vals_w.quantile(0.25):.4f}')
        rpt(f'    Q75 = {vals_w.quantile(0.75):.4f}')
        rpt(f'    Min = {vals_w.min():.4f}, Max = {vals_w.max():.4f}')
        rpt(f'    MUQ < 0 比例 = {(vals < 0).mean():.4f} ({(vals < 0).sum()}/{len(vals)})')
        rpt(f'    MUQ < 1 比例 = {(vals < 1).mean():.4f} ({(vals < 1).sum()}/{len(vals)})')

    # 投资强度分布
    if has_gdp and 'invest_intensity' in df_a.columns:
        ii = df_a['invest_intensity'].dropna()
        ii_w = winsorize(ii)
        rpt(f'\n  invest_intensity (新增住房价值/GDP) 分布:')
        rpt(f'    N = {len(ii_w)}, Mean = {ii_w.mean():.4f}, Median = {ii_w.median():.4f}')

    rpt(f'\n  hu_growth 分布:')
    hg = df_a['hu_growth'].dropna()
    hg_w = winsorize(hg)
    rpt(f'    N = {len(hg_w)}, Mean = {hg_w.mean():.4f}, Median = {hg_w.median():.4f}')

else:
    # 截面统计
    rpt(f'\n  2022 截面描述统计 (N={len(panel_diff)}):')
    rpt(f'  V_GDP_ratio (Q proxy): Mean={panel_diff["V_GDP_ratio"].mean():.4f}, '
        f'Median={panel_diff["V_GDP_ratio"].median():.4f}')
    rpt(f'  hu_per_capita: Mean={panel_diff["hu_per_capita"].mean():.4f}, '
        f'Median={panel_diff["hu_per_capita"].median():.4f}')
    rpt(f'  gdp_per_capita: Mean={panel_diff["gdp_per_capita"].mean():.0f}, '
        f'Median={panel_diff["gdp_per_capita"].median():.0f}')

# ============================================================
# 步骤 7: 核心回归 — MUQ vs 投资强度
# ============================================================
rpt('\n' + '=' * 72)
rpt('Part B: MUQ vs 投资强度 (核心检验)')
rpt('=' * 72)

def run_ols(y, X, label=''):
    """运行 OLS 并报告结果"""
    X_c = sm.add_constant(X)
    mask = y.notna() & X_c.notna().all(axis=1)
    y_clean = y[mask]
    X_clean = X_c[mask]
    if len(y_clean) < 20:
        rpt(f'  {label}: 样本不足 ({len(y_clean)}), 跳过')
        return None
    model = sm.OLS(y_clean, X_clean).fit(cov_type='HC1')
    return model

def report_model(model, label, x_name):
    """报告回归模型结果"""
    if model is None:
        return
    rpt(f'\n  {label}:')
    rpt(f'    N = {int(model.nobs)}')
    beta = model.params[x_name]
    ci = model.conf_int().loc[x_name]
    t_val = model.tvalues[x_name]
    p_val = model.pvalues[x_name]
    rpt(f'    beta({x_name}) = {beta:.4f}')
    rpt(f'    95% CI = [{ci[0]:.4f}, {ci[1]:.4f}]')
    rpt(f'    t = {t_val:.3f}, p = {p_val:.6f}')
    rpt(f'    R-squared = {model.rsquared:.4f}')

if PANEL_MODE and has_gdp:
    df_b = panel_diff.copy()

    # --- B1: MUQ_gdp vs hu_growth (住房增长率作为投资强度) ---
    rpt('\nB1: MUQ_gdp vs hu_growth (Pooled OLS, HC1)')
    mask_b1 = df_b['MUQ_gdp'].notna() & df_b['hu_growth'].notna()
    df_b1 = df_b[mask_b1].copy()
    # Winsorize
    df_b1['MUQ_gdp_w'] = winsorize(df_b1['MUQ_gdp'])
    df_b1['hu_growth_w'] = winsorize(df_b1['hu_growth'])
    m1 = run_ols(df_b1['MUQ_gdp_w'], df_b1[['hu_growth_w']], 'B1')
    report_model(m1, 'MUQ_gdp ~ hu_growth', 'hu_growth_w')

    # --- B2: MUQ_gdp vs invest_intensity ---
    if 'invest_intensity' in df_b.columns:
        rpt('\nB2: MUQ_gdp vs invest_intensity (新增住房价值/GDP)')
        mask_b2 = (df_b['MUQ_gdp'].notna() & df_b['invest_intensity'].notna() &
                   np.isfinite(df_b['invest_intensity']))
        df_b2 = df_b[mask_b2].copy()
        df_b2['MUQ_gdp_w'] = winsorize(df_b2['MUQ_gdp'])
        df_b2['invest_intensity_w'] = winsorize(df_b2['invest_intensity'])
        m2 = run_ols(df_b2['MUQ_gdp_w'], df_b2[['invest_intensity_w']], 'B2')
        report_model(m2, 'MUQ_gdp ~ invest_intensity', 'invest_intensity_w')

    # --- B3: 分位数回归 ---
    rpt('\nB3: 分位数回归 MUQ_gdp ~ hu_growth')
    mask_b3 = df_b['MUQ_gdp'].notna() & df_b['hu_growth'].notna()
    df_b3 = df_b[mask_b3].copy()
    df_b3['MUQ_gdp_w'] = winsorize(df_b3['MUQ_gdp'])
    df_b3['hu_growth_w'] = winsorize(df_b3['hu_growth'])
    X_qr = sm.add_constant(df_b3['hu_growth_w'])
    for q in [0.10, 0.25, 0.50, 0.75, 0.90]:
        try:
            qm = QuantReg(df_b3['MUQ_gdp_w'], X_qr).fit(q=q)
            beta_q = qm.params['hu_growth_w']
            ci_q = qm.conf_int().loc['hu_growth_w']
            p_q = qm.pvalues['hu_growth_w']
            rpt(f'  Q{int(q*100):02d}: beta = {beta_q:.4f}, '
                f'95% CI = [{ci_q[0]:.4f}, {ci_q[1]:.4f}], p = {p_q:.6f}')
        except Exception as e:
            rpt(f'  Q{int(q*100):02d}: 拟合失败 - {e}')

    # --- B4: 面板固定效应 ---
    rpt('\nB4: 面板固定效应回归')
    rpt('  MUQ_gdp(i,t) = beta*hu_growth(i,t) + MSA_FE + Year_FE')
    df_b4 = df_b[df_b['MUQ_gdp'].notna() & df_b['hu_growth'].notna()].copy()
    df_b4['MUQ_gdp_w'] = winsorize(df_b4['MUQ_gdp'])
    df_b4['hu_growth_w'] = winsorize(df_b4['hu_growth'])

    # 组内去均值 (within estimator)
    for col in ['MUQ_gdp_w', 'hu_growth_w']:
        group_mean = df_b4.groupby('cbsa_code')[col].transform('mean')
        df_b4[col + '_dm'] = df_b4[col] - group_mean
    # 年份去均值
    for col in ['MUQ_gdp_w_dm', 'hu_growth_w_dm']:
        year_mean = df_b4.groupby('year')[col].transform('mean')
        df_b4[col + '_twfe'] = df_b4[col] - year_mean

    m4 = run_ols(df_b4['MUQ_gdp_w_dm_twfe'], df_b4[['hu_growth_w_dm_twfe']], 'B4-TWFE')
    if m4 is not None:
        report_model(m4, 'Within estimator (TWFE)', 'hu_growth_w_dm_twfe')

elif not PANEL_MODE:
    # 截面回归
    rpt('\nB1: V_GDP_ratio ~ hu_per_capita (截面 OLS)')
    df_b = panel_diff.dropna(subset=['V_GDP_ratio', 'hu_per_capita']).copy()
    df_b['V_GDP_ratio_w'] = winsorize(df_b['V_GDP_ratio'])
    df_b['hu_per_capita_w'] = winsorize(df_b['hu_per_capita'])
    m1 = run_ols(df_b['V_GDP_ratio_w'], df_b[['hu_per_capita_w']], 'B1-cross')
    report_model(m1, 'V_GDP_ratio ~ hu_per_capita', 'hu_per_capita_w')

    rpt('\nB2: V_GDP_ratio ~ ln(population) (截面 OLS)')
    df_b['ln_pop'] = np.log(df_b['population'])
    m2 = run_ols(df_b['V_GDP_ratio_w'], df_b[['ln_pop']], 'B2-cross')
    report_model(m2, 'V_GDP_ratio ~ ln_pop', 'ln_pop')

    # 分位数回归
    rpt('\nB3: 分位数回归 V_GDP_ratio ~ hu_per_capita')
    X_qr = sm.add_constant(df_b['hu_per_capita_w'])
    for q in [0.10, 0.25, 0.50, 0.75, 0.90]:
        try:
            qm = QuantReg(df_b['V_GDP_ratio_w'], X_qr).fit(q=q)
            beta_q = qm.params['hu_per_capita_w']
            ci_q = qm.conf_int().loc['hu_per_capita_w']
            p_q = qm.pvalues['hu_per_capita_w']
            rpt(f'  Q{int(q*100):02d}: beta = {beta_q:.4f}, '
                f'95% CI = [{ci_q[0]:.4f}, {ci_q[1]:.4f}], p = {p_q:.6f}')
        except Exception as e:
            rpt(f'  Q{int(q*100):02d}: 拟合失败 - {e}')

# ============================================================
# 步骤 8: MUQ vs 城市规模
# ============================================================
rpt('\n' + '=' * 72)
rpt('Part C: MUQ vs 城市规模')
rpt('=' * 72)

if PANEL_MODE and 'MUQ_gdp' in panel_diff.columns:
    df_c = panel_diff[panel_diff['MUQ_gdp'].notna()].copy()
    df_c['MUQ_gdp_w'] = winsorize(df_c['MUQ_gdp'])
    df_c['ln_pop'] = np.log(df_c['population'])
    mc = run_ols(df_c['MUQ_gdp_w'], df_c[['ln_pop']], 'C1')
    report_model(mc, 'MUQ_gdp ~ ln(population)', 'ln_pop')
else:
    rpt('  (使用截面 V_GDP_ratio, 已在 B2 报告)')

# ============================================================
# 步骤 9: 区域差异
# ============================================================
rpt('\n' + '=' * 72)
rpt('Part D: 区域差异')
rpt('=' * 72)

if 'region' in panel_diff.columns:
    if PANEL_MODE and 'MUQ_gdp' in panel_diff.columns:
        muq_col = 'MUQ_gdp'
    else:
        muq_col = 'V_GDP_ratio'

    df_d = panel_diff[panel_diff[muq_col].notna() & panel_diff['region'].notna()].copy()
    df_d[muq_col + '_w'] = winsorize(df_d[muq_col])

    region_stats = df_d.groupby('region')[muq_col + '_w'].agg(['mean', 'median', 'std', 'count'])
    rpt(f'\n  区域 {muq_col} 分布:')
    rpt(region_stats.to_string())

    # Kruskal-Wallis 检验
    groups = [g[muq_col + '_w'].dropna().values for _, g in df_d.groupby('region')]
    groups = [g for g in groups if len(g) > 5]
    if len(groups) >= 2:
        h_stat, h_p = stats.kruskal(*groups)
        rpt(f'\n  Kruskal-Wallis 检验: H = {h_stat:.3f}, p = {h_p:.6f}')

# ============================================================
# 步骤 10: 跨国对比表
# ============================================================
rpt('\n' + '=' * 72)
rpt('Part E: 跨国对比 (中国 vs 美国)')
rpt('=' * 72)

rpt('''
  指标                     中国 290 城市 (2010-2016)    美国 MSA
  ----------------------------------------------------------------
  投资强度指标             FAI/GDP                      hu_growth / invest_intensity
  MUQ 指标                ΔV/I (with K-stock)          ΔV/GDP or ΔV/(ΔHU×P)
  核心发现:
    中国: beta(FAI/GDP) = -2.2342, p < 10^-6, R2 = 0.124
    (Pooled OLS, N=455)
''')

# 填入美国结果
if PANEL_MODE and has_gdp and m1 is not None:
    rpt(f'    美国: beta(hu_growth) = {m1.params.iloc[1]:.4f}, '
        f'p = {m1.pvalues.iloc[1]:.6f}, R2 = {m1.rsquared:.4f}')
    rpt(f'    (Pooled OLS, N={int(m1.nobs)})')
    if m1.params.iloc[1] < 0:
        rpt('\n  >>> 结论: 投资强度与 MUQ 的负相关在美国也成立!')
        rpt('  >>> 这支持了 "过度建设降低边际效率" 的跨国普遍性')
    else:
        rpt('\n  >>> 注意: 美国的系数为正, 与中国方向不一致')
        rpt('  >>> 可能原因: 美国住房市场供给弹性不同 / 投资强度度量差异')

elif not PANEL_MODE and m1 is not None:
    rpt(f'    美国 (截面): beta(hu_per_capita) = {m1.params.iloc[1]:.4f}, '
        f'p = {m1.pvalues.iloc[1]:.6f}, R2 = {m1.rsquared:.4f}')
    rpt(f'    (截面 OLS, N={int(m1.nobs)})')

rpt('\n  方法论注意事项:')
rpt('  1. 中国使用 FAI (固定资产投资) 含建筑/设备/安装, 美国使用住房单元增量')
rpt('  2. 中国 MUQ 基于永续盘存法资本存量, 美国基于中位价×单元数')
rpt('  3. 美国住房市场供给弹性地区差异大 (Saiz 2010), 影响 MUQ 含义')
rpt('  4. ACS 中位房价反映存量价值, 非新建成本, 可能引入估值偏差')

# ============================================================
# 步骤 11: 可视化
# ============================================================
rpt('\n' + '=' * 72)
rpt('步骤 11: 可视化')
rpt('=' * 72)

fig = plt.figure(figsize=(18, 14))
gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.30)

# 配色
color_main = '#2166AC'
color_accent = '#B2182B'
color_fit = '#D6604D'
alpha_pts = 0.3

if PANEL_MODE and has_gdp and 'MUQ_gdp' in panel_diff.columns:
    df_plot = panel_diff.copy()
    df_plot = df_plot[df_plot['MUQ_gdp'].notna()].copy()
    df_plot['MUQ_gdp_w'] = winsorize(df_plot['MUQ_gdp'])

    # Panel A: MUQ 分布直方图
    ax1 = fig.add_subplot(gs[0, 0])
    vals = df_plot['MUQ_gdp_w']
    ax1.hist(vals, bins=60, color=color_main, alpha=0.7, edgecolor='white', linewidth=0.3)
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='MUQ=0')
    ax1.axvline(x=1, color='orange', linestyle='--', linewidth=1.5, label='MUQ=1')
    ax1.axvline(x=vals.median(), color='green', linestyle='-', linewidth=1.5,
                label=f'Median={vals.median():.2f}')
    ax1.set_xlabel('MUQ (dV/GDP)', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('(a) Distribution of MUQ', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=8)

    # Panel B: MUQ vs hu_growth (散点 + 回归线)
    ax2 = fig.add_subplot(gs[0, 1])
    mask = df_plot['hu_growth'].notna()
    df_p2 = df_plot[mask].copy()
    df_p2['hu_growth_w'] = winsorize(df_p2['hu_growth'])
    ax2.scatter(df_p2['hu_growth_w'], df_p2['MUQ_gdp_w'],
               s=5, alpha=alpha_pts, color=color_main, rasterized=True)
    # 回归线
    x_fit = df_p2['hu_growth_w'].dropna()
    y_fit = df_p2.loc[x_fit.index, 'MUQ_gdp_w']
    mask_fit = x_fit.notna() & y_fit.notna()
    if mask_fit.sum() > 20:
        z = np.polyfit(x_fit[mask_fit], y_fit[mask_fit], 1)
        x_line = np.linspace(x_fit[mask_fit].quantile(0.02), x_fit[mask_fit].quantile(0.98), 100)
        ax2.plot(x_line, np.polyval(z, x_line), color=color_fit, linewidth=2.5,
                label=f'OLS: b={z[0]:.2f}')
    ax2.axhline(y=0, color='grey', linestyle=':', linewidth=0.8)
    ax2.set_xlabel('Housing Unit Growth Rate', fontsize=11)
    ax2.set_ylabel('MUQ (dV/GDP)', fontsize=11)
    ax2.set_title('(b) MUQ vs Investment Intensity', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)

    # Panel C: MUQ vs ln(population)
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.scatter(df_plot['ln_pop'], df_plot['MUQ_gdp_w'],
               s=5, alpha=alpha_pts, color=color_main, rasterized=True)
    z3 = np.polyfit(df_plot['ln_pop'].dropna(), df_plot.loc[df_plot['ln_pop'].notna(), 'MUQ_gdp_w'], 1)
    x_line3 = np.linspace(df_plot['ln_pop'].min(), df_plot['ln_pop'].max(), 100)
    ax3.plot(x_line3, np.polyval(z3, x_line3), color=color_fit, linewidth=2.5,
            label=f'OLS: b={z3[0]:.2f}')
    ax3.set_xlabel('ln(Population)', fontsize=11)
    ax3.set_ylabel('MUQ (dV/GDP)', fontsize=11)
    ax3.set_title('(c) MUQ vs City Size', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)

    # Panel D: 区域箱线图
    ax4 = fig.add_subplot(gs[1, 0])
    if 'region' in df_plot.columns:
        regions_order = ['Northeast', 'Midwest', 'South', 'West']
        region_data = [df_plot[df_plot['region'] == r]['MUQ_gdp_w'].dropna()
                      for r in regions_order if r in df_plot['region'].values]
        region_labels = [r for r in regions_order if r in df_plot['region'].values]
        bp = ax4.boxplot(region_data, labels=region_labels, patch_artist=True,
                        showfliers=False, medianprops=dict(color='black', linewidth=2))
        colors_box = ['#4393C3', '#92C5DE', '#F4A582', '#D6604D']
        for patch, color in zip(bp['boxes'], colors_box[:len(region_data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    ax4.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax4.set_ylabel('MUQ (dV/GDP)', fontsize=11)
    ax4.set_title('(d) MUQ by Region', fontsize=13, fontweight='bold')

    # Panel E: MUQ 时间趋势
    ax5 = fig.add_subplot(gs[1, 1])
    yearly = df_plot.groupby('year')['MUQ_gdp_w'].agg(['mean', 'median',
                                                         lambda x: x.quantile(0.25),
                                                         lambda x: x.quantile(0.75)])
    yearly.columns = ['mean', 'median', 'q25', 'q75']
    ax5.fill_between(yearly.index, yearly['q25'], yearly['q75'],
                    alpha=0.2, color=color_main, label='IQR')
    ax5.plot(yearly.index, yearly['median'], 'o-', color=color_main,
            linewidth=2, markersize=5, label='Median')
    ax5.plot(yearly.index, yearly['mean'], 's--', color=color_accent,
            linewidth=1.5, markersize=4, label='Mean')
    ax5.axhline(y=0, color='grey', linestyle=':', linewidth=0.8)
    ax5.set_xlabel('Year', fontsize=11)
    ax5.set_ylabel('MUQ (dV/GDP)', fontsize=11)
    ax5.set_title('(e) MUQ Time Trend', fontsize=13, fontweight='bold')
    ax5.legend(fontsize=9)

    # Panel F: 分位数回归系数图
    ax6 = fig.add_subplot(gs[1, 2])
    quantiles = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    betas_q = []
    ci_lo_q = []
    ci_hi_q = []
    df_qr = df_plot[df_plot['hu_growth'].notna()].copy()
    df_qr['hu_growth_w'] = winsorize(df_qr['hu_growth'])
    X_qr_plot = sm.add_constant(df_qr['hu_growth_w'])
    for q in quantiles:
        try:
            qm = QuantReg(df_qr['MUQ_gdp_w'], X_qr_plot).fit(q=q)
            betas_q.append(qm.params['hu_growth_w'])
            ci = qm.conf_int().loc['hu_growth_w']
            ci_lo_q.append(ci[0])
            ci_hi_q.append(ci[1])
        except Exception:
            betas_q.append(np.nan)
            ci_lo_q.append(np.nan)
            ci_hi_q.append(np.nan)

    ax6.fill_between(quantiles, ci_lo_q, ci_hi_q, alpha=0.2, color=color_main)
    ax6.plot(quantiles, betas_q, 'o-', color=color_main, linewidth=2, markersize=6)
    ax6.axhline(y=0, color='red', linestyle='--', linewidth=1)
    # OLS 估计
    if m1 is not None:
        ax6.axhline(y=m1.params.iloc[1], color=color_accent, linestyle=':', linewidth=1.5,
                    label=f'OLS: {m1.params.iloc[1]:.2f}')
    ax6.set_xlabel('Quantile', fontsize=11)
    ax6.set_ylabel('Coefficient on Investment Intensity', fontsize=11)
    ax6.set_title('(f) Quantile Regression Coefficients', fontsize=13, fontweight='bold')
    ax6.legend(fontsize=9)

else:
    # 截面版本图
    df_plot = panel_diff.dropna(subset=['V_GDP_ratio', 'hu_per_capita']).copy()
    df_plot['V_GDP_ratio_w'] = winsorize(df_plot['V_GDP_ratio'])
    df_plot['hu_per_capita_w'] = winsorize(df_plot['hu_per_capita'])

    # A: V/GDP 分布
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(df_plot['V_GDP_ratio_w'], bins=50, color=color_main, alpha=0.7, edgecolor='white')
    ax1.axvline(x=1, color='red', linestyle='--', linewidth=1.5, label='V/GDP=1')
    ax1.axvline(x=df_plot['V_GDP_ratio_w'].median(), color='green', linestyle='-',
                linewidth=1.5, label=f'Median={df_plot["V_GDP_ratio_w"].median():.2f}')
    ax1.set_xlabel('V/GDP Ratio', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('(a) Distribution of V/GDP', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)

    # B: V/GDP vs hu_per_capita
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.scatter(df_plot['hu_per_capita_w'], df_plot['V_GDP_ratio_w'],
               s=10, alpha=0.4, color=color_main)
    z2 = np.polyfit(df_plot['hu_per_capita_w'], df_plot['V_GDP_ratio_w'], 1)
    x_line = np.linspace(df_plot['hu_per_capita_w'].min(), df_plot['hu_per_capita_w'].max(), 100)
    ax2.plot(x_line, np.polyval(z2, x_line), color=color_fit, linewidth=2.5,
            label=f'OLS: b={z2[0]:.2f}')
    ax2.set_xlabel('Housing Units per Capita', fontsize=11)
    ax2.set_ylabel('V/GDP Ratio', fontsize=11)
    ax2.set_title('(b) V/GDP vs Housing Density', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)

    # C: V/GDP vs ln(pop)
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.scatter(df_plot['ln_pop'], df_plot['V_GDP_ratio_w'],
               s=10, alpha=0.4, color=color_main)
    z3 = np.polyfit(df_plot['ln_pop'], df_plot['V_GDP_ratio_w'], 1)
    x_line3 = np.linspace(df_plot['ln_pop'].min(), df_plot['ln_pop'].max(), 100)
    ax3.plot(x_line3, np.polyval(z3, x_line3), color=color_fit, linewidth=2.5,
            label=f'OLS: b={z3[0]:.2f}')
    ax3.set_xlabel('ln(Population)', fontsize=11)
    ax3.set_ylabel('V/GDP Ratio', fontsize=11)
    ax3.set_title('(c) V/GDP vs City Size', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)

    # D: 区域箱线图
    ax4 = fig.add_subplot(gs[1, 0])
    if 'region' in df_plot.columns:
        regions_order = ['Northeast', 'Midwest', 'South', 'West']
        region_data = [df_plot[df_plot['region'] == r]['V_GDP_ratio_w'].dropna()
                      for r in regions_order if r in df_plot['region'].values]
        region_labels = [r for r in regions_order if r in df_plot['region'].values]
        bp = ax4.boxplot(region_data, labels=region_labels, patch_artist=True,
                        showfliers=False, medianprops=dict(color='black', linewidth=2))
        colors_box = ['#4393C3', '#92C5DE', '#F4A582', '#D6604D']
        for patch, color in zip(bp['boxes'], colors_box[:len(region_data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    ax4.set_ylabel('V/GDP Ratio', fontsize=11)
    ax4.set_title('(d) V/GDP by Region', fontsize=13, fontweight='bold')

    # E: Metro vs Micro
    ax5 = fig.add_subplot(gs[1, 1])
    if 'is_metro' in df_plot.columns:
        metro_data = [df_plot[df_plot['is_metro'] == True]['V_GDP_ratio_w'].dropna(),
                     df_plot[df_plot['is_metro'] == False]['V_GDP_ratio_w'].dropna()]
        bp5 = ax5.boxplot(metro_data, labels=['Metro', 'Micro'], patch_artist=True,
                         showfliers=False, medianprops=dict(color='black', linewidth=2))
        bp5['boxes'][0].set_facecolor('#2166AC')
        bp5['boxes'][0].set_alpha(0.7)
        bp5['boxes'][1].set_facecolor('#B2182B')
        bp5['boxes'][1].set_alpha(0.7)
    ax5.set_ylabel('V/GDP Ratio', fontsize=11)
    ax5.set_title('(e) Metro vs Micro Areas', fontsize=13, fontweight='bold')

    # F: 分位数回归系数
    ax6 = fig.add_subplot(gs[1, 2])
    quantiles = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    betas_q = []
    ci_lo_q = []
    ci_hi_q = []
    X_qr_plot = sm.add_constant(df_plot['hu_per_capita_w'])
    for q in quantiles:
        try:
            qm = QuantReg(df_plot['V_GDP_ratio_w'], X_qr_plot).fit(q=q)
            betas_q.append(qm.params['hu_per_capita_w'])
            ci = qm.conf_int().loc['hu_per_capita_w']
            ci_lo_q.append(ci[0])
            ci_hi_q.append(ci[1])
        except Exception:
            betas_q.append(np.nan)
            ci_lo_q.append(np.nan)
            ci_hi_q.append(np.nan)
    ax6.fill_between(quantiles, ci_lo_q, ci_hi_q, alpha=0.2, color=color_main)
    ax6.plot(quantiles, betas_q, 'o-', color=color_main, linewidth=2, markersize=6)
    ax6.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax6.set_xlabel('Quantile', fontsize=11)
    ax6.set_ylabel('Coefficient on HU per Capita', fontsize=11)
    ax6.set_title('(f) Quantile Regression Coefficients', fontsize=13, fontweight='bold')

fig.suptitle('US MSA: Marginal Urban Q Analysis', fontsize=16, fontweight='bold', y=0.98)
fig_path = os.path.join(FIGS, 'fig_us_msa_muq.png')
plt.savefig(fig_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
rpt(f'\n  图表已保存: {fig_path}')

# 保存 source data
if PANEL_MODE and 'MUQ_gdp' in panel_diff.columns:
    src_cols = ['cbsa_code', 'msa_name', 'year', 'population', 'housing_units',
                'median_home_value', 'gdp_millions', 'V_total', 'MUQ_gdp', 'hu_growth']
    src_cols = [c for c in src_cols if c in panel_diff.columns]
    panel_diff[src_cols].to_csv(os.path.join(SOURCE_DIR, 'fig_us_msa_muq_source.csv'), index=False)

# ============================================================
# 保存报告
# ============================================================
report_path = os.path.join(MODELS, 'us_msa_muq_report.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rpt(f'\n报告已保存: {report_path}')

rpt('\n' + '=' * 72)
rpt('完成!')
rpt('=' * 72)
