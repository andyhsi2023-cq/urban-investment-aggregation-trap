#!/usr/bin/env python3
"""
82b_oecd_real_threshold.py
===========================
目的: 从 OECD SDMX API 获取 GFCF by asset type 真实数据，
      计算建设投资(Dwellings + Other buildings)/GDP，
      用真实比率重跑 Hansen 阈值面板模型

输入:
  - OECD SDMX API: DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_GFCF_ASSET
  - global_q_revised_panel.csv (已有面板数据)

输出:
  - 原始: 02-data/raw/oecd_gfcf_by_asset_real.csv
  - 处理: 02-data/processed/oecd_construction_gdp_panel.csv
  - 报告: 03-analysis/models/oecd_real_threshold_report.txt
  - 图表: 04-figures/drafts/fig_oecd_real_threshold.png
  - 脚本: 本文件

依赖: pandas, numpy, scipy, statsmodels, matplotlib, requests
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import requests
import time
import io

# ============================================================
# 路径配置
# ============================================================
BASE = Path('/Users/andy/Desktop/Claude/urban-q-phase-transition')
PANEL_PATH = BASE / '02-data/processed/global_q_revised_panel.csv'
RAW_PATH = BASE / '02-data/raw/oecd_gfcf_by_asset_real.csv'
PROC_PATH = BASE / '02-data/processed/oecd_construction_gdp_panel.csv'
REPORT_PATH = BASE / '03-analysis/models/oecd_real_threshold_report.txt'
FIG_PATH = BASE / '04-figures/drafts/fig_oecd_real_threshold.png'

for p in [RAW_PATH.parent, PROC_PATH.parent, REPORT_PATH.parent, FIG_PATH.parent]:
    p.mkdir(parents=True, exist_ok=True)

# 报告缓冲
report_lines = []
def log(msg=''):
    print(msg)
    report_lines.append(str(msg))

log('=' * 72)
log('OECD 真实建设投资/GDP 阈值分析')
log('Hansen Threshold Panel Model -- Real Construction Investment Data')
log(f'运行时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
log('=' * 72)
log()

# ============================================================
# STEP 1: 从 OECD SDMX API 下载 GFCF by asset type
# ============================================================
log('STEP 1: 从 OECD 下载 GFCF by asset type 数据')
log('-' * 72)

# API 端点模板
# 12维: FREQ.REF_AREA.SECTOR.COUNTERPART_SECTOR.TRANSACTION.INSTR_ASSET.ACTIVITY.EXPENDITURE.UNIT_MEASURE.PRICE_BASE.TRANSFORMATION.TABLE_IDENTIFIER
# 资产: N111G=Dwellings(gross), N112G=Other buildings(gross), N11G=Total fixed assets(gross)
# 单位: XDC=本币当前价格
# 价格基期: V=current prices

API_BASE = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_GFCF_ASSET,2.0"

# 分批下载: 按资产类型分批，避免超时
assets = {
    'N111G': 'Dwellings',
    'N112G': 'Other buildings and structures',
    'N11G': 'Total fixed assets'
}

all_frames = []
download_success = False

for asset_code, asset_name in assets.items():
    # 构造查询: A.{all countries}.S1.S1.P51G.{asset}._T._Z.XDC.V.N.T0102
    # 用 . 通配所有国家 (REF_AREA)
    query = f"A..S1.S1.P51G.{asset_code}._T._Z.XDC.V.N.T0102"
    url = f"{API_BASE}/{query}?startPeriod=1970&endPeriod=2023&format=csvfilewithlabels"

    log(f'  下载 {asset_name} ({asset_code})...')
    log(f'  URL: {url[:120]}...')

    try:
        resp = requests.get(url, timeout=60, headers={
            'Accept': 'text/csv'
        })
        log(f'  状态码: {resp.status_code}, 大小: {len(resp.content)} bytes')

        if resp.status_code == 200 and len(resp.content) > 100:
            df_asset = pd.read_csv(io.StringIO(resp.text))
            log(f'  行数: {len(df_asset)}, 列: {list(df_asset.columns)[:8]}...')
            df_asset['asset_query'] = asset_code
            df_asset['asset_label'] = asset_name
            all_frames.append(df_asset)
            download_success = True
        else:
            log(f'  警告: 响应异常，跳过')
            if len(resp.content) < 2000:
                log(f'  响应内容: {resp.text[:500]}')
    except Exception as e:
        log(f'  错误: {e}')

log()

if not download_success:
    log('所有 API 请求失败，尝试备选方案...')
    log()

    # 备选方案: 尝试不同的 format 参数或不同的查询结构
    # 尝试不指定 TABLE_IDENTIFIER
    for asset_code, asset_name in assets.items():
        query = f"A..S1.S1.P51G.{asset_code}._T._Z.XDC.V.N."
        url = f"{API_BASE}/{query}?startPeriod=1970&endPeriod=2023&format=csvfilewithlabels"
        log(f'  备选尝试 {asset_name}: {url[:120]}...')
        try:
            resp = requests.get(url, timeout=60)
            log(f'  状态码: {resp.status_code}, 大小: {len(resp.content)} bytes')
            if resp.status_code == 200 and len(resp.content) > 100:
                df_asset = pd.read_csv(io.StringIO(resp.text))
                log(f'  行数: {len(df_asset)}')
                df_asset['asset_query'] = asset_code
                df_asset['asset_label'] = asset_name
                all_frames.append(df_asset)
                download_success = True
            else:
                if len(resp.content) < 2000:
                    log(f'  响应: {resp.text[:500]}')
        except Exception as e:
            log(f'  错误: {e}')
    log()

if not download_success:
    log('备选方案也失败，尝试第三种查询格式...')
    log()
    # 尝试用 + 连接多个资产，一次性下载
    query = "A..S1.S1.P51G.N111G+N112G+N11G._T._Z.XDC.V.N.T0102"
    url = f"{API_BASE}/{query}?startPeriod=1970&endPeriod=2023&format=csvfilewithlabels"
    log(f'  合并查询: {url[:120]}...')
    try:
        resp = requests.get(url, timeout=90)
        log(f'  状态码: {resp.status_code}, 大小: {len(resp.content)} bytes')
        if resp.status_code == 200 and len(resp.content) > 100:
            df_all = pd.read_csv(io.StringIO(resp.text))
            log(f'  行数: {len(df_all)}, 列: {list(df_all.columns)[:10]}')
            all_frames.append(df_all)
            download_success = True
        else:
            if len(resp.content) < 2000:
                log(f'  响应: {resp.text[:500]}')
    except Exception as e:
        log(f'  错误: {e}')
    log()

# ============================================================
# STEP 2: 解析和清洗数据
# ============================================================
log('STEP 2: 解析和清洗数据')
log('-' * 72)

if not download_success or len(all_frames) == 0:
    log('错误: 无法从 OECD 获取数据，退出')
    # 保存报告
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    raise SystemExit('OECD API 数据下载失败')

# 合并所有下载帧
raw_df = pd.concat(all_frames, ignore_index=True)
log(f'合并后原始数据: {len(raw_df)} 行')
log(f'列名: {list(raw_df.columns)}')
log()

# 保存原始数据
raw_df.to_csv(RAW_PATH, index=False)
log(f'原始数据已保存: {RAW_PATH}')

# 识别关键列名 (OECD CSV 格式可能有变化)
# 典型列: REF_AREA, TIME_PERIOD, OBS_VALUE, INSTR_ASSET (或带 label 后缀)
col_map = {}
for col in raw_df.columns:
    col_lower = col.lower()
    if 'ref_area' in col_lower and 'label' not in col_lower:
        col_map['country'] = col
    elif 'time_period' in col_lower:
        col_map['year'] = col
    elif 'obs_value' in col_lower:
        col_map['value'] = col
    elif 'instr_asset' in col_lower and 'label' not in col_lower:
        col_map['asset'] = col
    elif col_lower == 'ref_area: reference area':
        col_map['country_name'] = col

log(f'列映射: {col_map}')

if not all(k in col_map for k in ['country', 'year', 'value']):
    log('警告: 无法识别关键列名，尝试备用解析...')
    log(f'前5行:\n{raw_df.head().to_string()}')
    # 尝试位置映射
    log(f'所有列: {list(raw_df.columns)}')
    # 保存报告并退出
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    raise SystemExit('无法解析 OECD 数据列名')

# 标准化
oecd = raw_df.rename(columns={
    col_map['country']: 'country_code',
    col_map['year']: 'year',
    col_map['value']: 'value'
})

# 资产类型列
if 'asset' in col_map:
    oecd = oecd.rename(columns={col_map['asset']: 'asset_code'})
elif 'asset_query' in oecd.columns:
    oecd['asset_code'] = oecd['asset_query']
else:
    log('警告: 无法识别资产类型列')
    log(f'可用列: {list(oecd.columns)}')

oecd['year'] = pd.to_numeric(oecd['year'], errors='coerce')
oecd['value'] = pd.to_numeric(oecd['value'], errors='coerce')

# 清除 NaN
oecd = oecd.dropna(subset=['country_code', 'year', 'value', 'asset_code'])
log(f'清洗后: {len(oecd)} 行, {oecd["country_code"].nunique()} 国')
log(f'资产类型分布:\n{oecd["asset_code"].value_counts().to_string()}')
log(f'年份范围: {oecd["year"].min():.0f} - {oecd["year"].max():.0f}')
log()

# ============================================================
# STEP 3: 计算建设投资/GDP
# ============================================================
log('STEP 3: 计算建设投资/GDP')
log('-' * 72)

# 透视: country-year 为行, asset_code 为列
pivot = oecd.pivot_table(
    index=['country_code', 'year'],
    columns='asset_code',
    values='value',
    aggfunc='sum'  # 如有重复取和
).reset_index()

# 计算建设投资 = Dwellings + Other buildings
# 有些国家可能只有 N111G 或 N112G
if 'N111G' in pivot.columns and 'N112G' in pivot.columns:
    pivot['construction'] = pivot['N111G'].fillna(0) + pivot['N112G'].fillna(0)
    # 只有两者都缺失才设为 NaN
    both_missing = pivot['N111G'].isna() & pivot['N112G'].isna()
    pivot.loc[both_missing, 'construction'] = np.nan
elif 'N111G' in pivot.columns:
    pivot['construction'] = pivot['N111G']
elif 'N112G' in pivot.columns:
    pivot['construction'] = pivot['N112G']
else:
    log('错误: 无 Dwellings 或 Other buildings 数据')
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    raise SystemExit('缺少建设投资数据')

# Total fixed assets
if 'N11G' in pivot.columns:
    pivot['total_fa'] = pivot['N11G']
else:
    log('警告: 无 Total fixed assets (N11G) 数据')
    pivot['total_fa'] = np.nan

# 计算建设占 GFCF 比例 (内部比率，无需匹配 GDP 口径)
pivot['constr_share_gfcf'] = pivot['construction'] / pivot['total_fa']

log(f'透视后: {len(pivot)} 行, {pivot["country_code"].nunique()} 国')
log(f'  Dwellings (N111G) 非空: {pivot["N111G"].notna().sum() if "N111G" in pivot.columns else 0}')
log(f'  Other buildings (N112G) 非空: {pivot["N112G"].notna().sum() if "N112G" in pivot.columns else 0}')
log(f'  Construction 非空: {pivot["construction"].notna().sum()}')
log(f'  Total FA (N11G) 非空: {pivot["total_fa"].notna().sum()}')
log(f'  Construction/GFCF 比例非空: {pivot["constr_share_gfcf"].notna().sum()}')
log()

# 统计: 建设占 GFCF 的比例分布
valid_share = pivot['constr_share_gfcf'].dropna()
if len(valid_share) > 0:
    log(f'建设占 GFCF 比例统计:')
    log(f'  均值: {valid_share.mean():.3f} ({valid_share.mean()*100:.1f}%)')
    log(f'  中位数: {valid_share.median():.3f} ({valid_share.median()*100:.1f}%)')
    log(f'  P25-P75: [{valid_share.quantile(0.25):.3f}, {valid_share.quantile(0.75):.3f}]')
    log(f'  最小值: {valid_share.min():.3f}, 最大值: {valid_share.max():.3f}')
log()

# ============================================================
# STEP 4: 合并到已有面板
# ============================================================
log('STEP 4: 合并到已有面板')
log('-' * 72)

panel = pd.read_csv(PANEL_PATH)
panel = panel.sort_values(['country_code', 'year'])

# 关键变量
panel['dCPR'] = panel.groupby('country_code')['CPR'].diff()
panel['gdp_growth'] = panel.groupby('country_code')['gdp_constant_2015'].pct_change() * 100

# 合并 OECD 建设数据
merge_cols = ['country_code', 'year', 'construction', 'total_fa', 'constr_share_gfcf']
if 'N111G' in pivot.columns:
    merge_cols.append('N111G')
if 'N112G' in pivot.columns:
    merge_cols.append('N112G')

merged = panel.merge(
    pivot[merge_cols],
    on=['country_code', 'year'],
    how='left'
)

# 计算 Construction/GDP
# 方法: Construction/GDP = (Construction/Total_GFCF) * (Total_GFCF/GDP)
# Total_GFCF/GDP 已有: gfcf_pct_gdp (百分比)
merged['construction_gdp'] = merged['constr_share_gfcf'] * merged['gfcf_pct_gdp']

# 统计合并结果
n_with_constr = merged['construction_gdp'].notna().sum()
n_countries_constr = merged[merged['construction_gdp'].notna()]['country_code'].nunique()
log(f'合并结果:')
log(f'  总行数: {len(merged)}')
log(f'  有建设/GDP 数据的观测: {n_with_constr}')
log(f'  覆盖国家: {n_countries_constr}')
log()

# 可用国家列表
countries_avail = merged[merged['construction_gdp'].notna()]['country_code'].unique()
log(f'有建设投资数据的国家 ({len(countries_avail)}):')
for i in range(0, len(countries_avail), 10):
    log(f'  {", ".join(countries_avail[i:i+10])}')
log()

# 保存处理后的面板
merged.to_csv(PROC_PATH, index=False)
log(f'处理后面板已保存: {PROC_PATH}')
log()

# Construction/GDP 描述统计
constr_gdp = merged['construction_gdp'].dropna()
if len(constr_gdp) > 0:
    log(f'Construction/GDP (%) 描述统计:')
    log(f'  观测数: {len(constr_gdp)}')
    log(f'  均值: {constr_gdp.mean():.2f}%')
    log(f'  中位数: {constr_gdp.median():.2f}%')
    log(f'  标准差: {constr_gdp.std():.2f}%')
    log(f'  P5: {constr_gdp.quantile(0.05):.2f}%, P95: {constr_gdp.quantile(0.95):.2f}%')
    log(f'  最小: {constr_gdp.min():.2f}%, 最大: {constr_gdp.max():.2f}%')
log()

# ============================================================
# STEP 5: Hansen 阈值面板模型
# ============================================================
log('=' * 72)
log('STEP 5: Hansen 阈值面板模型 -- Construction/GDP')
log('=' * 72)
log()

# 工作样本
work = merged.dropna(subset=['CPR', 'construction_gdp', 'dCPR', 'urban_pct']).copy()
work = work[(work['construction_gdp'] > 0) & (work['construction_gdp'] < 50)]

# 去除 dCPR 极端值
q_low, q_high = work['dCPR'].quantile(0.005), work['dCPR'].quantile(0.995)
work = work[(work['dCPR'] >= q_low) & (work['dCPR'] <= q_high)]

log(f'工作样本: {work.shape[0]} 观测, {work["country_code"].nunique()} 国')
log(f'Construction/GDP 范围: {work["construction_gdp"].min():.2f}% - {work["construction_gdp"].max():.2f}%')
log(f'dCPR 范围: {work["dCPR"].min():.4f} - {work["dCPR"].max():.4f}')
log()

if len(work) < 100:
    log('错误: 工作样本不足 100 观测，无法进行阈值分析')
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    raise SystemExit('样本量不足')


# --- 双向固定效应 within 变换 ---
def demean_twoway(data, y_col, x_vars):
    """双向固定效应 within 变换"""
    d = data.copy()
    cols = [y_col] + x_vars
    d_clean = d.dropna(subset=cols).copy()

    y = d_clean[y_col].values
    cm_y = d_clean.groupby('country_code')[y_col].transform('mean')
    ym_y = d_clean.groupby('year')[y_col].transform('mean')
    y_dm = y - cm_y.values - ym_y.values + y.mean()

    X_list = []
    for v in x_vars:
        cm = d_clean.groupby('country_code')[v].transform('mean')
        ym = d_clean.groupby('year')[v].transform('mean')
        X_list.append(d_clean[v].values - cm.values - ym.values + d_clean[v].mean())
    X = np.column_stack(X_list)

    return y_dm, X, d_clean


def threshold_panel(data, gamma, y_col='dCPR', threshold_col='construction_gdp',
                    controls=None):
    """
    阈值面板回归:
    dCPR = mu_i + lambda_t + alpha*I(high) + beta_low*x*I(low) + beta_high*x*I(high) + controls + eps
    """
    d = data.copy()
    low = (d[threshold_col] < gamma).astype(float)
    high = (d[threshold_col] >= gamma).astype(float)

    d['regime_high'] = high
    d['x_low'] = d[threshold_col] * low
    d['x_high'] = d[threshold_col] * high

    x_vars = ['regime_high', 'x_low', 'x_high']
    if controls:
        for c in controls:
            if c in d.columns and d[c].notna().sum() > 0.5 * len(d):
                x_vars.append(c)

    y_dm, X, d_clean = demean_twoway(d, y_col, x_vars)

    try:
        betas, residuals, rank, sv = np.linalg.lstsq(X, y_dm, rcond=None)
        resid = y_dm - X @ betas
        ssr = np.sum(resid ** 2)
        n = len(y_dm)
        k = X.shape[1]
        sigma2 = ssr / (n - k) if n > k else np.nan
        try:
            XtX_inv = np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(sigma2 * XtX_inv))
        except:
            se = np.full(k, np.nan)

        n_low = int((d_clean[threshold_col] < gamma).sum())
        n_high = int((d_clean[threshold_col] >= gamma).sum())

        return {
            'ssr': ssr, 'n': n, 'k': k,
            'betas': dict(zip(x_vars, betas)),
            'se': dict(zip(x_vars, se)),
            'n_low': n_low, 'n_high': n_high
        }
    except:
        return {'ssr': np.inf, 'n': 0, 'k': 0, 'betas': {}, 'se': {},
                'n_low': 0, 'n_high': 0}


def linear_panel(data, y_col='dCPR', threshold_col='construction_gdp', controls=None):
    """线性面板 (无阈值)"""
    d = data.copy()
    x_vars = [threshold_col]
    if controls:
        for c in controls:
            if c in d.columns and d[c].notna().sum() > 0.5 * len(d):
                x_vars.append(c)
    y_dm, X, d_clean = demean_twoway(d, y_col, x_vars)
    betas = np.linalg.lstsq(X, y_dm, rcond=None)[0]
    resid = y_dm - X @ betas
    return np.sum(resid ** 2), len(y_dm), X.shape[1]


# --- PART A: 非参数探索 ---
log('PART A: 非参数探索')
log('-' * 72)

# A1: 分 bin 统计
n_bins = min(10, len(work) // 30)
if n_bins >= 3:
    work['constr_bin'] = pd.qcut(work['construction_gdp'], n_bins, duplicates='drop')
    bin_stats = work.groupby('constr_bin', observed=True).agg(
        n=('dCPR', 'count'),
        median_dCPR=('dCPR', 'median'),
        mean_dCPR=('dCPR', 'mean'),
        std_dCPR=('dCPR', 'std'),
        median_constr=('construction_gdp', 'median')
    ).reset_index()

    log(f'Construction/GDP {n_bins}分位 bin 统计:')
    log(f'{"Bin":<30s} {"N":>5s} {"Med dCPR":>10s} {"Mean dCPR":>10s} {"Med C/GDP":>10s}')
    log('-' * 72)
    for _, row in bin_stats.iterrows():
        log(f'{str(row["constr_bin"]):<30s} {row["n"]:>5.0f} {row["median_dCPR"]:>10.4f} '
            f'{row["mean_dCPR"]:>10.4f} {row["median_constr"]:>10.2f}')
    log()

# A2: LOESS 回归
x_vals = work['construction_gdp'].values
y_vals = work['dCPR'].values

lowess_result = sm.nonparametric.lowess(y_vals, x_vals, frac=0.3, return_sorted=True)
lowess_x = lowess_result[:, 0]
lowess_y = lowess_result[:, 1]

# 零线交叉
zero_crossings = []
for i in range(len(lowess_y) - 1):
    if lowess_y[i] * lowess_y[i+1] < 0:
        x_cross = lowess_x[i] + (0 - lowess_y[i]) * (lowess_x[i+1] - lowess_x[i]) / (lowess_y[i+1] - lowess_y[i])
        zero_crossings.append(x_cross)

log(f'LOESS 零线交叉点: {[f"{x:.2f}%" for x in zero_crossings]}')
log()

# --- PART B: Hansen 阈值模型 grid search ---
log('PART B: Hansen 阈值面板模型')
log('-' * 72)

controls = ['urban_pct', 'gdp_growth']
work_hansen = work.dropna(subset=['dCPR', 'construction_gdp', 'urban_pct', 'gdp_growth']).copy()
log(f'Hansen 模型样本: {len(work_hansen)} 观测, {work_hansen["country_code"].nunique()} 国')

# 网格搜索范围
gamma_lo = max(2.0, work_hansen['construction_gdp'].quantile(0.10))
gamma_hi = min(30.0, work_hansen['construction_gdp'].quantile(0.90))
step = 0.2  # 更精细的步长

gamma_grid = np.arange(gamma_lo, gamma_hi + step, step)
gamma_grid = np.round(gamma_grid, 1)
log(f'Grid search: [{gamma_lo:.1f}%, {gamma_hi:.1f}%], 步长 {step}pp, {len(gamma_grid)} 点')
log()

# SSR profile
ssr_profile = []
t_start = time.time()
for gamma in gamma_grid:
    res = threshold_panel(work_hansen, gamma, controls=controls)
    ssr_profile.append({
        'gamma': gamma,
        'ssr': res['ssr'],
        'beta_x_low': res['betas'].get('x_low', np.nan),
        'beta_x_high': res['betas'].get('x_high', np.nan),
        'se_x_low': res['se'].get('x_low', np.nan),
        'se_x_high': res['se'].get('x_high', np.nan),
        'beta_regime': res['betas'].get('regime_high', np.nan),
        'se_regime': res['se'].get('regime_high', np.nan),
        'n_low': res['n_low'],
        'n_high': res['n_high']
    })

ssr_df = pd.DataFrame(ssr_profile)
t_elapsed = time.time() - t_start

# 最优 gamma (每个体制至少 5% 样本)
min_regime_n = max(30, len(work_hansen) * 0.05)
valid = ssr_df[(ssr_df['n_low'] >= min_regime_n) & (ssr_df['n_high'] >= min_regime_n)]

if len(valid) == 0:
    log('错误: 无满足最小样本要求的阈值点')
    min_regime_n = 10
    valid = ssr_df[(ssr_df['n_low'] >= min_regime_n) & (ssr_df['n_high'] >= min_regime_n)]

best = valid.loc[valid['ssr'].idxmin()]
gamma_hat = best['gamma']

log(f'Grid search 完成 ({t_elapsed:.1f}s)')
log()

# SSR profile 摘要
log('SSR Profile (关键点):')
log(f'{"gamma":>7s} {"SSR":>12s} {"beta_low":>10s} {"beta_high":>10s} {"regime":>10s} {"n_low":>6s} {"n_high":>6s}')
log('-' * 72)
# 显示每 1pp 的点 + 最优点
display_gammas = set(np.arange(np.floor(gamma_lo), np.ceil(gamma_hi) + 1, 1.0))
display_gammas.add(gamma_hat)
for _, row in ssr_df.iterrows():
    if row['gamma'] in display_gammas or abs(row['gamma'] - gamma_hat) < 0.01:
        marker = ' <<<' if abs(row['gamma'] - gamma_hat) < 0.01 else ''
        log(f'{row["gamma"]:>7.1f} {row["ssr"]:>12.2f} {row["beta_x_low"]:>10.6f} '
            f'{row["beta_x_high"]:>10.6f} {row["beta_regime"]:>10.4f} '
            f'{row["n_low"]:>6.0f} {row["n_high"]:>6.0f}{marker}')
log()

log(f'最优阈值 gamma_hat = {gamma_hat:.1f}%')
log(f'  SSR = {best["ssr"]:.2f}')
log(f'  beta (low regime, C/GDP < {gamma_hat:.1f}%): {best["beta_x_low"]:.6f} (SE = {best["se_x_low"]:.6f})')
log(f'  beta (high regime, C/GDP >= {gamma_hat:.1f}%): {best["beta_x_high"]:.6f} (SE = {best["se_x_high"]:.6f})')
log(f'  regime intercept diff: {best["beta_regime"]:.4f} (SE = {best["se_regime"]:.4f})')
log(f'  n_low = {best["n_low"]:.0f}, n_high = {best["n_high"]:.0f}')
log()

# 经济含义
log('经济含义:')
log(f'  Construction/GDP < {gamma_hat:.1f}%: 每增加1pp建设投资, dCPR = {best["beta_x_low"]:.4f}')
log(f'  Construction/GDP >= {gamma_hat:.1f}%: 每增加1pp建设投资, dCPR = {best["beta_x_high"]:.4f}')
beta_diff = best['beta_x_high'] - best['beta_x_low']
log(f'  两体制斜率差: {beta_diff:.4f}')
if best['beta_x_low'] > 0 and best['beta_x_high'] < 0:
    log(f'  => 建设投资效率发生质变: 低于阈值时投资提升资本效率，高于阈值时投资降低效率')
elif best['beta_x_high'] < best['beta_x_low']:
    log(f'  => 超过阈值后建设投资的边际效率显著下降')
log()

# F 检验
ssr_linear, n_total, k_linear = linear_panel(work_hansen, controls=controls)
ssr_threshold = best['ssr']
k_threshold = k_linear + 2
k_diff = k_threshold - k_linear

F_stat = ((ssr_linear - ssr_threshold) / k_diff) / (ssr_threshold / (n_total - k_threshold))
p_F = 1 - stats.f.cdf(F_stat, k_diff, n_total - k_threshold)

log(f'阈值效应 F 检验:')
log(f'  SSR_linear = {ssr_linear:.4f}')
log(f'  SSR_threshold = {ssr_threshold:.4f}')
log(f'  F({k_diff}, {n_total - k_threshold}) = {F_stat:.4f}')
log(f'  p = {p_F:.6f}')
sig = "***" if p_F < 0.001 else "**" if p_F < 0.01 else "*" if p_F < 0.05 else "n.s."
log(f'  显著性: {sig}')
log()


# --- Bootstrap 95% CI ---
log('Bootstrap 95% CI (500 replications, cluster by country)...')
np.random.seed(42)
n_boot = 500
gamma_boot = []
countries = work_hansen['country_code'].unique()

for b in range(n_boot):
    boot_countries = np.random.choice(countries, size=len(countries), replace=True)
    boot_data = []
    for i, c in enumerate(boot_countries):
        chunk = work_hansen[work_hansen['country_code'] == c].copy()
        chunk['country_code'] = f'{c}_{i}'
        boot_data.append(chunk)
    boot_df = pd.concat(boot_data, ignore_index=True)

    # 粗搜索 (1pp)
    best_ssr_b = np.inf
    best_g_b = gamma_hat
    min_n_boot = max(20, len(boot_df) * 0.03)
    for gamma in np.arange(gamma_lo, gamma_hi + 1, 1.0):
        res = threshold_panel(boot_df, gamma, controls=controls)
        if res['ssr'] < best_ssr_b and res['n_low'] >= min_n_boot and res['n_high'] >= min_n_boot:
            best_ssr_b = res['ssr']
            best_g_b = gamma

    # 精搜索 (0.2pp)
    for gamma in np.arange(max(gamma_lo, best_g_b - 3), min(gamma_hi, best_g_b + 3) + 0.2, 0.2):
        gamma = round(gamma, 1)
        res = threshold_panel(boot_df, gamma, controls=controls)
        if res['ssr'] < best_ssr_b and res['n_low'] >= min_n_boot and res['n_high'] >= min_n_boot:
            best_ssr_b = res['ssr']
            best_g_b = gamma

    gamma_boot.append(best_g_b)
    if (b + 1) % 100 == 0:
        print(f'  Bootstrap {b+1}/{n_boot}...')

gamma_boot = np.array(gamma_boot)
ci_low = np.percentile(gamma_boot, 2.5)
ci_high = np.percentile(gamma_boot, 97.5)
ci_width = ci_high - ci_low

log(f'\nBootstrap 结果:')
log(f'  gamma_hat = {gamma_hat:.1f}%')
log(f'  95% CI = [{ci_low:.1f}%, {ci_high:.1f}%]')
log(f'  CI 宽度 = {ci_width:.1f}pp')
log(f'  Bootstrap 均值 = {gamma_boot.mean():.1f}%')
log(f'  Bootstrap 中位数 = {np.median(gamma_boot):.1f}%')
log()

gamma_robust = np.median(gamma_boot)
if abs(gamma_robust - gamma_hat) > 2:
    log(f'注意: Bootstrap 中位数 ({gamma_robust:.1f}%) 与点估计 ({gamma_hat:.1f}%) 差异较大')
    log(f'采用 Bootstrap 中位数作为稳健估计')
    gamma_report = gamma_robust
else:
    gamma_report = gamma_hat
log()


# ============================================================
# STEP 6: 分收入组稳定性检验
# ============================================================
log('=' * 72)
log('STEP 6: 分收入组稳定性检验')
log('=' * 72)
log()

income_groups = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
income_results = {}

for ig in income_groups:
    sub = work_hansen[work_hansen['income_group'] == ig]
    if len(sub) < 50:
        log(f'{ig}: 样本量不足 ({len(sub)}), 跳过')
        income_results[ig] = {'gamma': np.nan, 'ci_low': np.nan, 'ci_high': np.nan, 'n': len(sub)}
        continue

    g_lo_ig = max(1, sub['construction_gdp'].quantile(0.15))
    g_hi_ig = min(30, sub['construction_gdp'].quantile(0.85))
    min_n_ig = max(10, len(sub) * 0.05)

    best_ssr_ig = np.inf
    best_g_ig = np.nan
    best_info_ig = {}
    for gamma in np.arange(g_lo_ig, g_hi_ig + 0.5, 0.5):
        res = threshold_panel(sub, gamma, controls=controls)
        if res['ssr'] < best_ssr_ig and res['n_low'] >= min_n_ig and res['n_high'] >= min_n_ig:
            best_ssr_ig = res['ssr']
            best_g_ig = gamma
            best_info_ig = res

    # Bootstrap (200x)
    boot_g_ig = []
    sub_countries = sub['country_code'].unique()
    np.random.seed(42)
    for b_idx in range(200):
        bc = np.random.choice(sub_countries, size=len(sub_countries), replace=True)
        bd = []
        for i, c in enumerate(bc):
            chunk = sub[sub['country_code'] == c].copy()
            chunk['country_code'] = f'{c}_{i}'
            bd.append(chunk)
        bdf = pd.concat(bd, ignore_index=True)

        bs = np.inf
        bg = best_g_ig if not np.isnan(best_g_ig) else (g_lo_ig + g_hi_ig) / 2
        for gamma in np.arange(g_lo_ig, g_hi_ig + 1, 1.0):
            res = threshold_panel(bdf, gamma, controls=controls)
            if res['ssr'] < bs and res['n_low'] >= 5 and res['n_high'] >= 5:
                bs = res['ssr']
                bg = gamma
        boot_g_ig.append(bg)

    boot_g_ig = np.array(boot_g_ig)
    income_results[ig] = {
        'gamma': best_g_ig,
        'ci_low': np.percentile(boot_g_ig, 2.5),
        'ci_high': np.percentile(boot_g_ig, 97.5),
        'n': len(sub),
        'beta_low': best_info_ig.get('betas', {}).get('x_low', np.nan),
        'beta_high': best_info_ig.get('betas', {}).get('x_high', np.nan),
    }

log(f'{"Income Group":<25s} {"N":>6s} {"gamma":>8s} {"95% CI":>18s} {"CI Width":>10s}')
log('-' * 72)
for ig in income_groups:
    r = income_results[ig]
    if np.isnan(r.get('gamma', np.nan)):
        log(f'{ig:<25s} {r["n"]:>6d} {"N/A":>8s} {"N/A":>18s} {"N/A":>10s}')
    else:
        ci_str = f'[{r["ci_low"]:.1f}, {r["ci_high"]:.1f}]'
        ci_w = f'{r["ci_high"] - r["ci_low"]:.1f}'
        log(f'{ig:<25s} {r["n"]:>6d} {r["gamma"]:>8.1f} {ci_str:>18s} {ci_w:>10s}')
log()


# ============================================================
# STEP 7: 与代理变量结果对比
# ============================================================
log('=' * 72)
log('STEP 7: 与代理变量结果对比')
log('=' * 72)
log()

log('代理变量结果 (来自 82_oecd_construction_threshold.py):')
log('  阈值变量: GFCF/GDP (总固定资本形成/GDP)')
log('  gamma_hat = 9.1%')
log('  95% CI = [8.1%, 17.6%]')
log('  CI 宽度 = 9.5pp')
log()
log('真实建设投资数据结果:')
log(f'  阈值变量: Construction/GDP (建设投资/GDP)')
log(f'  gamma_hat = {gamma_report:.1f}%')
log(f'  95% CI = [{ci_low:.1f}%, {ci_high:.1f}%]')
log(f'  CI 宽度 = {ci_width:.1f}pp')
log()

# 理论一致性检验
# 如果代理变量阈值 9.1% 对应约 50% 建设占比，则真实建设阈值应约 4.5%
log('理论一致性:')
median_share = valid_share.median() if len(valid_share) > 0 else 0.5
log(f'  建设占GFCF中位数比例: {median_share:.1%}')
log(f'  代理变量阈值(GFCF/GDP) x 建设占比 = {9.1 * median_share:.1f}%')
log(f'  真实建设投资阈值: {gamma_report:.1f}%')
log()


# ============================================================
# STEP 8: 可视化
# ============================================================
log('STEP 8: 生成图表')
log('-' * 72)

fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

# --- Panel (a): SSR Profile ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(ssr_df['gamma'], ssr_df['ssr'], 'b-', linewidth=1.5, alpha=0.8)
ax1.axvline(gamma_hat, color='red', linestyle='--', linewidth=1.5, label=f'$\\hat{{\\gamma}}$ = {gamma_hat:.1f}%')
ax1.axvspan(ci_low, ci_high, alpha=0.15, color='red', label=f'95% CI [{ci_low:.1f}, {ci_high:.1f}]')
ax1.set_xlabel('Construction/GDP (%)', fontsize=11)
ax1.set_ylabel('Sum of Squared Residuals', fontsize=11)
ax1.set_title('(a) SSR Profile: Threshold Search', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# --- Panel (b): LOESS + Scatter ---
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(work['construction_gdp'], work['dCPR'], alpha=0.15, s=8, c='gray', label='Observations')
ax2.plot(lowess_x, lowess_y, 'b-', linewidth=2.5, label='LOESS')
ax2.axhline(0, color='black', linewidth=0.5, linestyle='-')
ax2.axvline(gamma_hat, color='red', linestyle='--', linewidth=1.5, label=f'Threshold = {gamma_hat:.1f}%')
for zc in zero_crossings:
    ax2.axvline(zc, color='green', linestyle=':', linewidth=1, alpha=0.7)
ax2.set_xlabel('Construction/GDP (%)', fontsize=11)
ax2.set_ylabel('dCPR (Capital-Output Ratio Change)', fontsize=11)
ax2.set_title('(b) Nonparametric Relationship', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# --- Panel (c): 分体制回归线 ---
ax3 = fig.add_subplot(gs[1, 0])
low_mask = work_hansen['construction_gdp'] < gamma_hat
high_mask = work_hansen['construction_gdp'] >= gamma_hat

ax3.scatter(work_hansen.loc[low_mask, 'construction_gdp'],
            work_hansen.loc[low_mask, 'dCPR'],
            alpha=0.2, s=10, c='steelblue', label=f'Low regime (n={low_mask.sum()})')
ax3.scatter(work_hansen.loc[high_mask, 'construction_gdp'],
            work_hansen.loc[high_mask, 'dCPR'],
            alpha=0.2, s=10, c='coral', label=f'High regime (n={high_mask.sum()})')

# 线性拟合
for mask, color, label in [(low_mask, 'blue', 'Low fit'), (high_mask, 'red', 'High fit')]:
    sub = work_hansen[mask]
    if len(sub) > 10:
        slope, intercept, _, _, _ = stats.linregress(sub['construction_gdp'], sub['dCPR'])
        x_fit = np.linspace(sub['construction_gdp'].min(), sub['construction_gdp'].max(), 100)
        ax3.plot(x_fit, intercept + slope * x_fit, color=color, linewidth=2, label=f'{label}: slope={slope:.4f}')

ax3.axvline(gamma_hat, color='red', linestyle='--', linewidth=1.5)
ax3.axhline(0, color='black', linewidth=0.5)
ax3.set_xlabel('Construction/GDP (%)', fontsize=11)
ax3.set_ylabel('dCPR', fontsize=11)
ax3.set_title('(c) Two-Regime Regression', fontsize=12, fontweight='bold')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# --- Panel (d): Bootstrap Histogram ---
ax4 = fig.add_subplot(gs[1, 1])
ax4.hist(gamma_boot, bins=30, color='steelblue', alpha=0.7, edgecolor='white')
ax4.axvline(gamma_hat, color='red', linestyle='--', linewidth=2, label=f'Point est. = {gamma_hat:.1f}%')
ax4.axvline(ci_low, color='darkred', linestyle=':', linewidth=1.5)
ax4.axvline(ci_high, color='darkred', linestyle=':', linewidth=1.5, label=f'95% CI [{ci_low:.1f}, {ci_high:.1f}]')
ax4.set_xlabel('Threshold Estimate (%)', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.set_title('(d) Bootstrap Distribution (500 reps)', fontsize=12, fontweight='bold')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

fig.suptitle('Hansen Threshold Model: Construction Investment / GDP\n'
             'Dependent Variable: dCPR (Capital-Output Ratio Change)',
             fontsize=14, fontweight='bold', y=0.98)

plt.savefig(FIG_PATH, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
log(f'图表已保存: {FIG_PATH}')
log()


# ============================================================
# 保存报告
# ============================================================
log('=' * 72)
log('分析完成')
log('=' * 72)

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f'\n报告已保存: {REPORT_PATH}')
print(f'图表已保存: {FIG_PATH}')
print(f'原始数据: {RAW_PATH}')
print(f'处理后面板: {PROC_PATH}')
