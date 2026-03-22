"""
01_china_urban_q.py
===================
目的：构造中国 Urban Q 时序（多种定义），计算边际 Urban Q (MUQ)，生成可视化

输入数据：
  - six-curves 项目主数据集 (six_curves_master_dataset_processed.csv)
  - 资产价值分析结果 (c5_asset_value_analysis.csv)
  - SGI 剪刀差指数 (sgi_scissors_gap_index.csv)
  - ICR 投资资本化率 (investment_capitalization_rate.csv)

输出：
  - china_urban_q_timeseries.csv — Urban Q 各定义的完整时序
  - fig01_china_urban_q.png — 2×2 面板图

依赖包：pandas, numpy, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# ============================================================
# 0. 路径设置
# ============================================================

SIX_CURVES_DIR = Path("/Users/andy/Desktop/Claude/six-curves-urban-transition")
OUTPUT_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")

# ============================================================
# 1. 读取数据
# ============================================================

# 主数据集
master = pd.read_csv(SIX_CURVES_DIR / "02-data/processed/six_curves_master_dataset_processed.csv")

# 资产价值分析（含住宅市场总价值）
asset = pd.read_csv(SIX_CURVES_DIR / "03-analysis/models/c5_asset_value_analysis.csv")

# SGI 和 ICR
sgi = pd.read_csv(SIX_CURVES_DIR / "03-analysis/models/sgi_scissors_gap_index.csv")
icr = pd.read_csv(SIX_CURVES_DIR / "03-analysis/models/investment_capitalization_rate.csv")

# 合并到主数据框
df = master[['year', 'urbanization_rate_pct', 'housing_stock_10k_m2',
             'commercial_housing_avg_price_yuan_m2',
             'commercial_housing_sales_area_10k_m2',
             'commercial_housing_sales_amount_100m',
             'realestate_inv', 'infra_inv', 'total_construction_inv',
             'land_transfer_revenue_100m']].copy()

# 从 asset 表合并住宅市场总价值
asset_cols = asset[['year', 'housing_market_value_100m']].copy()
df = df.merge(asset_cols, on='year', how='left')

# 从 icr 表合并 ICR
icr_cols = icr[['year', 'ICR_re', 'ICR_total']].copy()
df = df.merge(icr_cols, on='year', how='left')

# 从 sgi 表合并 SGI
sgi_cols = sgi[['year', 'SGI_index']].copy()
df = df.merge(sgi_cols, on='year', how='left')

print(f"数据范围: {df['year'].min()} - {df['year'].max()}")
print(f"共 {len(df)} 年观测值")

# ============================================================
# 2. 构造 V(t) — 城市资产市场价值（三种定义）
# ============================================================

# --- V1: 住宅市场总价值 = 存量面积 × 当年均价 ---
# 已在 asset 表中计算：housing_market_value_100m (单位：亿元)
# 原始计算: housing_stock_10k_m2 * commercial_housing_avg_price_yuan_m2
# 注意单位转换：10k_m2 * 元/m2 = 万元，再除以 10000 得到亿元
# 验证：706300 万m2 * 2063 元/m2 = 1456.9 亿 ... 实际表中为 145709.69 亿
#   因为 706300 * 10000 m2 * 2063 = 1.457e12 元 = 145709 亿元 ✓ (housing_stock是万平方米)
df['V1_housing_value_100m'] = df['housing_market_value_100m']

# --- V2: 住宅市场价值 + 基础设施资本存量（折旧调整） ---
# 用 PIM 法估算基础设施资本存量
# K_infra(t) = K_infra(t-1) * (1-delta) + I_infra(t)
# 基础设施折旧率取 4%/年（较建筑物高，因含设备）
delta_infra = 0.04

# 筛选有基础设施投资的年份（1990起）
df_infra = df[df['infra_inv'].notna()].copy()
infra_stock = []
for i, row in df_infra.iterrows():
    if len(infra_stock) == 0:
        # 基期假设：1990年前累计基础设施投资约为当年投资的5倍（粗略估计）
        initial_stock = row['infra_inv'] * 5
        infra_stock.append(initial_stock)
    else:
        prev = infra_stock[-1]
        infra_stock.append(prev * (1 - delta_infra) + row['infra_inv'])

df.loc[df['infra_inv'].notna(), 'infra_capital_stock_100m'] = infra_stock

# V2 = V1 + 基础设施资本存量
df['V2_total_urban_value_100m'] = df['V1_housing_value_100m'] + df['infra_capital_stock_100m']

# --- V3: 流量指标近似 = 商品房销售额 + 土地出让收入 ---
df['V3_flow_proxy_100m'] = (df['commercial_housing_sales_amount_100m'].fillna(0) +
                             df['land_transfer_revenue_100m'].fillna(0))

print("\n=== V(t) 构造完成 ===")
print(df[['year', 'V1_housing_value_100m', 'V2_total_urban_value_100m', 'V3_flow_proxy_100m']].dropna(subset=['V1_housing_value_100m']).to_string(index=False))

# ============================================================
# 3. 构造 K(t) — 累计建设投资（两种定义）
# ============================================================

# --- K1: 简单累计（房地产投资 + 基础设施投资） ---
# 从1990年开始（两个投资序列都可用的最早年份）
# 先对 total_construction_inv 做累计
df['K1_cumulative_inv_100m'] = np.nan

# 需要逐年累加 total_construction_inv
# total_construction_inv = realestate_inv + infra_inv（已在主数据集中计算）
mask_inv = df['total_construction_inv'].notna()
df.loc[mask_inv, 'K1_cumulative_inv_100m'] = df.loc[mask_inv, 'total_construction_inv'].cumsum()

# --- K2: PIM法折旧调整的资本存量 ---
# K2(t) = K2(t-1) * (1-delta) + I(t)
# 建筑物综合折旧率: 2.5%/年（住宅约2%，基础设施约4%，加权平均）
delta_total = 0.025

k2_values = []
for i, row in df[mask_inv].iterrows():
    inv = row['total_construction_inv']
    if len(k2_values) == 0:
        # 基期假设：1987年以前的累计投资约为当年投资的8倍
        # 1990年的 total_construction_inv = 1105.8 亿元
        # 1987-1989年仅有房地产投资（约700亿），加上1990年前基础设施投资
        # 粗略初始存量 ≈ 当年投资 × 8
        initial_k2 = inv * 8
        k2_values.append(initial_k2)
    else:
        prev = k2_values[-1]
        k2_values.append(prev * (1 - delta_total) + inv)

df.loc[mask_inv, 'K2_pim_capital_stock_100m'] = k2_values

print("\n=== K(t) 构造完成 ===")
print(df[['year', 'K1_cumulative_inv_100m', 'K2_pim_capital_stock_100m']].dropna(subset=['K1_cumulative_inv_100m']).to_string(index=False))

# ============================================================
# 4. 计算 Urban Q 和 MUQ
# ============================================================

# 分析窗口：1998-2024（V1可用的年份范围）
df_q = df[(df['year'] >= 1998) & (df['V1_housing_value_100m'].notna())].copy()

# --- Urban Q: V/K 的六种组合 ---
# 主要规格：V1/K1, V1/K2
# 扩展规格：V2/K1, V2/K2
# 流量参考：V3 不计算 Q（因 V3 是流量，K 是存量，量纲不一致）

df_q['Q_V1K1'] = df_q['V1_housing_value_100m'] / df_q['K1_cumulative_inv_100m']
df_q['Q_V1K2'] = df_q['V1_housing_value_100m'] / df_q['K2_pim_capital_stock_100m']
df_q['Q_V2K1'] = df_q['V2_total_urban_value_100m'] / df_q['K1_cumulative_inv_100m']
df_q['Q_V2K2'] = df_q['V2_total_urban_value_100m'] / df_q['K2_pim_capital_stock_100m']

# --- 边际 Urban Q (MUQ): ΔV / ΔI ---
# ΔV = V(t) - V(t-1), ΔI = 当年新增投资 I(t)
for v_col, muq_col in [('V1_housing_value_100m', 'MUQ_V1'),
                        ('V2_total_urban_value_100m', 'MUQ_V2')]:
    df_q[f'delta_{v_col}'] = df_q[v_col].diff()
    # MUQ 用 total_construction_inv 作为 ΔI
    df_q[muq_col] = df_q[f'delta_{v_col}'] / df_q['total_construction_inv']

# --- 与 ICR 和 SGI 的对照 ---
# ICR_total = ΔV_housing / total_construction_inv → 与 MUQ_V1 相同
# Q ≈ 1/SGI 的关系验证（SGI 是投资指数/资产指数，Q 是资产/投资）
df_q['Q_vs_inv_SGI'] = np.where(df_q['SGI_index'].notna(),
                                 1.0 / df_q['SGI_index'], np.nan)

print("\n=== Urban Q 计算完成 ===")
print(df_q[['year', 'Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2',
            'MUQ_V1', 'MUQ_V2']].to_string(index=False))

# ============================================================
# 5. 识别关键转折点
# ============================================================

print("\n" + "="*60)
print("关键转折点分析")
print("="*60)

# 5.1 Urban Q = 1 的年份
for q_col in ['Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2']:
    vals = df_q[['year', q_col]].dropna()
    # 找 Q 从 >1 跌破 1 或从 <1 升破 1 的年份
    crossings = []
    for i in range(1, len(vals)):
        prev_val = vals.iloc[i-1][q_col]
        curr_val = vals.iloc[i][q_col]
        if (prev_val - 1) * (curr_val - 1) < 0:  # 符号变化
            # 线性插值找精确年份
            y1, y2 = vals.iloc[i-1]['year'], vals.iloc[i]['year']
            frac = (1 - prev_val) / (curr_val - prev_val)
            cross_year = y1 + frac * (y2 - y1)
            direction = "下穿" if prev_val > 1 else "上穿"
            crossings.append((cross_year, direction))

    first_val = vals.iloc[0][q_col]
    last_val = vals.iloc[-1][q_col]
    print(f"\n{q_col}:")
    print(f"  起始值 ({int(vals.iloc[0]['year'])}): {first_val:.3f}")
    print(f"  终止值 ({int(vals.iloc[-1]['year'])}): {last_val:.3f}")
    if crossings:
        for cy, d in crossings:
            print(f"  Q=1 交叉点: {cy:.1f} 年 ({d})")
    else:
        if first_val > 1 and last_val > 1:
            print(f"  始终 > 1，未出现相变点")
        elif first_val < 1 and last_val < 1:
            print(f"  始终 < 1")
        else:
            print(f"  无交叉")

# 5.2 MUQ = 1 的年份
for muq_col in ['MUQ_V1', 'MUQ_V2']:
    vals = df_q[['year', muq_col]].dropna()
    crossings = []
    for i in range(1, len(vals)):
        prev_val = vals.iloc[i-1][muq_col]
        curr_val = vals.iloc[i][muq_col]
        if (prev_val - 1) * (curr_val - 1) < 0:
            y1, y2 = vals.iloc[i-1]['year'], vals.iloc[i]['year']
            frac = (1 - prev_val) / (curr_val - prev_val)
            cross_year = y1 + frac * (y2 - y1)
            direction = "下穿" if prev_val > 1 else "上穿"
            crossings.append((cross_year, direction, int(vals.iloc[i]['year'])))

    print(f"\n{muq_col}:")
    if crossings:
        for cy, d, yr in crossings:
            print(f"  MUQ=1 交叉点: {cy:.1f} 年 ({d})，首次落入年份: {yr}")
    else:
        print(f"  无交叉记录")

# 5.3 Q 与 1/SGI 的关系
print(f"\n=== Q 与 1/SGI 对照 ===")
compare = df_q[['year', 'Q_V1K1', 'Q_vs_inv_SGI']].dropna()
if len(compare) > 0:
    corr = compare['Q_V1K1'].corr(compare['Q_vs_inv_SGI'])
    print(f"  Q_V1K1 与 1/SGI 的相关系数: {corr:.4f}")
    print(f"  注: SGI 基于指数（2000=100），Q 基于绝对值，两者度量不同但趋势应一致")

# ============================================================
# 6. 敏感性分析：初始存量假设的影响
# ============================================================

print(f"\n=== 敏感性分析：初始存量假设 ===")
# 对 K2 的初始存量乘数做敏感性（基准=8，范围 4-12）
for mult in [4, 6, 8, 10, 12]:
    k2_test = []
    for i, row in df[mask_inv].iterrows():
        inv = row['total_construction_inv']
        if len(k2_test) == 0:
            k2_test.append(inv * mult)
        else:
            k2_test.append(k2_test[-1] * (1 - delta_total) + inv)

    # 取2024年的值
    k2_2024 = k2_test[-1]
    v1_2024 = df_q[df_q['year'] == 2024]['V1_housing_value_100m'].values[0]
    q_2024 = v1_2024 / k2_2024
    print(f"  初始乘数={mult}: K2(2024)={k2_2024:.0f} 亿元, Q_V1K2(2024)={q_2024:.3f}")

# ============================================================
# 7. 保存结果
# ============================================================

output_cols = ['year', 'urbanization_rate_pct',
               'V1_housing_value_100m', 'V2_total_urban_value_100m', 'V3_flow_proxy_100m',
               'K1_cumulative_inv_100m', 'K2_pim_capital_stock_100m',
               'Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2',
               'MUQ_V1', 'MUQ_V2',
               'total_construction_inv', 'realestate_inv', 'infra_inv',
               'ICR_re', 'ICR_total', 'SGI_index', 'Q_vs_inv_SGI']

output_path = OUTPUT_DIR / "03-analysis/models/china_urban_q_timeseries.csv"
df_q[output_cols].to_csv(output_path, index=False, float_format='%.4f')
print(f"\n结果已保存: {output_path}")

# ============================================================
# 8. 可视化：2×2 面板图
# ============================================================

# 设置中文字体（macOS）
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti SC', 'PingFang SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Nature 风格设置
plt.rcParams.update({
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 7.5,
    'figure.dpi': 300,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
})

# 颜色方案（学术风格）
COLORS = {
    'V1K1': '#2166AC',   # 深蓝
    'V1K2': '#4393C3',   # 中蓝
    'V2K1': '#D6604D',   # 砖红
    'V2K2': '#F4A582',   # 浅红
    'V': '#2166AC',
    'K': '#B2182B',
    'ref': '#666666',
}

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
fig.subplots_adjust(hspace=0.35, wspace=0.35, top=0.93, bottom=0.08, left=0.10, right=0.92)

years = df_q['year']

# ------ Panel A: Urban Q 时序 ------
ax = axes[0, 0]
ax.plot(years, df_q['Q_V1K1'], '-o', color=COLORS['V1K1'], markersize=3,
        linewidth=1.5, label='Q(V1/K1): 住宅价值/累计投资', zorder=3)
ax.plot(years, df_q['Q_V1K2'], '-s', color=COLORS['V1K2'], markersize=3,
        linewidth=1.2, label='Q(V1/K2): 住宅价值/PIM资本存量', zorder=3)
ax.plot(years, df_q['Q_V2K1'], '-^', color=COLORS['V2K1'], markersize=3,
        linewidth=1.2, label='Q(V2/K1): 总资产/累计投资', zorder=3)
ax.plot(years, df_q['Q_V2K2'], '-d', color=COLORS['V2K2'], markersize=3,
        linewidth=1.2, label='Q(V2/K2): 总资产/PIM资本存量', zorder=3)

ax.axhline(y=1, color=COLORS['ref'], linestyle='--', linewidth=0.8, alpha=0.7)
ax.text(2024.5, 1.02, 'Q = 1', fontsize=7, color=COLORS['ref'], va='bottom')

ax.set_xlabel('年份')
ax.set_ylabel('Urban Q')
ax.set_title('A. Urban Q 时序（多种定义）', fontweight='bold', loc='left')
ax.legend(loc='upper left', frameon=False, borderpad=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlim(1997, 2025.5)

# ------ Panel B: MUQ 时序 ------
ax = axes[0, 1]
ax.plot(years, df_q['MUQ_V1'], '-o', color=COLORS['V1K1'], markersize=3,
        linewidth=1.5, label='MUQ(V1): ΔV住宅/ΔI', zorder=3)
ax.plot(years, df_q['MUQ_V2'], '-^', color=COLORS['V2K1'], markersize=3,
        linewidth=1.2, label='MUQ(V2): ΔV总资产/ΔI', zorder=3)

# 也画 ICR_total 作为对照
icr_plot = df_q[df_q['ICR_total'].notna()]
ax.plot(icr_plot['year'], icr_plot['ICR_total'], '--', color='#999999',
        linewidth=0.8, label='ICR(total): 参考', alpha=0.6)

ax.axhline(y=1, color=COLORS['ref'], linestyle='--', linewidth=0.8, alpha=0.7)
ax.text(2024.5, 1.05, 'MUQ = 1', fontsize=7, color=COLORS['ref'], va='bottom')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.4, alpha=0.3)

ax.set_xlabel('年份')
ax.set_ylabel('边际 Urban Q (MUQ)')
ax.set_title('B. 边际 Urban Q 时序', fontweight='bold', loc='left')
ax.legend(loc='upper left', frameon=False, borderpad=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlim(1997, 2025.5)
ax.set_ylim(-1.5, 5)

# ------ Panel C: V(t) 和 K(t) 双轴图 ------
ax = axes[1, 0]
ax2 = ax.twinx()

# V1 和 K1 转换为万亿元 (除以10000)
v1_trillion = df_q['V1_housing_value_100m'] / 10000
k1_trillion = df_q['K1_cumulative_inv_100m'] / 10000
k2_trillion = df_q['K2_pim_capital_stock_100m'] / 10000

ln1 = ax.plot(years, v1_trillion, '-o', color=COLORS['V'], markersize=3,
              linewidth=1.5, label='V1: 住宅市场价值', zorder=3)
ln2 = ax2.plot(years, k1_trillion, '-s', color=COLORS['K'], markersize=3,
               linewidth=1.2, label='K1: 累计投资', zorder=3)
ln3 = ax2.plot(years, k2_trillion, '--^', color='#F4A582', markersize=3,
               linewidth=1.0, label='K2: PIM资本存量', zorder=3)

ax.set_xlabel('年份')
ax.set_ylabel('V(t) 住宅价值（万亿元）', color=COLORS['V'])
ax2.set_ylabel('K(t) 累计投资（万亿元）', color=COLORS['K'])
ax.tick_params(axis='y', colors=COLORS['V'])
ax2.tick_params(axis='y', colors=COLORS['K'])

# 合并图例
lns = ln1 + ln2 + ln3
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc='upper left', frameon=False, borderpad=0.5)

ax.set_title('C. 资产价值 V(t) 与资本存量 K(t)', fontweight='bold', loc='left')
ax.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax.set_xlim(1997, 2025.5)

# ------ Panel D: Urban Q vs 城镇化率 散点图 ------
ax = axes[1, 1]
scatter_data = df_q[df_q['urbanization_rate_pct'].notna() & df_q['Q_V1K1'].notna()].copy()

# 用颜色编码年份
sc = ax.scatter(scatter_data['urbanization_rate_pct'], scatter_data['Q_V1K1'],
                c=scatter_data['year'], cmap='viridis', s=35, edgecolors='white',
                linewidth=0.5, zorder=3)

# 添加年份标注（每隔几年标一个）
for _, row in scatter_data.iterrows():
    yr = int(row['year'])
    if yr in [1998, 2003, 2008, 2014, 2018, 2021, 2024]:
        ax.annotate(str(yr), (row['urbanization_rate_pct'], row['Q_V1K1']),
                    fontsize=6.5, ha='left', va='bottom',
                    xytext=(3, 3), textcoords='offset points')

ax.axhline(y=1, color=COLORS['ref'], linestyle='--', linewidth=0.8, alpha=0.7)
ax.text(67, 1.02, 'Q = 1', fontsize=7, color=COLORS['ref'], va='bottom')

# 色条
cbar = plt.colorbar(sc, ax=ax, shrink=0.7, pad=0.02)
cbar.set_label('年份', fontsize=8)

ax.set_xlabel('城镇化率 (%)')
ax.set_ylabel('Urban Q (V1/K1)')
ax.set_title('D. Urban Q 与城镇化率', fontweight='bold', loc='left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 保存
fig_path = OUTPUT_DIR / "04-figures/drafts/fig01_china_urban_q.png"
fig.savefig(fig_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"\n图表已保存: {fig_path}")

# ============================================================
# 9. 终端输出关键结果摘要
# ============================================================

print("\n" + "="*60)
print("Urban Q 关键结果摘要")
print("="*60)

key_years = [2000, 2005, 2010, 2015, 2020, 2024]
summary = df_q[df_q['year'].isin(key_years)][['year', 'Q_V1K1', 'Q_V1K2', 'Q_V2K1', 'Q_V2K2', 'MUQ_V1']].copy()
print(summary.to_string(index=False))

print(f"\n=== Urban Q 趋势特征 ===")
q_2000 = df_q[df_q['year'] == 2000]['Q_V1K1'].values[0]
q_2024 = df_q[df_q['year'] == 2024]['Q_V1K1'].values[0]
q_peak_year = df_q.loc[df_q['Q_V1K1'].idxmax(), 'year']
q_peak_val = df_q['Q_V1K1'].max()
print(f"  Q(V1/K1) 2000年: {q_2000:.3f}")
print(f"  Q(V1/K1) 峰值: {q_peak_val:.3f} ({int(q_peak_year)}年)")
print(f"  Q(V1/K1) 2024年: {q_2024:.3f}")
print(f"  2000→2024 变化: {(q_2024/q_2000 - 1)*100:.1f}%")

# MUQ 转负年份
muq_neg = df_q[df_q['MUQ_V1'] < 0]
if len(muq_neg) > 0:
    print(f"\n  MUQ(V1) 转负年份: {list(muq_neg['year'].astype(int).values)}")
    print(f"  → 含义: 新增投资导致资产价值净减少（价值毁灭）")

print("\n分析完成。")
