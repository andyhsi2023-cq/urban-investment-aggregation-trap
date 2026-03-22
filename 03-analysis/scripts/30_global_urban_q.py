"""
30_global_urban_q.py
====================
目的：构建全球 158 国 Urban Q 面板数据集
输入：
  - 02-data/processed/world_bank_usable_panel.csv (158 国 World Bank 面板)
  - 02-data/raw/penn_world_table.csv (183 国 PWT 数据)
  - 02-data/raw/bis_property_prices.csv (OECD 房价数据)
输出：
  - 02-data/processed/global_urban_q_panel.csv (全球面板)
  - 02-data/processed/global_urban_q_summary.csv (国家摘要)
  - 03-analysis/models/global_urban_q_report.txt (分析报告)
  - 04-figures/drafts/fig10_global_urban_q.png (三张关键图)
依赖：pandas, numpy, matplotlib, scipy
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 路径设置
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
WB_PATH = f'{BASE}/02-data/processed/world_bank_usable_panel.csv'
PWT_PATH = f'{BASE}/02-data/raw/penn_world_table.csv'
BIS_PATH = f'{BASE}/02-data/raw/bis_property_prices.csv'
OUT_PANEL = f'{BASE}/02-data/processed/global_urban_q_panel.csv'
OUT_SUMMARY = f'{BASE}/02-data/processed/global_urban_q_summary.csv'
OUT_REPORT = f'{BASE}/03-analysis/models/global_urban_q_report.txt'
OUT_FIG = f'{BASE}/04-figures/drafts/fig10_global_urban_q.png'

report_lines = []
def rprint(msg):
    """同时打印到控制台和报告"""
    print(msg)
    report_lines.append(str(msg))

rprint("=" * 70)
rprint("全球 Urban Q 面板构建")
rprint("=" * 70)

# =============================================================================
# 步骤 1：读取与合并三个数据源
# =============================================================================
rprint("\n[步骤 1] 读取与合并数据源")
rprint("-" * 40)

# --- 1a. World Bank 数据 ---
wb = pd.read_csv(WB_PATH)
# 重命名列为可读名称
wb_rename = {
    'country_iso3': 'country_code',
    'country_name': 'country_name',
    'region': 'region',
    'year': 'year',
    'NY.GDP.MKTP.CD': 'gdp_current_usd',
    'NY.GDP.MKTP.KD': 'gdp_constant_2015',
    'NE.GDI.FTOT.ZS': 'gfcf_pct_gdp',
    'NE.GDI.FTOT.CD': 'gfcf_current_usd',
    'NE.CON.GOVT.ZS': 'gov_consumption_pct_gdp',
    'NV.SRV.TOTL.ZS': 'services_pct_gdp',
    'NV.IND.TOTL.ZS': 'industry_pct_gdp',
    'NV.AGR.TOTL.ZS': 'agriculture_pct_gdp',
    'SP.URB.TOTL.IN.ZS': 'urban_pct',
    'SP.URB.TOTL': 'urban_pop',
    'SP.POP.TOTL': 'total_pop',
    'SP.POP.1564.TO.ZS': 'pop_15_64_pct',
    'SP.POP.65UP.TO.ZS': 'pop_65plus_pct',
}
wb = wb.rename(columns=wb_rename)
# 清理 region 中的空格
wb['region'] = wb['region'].str.strip()
rprint(f"  World Bank: {wb['country_code'].nunique()} 国, {wb['year'].min()}-{wb['year'].max()}")

# --- 1b. PWT 数据 ---
pwt = pd.read_csv(PWT_PATH)
pwt_cols = {
    'countrycode': 'country_code',
    'year': 'year',
    'hc': 'hc',
    'rnna': 'rnna',          # 实际资本存量 (million 2017 US$)
    'rgdpna': 'rgdpna',      # 实际 GDP
    'ctfp': 'ctfp',          # TFP
    'delta': 'delta',        # 折旧率
}
pwt_sub = pwt[list(pwt_cols.keys())].rename(columns=pwt_cols)
rprint(f"  PWT: {pwt_sub['country_code'].nunique()} 国, {pwt_sub['year'].min()}-{pwt_sub['year'].max()}")

# --- 1c. BIS 房价数据（仅保留 RHP = Real House Prices）---
bis = pd.read_csv(BIS_PATH)
# 筛选真实房价指数（RHP: Real House Prices, 2010=100）
bis_rhp = bis[bis['measure'] == 'RHP'].copy()
# 排除聚合区域
aggregate_codes = {'OECD', 'EA', 'EA17', 'EU', 'EU27'}
bis_rhp = bis_rhp[~bis_rhp['country_code'].isin(aggregate_codes)]

# 解析季度，提取年份
bis_rhp['year'] = bis_rhp['period'].str[:4].astype(int)
bis_rhp['value'] = pd.to_numeric(bis_rhp['value'], errors='coerce')

# 按国家-年份取年度均值
bis_annual = (bis_rhp.groupby(['country_code', 'year'])['value']
              .mean().reset_index()
              .rename(columns={'value': 'real_property_price_index'}))
rprint(f"  BIS RHP: {bis_annual['country_code'].nunique()} 国 (排除聚合区域后), "
       f"{bis_annual['year'].min()}-{bis_annual['year'].max()}")

# --- 合并 ---
# 以 WB 为基础，左连接 PWT 和 BIS
panel = wb.merge(pwt_sub, on=['country_code', 'year'], how='left')
panel = panel.merge(bis_annual, on=['country_code', 'year'], how='left')

rprint(f"\n  合并后面板: {len(panel)} 行, {panel['country_code'].nunique()} 国")
rprint(f"  有 PWT 数据的国家: {panel.loc[panel['rnna'].notna(), 'country_code'].nunique()}")
rprint(f"  有 BIS 房价数据的国家: {panel.loc[panel['real_property_price_index'].notna(), 'country_code'].nunique()}")

# 关键变量缺失率
rprint("\n  关键变量缺失率:")
key_vars = ['gdp_current_usd', 'gfcf_current_usd', 'rnna', 'hc', 'delta',
            'real_property_price_index', 'urban_pct']
for v in key_vars:
    miss = panel[v].isna().mean() * 100
    rprint(f"    {v}: {miss:.1f}%")

# =============================================================================
# 步骤 2：用 PIM 方法构建各国 K(t) — 建设资本存量
# =============================================================================
rprint("\n[步骤 2] 构建建设资本存量 K(t)")
rprint("-" * 40)

def compute_pim_capital(group):
    """
    对单个国家使用 PIM 计算资本存量序列。
    K(t) = (1 - delta) * K(t-1) + I(t)
    K(0) = I(0) / (g + delta)，g 为前 5 年投资增长率均值
    """
    df = group.sort_values('year').copy()

    # 获取折旧率：优先用 PWT 国家级 delta，否则默认 5%
    delta_vals = df['delta'].dropna()
    if len(delta_vals) > 0:
        delta = delta_vals.median()  # 取中位数作为该国折旧率
    else:
        delta = 0.05

    df['delta_used'] = delta

    # 投资序列
    inv = df['gfcf_current_usd'].values
    years = df['year'].values

    # 找到第一个有投资数据的位置
    valid_mask = ~np.isnan(inv)
    if valid_mask.sum() < 3:
        df['K_pim'] = np.nan
        return df

    first_valid = np.argmax(valid_mask)

    # 计算初始资本存量 K(0)
    # 寻找前5年连续有数据的窗口来估计 g
    start_idx = first_valid
    end_idx = min(first_valid + 5, len(inv))
    inv_window = inv[start_idx:end_idx]
    inv_window = inv_window[~np.isnan(inv_window)]

    if len(inv_window) >= 2 and inv_window[0] > 0:
        # 计算平均增长率
        growth_rates = []
        for i in range(1, len(inv_window)):
            if inv_window[i-1] > 0:
                growth_rates.append(inv_window[i] / inv_window[i-1] - 1)
        if len(growth_rates) > 0:
            g = np.mean(growth_rates)
            g = max(g, 0.01)  # 下限 1%
        else:
            g = 0.05
    else:
        g = 0.05

    # 初始化
    K = np.full(len(inv), np.nan)
    I0 = inv[first_valid]
    if not np.isnan(I0) and I0 > 0:
        K[first_valid] = I0 / (g + delta)
    else:
        df['K_pim'] = np.nan
        return df

    # 递推
    for t in range(first_valid + 1, len(inv)):
        if np.isnan(inv[t]):
            # 无投资数据时仅折旧
            if not np.isnan(K[t-1]):
                K[t] = (1 - delta) * K[t-1]
        else:
            if not np.isnan(K[t-1]):
                K[t] = (1 - delta) * K[t-1] + inv[t]
            else:
                K[t] = inv[t] / (g + delta)

    df['K_pim'] = K
    return df

rprint("  正在计算 PIM 资本存量...")
panel = panel.groupby('country_code', group_keys=False).apply(compute_pim_capital)
panel = panel.reset_index(drop=True)

k_pim_countries = panel.loc[panel['K_pim'].notna(), 'country_code'].nunique()
k_rnna_countries = panel.loc[panel['rnna'].notna(), 'country_code'].nunique()
rprint(f"  K_PIM 可用国家: {k_pim_countries}")
rprint(f"  K_rnna (PWT) 可用国家: {k_rnna_countries}")

# 选择最佳 K(t) 口径：优先 PIM（基于名义投资），rnna 做备份
# 注意：rnna 单位是 million 2017 US$，需转换以与名义投资可比
# 为了计算 Urban Q，K 和 V 必须口径一致
# K_pim 基于名义美元投资 -> 用于与名义 V 配合
# rnna 基于实际值 -> 用于 V2 口径
panel['K_best'] = panel['K_pim']  # 主口径

rprint(f"  K_best 可用: {panel['K_best'].notna().sum()} 行, "
       f"{panel.loc[panel['K_best'].notna(), 'country_code'].nunique()} 国")

# =============================================================================
# 步骤 3：构建 V(t) — 城市资产价值代理（多口径）
# =============================================================================
rprint("\n[步骤 3] 构建城市资产价值 V(t)")
rprint("-" * 40)

# --- 口径 V1：有 OECD 房价指数的国家 ---
# V1(t) = K(base_year=2010) * RealPropertyPriceIndex(t) / RealPropertyPriceIndex(2010)
# BIS RHP 指数以 2010 = 100 为基期
rprint("  [V1] 基于房价指数 (约 47 国)")

def compute_v1(group):
    """使用房价指数对基期资本存量进行市值重估"""
    df = group.copy()
    # 找到 2010 年的 K_pim 作为基期
    k_2010 = df.loc[df['year'] == 2010, 'K_pim'].values
    rpi_series = df['real_property_price_index']

    if len(k_2010) > 0 and not np.isnan(k_2010[0]) and rpi_series.notna().any():
        k_base = k_2010[0]
        # RHP 指数本身以 2010=100
        df['V1'] = k_base * (rpi_series / 100.0)
    else:
        df['V1'] = np.nan
    return df

panel = panel.groupby('country_code', group_keys=False).apply(compute_v1)
panel = panel.reset_index(drop=True)
v1_countries = panel.loc[panel['V1'].notna(), 'country_code'].nunique()
rprint(f"  V1 可用国家: {v1_countries}")

# --- 口径 V2：PWT 资本存量 + GDP 平减指数调整 ---
# V2(t) = rnna(t) * (GDP_current(t) / GDP_constant(t))
# rnna 单位: million 2017 US$，乘以 GDP 平减指数转换为名义值
# 再乘以 1e6 转换为美元（与 K_pim 同单位）
rprint("  [V2] 基于 PWT 资本存量 + GDP 平减指数 (所有有数据国家)")

panel['gdp_deflator'] = panel['gdp_current_usd'] / panel['gdp_constant_2015']
panel['V2'] = panel['rnna'] * 1e6 * panel['gdp_deflator']
# 注意：V2 现在是名义美元，与 K_pim 可比

v2_countries = panel.loc[panel['V2'].notna(), 'country_code'].nunique()
rprint(f"  V2 可用国家: {v2_countries}")

# --- 口径 V3：GDP 为基础代理 ---
# V3(t) = GDP_current(t) * wealth_income_ratio
# wealth_income_ratio 从有完整数据的国家标定
# 国际经验：发达国家 wealth/GDP 约 4-6 倍，发展中 3-4 倍
# 这里用 V2/GDP 在有数据国家中的中位数标定
rprint("  [V3] 基于 GDP * 财富-收入比 (所有国家)")

# 用 2010-2019 年有 V2 数据的国家标定 wealth_income_ratio
mask_calib = (panel['year'].between(2010, 2019) &
              panel['V2'].notna() &
              panel['gdp_current_usd'].notna() &
              (panel['gdp_current_usd'] > 0))
ratio_series = panel.loc[mask_calib, 'V2'] / panel.loc[mask_calib, 'gdp_current_usd']
median_wir = ratio_series.median()
rprint(f"  标定 wealth_income_ratio (中位数): {median_wir:.2f}")

panel['V3'] = panel['gdp_current_usd'] * median_wir

# =============================================================================
# 步骤 4：计算全球 Urban Q
# =============================================================================
rprint("\n[步骤 4] 计算 Urban Q 指标")
rprint("-" * 40)

# 主口径：V2 / K_pim（名义美元口径一致）
panel['urban_q_v2'] = panel['V2'] / panel['K_best']

# 替代口径：V1 / K_pim（有房价数据的国家）
panel['urban_q_v1'] = panel['V1'] / panel['K_best']

# 替代口径：V3 / K_pim
panel['urban_q_v3'] = panel['V3'] / panel['K_best']

# 投资/GDP 比率
panel['ci_gdp_ratio'] = panel['gfcf_current_usd'] / panel['gdp_current_usd']

# 选择主 Urban Q：优先 V2 口径
panel['urban_q'] = panel['urban_q_v2']

# 处理极端值：Q < 0 或 Q > 20 设为缺失（数据质量问题）
extreme_mask = (panel['urban_q'] < 0) | (panel['urban_q'] > 20)
n_extreme = extreme_mask.sum()
panel.loc[extreme_mask, 'urban_q'] = np.nan
rprint(f"  剔除极端值 (Q<0 或 Q>20): {n_extreme} 行")

# 计算 MUQ = Delta_V / Delta_I (边际 Urban Q)
panel = panel.sort_values(['country_code', 'year'])
panel['delta_V'] = panel.groupby('country_code')['V2'].diff()
panel['delta_I'] = panel.groupby('country_code')['gfcf_current_usd'].diff()
panel['muq'] = panel['delta_V'] / panel['delta_I']
# MUQ 极端值处理
muq_extreme = (panel['muq'].abs() > 50) | (panel['muq'] < -10)
panel.loc[muq_extreme, 'muq'] = np.nan

# 投资增值率 = Delta_V / V
panel['delta_V_ratio'] = panel['delta_V'] / panel.groupby('country_code')['V2'].shift(1)

q_countries = panel.loc[panel['urban_q'].notna(), 'country_code'].nunique()
rprint(f"  Urban Q (V2/K_PIM) 可用国家: {q_countries}")
rprint(f"  Urban Q 中位数 (2010-2019): "
       f"{panel.loc[panel['year'].between(2010,2019), 'urban_q'].median():.3f}")

# =============================================================================
# 步骤 5：识别各国 Q = 1 临界年份
# =============================================================================
rprint("\n[步骤 5] 识别 Q = 1 临界年份")
rprint("-" * 40)

def find_q_crossover(group):
    """找到 Q 从 >1 降至 <1 的年份"""
    df = group.sort_values('year').dropna(subset=['urban_q'])
    if len(df) < 2:
        return pd.Series({
            'q_crossover_year': np.nan,
            'q_crossover_urban_pct': np.nan,
            'q_crossover_services_pct': np.nan,
            'q_crossover_hc': np.nan,
            'ever_above_1': False,
            'ever_below_1': False,
        })

    q_vals = df['urban_q'].values
    years = df['year'].values

    ever_above = (q_vals > 1).any()
    ever_below = (q_vals < 1).any()

    # 找第一次从 >1 跌至 <1
    crossover_year = np.nan
    for i in range(1, len(q_vals)):
        if q_vals[i-1] > 1 and q_vals[i] < 1:
            crossover_year = years[i]
            break

    if not np.isnan(crossover_year):
        row = df[df['year'] == crossover_year].iloc[0]
        return pd.Series({
            'q_crossover_year': crossover_year,
            'q_crossover_urban_pct': row.get('urban_pct', np.nan),
            'q_crossover_services_pct': row.get('services_pct_gdp', np.nan),
            'q_crossover_hc': row.get('hc', np.nan),
            'ever_above_1': ever_above,
            'ever_below_1': ever_below,
        })
    else:
        return pd.Series({
            'q_crossover_year': np.nan,
            'q_crossover_urban_pct': np.nan,
            'q_crossover_services_pct': np.nan,
            'q_crossover_hc': np.nan,
            'ever_above_1': ever_above,
            'ever_below_1': ever_below,
        })

crossover_df = panel.groupby('country_code').apply(find_q_crossover).reset_index()

n_crossover = crossover_df['q_crossover_year'].notna().sum()
n_always_above = ((crossover_df['ever_above_1']) & (~crossover_df['ever_below_1'])).sum()
n_always_below = ((~crossover_df['ever_above_1']) & (crossover_df['ever_below_1'])).sum()
rprint(f"  经历 Q=1 交叉的国家: {n_crossover}")
rprint(f"  始终 Q>1 的国家: {n_always_above}")
rprint(f"  始终 Q<1 的国家: {n_always_below}")

if n_crossover > 0:
    cross_stats = crossover_df[crossover_df['q_crossover_year'].notna()]
    rprint(f"  交叉年份中位数: {cross_stats['q_crossover_year'].median():.0f}")
    rprint(f"  交叉时城镇化率中位数: {cross_stats['q_crossover_urban_pct'].median():.1f}%")
    rprint(f"  交叉时服务业占比中位数: {cross_stats['q_crossover_services_pct'].median():.1f}%")

# =============================================================================
# 构建国家摘要表
# =============================================================================
rprint("\n[构建国家摘要表]")
rprint("-" * 40)

# 获取每国最新可用年份的 Q
latest_q = (panel.dropna(subset=['urban_q'])
            .sort_values('year')
            .groupby('country_code')
            .last()
            .reset_index()[['country_code', 'year', 'urban_q', 'urban_pct',
                           'ci_gdp_ratio', 'hc', 'services_pct_gdp',
                           'gdp_current_usd', 'total_pop']])
latest_q = latest_q.rename(columns={
    'year': 'latest_q_year',
    'urban_q': 'latest_q',
    'urban_pct': 'latest_urban_pct',
})

# 2010-2019 均值
avg_2010s = (panel[panel['year'].between(2010, 2019)]
             .groupby('country_code')
             .agg(
                 avg_q_2010s=('urban_q', 'mean'),
                 avg_ci_gdp_2010s=('ci_gdp_ratio', 'mean'),
                 avg_muq_2010s=('muq', 'mean'),
             ).reset_index())

# 国家基本信息
country_info = (panel.groupby('country_code')
                .agg(country_name=('country_name', 'first'),
                     region=('region', 'first'))
                .reset_index())

# 收入分类（基于 2019 GNI per capita 的简化分类，用 GDP per capita 近似）
gdp_pc_2019 = panel[panel['year'] == 2019].copy()
gdp_pc_2019['gdp_per_capita'] = gdp_pc_2019['gdp_current_usd'] / gdp_pc_2019['total_pop']

def classify_income(gdp_pc):
    """World Bank 收入分类阈值（2019 标准近似）"""
    if pd.isna(gdp_pc):
        return 'Unknown'
    elif gdp_pc >= 12536:
        return 'High income'
    elif gdp_pc >= 4046:
        return 'Upper middle income'
    elif gdp_pc >= 1036:
        return 'Lower middle income'
    else:
        return 'Low income'

gdp_pc_2019['income_group'] = gdp_pc_2019['gdp_per_capita'].apply(classify_income)
income_df = gdp_pc_2019[['country_code', 'income_group', 'gdp_per_capita']].copy()

# 大洲映射（基于 WB region）
continent_map = {
    'Sub-Saharan Africa': 'Africa',
    'Europe & Central Asia': 'Europe & Central Asia',
    'Latin America & Caribbean': 'Latin America',
    'East Asia & Pacific': 'East Asia & Pacific',
    'South Asia': 'South Asia',
    'Middle East, North Africa, Afghanistan & Pakistan': 'MENA',
    'North America': 'North America',
}

# 合并摘要
summary = (country_info
           .merge(income_df, on='country_code', how='left')
           .merge(latest_q, on='country_code', how='left')
           .merge(avg_2010s, on='country_code', how='left')
           .merge(crossover_df, on='country_code', how='left'))

summary['continent'] = summary['region'].map(continent_map).fillna('Other')

rprint(f"  摘要表: {len(summary)} 国")
rprint(f"  收入分组分布:")
for g, cnt in summary['income_group'].value_counts().items():
    rprint(f"    {g}: {cnt}")

# =============================================================================
# 步骤 6：可视化
# =============================================================================
rprint("\n[步骤 6] 生成可视化")
rprint("-" * 40)

fig = plt.figure(figsize=(20, 18))
gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

# --- 图 A：区域分组的最新 Urban Q 条形图 ---
ax_a = fig.add_subplot(gs[0, :])

# 按区域分组，展示各国最新 Q
plot_data = summary.dropna(subset=['latest_q']).copy()
plot_data = plot_data[plot_data['latest_q'] < 10]  # 排除极端值

# 按大洲和 Q 值排序
plot_data = plot_data.sort_values(['continent', 'latest_q'], ascending=[True, False])

# 颜色编码
def q_color(q):
    if q > 1.5:
        return '#2ecc71'   # 绿色
    elif q > 1.0:
        return '#f1c40f'   # 黄色
    elif q > 0.5:
        return '#e67e22'   # 橙色
    else:
        return '#e74c3c'   # 红色

colors = [q_color(q) for q in plot_data['latest_q']]

# 按区域分组展示 - 选取每区域 top/bottom 国家以控制数量
selected = []
for cont in plot_data['continent'].unique():
    sub = plot_data[plot_data['continent'] == cont].sort_values('latest_q', ascending=False)
    if len(sub) > 8:
        selected.append(pd.concat([sub.head(4), sub.tail(4)]))
    else:
        selected.append(sub)
if selected:
    plot_sub = pd.concat(selected)
else:
    plot_sub = plot_data.head(50)

# 重新排序
plot_sub = plot_sub.sort_values(['continent', 'latest_q'], ascending=[True, False])
colors_sub = [q_color(q) for q in plot_sub['latest_q']]

bars = ax_a.barh(range(len(plot_sub)), plot_sub['latest_q'], color=colors_sub, edgecolor='white', linewidth=0.5)
ax_a.set_yticks(range(len(plot_sub)))
ax_a.set_yticklabels(plot_sub['country_code'], fontsize=7)
ax_a.axvline(x=1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Q = 1')
ax_a.set_xlabel('Urban Q (latest available year)', fontsize=11)
ax_a.set_title('(A) Global Urban Q by Region (selected countries)', fontsize=14, fontweight='bold')
ax_a.legend(fontsize=10)
ax_a.invert_yaxis()

# 添加区域分隔线
prev_cont = None
for i, (_, row) in enumerate(plot_sub.iterrows()):
    if prev_cont is not None and row['continent'] != prev_cont:
        ax_a.axhline(y=i-0.5, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    prev_cont = row['continent']

# --- 图 B：投资强度 vs Urban Q 散点图 ---
ax_b = fig.add_subplot(gs[1, 0])

scatter_data = summary.dropna(subset=['avg_q_2010s', 'avg_ci_gdp_2010s']).copy()
scatter_data = scatter_data[(scatter_data['avg_q_2010s'] > 0) &
                            (scatter_data['avg_q_2010s'] < 10) &
                            (scatter_data['avg_ci_gdp_2010s'] > 0) &
                            (scatter_data['avg_ci_gdp_2010s'] < 0.6)]

# 颜色按大洲
continent_colors = {
    'Africa': '#e74c3c',
    'Europe & Central Asia': '#3498db',
    'Latin America': '#2ecc71',
    'East Asia & Pacific': '#e67e22',
    'South Asia': '#9b59b6',
    'MENA': '#f1c40f',
    'North America': '#1abc9c',
    'Other': '#95a5a6',
}

# 点大小按 GDP（对数缩放）
if scatter_data['gdp_current_usd'].notna().any():
    gdp_log = np.log10(scatter_data['gdp_current_usd'].clip(lower=1e8))
    size_scale = ((gdp_log - gdp_log.min()) / (gdp_log.max() - gdp_log.min() + 1e-10)) * 200 + 20
else:
    size_scale = 50

for cont, color in continent_colors.items():
    mask = scatter_data['continent'] == cont
    if mask.any():
        ax_b.scatter(scatter_data.loc[mask, 'avg_ci_gdp_2010s'] * 100,
                    scatter_data.loc[mask, 'avg_q_2010s'],
                    s=size_scale[mask] if hasattr(size_scale, '__getitem__') else 50,
                    c=color, alpha=0.7, edgecolors='white', linewidth=0.5,
                    label=cont, zorder=3)

# 拟合线
x_fit = scatter_data['avg_ci_gdp_2010s'].values * 100
y_fit = scatter_data['avg_q_2010s'].values
valid = ~(np.isnan(x_fit) | np.isnan(y_fit))
if valid.sum() > 5:
    z = np.polyfit(x_fit[valid], y_fit[valid], 2)
    p = np.poly1d(z)
    x_range = np.linspace(x_fit[valid].min(), x_fit[valid].max(), 100)
    ax_b.plot(x_range, p(x_range), 'k--', linewidth=1.5, alpha=0.5, label='Quadratic fit')

# 标注关键国家
highlight_countries = ['CHN', 'JPN', 'USA', 'GBR', 'DEU', 'KOR', 'IND', 'BRA', 'RUS', 'FRA']
for _, row in scatter_data.iterrows():
    if row['country_code'] in highlight_countries:
        ax_b.annotate(row['country_code'],
                     (row['avg_ci_gdp_2010s'] * 100, row['avg_q_2010s']),
                     fontsize=8, fontweight='bold',
                     xytext=(5, 5), textcoords='offset points')

ax_b.axhline(y=1.0, color='red', linestyle=':', linewidth=1, alpha=0.5)
ax_b.set_xlabel('Investment Intensity (GFCF/GDP, %, 2010-2019 avg)', fontsize=10)
ax_b.set_ylabel('Urban Q (2010-2019 avg)', fontsize=10)
ax_b.set_title('(B) Investment Intensity vs Urban Q', fontsize=13, fontweight='bold')
ax_b.legend(fontsize=7, loc='upper right', ncol=2)
ax_b.grid(True, alpha=0.3)

# --- 图 C：收入组 Urban Q 分布箱线图 ---
ax_c = fig.add_subplot(gs[1, 1])

box_data = summary.dropna(subset=['avg_q_2010s', 'income_group']).copy()
box_data = box_data[(box_data['avg_q_2010s'] > 0) & (box_data['avg_q_2010s'] < 10)]

income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
box_groups = []
box_labels = []
for ig in income_order:
    vals = box_data.loc[box_data['income_group'] == ig, 'avg_q_2010s'].dropna().values
    if len(vals) > 0:
        box_groups.append(vals)
        box_labels.append(f"{ig}\n(n={len(vals)})")

if box_groups:
    bp = ax_c.boxplot(box_groups, labels=box_labels, patch_artist=True,
                      widths=0.6, showfliers=True,
                      flierprops=dict(marker='o', markersize=4, alpha=0.5))

    box_colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71']
    for patch, color in zip(bp['boxes'], box_colors[:len(bp['boxes'])]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

ax_c.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Q = 1')
ax_c.set_ylabel('Urban Q (2010-2019 avg)', fontsize=10)
ax_c.set_title('(C) Urban Q Distribution by Income Group', fontsize=13, fontweight='bold')
ax_c.legend(fontsize=10)
ax_c.grid(True, axis='y', alpha=0.3)

plt.suptitle('Global Urban Q Analysis: 158 Countries',
             fontsize=16, fontweight='bold', y=0.98)

plt.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
rprint(f"  图表已保存: {OUT_FIG}")

# =============================================================================
# 步骤 7：输出
# =============================================================================
rprint("\n[步骤 7] 保存输出文件")
rprint("-" * 40)

# 选择面板输出列
panel_out_cols = [
    'country_code', 'country_name', 'region', 'year',
    # World Bank
    'gdp_current_usd', 'gdp_constant_2015', 'gfcf_pct_gdp', 'gfcf_current_usd',
    'services_pct_gdp', 'industry_pct_gdp', 'agriculture_pct_gdp',
    'urban_pct', 'urban_pop', 'total_pop', 'pop_15_64_pct', 'pop_65plus_pct',
    # PWT
    'hc', 'rnna', 'rgdpna', 'ctfp', 'delta',
    # OECD
    'real_property_price_index',
    # 构建变量
    'K_pim', 'K_best', 'V1', 'V2', 'V3',
    'urban_q', 'urban_q_v1', 'urban_q_v2', 'urban_q_v3',
    'ci_gdp_ratio', 'muq', 'delta_V_ratio',
]
panel_out = panel[[c for c in panel_out_cols if c in panel.columns]]
panel_out = panel_out.sort_values(['country_code', 'year'])
panel_out.to_csv(OUT_PANEL, index=False)
rprint(f"  面板数据: {OUT_PANEL}")
rprint(f"    {len(panel_out)} 行, {panel_out['country_code'].nunique()} 国")

# 摘要表
summary_out = summary[[
    'country_code', 'country_name', 'region', 'continent', 'income_group',
    'latest_q_year', 'latest_q', 'latest_urban_pct',
    'avg_q_2010s', 'avg_ci_gdp_2010s', 'avg_muq_2010s',
    'q_crossover_year', 'q_crossover_urban_pct', 'q_crossover_services_pct',
    'q_crossover_hc', 'ever_above_1', 'ever_below_1',
    'gdp_per_capita',
]].copy()
summary_out = summary_out.sort_values('avg_q_2010s', ascending=False)
summary_out.to_csv(OUT_SUMMARY, index=False)
rprint(f"  国家摘要: {OUT_SUMMARY}")

# =============================================================================
# 关键发现汇总
# =============================================================================
rprint("\n" + "=" * 70)
rprint("关键发现汇总")
rprint("=" * 70)

# Q 值分布
q_2010s = summary.dropna(subset=['avg_q_2010s'])
rprint(f"\n1. Urban Q 分布 (2010-2019 均值, n={len(q_2010s)}):")
rprint(f"   均值: {q_2010s['avg_q_2010s'].mean():.3f}")
rprint(f"   中位数: {q_2010s['avg_q_2010s'].median():.3f}")
rprint(f"   标准差: {q_2010s['avg_q_2010s'].std():.3f}")
rprint(f"   Q > 1 国家: {(q_2010s['avg_q_2010s'] > 1).sum()}")
rprint(f"   Q < 1 国家: {(q_2010s['avg_q_2010s'] < 1).sum()}")

# 按收入组
rprint(f"\n2. 各收入组 Urban Q 中位数 (2010-2019):")
for ig in income_order:
    vals = q_2010s.loc[q_2010s['income_group'] == ig, 'avg_q_2010s']
    if len(vals) > 0:
        rprint(f"   {ig}: {vals.median():.3f} (n={len(vals)})")

# 关键国家
rprint(f"\n3. 关键国家 Urban Q:")
key_countries = ['CHN', 'JPN', 'USA', 'GBR', 'DEU', 'KOR', 'IND', 'BRA', 'RUS', 'FRA',
                 'AUS', 'CAN', 'SGP', 'ZAF', 'MEX', 'TUR', 'SAU', 'IDN']
for cc in key_countries:
    row = summary[summary['country_code'] == cc]
    if len(row) > 0 and not pd.isna(row.iloc[0].get('avg_q_2010s', np.nan)):
        r = row.iloc[0]
        cross_str = f", Q=1 year: {int(r['q_crossover_year'])}" if not pd.isna(r.get('q_crossover_year', np.nan)) else ""
        rprint(f"   {r['country_name']} ({cc}): Q={r['avg_q_2010s']:.3f} "
               f"(CI/GDP={r.get('avg_ci_gdp_2010s', 0)*100:.1f}%{cross_str})")

# Q=1 交叉分析
rprint(f"\n4. Q=1 交叉分析:")
cross_sub = crossover_df[crossover_df['q_crossover_year'].notna()]
if len(cross_sub) > 0:
    rprint(f"   经历 Q=1 交叉的国家: {len(cross_sub)}")
    rprint(f"   交叉年份范围: {int(cross_sub['q_crossover_year'].min())}-{int(cross_sub['q_crossover_year'].max())}")
    # 列出所有交叉国家
    cross_detail = cross_sub.merge(country_info, on='country_code')
    for _, r in cross_detail.sort_values('q_crossover_year').iterrows():
        rprint(f"   {r['country_name']} ({r['country_code']}): "
               f"{int(r['q_crossover_year'])}, 城镇化率={r['q_crossover_urban_pct']:.1f}%")

# 保存报告
with open(OUT_REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
rprint(f"\n报告已保存: {OUT_REPORT}")

rprint("\n[完成] 全球 Urban Q 面板构建完毕。")
