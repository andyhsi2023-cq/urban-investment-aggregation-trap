#!/usr/bin/env python3
"""
32_subgroup_analysis.py
目的：分收入组的倒U型估计、OCR标准化、关键国家对比、可视化
输入：global_kstar_ocr_uci.csv, global_urban_q_panel.csv
输出：
  - 02-data/processed/global_ocr_uci_normalized.csv
  - 03-analysis/models/subgroup_inverted_u.txt
  - 03-analysis/models/key_countries_comparison.txt
  - 04-figures/drafts/fig13_subgroup_analysis.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from scipy import stats
import statsmodels.api as sm
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 路径配置
# ============================================================
BASE = Path('/Users/andy/Desktop/Claude/urban-q-phase-transition')
DATA_PROC = BASE / '02-data' / 'processed'
MODELS = BASE / '03-analysis' / 'models'
FIGS = BASE / '04-figures' / 'drafts'

# ============================================================
# 数据加载
# ============================================================
print("=" * 70)
print("加载数据...")
df_kstar = pd.read_csv(DATA_PROC / 'global_kstar_ocr_uci.csv')
df_uq = pd.read_csv(DATA_PROC / 'global_urban_q_panel.csv')

# 合并两个面板（以 kstar 为主，补充 urban_q_panel 的额外变量）
df = df_kstar.copy()
# 从 urban_q_panel 获取 hc, total_pop, urban_q 等
merge_cols = ['country_code', 'year', 'hc', 'total_pop', 'urban_q',
              'gfcf_pct_gdp', 'gdp_current_usd', 'gdp_constant_2015',
              'urban_pop', 'ctfp', 'delta']
merge_avail = [c for c in merge_cols if c in df_uq.columns]
df = df.merge(df_uq[merge_avail], on=['country_code', 'year'], how='left')

# 收入组标准化命名
income_order = ['Low', 'Lower-middle', 'Upper-middle', 'High']
income_labels = {'Low': 'Low income', 'Lower-middle': 'Lower-middle income',
                 'Upper-middle': 'Upper-middle income', 'High': 'High income'}
df['income_label'] = df['income_group'].map(income_labels)

# 计算人口增长率
df = df.sort_values(['country_code', 'year'])
df['pop_growth'] = df.groupby('country_code')['total_pop'].pct_change() * 100

print(f"合并后面板: {df.shape[0]} 行, {df['country_code'].nunique()} 个国家")
print(f"收入组分布: {df.groupby('income_group')['country_code'].nunique().to_dict()}")

# ============================================================
# 分析 1：分收入组倒U型估计
# ============================================================
print("\n" + "=" * 70)
print("分析 1：分收入组倒U型回归")
print("=" * 70)

# 使用 dV_V 作为因变量，inv_gdp_ratio 作为自变量
# dV/V = a + b*(I/GDP) - c*(I/GDP)^2

results_text = []
results_text.append("=" * 70)
results_text.append("分收入组倒U型回归结果")
results_text.append("模型: dV/V = a + b*(I/GDP) - c*(I/GDP)^2")
results_text.append("=" * 70)

regression_results = {}

for ig in income_order:
    sub = df[(df['income_group'] == ig) &
             df['dV_V'].notna() &
             df['inv_gdp_ratio'].notna()].copy()

    # 剔除极端值 (1st/99th percentile)
    for col in ['dV_V', 'inv_gdp_ratio']:
        q01, q99 = sub[col].quantile([0.01, 0.99])
        sub = sub[(sub[col] >= q01) & (sub[col] <= q99)]

    if len(sub) < 30:
        print(f"  {ig}: 样本量不足 ({len(sub)}), 跳过")
        continue

    y = sub['dV_V'].values
    x = sub['inv_gdp_ratio'].values
    x2 = x ** 2
    X = sm.add_constant(np.column_stack([x, x2]))

    model = sm.OLS(y, X).fit(cov_type='HC3')  # 异方差稳健标准误

    a, b, c_neg = model.params  # c_neg 应为负值（即 -c）
    c = -c_neg  # 转换为正值

    # 计算 I*_opt 和 I_destroy
    if c > 0 and b > 0:
        I_opt = b / (2 * c)
        I_destroy = b / c
    else:
        I_opt = np.nan
        I_destroy = np.nan

    regression_results[ig] = {
        'a': a, 'b': b, 'c': c,
        'b_se': model.bse[1], 'c_se': model.bse[2],
        'b_p': model.pvalues[1], 'c_p': model.pvalues[2],
        'I_opt': I_opt, 'I_destroy': I_destroy,
        'n': len(sub), 'r2': model.rsquared,
        'r2_adj': model.rsquared_adj,
        'x_range': (x.min(), x.max()),
        'model': model
    }

    label = income_labels[ig]
    results_text.append(f"\n{'─' * 50}")
    results_text.append(f"收入组: {label}")
    results_text.append(f"{'─' * 50}")
    results_text.append(f"样本量: N = {len(sub)}")
    results_text.append(f"国家数: {sub['country_code'].nunique()}")
    results_text.append(f"年份范围: {sub['year'].min()}-{sub['year'].max()}")
    results_text.append(f"I/GDP 范围: [{x.min():.3f}, {x.max():.3f}]")
    results_text.append(f"")
    results_text.append(f"回归系数:")
    results_text.append(f"  a (截距)  = {a:+.6f}")
    results_text.append(f"  b (线性)  = {b:+.6f}  (SE={model.bse[1]:.6f}, p={model.pvalues[1]:.4f})")
    results_text.append(f"  -c (二次) = {c_neg:+.6f}  (SE={model.bse[2]:.6f}, p={model.pvalues[2]:.4f})")
    results_text.append(f"")
    results_text.append(f"关键阈值:")
    results_text.append(f"  I*_opt (最优投资率)     = {I_opt:.4f}" if not np.isnan(I_opt) else f"  I*_opt: 无法计算")
    results_text.append(f"  I_destroy (资本毁损率)  = {I_destroy:.4f}" if not np.isnan(I_destroy) else f"  I_destroy: 无法计算")
    results_text.append(f"")
    results_text.append(f"模型拟合:")
    results_text.append(f"  R-squared     = {model.rsquared:.4f}")
    results_text.append(f"  Adj R-squared = {model.rsquared_adj:.4f}")
    results_text.append(f"  F-statistic   = {model.fvalue:.2f} (p = {model.f_pvalue:.2e})")

    print(f"  {label}: N={len(sub)}, b={b:.4f}(p={model.pvalues[1]:.4f}), "
          f"c={c:.4f}(p={model.pvalues[2]:.4f}), I*_opt={I_opt:.4f}, I_destroy={I_destroy:.4f}")

# 汇总对比表
results_text.append(f"\n{'=' * 70}")
results_text.append("汇总对比表")
results_text.append(f"{'=' * 70}")
results_text.append(f"{'收入组':<25} {'N':>6} {'b':>10} {'c':>10} {'I*_opt':>10} {'I_destroy':>10} {'R2':>8}")
results_text.append(f"{'─' * 80}")
for ig in income_order:
    if ig in regression_results:
        r = regression_results[ig]
        label = income_labels[ig]
        sig_b = '***' if r['b_p'] < 0.001 else '**' if r['b_p'] < 0.01 else '*' if r['b_p'] < 0.05 else ''
        sig_c = '***' if r['c_p'] < 0.001 else '**' if r['c_p'] < 0.01 else '*' if r['c_p'] < 0.05 else ''
        results_text.append(
            f"{label:<25} {r['n']:>6} {r['b']:>9.4f}{sig_b:<3} {r['c']:>9.4f}{sig_c:<3} "
            f"{r['I_opt']:>10.4f} {r['I_destroy']:>10.4f} {r['r2']:>8.4f}"
        )

results_text.append(f"\n显著性: *** p<0.001, ** p<0.01, * p<0.05")

# 保存回归结果
with open(MODELS / 'subgroup_inverted_u.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results_text))
print(f"\n回归结果已保存: {MODELS / 'subgroup_inverted_u.txt'}")

# ============================================================
# 分析 2：OCR 标准化
# ============================================================
print("\n" + "=" * 70)
print("分析 2：OCR 标准化")
print("=" * 70)

# 方案 A：以高收入国家中位数为基准
high_income_ocr = df.loc[(df['income_group'] == 'High') & df['OCR'].notna(), 'OCR']
ocr_hi_median = high_income_ocr.median()
print(f"高收入国家 OCR 中位数: {ocr_hi_median:.4f}")

df['OCR_norm'] = df['OCR'] / ocr_hi_median

# 方案 B：组内百分位标准化
def pctile_within_group(group):
    """计算组内百分位"""
    valid = group.notna()
    result = pd.Series(np.nan, index=group.index)
    if valid.sum() > 1:
        result[valid] = group[valid].rank(pct=True)
    return result

df['OCR_pctile'] = df.groupby(['income_group', 'year'])['OCR'].transform(pctile_within_group)

# 如果组内年份样本太少，退回到仅按组分组
null_pct = df['OCR_pctile'].isna().mean()
if null_pct > 0.5:
    print("  按组+年份分组百分位缺失过多，改为仅按收入组分组")
    df['OCR_pctile'] = df.groupby('income_group')['OCR'].transform(pctile_within_group)

# 标准化后的 UCI
df['UCI_norm'] = df['Q'] / df['OCR_norm']

print(f"\nOCR_norm 统计:")
print(df.groupby('income_group')['OCR_norm'].describe()[['count', 'mean', '50%', 'std']].round(3))
print(f"\nUCI_norm 统计:")
print(df.groupby('income_group')['UCI_norm'].describe()[['count', 'mean', '50%', 'std']].round(3))

# 保存标准化面板
out_cols = ['country_code', 'country_name', 'region', 'income_group', 'year',
            'Q', 'OCR', 'UCI', 'K_star', 'OCR_norm', 'OCR_pctile', 'UCI_norm',
            'inv_gdp_ratio', 'dV_V', 'urban_rate', 'hc']
out_cols_avail = [c for c in out_cols if c in df.columns]
df_out = df[out_cols_avail].copy()
df_out.to_csv(DATA_PROC / 'global_ocr_uci_normalized.csv', index=False)
print(f"\n标准化面板已保存: {DATA_PROC / 'global_ocr_uci_normalized.csv'}")

# ============================================================
# 分析 3：关键国家深度对比
# ============================================================
print("\n" + "=" * 70)
print("分析 3：关键国家深度对比")
print("=" * 70)

# NGA/ETH 不在数据中，替换为 TZA/RWA
key_countries = ['CHN', 'JPN', 'KOR', 'USA', 'GBR', 'DEU', 'IND', 'BRA', 'TZA', 'RWA']
key_labels = {
    'CHN': 'China', 'JPN': 'Japan', 'KOR': 'Korea', 'USA': 'United States',
    'GBR': 'United Kingdom', 'DEU': 'Germany', 'IND': 'India', 'BRA': 'Brazil',
    'TZA': 'Tanzania', 'RWA': 'Rwanda'
}

# 使用最近可用年份（2019 前后）的数据
df_recent = df[(df['year'] >= 2015) & (df['year'] <= 2022)].copy()
df_key = df_recent[df_recent['country_code'].isin(key_countries)].copy()

# 每个国家取最近有 Q 值的年份
comp_rows = []
for cc in key_countries:
    sub = df_key[df_key['country_code'] == cc].sort_values('year', ascending=False)
    # 找有 Q 值的最近年份
    sub_q = sub[sub['Q'].notna()]
    if len(sub_q) > 0:
        row = sub_q.iloc[0]
    elif len(sub) > 0:
        row = sub.iloc[0]
    else:
        continue
    comp_rows.append({
        'Country': key_labels.get(cc, cc),
        'Code': cc,
        'Year': int(row['year']),
        'Income Group': row.get('income_group', ''),
        'Q': row.get('Q', np.nan),
        'OCR': row.get('OCR', np.nan),
        'OCR_norm': row.get('OCR_norm', np.nan),
        'UCI': row.get('UCI', np.nan),
        'UCI_norm': row.get('UCI_norm', np.nan),
        'I/GDP': row.get('inv_gdp_ratio', np.nan),
        'Urban Rate (%)': row.get('urban_rate', np.nan),
        'hc': row.get('hc', np.nan),
        'Pop Growth (%)': row.get('pop_growth', np.nan),
    })

comp_df = pd.DataFrame(comp_rows)
print(comp_df.to_string(index=False, float_format='%.3f'))

# 保存
comp_text = []
comp_text.append("=" * 100)
comp_text.append("关键国家深度对比 (Key Countries Comparison)")
comp_text.append("=" * 100)
comp_text.append(f"注: NGA/ETH 不在全球面板中，以 TZA/RWA 替代作为低收入非洲代表")
comp_text.append("")
comp_text.append(comp_df.to_string(index=False, float_format='%.4f'))
comp_text.append("")
comp_text.append("─" * 100)
comp_text.append("变量说明:")
comp_text.append("  Q        = Urban Q (城市化资产估值比)")
comp_text.append("  OCR      = Overcapacity Ratio (建设过剩比)")
comp_text.append("  OCR_norm = OCR / median(OCR|High income) (标准化建设过剩比)")
comp_text.append("  UCI      = Q / OCR (城市化质量指数)")
comp_text.append("  UCI_norm = Q / OCR_norm (标准化城市化质量指数)")
comp_text.append("  I/GDP    = 固定资本形成总额占GDP比重")
comp_text.append("  hc       = 人力资本指数 (Penn World Table)")

with open(MODELS / 'key_countries_comparison.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(comp_text))
print(f"\n对比表已保存: {MODELS / 'key_countries_comparison.txt'}")

# ============================================================
# 可视化：4 个子图
# ============================================================
print("\n" + "=" * 70)
print("生成图表...")
print("=" * 70)

# 设置字体和风格
plt.rcParams['font.family'] = ['Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
from matplotlib.patches import Patch

# 颜色方案
colors = {
    'Low': '#e74c3c',
    'Lower-middle': '#e67e22',
    'Upper-middle': '#3498db',
    'High': '#2ecc71'
}

fig = plt.figure(figsize=(18, 16))
fig.suptitle('Subgroup Analysis: Income Groups, OCR Normalization & Country Comparison',
             fontsize=15, fontweight='bold', y=0.98)

# ──────────────────────────────────────────────
# (a) 分收入组倒U型拟合曲线
# ──────────────────────────────────────────────
ax = fig.add_subplot(2, 2, 1)
for ig in income_order:
    if ig not in regression_results:
        continue
    r = regression_results[ig]
    sub = df[(df['income_group'] == ig) &
             df['dV_V'].notna() & df['inv_gdp_ratio'].notna()].copy()
    for col in ['dV_V', 'inv_gdp_ratio']:
        q01, q99 = sub[col].quantile([0.01, 0.99])
        sub = sub[(sub[col] >= q01) & (sub[col] <= q99)]

    label = income_labels[ig]
    # inv_gdp_ratio 是百分比形式（如 25 表示 25%），转换为小数
    ax.scatter(sub['inv_gdp_ratio'] / 100, sub['dV_V'],
               alpha=0.06, s=6, color=colors[ig], rasterized=True)

    # 拟合曲线（x 轴用百分比原值拟合，显示时除以 100）
    x_fit = np.linspace(r['x_range'][0], r['x_range'][1], 200)
    m = r['model']
    y_fit = m.params[0] + m.params[1] * x_fit + m.params[2] * x_fit ** 2
    ax.plot(x_fit / 100, y_fit, color=colors[ig], linewidth=2.5,
            label=f"{label} (n={r['n']})")

    # 标记 I*_opt
    if not np.isnan(r['I_opt']) and r['x_range'][0] <= r['I_opt'] <= r['x_range'][1]:
        y_opt = m.params[0] + m.params[1] * r['I_opt'] + m.params[2] * r['I_opt'] ** 2
        ax.axvline(r['I_opt'] / 100, color=colors[ig], linestyle=':', alpha=0.6, linewidth=1.2)
        ax.annotate(f"I*={r['I_opt']:.0f}%", xy=(r['I_opt']/100, y_opt),
                    fontsize=7, color=colors[ig], ha='left')

ax.set_xlabel('Investment / GDP Ratio', fontsize=11)
ax.set_ylabel('$\\Delta V / V$ (Urban Value Growth Rate)', fontsize=11)
ax.set_title('(a) Inverted-U by Income Group', fontsize=12, fontweight='bold')
ax.legend(fontsize=8, loc='upper right')
ax.axhline(0, color='grey', linewidth=0.5, linestyle='--')
ax.set_xlim(0, 0.6)
ax.set_ylim(-0.5, 0.8)

# ──────────────────────────────────────────────
# (b) OCR_norm 按收入组的箱线图
# ──────────────────────────────────────────────
ax = fig.add_subplot(2, 2, 2)
box_data = []
box_labels_list = []
box_colors_list = []
for ig in income_order:
    vals = df.loc[(df['income_group'] == ig) & df['OCR_norm'].notna(), 'OCR_norm']
    # 截断极端值便于可视化
    vals = vals[vals <= vals.quantile(0.95)]
    box_data.append(vals.values)
    box_labels_list.append(income_labels[ig].replace(' income', ''))
    box_colors_list.append(colors[ig])

bp = ax.boxplot(box_data, labels=box_labels_list, patch_artist=True,
                medianprops=dict(color='black', linewidth=1.5),
                flierprops=dict(marker='.', markersize=2, alpha=0.3),
                widths=0.6)
for patch, color in zip(bp['boxes'], box_colors_list):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

ax.axhline(1.0, color='red', linestyle='--', linewidth=1, label='High-income median (=1.0)')
ax.set_ylabel('OCR$_{norm}$ (relative to high-income median)', fontsize=11)
ax.set_title('(b) Normalized OCR by Income Group', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.tick_params(axis='x', rotation=15)

# 添加中位数标注
for i, ig in enumerate(income_order):
    med = np.median(box_data[i])
    ax.text(i + 1, med + 0.15, f'{med:.2f}', ha='center', fontsize=8, fontweight='bold')

# ──────────────────────────────────────────────
# (c) UCI_norm 全球排名 (前15 + 后15)
# ──────────────────────────────────────────────
ax = fig.add_subplot(2, 2, 3)

# 取有 UCI_norm 的最新年份数据
df_with_uci = df[df['UCI_norm'].notna()].copy()
df_with_uci = df_with_uci.sort_values('year', ascending=False).drop_duplicates('country_code')
df_rank = df_with_uci[['country_code', 'country_name', 'income_group', 'UCI_norm', 'year']].copy()
df_rank = df_rank.sort_values('UCI_norm', ascending=True).reset_index(drop=True)

print(f"  UCI_norm 排名: {len(df_rank)} 个国家, UCI_norm 范围: {df_rank['UCI_norm'].min():.3f} - {df_rank['UCI_norm'].max():.3f}")

n_show = 15
top = df_rank.tail(n_show).copy()
bottom = df_rank.head(n_show).copy()
show_df = pd.concat([bottom, top]).reset_index(drop=True)

# 为条形图着色
bar_colors = [colors.get(ig, 'grey') for ig in show_df['income_group']]
y_pos = np.arange(len(show_df))
bars = ax.barh(y_pos, show_df['UCI_norm'], color=bar_colors, alpha=0.7, height=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels([f"{row['country_name']}" for _, row in show_df.iterrows()], fontsize=7)

# 在条形末端添加数值标签
max_val = show_df['UCI_norm'].max()
for i, (val, bar) in enumerate(zip(show_df['UCI_norm'], bars)):
    ax.text(val + max_val * 0.01, i, f'{val:.2f}', va='center', fontsize=6)

ax.axvline(1.0, color='grey', linestyle='--', linewidth=0.8, alpha=0.5, label='UCI$_{norm}$ = 1')

# 分隔线
ax.axhline(n_show - 0.5, color='black', linewidth=1.2, linestyle='-')
ax.text(0.02, 0.37, 'Bottom 15', transform=ax.transAxes,
        fontsize=9, fontweight='bold', style='italic', color='#555')
ax.text(0.02, 0.63, 'Top 15', transform=ax.transAxes,
        fontsize=9, fontweight='bold', style='italic', color='#555')

ax.set_xlabel('UCI$_{norm}$ (Q / OCR$_{norm}$)', fontsize=11)
ax.set_title('(c) UCI$_{norm}$ Global Ranking (Latest Available)', fontsize=12, fontweight='bold')
ax.set_xlim(0, max_val * 1.15)

legend_patches = [Patch(facecolor=colors[ig], alpha=0.7, label=income_labels[ig])
                  for ig in income_order]
ax.legend(handles=legend_patches, fontsize=7, loc='lower right')

# ──────────────────────────────────────────────
# (d) 关键国家雷达图（中国、日本、美国、印度）
# ──────────────────────────────────────────────
ax_radar = fig.add_subplot(2, 2, 4, projection='polar')

radar_countries = ['CHN', 'JPN', 'USA', 'IND']
radar_labels_map = {'CHN': 'China', 'JPN': 'Japan', 'USA': 'United States', 'IND': 'India'}
radar_colors = {'CHN': '#e74c3c', 'JPN': '#3498db', 'USA': '#2ecc71', 'IND': '#e67e22'}

# 指标
metrics = ['Q', 'OCR_norm', 'UCI_norm', 'I/GDP', 'Urban Rate (%)', 'hc']
metric_labels = ['Q', 'OCR (norm)', 'UCI (norm)', 'I/GDP', 'Urban Rate', 'Human Capital']

# 从 comp_df 提取数据
radar_data = {}
for cc in radar_countries:
    row = comp_df[comp_df['Code'] == cc]
    if len(row) == 0:
        continue
    row = row.iloc[0]
    vals = [row.get(m, np.nan) for m in metrics]
    radar_data[cc] = vals

# 标准化到 0-1 范围（添加 0.1 下限保证可见性）
all_vals = np.array(list(radar_data.values()))
mins = np.nanmin(all_vals, axis=0)
maxs = np.nanmax(all_vals, axis=0)
ranges = maxs - mins
ranges[ranges == 0] = 1

N_met = len(metrics)
angles = np.linspace(0, 2 * np.pi, N_met, endpoint=False).tolist()
angles += angles[:1]

for cc in radar_countries:
    if cc not in radar_data:
        continue
    vals = radar_data[cc]
    vals_norm = [(v - mn) / rng * 0.8 + 0.1 if not np.isnan(v) else 0.1
                 for v, mn, rng in zip(vals, mins, ranges)]
    vals_norm += vals_norm[:1]
    ax_radar.plot(angles, vals_norm, linewidth=2.2, color=radar_colors[cc],
                  label=radar_labels_map[cc], marker='o', markersize=4)
    ax_radar.fill(angles, vals_norm, alpha=0.08, color=radar_colors[cc])

ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(metric_labels, fontsize=9)
ax_radar.set_ylim(0, 1.05)
ax_radar.set_yticks([0.25, 0.5, 0.75, 1.0])
ax_radar.set_yticklabels(['25%', '50%', '75%', 'max'], fontsize=6, color='grey')
ax_radar.set_title('(d) Key Countries Radar (2019)', fontsize=12, fontweight='bold', pad=25)
ax_radar.legend(fontsize=9, loc='upper right', bbox_to_anchor=(1.35, 1.15))

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIGS / 'fig13_subgroup_analysis.png', dpi=200, bbox_inches='tight')
print(f"\n图表已保存: {FIGS / 'fig13_subgroup_analysis.png'}")

# ============================================================
# 汇总输出
# ============================================================
print("\n" + "=" * 70)
print("全部完成!")
print("=" * 70)
print(f"输出文件:")
print(f"  1. {DATA_PROC / 'global_ocr_uci_normalized.csv'}")
print(f"  2. {MODELS / 'subgroup_inverted_u.txt'}")
print(f"  3. {MODELS / 'key_countries_comparison.txt'}")
print(f"  4. {FIGS / 'fig13_subgroup_analysis.png'}")
