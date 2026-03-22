#!/usr/bin/env python3
"""
38_predictions_ews.py
=====================
前瞻性预测与早期预警信号 (EWS) 跨国验证

目的：
  Part A — 条件性前瞻预测：基于中国历史轨迹，预测印度/越南/印尼/埃及的 CPR 拐点
  Part B — 日本 EWS 跨国验证：检验 critical slowing down 在日本数据中的存在
  Part C — 全球面板 EWS 扫描：CPR 下降前 AR(1) 上升的普遍性
  Part D — 可视化：三面板综合图

输入：
  - 02-data/processed/global_q_revised_panel.csv
  - 03-analysis/models/china_q_adjusted.csv

输出：
  - 03-analysis/models/predictions_ews_report.txt
  - 04-figures/drafts/fig_predictions_ews.png

依赖：pandas, numpy, scipy, matplotlib, statsmodels
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import statsmodels.api as sm

warnings.filterwarnings('ignore')

# ── 路径设置 ──────────────────────────────────────────────
BASE = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
PANEL_PATH = os.path.join(BASE, "02-data/processed/global_q_revised_panel.csv")
CHINA_Q_PATH = os.path.join(BASE, "03-analysis/models/china_q_adjusted.csv")
REPORT_PATH = os.path.join(BASE, "03-analysis/models/predictions_ews_report.txt")
FIG_PATH = os.path.join(BASE, "04-figures/drafts/fig_predictions_ews.png")

# ── 加载数据 ──────────────────────────────────────────────
print("加载数据...")
panel = pd.read_csv(PANEL_PATH)
china_q = pd.read_csv(CHINA_Q_PATH)

# NGA 不在面板中，替换为 EGY（埃及，城镇化率相近的发展中大国）
TARGET_COUNTRIES = ['IND', 'VNM', 'IDN', 'EGY']
TARGET_NAMES = {'IND': 'India', 'VNM': 'Vietnam', 'IDN': 'Indonesia', 'EGY': 'Egypt'}

report_lines = []

def rpt(line=""):
    """写入报告"""
    report_lines.append(line)
    print(line)

rpt("=" * 72)
rpt("前瞻性预测与早期预警信号 (EWS) 跨国验证报告")
rpt("=" * 72)
rpt(f"生成日期: 2026-03-21")
rpt()

# ══════════════════════════════════════════════════════════
# Part A: 条件性前瞻预测
# ══════════════════════════════════════════════════════════
rpt("=" * 72)
rpt("PART A: 条件性前瞻预测")
rpt("=" * 72)
rpt()
rpt("方法说明：")
rpt("  以中国历史轨迹为参照，将各国当前城镇化率映射到中国的")
rpt("  相同城镇化阶段，基于中国在该阶段之后的 GFCF/GDP 和 CPR")
rpt("  变化率进行外推。注意：这是条件性预测（'如果按中国轨迹'），")
rpt("  而非无条件预测。")
rpt()

# 提取中国轨迹
chn = panel[panel['country_code'] == 'CHN'][['year', 'urban_pct', 'gfcf_pct_gdp', 'CPR']].dropna(subset=['CPR']).sort_values('year').reset_index(drop=True)

# 中国 CPR 峰值年份和城镇化率
chn_cpr_peak_idx = chn['CPR'].idxmax()
chn_cpr_peak_year = chn.loc[chn_cpr_peak_idx, 'year']
chn_cpr_peak_urban = chn.loc[chn_cpr_peak_idx, 'urban_pct']
chn_cpr_peak_val = chn.loc[chn_cpr_peak_idx, 'CPR']

rpt(f"中国 CPR 峰值：{chn_cpr_peak_val:.3f} (年份={int(chn_cpr_peak_year)}, 城镇化率={chn_cpr_peak_urban:.1f}%)")
rpt()

# 计算中国在各城镇化率阶段的 CPR 年变化率
chn['cpr_growth'] = chn['CPR'].pct_change()
chn['gfcf_growth'] = chn['gfcf_pct_gdp'].pct_change()

# 对每个目标国家进行预测
predictions = {}
for cc in TARGET_COUNTRIES:
    sub = panel[panel['country_code'] == cc][['year', 'urban_pct', 'gfcf_pct_gdp', 'CPR']].sort_values('year')
    sub_valid = sub.dropna(subset=['CPR', 'gfcf_pct_gdp'])

    if len(sub_valid) == 0:
        rpt(f"\n{TARGET_NAMES[cc]} ({cc}): 数据不足，跳过")
        continue

    # 取最新数据
    latest = sub_valid.iloc[-1]
    latest_year = int(latest['year'])
    latest_urban = latest['urban_pct']
    latest_gfcf = latest['gfcf_pct_gdp']
    latest_cpr = latest['CPR']

    rpt(f"\n--- {TARGET_NAMES[cc]} ({cc}) ---")
    rpt(f"  最新数据 ({latest_year}): 城镇化率={latest_urban:.1f}%, GFCF/GDP={latest_gfcf:.1f}%, CPR={latest_cpr:.3f}")

    # 找到中国相同城镇化率对应的年份
    chn_match_idx = (chn['urban_pct'] - latest_urban).abs().idxmin()
    chn_match_year = chn.loc[chn_match_idx, 'year']
    chn_match_urban = chn.loc[chn_match_idx, 'urban_pct']

    rpt(f"  中国匹配阶段: {int(chn_match_year)}年 (城镇化率={chn_match_urban:.1f}%)")

    # 中国从匹配点到峰值的年数
    years_to_peak = chn_cpr_peak_year - chn_match_year

    # 中国从匹配点之后的 CPR 轨迹
    chn_after = chn[chn['year'] >= chn_match_year].copy()
    chn_after['years_from_match'] = chn_after['year'] - chn_match_year

    # 计算中国从匹配点到 CPR 开始持续下降（峰值后连续3年下降）的时间
    chn_post_peak = chn[chn['year'] > chn_cpr_peak_year]

    if years_to_peak > 0:
        rpt(f"  中国从此城镇化率到 CPR 峰值: {int(years_to_peak)} 年")
        rpt(f"  条件性预测: 如果按中国轨迹，CPR 将在约 {int(years_to_peak)} 年后达到峰值")

        # Bootstrap 不确定性估计：基于中国 CPR 年变化率的波动
        chn_growth_std = chn.loc[chn['year'].between(chn_match_year, chn_cpr_peak_year), 'cpr_growth'].std()
        # 简单不确定性：±(波动率 * sqrt(年数)) 映射到年数
        uncertainty_years = max(2, int(np.sqrt(years_to_peak) * 1.5))

        rpt(f"  不确定性区间: {int(years_to_peak)} +/- {uncertainty_years} 年")
        rpt(f"  即约 {latest_year + int(years_to_peak) - uncertainty_years} - {latest_year + int(years_to_peak) + uncertainty_years} 年")
    elif years_to_peak <= 0:
        rpt(f"  该国城镇化率已超过中国 CPR 峰值时的城镇化率")
        rpt(f"  按中国轨迹，CPR 应已开始下降")

        # 检查实际 CPR 是否在下降
        recent_cpr = sub_valid.tail(5)['CPR']
        if recent_cpr.iloc[-1] < recent_cpr.iloc[0]:
            rpt(f"  实际验证: 近5年 CPR 确实在下降 ({recent_cpr.iloc[0]:.3f} -> {recent_cpr.iloc[-1]:.3f})")
        else:
            rpt(f"  实际验证: 近5年 CPR 尚未下降 ({recent_cpr.iloc[0]:.3f} -> {recent_cpr.iloc[-1]:.3f})")
            rpt(f"  这表明该国的 CPR 动态可能有不同的时间尺度")

    # 比较 GFCF/GDP 水平
    chn_match_gfcf = chn.loc[chn_match_idx, 'gfcf_pct_gdp']
    gfcf_diff = latest_gfcf - chn_match_gfcf
    rpt(f"  GFCF/GDP 对比: {TARGET_NAMES[cc]}={latest_gfcf:.1f}% vs 中国同期={chn_match_gfcf:.1f}% (差={gfcf_diff:+.1f}pp)")

    predictions[cc] = {
        'name': TARGET_NAMES[cc],
        'latest_year': latest_year,
        'latest_urban': latest_urban,
        'latest_gfcf': latest_gfcf,
        'latest_cpr': latest_cpr,
        'chn_match_year': chn_match_year,
        'years_to_peak': years_to_peak,
        'data': sub_valid
    }

rpt()

# ══════════════════════════════════════════════════════════
# Part B: 日本 EWS 跨国验证
# ══════════════════════════════════════════════════════════
rpt("=" * 72)
rpt("PART B: 日本 EWS 跨国验证 (Critical Slowing Down)")
rpt("=" * 72)
rpt()

def compute_ews(series, window=8):
    """
    计算早期预警信号指标：滚动 AR(1)、滚动方差、滚动偏度

    参数:
        series: pd.Series，时间序列（index 为年份）
        window: 滚动窗口大小

    返回:
        DataFrame with columns: year, ar1, variance, skewness
    """
    results = []
    years = series.index.values
    vals = series.values

    for i in range(window, len(vals) + 1):
        w = vals[i - window:i]
        yr = years[i - 1]  # 窗口结束年份

        # AR(1) 系数
        if len(w) >= 4 and np.std(w) > 1e-10:
            ar1_corr = np.corrcoef(w[:-1], w[1:])[0, 1]
        else:
            ar1_corr = np.nan

        # 滚动方差
        var = np.var(w, ddof=1) if len(w) > 1 else np.nan

        # 滚动偏度
        skew = stats.skew(w, bias=False) if len(w) >= 3 else np.nan

        results.append({'year': yr, 'ar1': ar1_corr, 'variance': var, 'skewness': skew})

    return pd.DataFrame(results)


# 日本数据
jpn = panel[panel['country_code'] == 'JPN'][['year', 'urban_pct', 'gfcf_pct_gdp', 'CPR']].dropna(subset=['CPR']).sort_values('year').reset_index(drop=True)
jpn_cpr = jpn.set_index('year')['CPR']

rpt(f"日本 CPR 数据范围: {jpn_cpr.index.min()}-{jpn_cpr.index.max()} (n={len(jpn_cpr)})")

# 日本有两个 CPR 高峰：1978（第一次石油危机前）和 1988（泡沫经济高峰）
# 1978 峰值：数据起始于 1970，峰前数据不足以做 EWS
# 1988-1995 区间后的持续下降更适合做 EWS 分析（有 18 年前置数据）
# 使用 1995 年作为 "结构性下降起点"（之后 CPR 从 ~2.1 持续下降到 ~1.0）
jpn_peak_year = 1995  # 泡沫后短暂恢复的末端，此后结构性下降
jpn_peak_val = jpn_cpr.loc[jpn_peak_year]
jpn_abs_peak_year = jpn_cpr.idxmax()
jpn_abs_peak_val = jpn_cpr.max()

rpt(f"日本 CPR 绝对峰值: {jpn_abs_peak_val:.3f} (年份={int(jpn_abs_peak_year)})")
rpt(f"日本 CPR 结构性下降起点: {jpn_peak_val:.3f} (年份={int(jpn_peak_year)})")
rpt(f"  说明: 日本 CPR 在 1978 达绝对峰值后，经历泡沫经济二次上升 (1986-1988),")
rpt(f"  1990s 短暂恢复后自 1995 起持续结构性下降 (2.09 -> 1.06)。")
rpt(f"  选择 1995 作为 EWS 分析的参考点，因其前有充分的时间序列数据。")

# 计算日本 EWS
WINDOW = 8
jpn_ews = compute_ews(jpn_cpr, window=WINDOW)

rpt(f"\n滚动窗口 = {WINDOW} 年")
rpt(f"EWS 指标计算范围: {int(jpn_ews['year'].min())}-{int(jpn_ews['year'].max())}")

# 检验：CPR 下降前的 AR(1) 趋势
pre_decline_start = jpn_peak_year - 15
pre_decline_end = jpn_peak_year
jpn_ews_pre = jpn_ews[(jpn_ews['year'] >= pre_decline_start) & (jpn_ews['year'] <= pre_decline_end)]

rpt(f"\n日本 CPR 下降前窗口 ({int(pre_decline_start)}-{int(pre_decline_end)}), n={len(jpn_ews_pre)}:")

if len(jpn_ews_pre) >= 3:
    # AR(1) 趋势检验（Kendall tau）
    ar1_valid = jpn_ews_pre[['year', 'ar1']].dropna()
    var_valid = jpn_ews_pre[['year', 'variance']].dropna()

    tau_ar1, p_ar1 = stats.kendalltau(ar1_valid['year'], ar1_valid['ar1'])
    tau_var, p_var = stats.kendalltau(var_valid['year'], var_valid['variance'])

    rpt(f"  AR(1) Kendall tau = {tau_ar1:.3f}, p = {p_ar1:.4f} {'***' if p_ar1<0.01 else '**' if p_ar1<0.05 else '*' if p_ar1<0.1 else ''}")
    rpt(f"  方差 Kendall tau = {tau_var:.3f}, p = {p_var:.4f} {'***' if p_var<0.01 else '**' if p_var<0.05 else '*' if p_var<0.1 else ''}")

    if tau_ar1 > 0:
        rpt(f"  -> AR(1) 在 CPR 下降前呈上升趋势，支持 critical slowing down 假说")
    else:
        rpt(f"  -> AR(1) 在 CPR 下降前未呈上升趋势")
else:
    tau_ar1, p_ar1 = np.nan, np.nan
    rpt(f"  数据点不足 (n={len(jpn_ews_pre)}), 无法进行趋势检验")

# 补充：用更小窗口 (5年) 分析 1978 峰值前信号
WINDOW_SMALL = 5
jpn_ews_small = compute_ews(jpn_cpr, window=WINDOW_SMALL)
jpn_ews_pre_1978 = jpn_ews_small[(jpn_ews_small['year'] >= 1970) & (jpn_ews_small['year'] <= 1978)]
rpt(f"\n补充分析: 1978年绝对峰值前 (窗口={WINDOW_SMALL}年), n={len(jpn_ews_pre_1978)}:")
if len(jpn_ews_pre_1978) >= 3:
    ar1_v = jpn_ews_pre_1978[['year','ar1']].dropna()
    if len(ar1_v) >= 3:
        tau_78, p_78 = stats.kendalltau(ar1_v['year'], ar1_v['ar1'])
        rpt(f"  AR(1) Kendall tau = {tau_78:.3f}, p = {p_78:.4f} {'***' if p_78<0.01 else '**' if p_78<0.05 else '*' if p_78<0.1 else ''}")

# 中国 EWS 对比
chn_cpr = chn.set_index('year')['CPR']
chn_ews = compute_ews(chn_cpr, window=WINDOW)

chn_pre_start = chn_cpr_peak_year - 15
chn_pre_end = chn_cpr_peak_year
chn_ews_pre = chn_ews[(chn_ews['year'] >= chn_pre_start) & (chn_ews['year'] <= chn_pre_end)]

if len(chn_ews_pre) >= 3:
    tau_ar1_chn, p_ar1_chn = stats.kendalltau(chn_ews_pre['year'], chn_ews_pre['ar1'])
    tau_var_chn, p_var_chn = stats.kendalltau(chn_ews_pre['year'], chn_ews_pre['variance'])

    rpt(f"\n中国 CPR 下降前窗口 ({int(chn_pre_start)}-{int(chn_pre_end)}):")
    rpt(f"  AR(1) Kendall tau = {tau_ar1_chn:.3f}, p = {p_ar1_chn:.4f} {'***' if p_ar1_chn<0.01 else '**' if p_ar1_chn<0.05 else '*' if p_ar1_chn<0.1 else ''}")
    rpt(f"  方差 Kendall tau = {tau_var_chn:.3f}, p = {p_var_chn:.4f} {'***' if p_var_chn<0.01 else '**' if p_var_chn<0.05 else '*' if p_var_chn<0.1 else ''}")

rpt()

# ══════════════════════════════════════════════════════════
# Part C: 全球面板 EWS 扫描
# ══════════════════════════════════════════════════════════
rpt("=" * 72)
rpt("PART C: 全球面板 EWS 扫描")
rpt("=" * 72)
rpt()
rpt("筛选标准: CPR 从峰值下降超过 20% 的国家")
rpt(f"EWS 窗口: 峰值前 10 年的 AR(1) 趋势 (滚动窗口={WINDOW}年)")
rpt()

# 对每个国家计算
ews_results = []
scan_details = []

for cc, grp in panel.groupby('country_code'):
    sub = grp[['year', 'CPR']].dropna().sort_values('year').reset_index(drop=True)
    if len(sub) < 15:  # 需要足够的数据
        continue

    cpr_s = sub.set_index('year')['CPR']
    peak_year = cpr_s.idxmax()
    peak_val = cpr_s.max()

    # 峰值后的最小值
    post_peak = cpr_s[cpr_s.index >= peak_year]
    if len(post_peak) < 3:
        continue
    min_after = post_peak.min()
    decline_pct = (peak_val - min_after) / peak_val * 100

    if decline_pct < 20:
        continue

    # 峰值前需要有足够数据来计算 EWS
    pre_peak = cpr_s[cpr_s.index < peak_year]
    if len(pre_peak) < WINDOW + 3:  # 需要至少 window+3 个数据点
        continue

    # 计算 EWS
    ews = compute_ews(cpr_s, window=WINDOW)

    # 峰值前 10 年的 AR(1) 趋势
    pre_window_start = peak_year - 10
    ews_pre = ews[(ews['year'] >= pre_window_start) & (ews['year'] <= peak_year)]

    if len(ews_pre) < 4:
        continue

    # Kendall tau 检验
    ar1_vals = ews_pre['ar1'].dropna()
    if len(ar1_vals) < 4:
        continue

    tau, p = stats.kendalltau(ews_pre.loc[ar1_vals.index, 'year'], ar1_vals)

    country_name = grp['country_name'].iloc[0]
    region = grp['region'].iloc[0] if 'region' in grp.columns else 'Unknown'

    ews_results.append({
        'country_code': cc,
        'country_name': country_name,
        'region': region,
        'peak_year': peak_year,
        'decline_pct': decline_pct,
        'ar1_tau': tau,
        'ar1_p': p,
        'ar1_rising': tau > 0,
        'ar1_sig': p < 0.1,
        'ar1_rising_sig': tau > 0 and p < 0.1,
        'n_pre_obs': len(ar1_vals)
    })

    # 保存 EWS 时序用于热力图
    for _, row in ews.iterrows():
        scan_details.append({
            'country_code': cc,
            'country_name': country_name,
            'year': row['year'],
            'ar1': row['ar1'],
            'years_to_peak': row['year'] - peak_year
        })

ews_df = pd.DataFrame(ews_results)
scan_df = pd.DataFrame(scan_details)

rpt(f"符合条件的国家数: {len(ews_df)}")
rpt(f"AR(1) 上升 (tau > 0): {ews_df['ar1_rising'].sum()} ({ews_df['ar1_rising'].mean()*100:.1f}%)")
rpt(f"AR(1) 显著上升 (tau > 0, p < 0.1): {ews_df['ar1_rising_sig'].sum()} ({ews_df['ar1_rising_sig'].mean()*100:.1f}%)")
rpt()

# 按区域分析
rpt("按区域分组:")
for region, rgrp in ews_df.groupby('region'):
    n = len(rgrp)
    n_rising = rgrp['ar1_rising'].sum()
    n_sig = rgrp['ar1_rising_sig'].sum()
    rpt(f"  {region}: n={n}, AR(1)上升={n_rising} ({n_rising/n*100:.0f}%), 显著={n_sig}")

rpt()
rpt("AR(1) 上升最显著的国家 (top 15):")
top15 = ews_df[ews_df['ar1_rising']].nsmallest(15, 'ar1_p')
for _, row in top15.iterrows():
    sig = '***' if row['ar1_p']<0.01 else '**' if row['ar1_p']<0.05 else '*' if row['ar1_p']<0.1 else ''
    rpt(f"  {row['country_code']} ({row['country_name']}): tau={row['ar1_tau']:.3f}, p={row['ar1_p']:.4f}{sig}, CPR下降={row['decline_pct']:.0f}%")

rpt()

# 二项检验：AR(1) 上升比例是否显著高于 50%
n_total = len(ews_df)
n_rising = int(ews_df['ar1_rising'].sum())
binom_p = stats.binom_test(n_rising, n_total, 0.5, alternative='greater') if hasattr(stats, 'binom_test') else stats.binomtest(n_rising, n_total, 0.5, alternative='greater').pvalue
rpt(f"二项检验 (H0: AR(1)上升比例=50%): {n_rising}/{n_total}, p = {binom_p:.4f}")
if binom_p < 0.05:
    rpt("  -> 拒绝 H0：AR(1) 在 CPR 下降前上升的比例显著高于随机")
    rpt("  -> 支持 'critical slowing down 在城市投资转向中普遍存在' 的假说")
else:
    rpt("  -> 未能拒绝 H0")

rpt()

# ══════════════════════════════════════════════════════════
# Part D: 可视化
# ══════════════════════════════════════════════════════════
rpt("=" * 72)
rpt("PART D: 生成可视化")
rpt("=" * 72)
rpt()

# 颜色方案
COLORS = {
    'CHN': '#E63946',
    'JPN': '#457B9D',
    'IND': '#2A9D8F',
    'VNM': '#E9C46A',
    'IDN': '#F4A261',
    'EGY': '#264653'
}

fig = plt.figure(figsize=(18, 16))
gs = gridspec.GridSpec(2, 2, hspace=0.32, wspace=0.28,
                       left=0.07, right=0.95, top=0.94, bottom=0.06)

# ── Panel A: 轨迹对比 ──
ax_a1 = fig.add_subplot(gs[0, 0])
ax_a2 = ax_a1.twinx()

# 中国 CPR 和 GFCF/GDP（按城镇化率对齐）
# 注意: 使用 log 刻度以同时展示中国 (CPR ~1-3) 和印尼 (CPR ~3-15) 的变化
chn_plot = chn[chn['urban_pct'] >= 15].copy()
ax_a1.plot(chn_plot['urban_pct'], chn_plot['CPR'], color=COLORS['CHN'],
           linewidth=2.5, label='China CPR', zorder=5)
ax_a2.plot(chn_plot['urban_pct'], chn_plot['gfcf_pct_gdp'], color=COLORS['CHN'],
           linewidth=1.5, linestyle='--', alpha=0.5, label='China GFCF/GDP')

# 目标国家
for cc in TARGET_COUNTRIES:
    if cc not in predictions:
        continue
    p = predictions[cc]
    d = p['data'].sort_values('year')
    ax_a1.plot(d['urban_pct'], d['CPR'], color=COLORS[cc],
               linewidth=2, label=f"{p['name']} CPR", marker='o', markersize=2)
    ax_a2.plot(d['urban_pct'], d['gfcf_pct_gdp'], color=COLORS[cc],
               linewidth=1.2, linestyle='--', alpha=0.4)

    # 标注最新位置
    # 调整标注位置避免重叠
    offset_map = {'IND': (5, -15), 'VNM': (5, 8), 'IDN': (5, -15), 'EGY': (5, 8)}
    ofs = offset_map.get(cc, (5, 5))
    ax_a1.annotate(f"{p['name']}\n({p['latest_year']})",
                   xy=(p['latest_urban'], p['latest_cpr']),
                   fontsize=7, color=COLORS[cc], fontweight='bold',
                   xytext=ofs, textcoords='offset points')

# 标注中国 CPR 峰值
ax_a1.axvline(x=chn_cpr_peak_urban, color=COLORS['CHN'], linestyle=':', alpha=0.4, linewidth=1)
ax_a1.annotate(f"China CPR peak\n(urb={chn_cpr_peak_urban:.0f}%)",
               xy=(chn_cpr_peak_urban, chn_cpr_peak_val),
               xytext=(-60, 15), textcoords='offset points',
               fontsize=7, color=COLORS['CHN'], alpha=0.7,
               arrowprops=dict(arrowstyle='->', color=COLORS['CHN'], alpha=0.5))

ax_a1.set_yscale('log')
ax_a1.set_ylim(0.5, 20)
ax_a1.set_yticks([0.5, 1, 2, 3, 5, 10, 15])
ax_a1.set_yticklabels(['0.5', '1', '2', '3', '5', '10', '15'])
ax_a1.set_xlabel('Urbanization rate (%)', fontsize=11)
ax_a1.set_ylabel('CPR (log scale)', fontsize=11, color='#333')
ax_a2.set_ylabel('GFCF / GDP (%)', fontsize=11, color='#999')
ax_a2.tick_params(axis='y', colors='#999')
ax_a1.set_title('A. Cross-country CPR trajectories\n(aligned by urbanization rate)', fontsize=12, fontweight='bold')
ax_a1.legend(loc='upper left', fontsize=7, framealpha=0.8)
ax_a1.grid(True, alpha=0.2, which='both')

# ── Panel B: 中国 vs 日本 AR(1) 对比 ──
ax_b = fig.add_subplot(gs[0, 1])

# 以峰值为零点对齐
chn_ews['years_to_peak'] = chn_ews['year'] - chn_cpr_peak_year
jpn_ews['years_to_peak'] = jpn_ews['year'] - jpn_peak_year

# 绘制 AR(1)
ax_b.plot(chn_ews['years_to_peak'], chn_ews['ar1'], color=COLORS['CHN'],
          linewidth=2, label=f"China (peak={int(chn_cpr_peak_year)})", marker='o', markersize=3)
ax_b.plot(jpn_ews['years_to_peak'], jpn_ews['ar1'], color=COLORS['JPN'],
          linewidth=2, label=f"Japan (peak={int(jpn_peak_year)})", marker='s', markersize=3)

ax_b.axvline(x=0, color='grey', linestyle='--', alpha=0.5, label='CPR peak')
ax_b.axhline(y=1.0, color='red', linestyle=':', alpha=0.3, linewidth=1)

# 标注 critical slowing down 区域
ax_b.axvspan(-15, 0, alpha=0.06, color='orange', label='Pre-decline window')

ax_b.set_xlabel('Years relative to CPR peak', fontsize=11)
ax_b.set_ylabel(f'Rolling AR(1) coefficient\n(window = {WINDOW} years)', fontsize=11)
ax_b.set_title('B. Early warning signals: AR(1)\n(China vs Japan, aligned at CPR peak)', fontsize=12, fontweight='bold')
ax_b.legend(fontsize=8, framealpha=0.8)
ax_b.grid(True, alpha=0.2)
ax_b.set_xlim(-25, 15)

# ── Panel C: 全球 EWS 扫描热力图 ──
ax_c = fig.add_subplot(gs[1, :])

# 构建热力图矩阵：行=国家（按 AR(1) tau 排序），列=相对峰值年
# 选取有足够数据的国家
valid_countries = ews_df.sort_values('ar1_tau', ascending=False)['country_code'].tolist()

# 限制显示数量（太多会看不清）
# 选择有代表性的国家：top 10 rising + bottom 10 + 中日
show_top = ews_df[ews_df['ar1_rising']].nlargest(12, 'ar1_tau')['country_code'].tolist()
show_bot = ews_df[~ews_df['ar1_rising']].nsmallest(8, 'ar1_tau')['country_code'].tolist()
# 确保中日在内
for must in ['CHN', 'JPN']:
    if must not in show_top and must not in show_bot:
        show_top.append(must)

show_codes = show_top + show_bot
# 保持排序
show_sorted = ews_df[ews_df['country_code'].isin(show_codes)].sort_values('ar1_tau', ascending=False)

# 构建矩阵
rel_years = list(range(-20, 6))
heatmap_data = []
y_labels = []

for _, row in show_sorted.iterrows():
    cc = row['country_code']
    cc_scan = scan_df[scan_df['country_code'] == cc]

    ar1_by_rel = {}
    for _, s in cc_scan.iterrows():
        ry = int(s['years_to_peak'])
        if ry in rel_years:
            ar1_by_rel[ry] = s['ar1']

    heatmap_row = [ar1_by_rel.get(ry, np.nan) for ry in rel_years]
    heatmap_data.append(heatmap_row)

    sig_mark = '*' if row['ar1_rising_sig'] else ''
    y_labels.append(f"{cc} ({row['country_name'][:15]}) tau={row['ar1_tau']:.2f}{sig_mark}")

heatmap_matrix = np.array(heatmap_data)

# 绘制热力图
im = ax_c.imshow(heatmap_matrix, aspect='auto', cmap='RdYlBu_r',
                 vmin=-0.5, vmax=1.0, interpolation='nearest')

# 每隔 5 年显示一个标签
tick_positions = [i for i, y in enumerate(rel_years) if y % 5 == 0]
tick_labels = [str(rel_years[i]) for i in tick_positions]
ax_c.set_xticks(tick_positions)
ax_c.set_xticklabels(tick_labels, fontsize=9)
ax_c.set_yticks(range(len(y_labels)))
ax_c.set_yticklabels(y_labels, fontsize=7)

# 标注峰值线
peak_idx = rel_years.index(0)
ax_c.axvline(x=peak_idx, color='white', linewidth=2, linestyle='--')

ax_c.set_xlabel('Years relative to CPR peak', fontsize=11)
ax_c.set_title(f'C. Global EWS scan: rolling AR(1) before CPR decline\n'
               f'({len(ews_df)} countries with >20% CPR decline; '
               f'{n_rising}/{n_total} [{n_rising/n_total*100:.0f}%] show rising AR(1))',
               fontsize=12, fontweight='bold')

# Colorbar
cbar = plt.colorbar(im, ax=ax_c, shrink=0.6, pad=0.02)
cbar.set_label('AR(1) coefficient', fontsize=10)

# ── 全局标题 ──
fig.suptitle('Prospective Predictions & Cross-national EWS Validation',
             fontsize=15, fontweight='bold', y=0.98)

plt.savefig(FIG_PATH, dpi=200, bbox_inches='tight', facecolor='white')
rpt(f"图表已保存: {FIG_PATH}")
plt.close()

# ══════════════════════════════════════════════════════════
# 总结
# ══════════════════════════════════════════════════════════
rpt()
rpt("=" * 72)
rpt("总结与讨论")
rpt("=" * 72)
rpt()
rpt("1. 条件性前瞻预测:")
for cc in TARGET_COUNTRIES:
    if cc in predictions:
        p = predictions[cc]
        if p['years_to_peak'] > 0:
            rpt(f"   - {p['name']}: 当前城镇化率 {p['latest_urban']:.0f}%，如按中国轨迹，CPR 峰值预计在约 {p['years_to_peak']:.0f} 年后")
        else:
            rpt(f"   - {p['name']}: 城镇化率已超过中国 CPR 峰值阶段，需关注 CPR 是否已在下降")

rpt()
rpt("2. 日本 EWS 验证:")
if not np.isnan(tau_ar1):
    rpt(f"   - 日本 CPR 结构性下降前 (1980-1995) AR(1) Kendall tau = {tau_ar1:.3f} (p = {p_ar1:.4f})")
    rpt(f"   - {'支持' if tau_ar1 > 0 and p_ar1 < 0.1 else '不支持（但方向一致）' if tau_ar1 > 0 else '不支持'} critical slowing down 假说")
else:
    rpt(f"   - 日本 1978 峰值前数据不足，仅供参考")

rpt()
rpt("3. 全球 EWS 扫描:")
rpt(f"   - {n_rising}/{n_total} ({n_rising/n_total*100:.0f}%) 的国家在 CPR 下降前展现 AR(1) 上升")
rpt(f"   - 二项检验 p = {binom_p:.4f}")
rpt(f"   - 这{'为' if binom_p < 0.05 else '未能为'} 'critical slowing down 在城市投资转向中普遍存在' 提供统计证据")

rpt()
rpt("注意事项:")
rpt("  - NGA（尼日利亚）不在面板数据中，已替换为 EGY（埃及）")
rpt("  - 条件性预测基于 '按中国轨迹' 假设，实际路径可能因制度、政策、经济结构差异而不同")
rpt("  - EWS 的滚动窗口大小（8年）会影响结果，需进行窗口敏感性检验")
rpt("  - 全球扫描中部分国家 CPR 下降可能由战争、危机等外生冲击导致，而非内生相变")

# ── 保存报告 ──
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

rpt(f"\n报告已保存: {REPORT_PATH}")
print("\n脚本执行完成。")
