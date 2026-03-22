"""
n22_oecd_wdi_update.py
======================
目的：
  任务 A: 利用 OECD SNA Table 5 的住宅专项 GFCF (Dwellings) 构建 dwelling-specific MUQ，
          回应审稿人"MUQ 分子是住房但分母是全口径 FAI"的批评。
  任务 B: 检查并扩展全球面板中 WDI 数据至 2023，重算 GDP-based MUQ，
          处理 COVID-2020 异常值，执行敏感性分析。

输入：
  - 02-data/raw/oecd_gfcf_by_asset_real.csv  (OECD GFCF by asset, current prices, nominal)
  - 02-data/raw/bis_property_prices.csv  (BIS 房价指数)
  - 02-data/processed/global_urban_q_panel.csv  (现有全球面板)
  - 02-data/raw/world_bank_all_countries.csv  (WB 原始数据，用于收入分类辅助)

输出：
  - 03-analysis/models/oecd_dwelling_muq_report.txt
  - 03-analysis/models/wdi_update_report.txt
  - 02-data/processed/global_urban_q_panel_v2.csv

依赖：pandas, numpy, scipy
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

# =============================================================================
# 路径设置
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
OECD_REAL_PATH = f'{BASE}/02-data/raw/oecd_gfcf_by_asset_real.csv'
BIS_PATH = f'{BASE}/02-data/raw/bis_property_prices.csv'
PANEL_PATH = f'{BASE}/02-data/processed/global_urban_q_panel.csv'
WB_RAW_PATH = f'{BASE}/02-data/raw/world_bank_all_countries.csv'

OECD_REPORT = f'{BASE}/03-analysis/models/oecd_dwelling_muq_report.txt'
WDI_REPORT = f'{BASE}/03-analysis/models/wdi_update_report.txt'
PANEL_V2_PATH = f'{BASE}/02-data/processed/global_urban_q_panel_v2.csv'

np.random.seed(42)

# 报告工具
oecd_lines = []
wdi_lines = []

def oprint(msg):
    print(msg)
    oecd_lines.append(str(msg))

def wprint(msg):
    print(msg)
    wdi_lines.append(str(msg))


# #############################################################################
# 任务 A: OECD Dwelling-Specific MUQ
# #############################################################################

oprint("=" * 70)
oprint("任务 A: OECD Dwelling-Specific MUQ")
oprint("=" * 70)

# ---- A1: 加载并清洗 OECD GFCF by Asset ----
oprint("\n[A1] 加载 OECD GFCF by Asset 数据")
oprint("-" * 40)

oecd_raw = pd.read_csv(OECD_REAL_PATH)
oprint(f"  原始行数: {len(oecd_raw)}")
oprint(f"  资产类型: {list(oecd_raw['asset_label'].unique())}")

# 排除聚合区域 (EA20, EU27_2020, DEU_F)
aggregate_codes = {'EA20', 'EU27_2020', 'DEU_F'}
oecd = oecd_raw[~oecd_raw['REF_AREA'].isin(aggregate_codes)].copy()

# 提取关键字段
oecd = oecd[['REF_AREA', 'Reference area', 'INSTR_ASSET', 'asset_label',
             'TIME_PERIOD', 'OBS_VALUE', 'UNIT_MULT', 'CURRENCY']].copy()
oecd.columns = ['country_code', 'country_name', 'asset_code', 'asset_label',
                'year', 'value', 'unit_mult', 'currency']
oecd['year'] = oecd['year'].astype(int)
oecd['value'] = pd.to_numeric(oecd['value'], errors='coerce')

# 注意: PRICE_BASE = 'V' 表示 Current prices (名义值)
# UNIT_MULT = 6 表示百万本币
oprint(f"  清洗后: {len(oecd)} 行, {oecd['country_code'].nunique()} 国 (排除聚合区域)")
oprint(f"  年份范围: {oecd['year'].min()}-{oecd['year'].max()}")

# ---- A2: 构建 Dwellings vs Total GFCF 面板 ----
oprint("\n[A2] 构建 Dwellings GFCF 面板")
oprint("-" * 40)

# Pivot: 每行 = country-year, 列 = asset_label
dwellings = oecd[oecd['asset_code'] == 'N111G'][['country_code', 'year', 'value']].copy()
dwellings.columns = ['country_code', 'year', 'gfcf_dwellings']

total_assets = oecd[oecd['asset_code'] == 'N11G'][['country_code', 'year', 'value']].copy()
total_assets.columns = ['country_code', 'year', 'gfcf_total']

other_bldg = oecd[oecd['asset_code'] == 'N112G'][['country_code', 'year', 'value']].copy()
other_bldg.columns = ['country_code', 'year', 'gfcf_other_buildings']

# 合并
oecd_panel = dwellings.merge(total_assets, on=['country_code', 'year'], how='outer')
oecd_panel = oecd_panel.merge(other_bldg, on=['country_code', 'year'], how='outer')

# 住宅占比
oecd_panel['dwelling_share'] = oecd_panel['gfcf_dwellings'] / oecd_panel['gfcf_total']

oprint(f"  OECD 面板: {len(oecd_panel)} 行, {oecd_panel['country_code'].nunique()} 国")
oprint(f"  有 Dwellings 数据的国家: {dwellings['country_code'].nunique()}")

# 描述性统计: 住宅占总 GFCF 比例
valid_share = oecd_panel.dropna(subset=['dwelling_share'])
oprint(f"\n  住宅 GFCF / 总 GFCF 占比统计 (N={len(valid_share)}):")
oprint(f"    均值:   {valid_share['dwelling_share'].mean():.3f}")
oprint(f"    中位数: {valid_share['dwelling_share'].median():.3f}")
oprint(f"    P25:    {valid_share['dwelling_share'].quantile(0.25):.3f}")
oprint(f"    P75:    {valid_share['dwelling_share'].quantile(0.75):.3f}")

# ---- A3: 加载 BIS 房价数据并与 OECD GFCF 合并 ----
oprint("\n[A3] 合并 BIS 房价数据")
oprint("-" * 40)

bis = pd.read_csv(BIS_PATH)
# 筛选 Real House Price Index (RHP)
bis_rhp = bis[bis['measure'] == 'RHP'].copy()
# 排除聚合
agg_codes = {'OECD', 'EA', 'EA17', 'EU', 'EU27'}
bis_rhp = bis_rhp[~bis_rhp['country_code'].isin(agg_codes)]

# 提取年份 (季度数据取年均)
bis_rhp['year'] = bis_rhp['period'].str[:4].astype(int)
bis_rhp['value'] = pd.to_numeric(bis_rhp['value'], errors='coerce')
bis_annual = (bis_rhp.groupby(['country_code', 'year'])['value']
              .mean().reset_index()
              .rename(columns={'value': 'rhp_index'}))

# 同时获取 Nominal (HPI) 房价指数
bis_hpi = bis[bis['measure'] == 'HPI'].copy()
bis_hpi = bis_hpi[~bis_hpi['country_code'].isin(agg_codes)]
bis_hpi['year'] = bis_hpi['period'].str[:4].astype(int)
bis_hpi['value'] = pd.to_numeric(bis_hpi['value'], errors='coerce')
bis_hpi_annual = (bis_hpi.groupby(['country_code', 'year'])['value']
                  .mean().reset_index()
                  .rename(columns={'value': 'hpi_index'}))

# 合并
oecd_panel = oecd_panel.merge(bis_annual, on=['country_code', 'year'], how='left')
oecd_panel = oecd_panel.merge(bis_hpi_annual, on=['country_code', 'year'], how='left')

overlap = oecd_panel.dropna(subset=['gfcf_dwellings', 'rhp_index'])
oprint(f"  同时有 Dwellings GFCF + BIS RHP 的国家: {overlap['country_code'].nunique()}")
oprint(f"  重叠观测数: {len(overlap)}")

# ---- A4: 构建 Dwelling-Specific MUQ ----
oprint("\n[A4] 构建 Dwelling-Specific MUQ")
oprint("-" * 40)

# 方法: MUQ_dwelling = Delta(RHP_index) / GFCF_dwellings_growth
# 更准确的方法: 构建住宅存量价值指数，然后取变化量 / 住宅投资流量
#
# 简化版: MUQ_dwell = Delta(V_dwelling) / GFCF_dwelling
# 其中 V_dwelling(t) = V_dwelling(t-1) * (RHP(t)/RHP(t-1)) + GFCF_dwelling(t)
# 或者: V_dwelling(t) 直接用 PIM + 房价调整
#
# 最干净的做法:
# 1) 用 GFCF_dwellings 通过 PIM 累积住宅资本存量 K_dwell(t)
# 2) 用 RHP 指数对 K_dwell 进行市值重估: V_dwell(t) = K_dwell(2010) * RHP(t)/100
# 3) MUQ_dwell = Delta(V_dwell) / GFCF_dwellings

oecd_panel = oecd_panel.sort_values(['country_code', 'year'])

def compute_dwelling_muq(group):
    """对单个国家计算 dwelling-specific MUQ"""
    df = group.copy()

    # PIM 累积住宅资本存量
    inv = df['gfcf_dwellings'].values
    years = df['year'].values

    valid_mask = ~np.isnan(inv)
    if valid_mask.sum() < 5:
        df['K_dwell'] = np.nan
        df['V_dwell'] = np.nan
        df['muq_dwell'] = np.nan
        return df

    # 折旧率: 住宅通常使用 2-3% (低于整体资本 5%)
    delta_dwell = 0.025

    first_valid = np.argmax(valid_mask)

    # 估计初始增长率
    start_idx = first_valid
    end_idx = min(first_valid + 5, len(inv))
    inv_window = inv[start_idx:end_idx]
    inv_window = inv_window[~np.isnan(inv_window)]

    if len(inv_window) >= 2 and inv_window[0] > 0:
        growth_rates = []
        for i in range(1, len(inv_window)):
            if inv_window[i-1] > 0:
                growth_rates.append(inv_window[i] / inv_window[i-1] - 1)
        g = np.mean(growth_rates) if growth_rates else 0.03
        g = max(g, 0.01)
    else:
        g = 0.03

    # PIM 递推
    K = np.full(len(inv), np.nan)
    I0 = inv[first_valid]
    if not np.isnan(I0) and I0 > 0:
        K[first_valid] = I0 / (g + delta_dwell)
    else:
        df['K_dwell'] = np.nan
        df['V_dwell'] = np.nan
        df['muq_dwell'] = np.nan
        return df

    for t in range(first_valid + 1, len(inv)):
        if np.isnan(inv[t]):
            if not np.isnan(K[t-1]):
                K[t] = (1 - delta_dwell) * K[t-1]
        else:
            if not np.isnan(K[t-1]):
                K[t] = (1 - delta_dwell) * K[t-1] + inv[t]
            else:
                K[t] = inv[t] / (g + delta_dwell)

    df['K_dwell'] = K

    # 市值重估: 使用 RHP 指数 (2010=100)
    # V_dwell(t) = K_dwell(2010) * RHP(t) / 100
    rhp = df['rhp_index'].values
    k_2010_mask = df['year'] == 2010
    k_2010_vals = df.loc[k_2010_mask, 'K_dwell'].values

    if len(k_2010_vals) > 0 and not np.isnan(k_2010_vals[0]) and (~np.isnan(rhp)).any():
        k_base = k_2010_vals[0]
        V_dwell = k_base * (rhp / 100.0)
        df['V_dwell'] = V_dwell
    else:
        # 退回使用 K_dwell 本身 (不做房价调整)
        df['V_dwell'] = K

    # MUQ_dwell = Delta(V_dwell) / GFCF_dwellings
    V = df['V_dwell'].values
    delta_V = np.full(len(V), np.nan)
    for t in range(1, len(V)):
        if not np.isnan(V[t]) and not np.isnan(V[t-1]):
            delta_V[t] = V[t] - V[t-1]

    muq = np.full(len(inv), np.nan)
    for t in range(len(inv)):
        if not np.isnan(delta_V[t]) and not np.isnan(inv[t]) and inv[t] > 0:
            muq[t] = delta_V[t] / inv[t]

    df['muq_dwell'] = muq

    return df

oprint("  正在计算 dwelling-specific MUQ...")
oecd_panel = oecd_panel.groupby('country_code', group_keys=False).apply(compute_dwelling_muq)
oecd_panel = oecd_panel.reset_index(drop=True)

# 极端值处理
oecd_panel['muq_dwell'] = oecd_panel['muq_dwell'].replace([np.inf, -np.inf], np.nan)
q01 = oecd_panel['muq_dwell'].quantile(0.01)
q99 = oecd_panel['muq_dwell'].quantile(0.99)
oecd_panel['muq_dwell'] = oecd_panel['muq_dwell'].clip(q01, q99)

valid_muq_dwell = oecd_panel['muq_dwell'].notna().sum()
n_countries_dwell = oecd_panel.loc[oecd_panel['muq_dwell'].notna(), 'country_code'].nunique()
oprint(f"  MUQ_dwell 有效观测: {valid_muq_dwell}, {n_countries_dwell} 国")
oprint(f"  MUQ_dwell 中位数: {oecd_panel['muq_dwell'].median():.4f}")
oprint(f"  MUQ_dwell 均值:   {oecd_panel['muq_dwell'].mean():.4f}")

# ---- A5: 收入组分类 + Simpson's Paradox 检验 ----
oprint("\n[A5] 收入组分类与 Simpson's Paradox 检验")
oprint("-" * 40)

# 加载全球面板以获取城镇化率和收入组代理
panel = pd.read_csv(PANEL_PATH)

# 通过人均 GDP 对 OECD 国家分组
# 首先从 panel 获取各国 GDP per capita
panel_gdppc = panel.dropna(subset=['gdp_constant_2015', 'total_pop']).copy()
panel_gdppc['gdp_pc'] = panel_gdppc['gdp_constant_2015'] / panel_gdppc['total_pop']
latest = panel_gdppc.groupby('country_code').apply(
    lambda x: x.loc[x['year'].idxmax()]
)[['country_code', 'gdp_pc']].reset_index(drop=True)

def assign_income_group(gdp_pc):
    if pd.isna(gdp_pc):
        return np.nan
    elif gdp_pc < 1500:
        return 'Low income'
    elif gdp_pc < 5000:
        return 'Lower middle income'
    elif gdp_pc < 15000:
        return 'Upper middle income'
    else:
        return 'High income'

latest['income_group'] = latest['gdp_pc'].apply(assign_income_group)

# 获取城镇化率
urban = panel[['country_code', 'year', 'urban_pct']].dropna()

# 合并到 OECD 面板
oecd_panel = oecd_panel.merge(latest[['country_code', 'income_group']], on='country_code', how='left')
oecd_panel = oecd_panel.merge(urban, on=['country_code', 'year'], how='left')

# Simpson's Paradox 检验: MUQ_dwell vs urban_pct
oprint("\n  --- Simpson's Paradox: Dwelling-Specific MUQ ---")

valid_sp = oecd_panel.dropna(subset=['muq_dwell', 'urban_pct', 'income_group']).copy()
oprint(f"  有效观测: {len(valid_sp)}, {valid_sp['country_code'].nunique()} 国")

# 全样本
rho_all, p_all = stats.spearmanr(valid_sp['urban_pct'], valid_sp['muq_dwell'])
oprint(f"\n  全样本 (pooled): rho = {rho_all:+.4f}, p = {p_all:.6f}, N = {len(valid_sp)}")

income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
oprint(f"\n  {'收入组':<25} {'N':>6} {'国家':>5} {'rho':>8} {'p-value':>12} {'方向':>6}")
oprint("  " + "-" * 65)

sp_results_dwell = {}
for ig in income_order:
    sub = valid_sp[valid_sp['income_group'] == ig]
    if len(sub) < 10:
        oprint(f"  {ig:<25} {len(sub):>6} {'--':>5} {'--':>8} {'--':>12} {'--':>6}")
        continue
    rho, p = stats.spearmanr(sub['urban_pct'], sub['muq_dwell'])
    n_c = sub['country_code'].nunique()
    direction = "DOWN" if rho < 0 else "UP"
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    sp_results_dwell[ig] = {'rho': rho, 'p': p, 'n': len(sub), 'n_countries': n_c}
    oprint(f"  {ig:<25} {len(sub):>6} {n_c:>5} {rho:>+8.4f} {p:>12.6f}{sig} {direction:>6}")

# 方向一致性检验
if sp_results_dwell:
    within_directions = [r['rho'] < 0 for r in sp_results_dwell.values()]
    pooled_direction = rho_all < 0

    all_within_negative = all(within_directions)
    pooled_positive = not pooled_direction

    # Simpson's Paradox = pooled direction differs from within-group direction
    is_simpson = (pooled_positive and all_within_negative) or (not pooled_positive and not any(within_directions))

    oprint(f"\n  Pooled 方向: {'DOWN' if pooled_direction else 'UP'}")
    oprint(f"  Within-group 全部 DOWN: {all_within_negative}")
    oprint(f"  Simpson's Paradox 成立: {is_simpson}")

# ---- A6: 与全口径 MUQ 和 GDP-based MUQ 对比 ----
oprint("\n[A6] 对比: Dwelling MUQ vs 全口径 MUQ vs GDP-based MUQ")
oprint("-" * 40)

# 构建 GDP-based MUQ 用于对比 (OECD 国家子集)
# 合并 panel 中的 GDP 数据
panel_gdp = panel[['country_code', 'year', 'gdp_constant_2015', 'gfcf_pct_gdp',
                    'gdp_current_usd', 'gfcf_current_usd']].copy()
oecd_panel = oecd_panel.merge(panel_gdp, on=['country_code', 'year'], how='left')

# GDP-based MUQ
oecd_panel['gfcf_constant'] = oecd_panel['gdp_constant_2015'] * oecd_panel['gfcf_pct_gdp'] / 100
oecd_panel['delta_gdp'] = oecd_panel.groupby('country_code')['gdp_constant_2015'].diff()
oecd_panel['muq_gdp'] = oecd_panel['delta_gdp'] / oecd_panel['gfcf_constant']
oecd_panel['muq_gdp'] = oecd_panel['muq_gdp'].replace([np.inf, -np.inf], np.nan)
q01g = oecd_panel['muq_gdp'].quantile(0.01)
q99g = oecd_panel['muq_gdp'].quantile(0.99)
oecd_panel['muq_gdp'] = oecd_panel['muq_gdp'].clip(q01g, q99g)

# 全口径 MUQ (从 panel 的 muq 列, 基于 V2/GFCF 变化)
panel_muq = panel[['country_code', 'year', 'muq']].rename(columns={'muq': 'muq_full'})
oecd_panel = oecd_panel.merge(panel_muq, on=['country_code', 'year'], how='left')

# 三种 MUQ 的相关性
for pair_name, (col_a, col_b) in [
    ('Dwelling vs Full', ('muq_dwell', 'muq_full')),
    ('Dwelling vs GDP', ('muq_dwell', 'muq_gdp')),
    ('Full vs GDP', ('muq_full', 'muq_gdp')),
]:
    valid_pair = oecd_panel.dropna(subset=[col_a, col_b])
    if len(valid_pair) > 10:
        rho, p = stats.spearmanr(valid_pair[col_a], valid_pair[col_b])
        oprint(f"  {pair_name}: rho = {rho:+.4f}, p = {p:.6f}, N = {len(valid_pair)}")
    else:
        oprint(f"  {pair_name}: 数据不足 (N={len(valid_pair)})")

# 各指标描述性统计对比 (2000-2019 窗口)
oprint(f"\n  描述性统计 (2000-2019, OECD 国家子集):")
mask_window = oecd_panel['year'].between(2000, 2019)
for col, label in [('muq_dwell', 'MUQ_dwell'), ('muq_full', 'MUQ_full'), ('muq_gdp', 'MUQ_GDP')]:
    sub = oecd_panel.loc[mask_window, col].dropna()
    if len(sub) > 0:
        oprint(f"    {label:12s}: N={len(sub):>5}, median={sub.median():>8.4f}, "
               f"mean={sub.mean():>8.4f}, sd={sub.std():>8.4f}")

# ---- A7: 按收入组 Simpson's Paradox (所有三种 MUQ 对比) ----
oprint("\n[A7] 三种 MUQ 的 Simpson's Paradox 对比")
oprint("-" * 40)

for muq_label, muq_col in [('MUQ_dwell', 'muq_dwell'), ('MUQ_full', 'muq_full'), ('MUQ_GDP', 'muq_gdp')]:
    vv = oecd_panel.dropna(subset=[muq_col, 'urban_pct', 'income_group'])
    if len(vv) < 20:
        oprint(f"\n  {muq_label}: 数据不足，跳过")
        continue
    rho_pool, p_pool = stats.spearmanr(vv['urban_pct'], vv[muq_col])
    oprint(f"\n  {muq_label} pooled: rho={rho_pool:+.4f}, p={p_pool:.6f}, N={len(vv)}")

    within_rhos = []
    within_ns = []
    for ig in income_order:
        ss = vv[vv['income_group'] == ig]
        if len(ss) < 10:
            continue
        rho_ig, p_ig = stats.spearmanr(ss['urban_pct'], ss[muq_col])
        within_rhos.append(rho_ig)
        within_ns.append(len(ss))
        direction = "DOWN" if rho_ig < 0 else "UP"
        oprint(f"    {ig:<25} rho={rho_ig:+.4f}, p={p_ig:.6f}, N={len(ss)} -> {direction}")

    if within_rhos:
        # 加权 within
        total_n = sum(within_ns)
        weighted_within = sum(r * n / total_n for r, n in zip(within_rhos, within_ns))
        between = rho_pool - weighted_within
        oprint(f"    Weighted within: {weighted_within:+.4f}")
        oprint(f"    Between-group:   {between:+.4f}")

# 保存 OECD 报告
with open(OECD_REPORT, 'w') as f:
    f.write('\n'.join(oecd_lines))
oprint(f"\n报告已保存: {OECD_REPORT}")


# #############################################################################
# 任务 B: WDI 全球面板更新至 2023 + GDP-based MUQ 扩展
# #############################################################################

wprint("\n" + "=" * 70)
wprint("任务 B: WDI 全球面板更新至 2023")
wprint("=" * 70)

# ---- B1: 检查现有面板覆盖 ----
wprint("\n[B1] 检查现有面板覆盖")
wprint("-" * 40)

panel = pd.read_csv(PANEL_PATH)
wprint(f"  面板尺寸: {panel.shape}")
wprint(f"  国家数: {panel['country_code'].nunique()}")
wprint(f"  年份范围: {panel['year'].min()}-{panel['year'].max()}")

# WDI 部分覆盖检查
wdi_vars = ['gdp_current_usd', 'gdp_constant_2015', 'gfcf_pct_gdp', 'gfcf_current_usd',
            'services_pct_gdp', 'industry_pct_gdp', 'urban_pct']
wprint(f"\n  WDI 变量覆盖 (2020-2023):")
for v in wdi_vars:
    sub_2020 = panel[panel['year'] >= 2020]
    valid_count = sub_2020[v].notna().sum()
    n_countries = sub_2020.loc[sub_2020[v].notna(), 'country_code'].nunique() if valid_count > 0 else 0
    wprint(f"    {v}: {valid_count} 观测, {n_countries} 国")

# PWT 部分覆盖检查
pwt_vars = ['hc', 'rnna', 'rgdpna', 'ctfp', 'delta']
wprint(f"\n  PWT 变量覆盖:")
for v in pwt_vars:
    valid = panel[v].notna()
    max_year = panel.loc[valid, 'year'].max() if valid.any() else 'N/A'
    n_obs = valid.sum()
    wprint(f"    {v}: 截止 {max_year}, {n_obs} 观测")

# MUQ 覆盖
muq_valid = panel['muq'].notna()
wprint(f"\n  原始 MUQ: {muq_valid.sum()} 观测, 截止 {panel.loc[muq_valid, 'year'].max()}")
wprint(f"  原因: MUQ 基于 V2 (需要 PWT rnna)，PWT 截止 2019")

# ---- B2: 检查 2020-2023 WDI 数据是否已存在 ----
wprint("\n[B2] 2020-2023 数据状态")
wprint("-" * 40)

gdp_2020_23 = panel[(panel['year'] >= 2020) & panel['gdp_constant_2015'].notna()]
wprint(f"  GDP constant 2015 (2020-2023): {len(gdp_2020_23)} 观测, "
       f"{gdp_2020_23['country_code'].nunique()} 国")
for yr in [2020, 2021, 2022, 2023]:
    n = panel[(panel['year'] == yr) & panel['gdp_constant_2015'].notna()].shape[0]
    wprint(f"    {yr}: {n} 国有 GDP 数据")

wdi_already_2023 = len(panel[(panel['year'] == 2023) & panel['gdp_constant_2015'].notna()]) > 0
wprint(f"\n  WDI 数据已覆盖至 2023: {wdi_already_2023}")
wprint(f"  结论: WDI 数据已在面板中, 但 MUQ 未计算 (因 PWT 限制)")

# ---- B3: 扩展 GDP-based MUQ 至 2023 ----
wprint("\n[B3] 计算 GDP-based MUQ (2020-2023 扩展)")
wprint("-" * 40)

panel = panel.sort_values(['country_code', 'year'])

# GDP-based MUQ: Delta(GDP_constant_2015) / GFCF_constant_2015
panel['gfcf_constant_2015'] = panel['gdp_constant_2015'] * panel['gfcf_pct_gdp'] / 100
panel['delta_gdp_constant'] = panel.groupby('country_code')['gdp_constant_2015'].diff()
panel['muq_gdp'] = panel['delta_gdp_constant'] / panel['gfcf_constant_2015']

# 清洗极端值
panel['muq_gdp'] = panel['muq_gdp'].replace([np.inf, -np.inf], np.nan)
q01 = panel['muq_gdp'].quantile(0.01)
q99 = panel['muq_gdp'].quantile(0.99)
panel['muq_gdp'] = panel['muq_gdp'].clip(q01, q99)

muq_gdp_total = panel['muq_gdp'].notna().sum()
muq_gdp_2020_23 = panel[(panel['year'] >= 2020) & panel['muq_gdp'].notna()].shape[0]
wprint(f"  MUQ_GDP 总有效观测: {muq_gdp_total}")
wprint(f"  MUQ_GDP 2020-2023 新增: {muq_gdp_2020_23}")

for yr in [2019, 2020, 2021, 2022, 2023]:
    n = panel[(panel['year'] == yr) & panel['muq_gdp'].notna()].shape[0]
    med = panel.loc[(panel['year'] == yr) & panel['muq_gdp'].notna(), 'muq_gdp'].median()
    med_str = f"{med:.4f}" if not np.isnan(med) else "N/A"
    wprint(f"    {yr}: {n} 国, 中位数 = {med_str}")

# ---- B4: COVID-2020 冲击标记 ----
wprint("\n[B4] COVID-2020 冲击检测与标记")
wprint("-" * 40)

# 2020 年 GDP 暴跌会导致 MUQ_GDP 异常 (delta_GDP 大幅为负)
panel['is_covid_year'] = (panel['year'] == 2020).astype(int)

# 检测 2020 异常: delta_GDP / GDP < -3%
panel['gdp_growth'] = panel['delta_gdp_constant'] / panel.groupby('country_code')['gdp_constant_2015'].shift(1)

covid_data = panel[panel['year'] == 2020].dropna(subset=['gdp_growth'])
n_negative = (covid_data['gdp_growth'] < -0.03).sum()
n_total_covid = len(covid_data)
wprint(f"  2020 年有 GDP 增长率数据的国家: {n_total_covid}")
wprint(f"  其中 GDP 下降 >3%: {n_negative} ({n_negative/n_total_covid*100:.1f}%)")
wprint(f"  2020 GDP 增长率中位数: {covid_data['gdp_growth'].median():.4f}")
wprint(f"  2020 GDP 增长率 P25: {covid_data['gdp_growth'].quantile(0.25):.4f}")
wprint(f"  2020 MUQ_GDP 中位数: {covid_data['muq_gdp'].median():.4f}")

# 也标记 2021 反弹年
panel['is_covid_rebound'] = (panel['year'] == 2021).astype(int)

# ---- B5: 收入组分类 ----
wprint("\n[B5] 收入组分类")
wprint("-" * 40)

panel_pc = panel.dropna(subset=['gdp_constant_2015', 'total_pop']).copy()
panel_pc['gdp_pc'] = panel_pc['gdp_constant_2015'] / panel_pc['total_pop']
latest_pc = panel_pc.groupby('country_code').apply(
    lambda x: x.loc[x['year'].idxmax()]
)[['country_code', 'gdp_pc']].reset_index(drop=True)
latest_pc['income_group'] = latest_pc['gdp_pc'].apply(assign_income_group)

panel = panel.merge(latest_pc[['country_code', 'income_group']], on='country_code', how='left')

ig_dist = panel.dropna(subset=['income_group']).groupby('income_group')['country_code'].nunique()
wprint(f"  收入组国家分布:")
for ig in income_order:
    n = ig_dist.get(ig, 0)
    wprint(f"    {ig}: {n} 国")

# ---- B6: Simpson's Paradox 检验 (GDP-based MUQ, 含/排除 2020) ----
wprint("\n[B6] Simpson's Paradox 检验 (GDP-based MUQ)")
wprint("-" * 40)

for scenario_name, exclude_years in [
    ("全样本 (含 COVID 2020)", set()),
    ("排除 2020", {2020}),
    ("排除 2020-2021", {2020, 2021}),
    ("仅 2000-2019 (稳态期)", None),  # 特殊处理
]:
    wprint(f"\n  === 情景: {scenario_name} ===")

    if exclude_years is None:
        valid = panel[(panel['year'].between(2000, 2019))].dropna(
            subset=['muq_gdp', 'urban_pct', 'income_group']).copy()
    else:
        valid = panel[~panel['year'].isin(exclude_years)].dropna(
            subset=['muq_gdp', 'urban_pct', 'income_group']).copy()

    if len(valid) < 50:
        wprint(f"  数据不足 (N={len(valid)})，跳过")
        continue

    rho_pool, p_pool = stats.spearmanr(valid['urban_pct'], valid['muq_gdp'])
    wprint(f"  Pooled: rho = {rho_pool:+.4f}, p = {p_pool:.6f}, N = {len(valid)}, "
           f"{valid['country_code'].nunique()} 国")

    wprint(f"  {'收入组':<25} {'N':>6} {'国家':>5} {'rho':>8} {'p-value':>12} {'方向':>6}")
    wprint("  " + "-" * 65)

    within_rhos = []
    within_ns = []
    for ig in income_order:
        sub = valid[valid['income_group'] == ig]
        if len(sub) < 10:
            wprint(f"  {ig:<25} {len(sub):>6} {'--':>5} {'--':>8} {'--':>12} {'--':>6}")
            continue
        rho, p = stats.spearmanr(sub['urban_pct'], sub['muq_gdp'])
        n_c = sub['country_code'].nunique()
        direction = "DOWN" if rho < 0 else "UP"
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        within_rhos.append(rho)
        within_ns.append(len(sub))
        wprint(f"  {ig:<25} {len(sub):>6} {n_c:>5} {rho:>+8.4f} {p:>12.6f}{sig} {direction:>6}")

    if within_rhos:
        total_n = sum(within_ns)
        weighted_within = sum(r * n / total_n for r, n in zip(within_rhos, within_ns))
        between = rho_pool - weighted_within
        wprint(f"  Weighted within: {weighted_within:+.4f}")
        wprint(f"  Between-group:   {between:+.4f}")

# ---- B7: 敏感性分析 — 不同 MUQ 口径在 2020 冲击下的表现 ----
wprint("\n[B7] 敏感性分析: COVID 冲击对不同 MUQ 口径的影响")
wprint("-" * 40)

# 对比 2019 vs 2020 各口径的中位数变化
for yr in [2018, 2019, 2020, 2021, 2022, 2023]:
    sub = panel[panel['year'] == yr]
    muq_gdp_med = sub['muq_gdp'].median()
    muq_orig_med = sub['muq'].median()
    n_gdp = sub['muq_gdp'].notna().sum()
    n_orig = sub['muq'].notna().sum()

    muq_gdp_str = f"{muq_gdp_med:>8.4f}" if not pd.isna(muq_gdp_med) else "     N/A"
    muq_orig_str = f"{muq_orig_med:>8.4f}" if not pd.isna(muq_orig_med) else "     N/A"

    wprint(f"  {yr}: MUQ_GDP={muq_gdp_str} (N={n_gdp:>3}), "
           f"MUQ_orig={muq_orig_str} (N={n_orig:>3})")

# ---- B8: 将 OECD dwelling MUQ 合并到全球面板 ----
wprint("\n[B8] 合并 OECD dwelling MUQ 到全球面板")
wprint("-" * 40)

# 仅保留关键列
oecd_merge = oecd_panel[['country_code', 'year', 'gfcf_dwellings', 'gfcf_total',
                          'dwelling_share', 'muq_dwell', 'K_dwell', 'V_dwell']].copy()

# 左连接到主面板
panel = panel.merge(oecd_merge, on=['country_code', 'year'], how='left')

n_dwell_in_panel = panel['muq_dwell'].notna().sum()
n_countries_dwell_panel = panel.loc[panel['muq_dwell'].notna(), 'country_code'].nunique()
wprint(f"  面板中新增 dwelling MUQ: {n_dwell_in_panel} 观测, {n_countries_dwell_panel} 国")

# ---- B9: 保存更新后的面板 ----
wprint("\n[B9] 保存更新面板")
wprint("-" * 40)

# 选择保存的列
save_cols = [
    # 基础标识
    'country_code', 'country_name', 'region', 'year',
    # WDI
    'gdp_current_usd', 'gdp_constant_2015', 'gfcf_pct_gdp', 'gfcf_current_usd',
    'services_pct_gdp', 'industry_pct_gdp', 'agriculture_pct_gdp',
    'urban_pct', 'urban_pop', 'total_pop', 'pop_15_64_pct', 'pop_65plus_pct',
    # PWT
    'hc', 'rnna', 'rgdpna', 'ctfp', 'delta',
    # BIS 房价
    'real_property_price_index',
    # 资本存量
    'K_pim', 'K_best',
    # 价值评估 (V)
    'V1', 'V2', 'V3',
    # Urban Q (原始)
    'urban_q', 'urban_q_v1', 'urban_q_v2', 'urban_q_v3',
    # 投资比率
    'ci_gdp_ratio',
    # MUQ 原始 (V2-based, 截止 2019)
    'muq', 'delta_V_ratio',
    # 新增: GDP-based MUQ (延伸至 2023)
    'muq_gdp',
    # 新增: GDP 增长率
    'gdp_growth',
    # 新增: COVID 标记
    'is_covid_year', 'is_covid_rebound',
    # 新增: 收入组
    'income_group',
    # 新增: OECD dwelling-specific
    'gfcf_dwellings', 'gfcf_total', 'dwelling_share',
    'K_dwell', 'V_dwell', 'muq_dwell',
]

# 仅保留存在的列
save_cols = [c for c in save_cols if c in panel.columns]
panel_save = panel[save_cols].copy()

panel_save.to_csv(PANEL_V2_PATH, index=False)
wprint(f"  保存面板: {PANEL_V2_PATH}")
wprint(f"  尺寸: {panel_save.shape}")
wprint(f"  国家: {panel_save['country_code'].nunique()}")
wprint(f"  年份: {panel_save['year'].min()}-{panel_save['year'].max()}")

# 新增变量覆盖统计
wprint(f"\n  新增变量覆盖:")
new_vars = ['muq_gdp', 'income_group', 'muq_dwell', 'dwelling_share',
            'is_covid_year', 'gdp_growth']
for v in new_vars:
    if v in panel_save.columns:
        nn = panel_save[v].notna().sum()
        wprint(f"    {v}: {nn} 有效观测")

# 保存 WDI 报告
with open(WDI_REPORT, 'w') as f:
    f.write('\n'.join(wdi_lines))
wprint(f"\n报告已保存: {WDI_REPORT}")

print("\n" + "=" * 70)
print("所有任务完成")
print("=" * 70)
print(f"  OECD 报告: {OECD_REPORT}")
print(f"  WDI 报告:  {WDI_REPORT}")
print(f"  更新面板:  {PANEL_V2_PATH}")
