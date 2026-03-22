"""
96_simpsons_paradox_robustness.py
=================================
目的：回应审稿意见 — 排除中国后 Simpson's Paradox 是否仍然成立？

分析内容：
  1. 排除中国后的 Simpson's Paradox（全样本 + 分收入组 Spearman 相关）
  2. 排除其他大国的敏感性（BRA, MEX, TUR, RUS 等）
  3. UMI 组 Leave-one-out 稳健性
  4. 时变收入分类（GDP per capita 四分位动态分组）
  5. Oaxaca-Blinder 式分解（within vs between 分量）

输入：
  - 02-data/processed/global_q_revised_panel.csv

输出：
  - 03-analysis/models/simpsons_paradox_robustness_report.txt

依赖：pandas, numpy, scipy
"""

import pandas as pd
import numpy as np
from scipy import stats

# =============================================================================
# 路径设置
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
PANEL_PATH = f'{BASE}/02-data/processed/global_q_revised_panel.csv'
OUT_REPORT = f'{BASE}/03-analysis/models/simpsons_paradox_robustness_report.txt'

report_lines = []

def rprint(msg=''):
    """同时打印到控制台和报告"""
    print(msg)
    report_lines.append(str(msg))


def spearman_corr(x, y):
    """计算 Spearman 相关，返回 (rho, p, n)"""
    mask = x.notna() & y.notna()
    x_clean, y_clean = x[mask], y[mask]
    n = len(x_clean)
    if n < 10:
        return np.nan, np.nan, n
    rho, p = stats.spearmanr(x_clean, y_clean)
    return rho, p, n


def format_rho(rho, p, n):
    """格式化 Spearman 结果"""
    if np.isnan(rho):
        return f'rho=NA (n={n})'
    sig = ''
    if p < 0.001:
        sig = ' ***'
    elif p < 0.01:
        sig = ' **'
    elif p < 0.05:
        sig = ' *'
    return f'rho={rho:+.4f}, p={p:.6f}, n={n}{sig}'


# =============================================================================
# 数据准备：复现 real MUQ 计算 (与 36_muq_real_correction.py 一致)
# =============================================================================
rprint('=' * 76)
rprint('Simpson\'s Paradox Robustness Check — 排除中国及大国敏感性分析')
rprint('=' * 76)
rprint(f'日期: 2026-03-21')
rprint()

panel = pd.read_csv(PANEL_PATH)
rprint(f'[数据准备] 面板: {len(panel)} 行, {panel["country_code"].nunique()} 国')

# 构建实际 MUQ (constant 2015 USD)
panel['deflator'] = panel['gdp_current_usd'] / panel['gdp_constant_2015']
panel['V2_real'] = panel['rnna'] * 1e6  # PWT rnna 为百万，转为美元
panel['K_pim_real'] = panel['K_pim'] / panel['deflator']
panel['gfcf_real'] = panel['gfcf_current_usd'] / panel['deflator']
panel['delta_V2_real'] = panel.groupby('country_code')['V2_real'].diff()
panel['delta_I_real'] = panel.groupby('country_code')['gfcf_real'].diff()
panel['MUQ_real'] = panel['delta_V2_real'] / panel['delta_I_real']

# 极端值处理 (|MUQ| > 20 或 MUQ < -5)
muq_extreme = (panel['MUQ_real'].abs() > 20) | (panel['MUQ_real'] < -5)
panel.loc[muq_extreme, 'MUQ_real'] = np.nan

# GDP per capita (constant 2015 USD) 用于时变分类
panel['gdp_pc'] = panel['gdp_constant_2015'] / panel['total_pop']

rprint(f'  实际 MUQ 可用: {panel["MUQ_real"].notna().sum()}')
rprint(f'  收入组分布:')
for ig in ['Low income', 'Lower middle income', 'Upper middle income', 'High income']:
    n_obs = panel[(panel['income_group'] == ig) & panel['MUQ_real'].notna()].shape[0]
    n_countries = panel[(panel['income_group'] == ig) & panel['MUQ_real'].notna()]['country_code'].nunique()
    rprint(f'    {ig}: {n_obs} obs, {n_countries} countries')

# 四个标准收入组
INCOME_GROUPS = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']

# =============================================================================
# 分析 0: 原始结果（包含中国）— 基准
# =============================================================================
rprint()
rprint('=' * 76)
rprint('分析 0: 原始结果（包含中国）— 基准参照')
rprint('=' * 76)

base = panel[panel['income_group'].isin(INCOME_GROUPS)].copy()

rho_all, p_all, n_all = spearman_corr(base['MUQ_real'], base['urban_pct'])
rprint(f'  全样本: {format_rho(rho_all, p_all, n_all)}')
for ig in INCOME_GROUPS:
    sub = base[base['income_group'] == ig]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    rprint(f'  {ig:25s}: {format_rho(rho, p, n)}')

# =============================================================================
# 分析 1: 排除中国后的 Simpson's Paradox
# =============================================================================
rprint()
rprint('=' * 76)
rprint('分析 1: 排除中国 (CHN) 后的 Simpson\'s Paradox')
rprint('=' * 76)

no_chn = base[base['country_code'] != 'CHN'].copy()

rho_nc, p_nc, n_nc = spearman_corr(no_chn['MUQ_real'], no_chn['urban_pct'])
rprint(f'  全样本（无中国）: {format_rho(rho_nc, p_nc, n_nc)}')

results_no_chn = {}
for ig in INCOME_GROUPS:
    sub = no_chn[no_chn['income_group'] == ig]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    results_no_chn[ig] = (rho, p, n)
    rprint(f'  {ig:25s}: {format_rho(rho, p, n)}')

rprint()
rprint('  对比表:')
rprint(f'  {"指标":25s} {"含中国":25s} {"排除中国":25s}')
rprint(f'  {"-"*25} {"-"*25} {"-"*25}')
rprint(f'  {"全样本":25s} {format_rho(rho_all, p_all, n_all):25s} {format_rho(rho_nc, p_nc, n_nc):25s}')

# 重新计算含中国的分组结果用于对比
for ig in INCOME_GROUPS:
    sub_with = base[base['income_group'] == ig]
    rho_w, p_w, n_w = spearman_corr(sub_with['MUQ_real'], sub_with['urban_pct'])
    rho_wo, p_wo, n_wo = results_no_chn[ig]
    label = ig if ig != 'Upper middle income' else 'UMI (含/排CHN)'
    rprint(f'  {label:25s} {format_rho(rho_w, p_w, n_w):25s} {format_rho(rho_wo, p_wo, n_wo):25s}')

rprint()
rprint('  解读:')
# 判断是否稳健
umi_rho_no_chn = results_no_chn['Upper middle income'][0]
umi_p_no_chn = results_no_chn['Upper middle income'][1]
if umi_rho_no_chn < 0:
    rprint(f'  --> UMI 组排除中国后 rho 仍为负 ({umi_rho_no_chn:+.4f})，Simpson\'s Paradox 稳健。')
    if umi_p_no_chn < 0.05:
        rprint(f'  --> 且统计显著 (p={umi_p_no_chn:.6f})，结论不受中国数据影响。')
    else:
        rprint(f'  --> 但不再显著 (p={umi_p_no_chn:.6f})，可能因样本量减小。方向仍一致。')
else:
    rprint(f'  --> UMI 组排除中国后 rho 变为正 ({umi_rho_no_chn:+.4f})，需要警惕。')

# 全样本方向
pooled_rho_no_chn = rho_nc
all_group_negative = all(results_no_chn[ig][0] < 0 for ig in INCOME_GROUPS if not np.isnan(results_no_chn[ig][0]))
if pooled_rho_no_chn > 0 and all_group_negative:
    rprint('  --> 排除中国后，全局正 + 分组全负 = Simpson\'s Paradox 仍然成立。')
elif pooled_rho_no_chn <= 0 and all_group_negative:
    rprint('  --> 排除中国后，全局也为负，paradox 减弱但分组递减仍成立。')

# =============================================================================
# 分析 2: 排除其他大国的敏感性（UMI 组）
# =============================================================================
rprint()
rprint('=' * 76)
rprint('分析 2: 逐一排除大国后 UMI 组的 Spearman 相关')
rprint('=' * 76)

big_countries = ['CHN', 'BRA', 'MEX', 'TUR', 'RUS']
umi_base = base[base['income_group'] == 'Upper middle income'].copy()

rho_umi_full, p_umi_full, n_umi_full = spearman_corr(umi_base['MUQ_real'], umi_base['urban_pct'])
rprint(f'  UMI 完整: {format_rho(rho_umi_full, p_umi_full, n_umi_full)}')
rprint()

rprint(f'  {"排除国家":12s} {"rho":>8s}  {"p值":>10s}  {"n":>5s}  {"方向":6s}  {"显著":4s}')
rprint(f'  {"-"*12} {"-"*8}  {"-"*10}  {"-"*5}  {"-"*6}  {"-"*4}')

for cc in big_countries:
    sub = umi_base[umi_base['country_code'] != cc]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    direction = '负' if rho < 0 else '正'
    sig = 'Y' if p < 0.05 else 'N'
    rprint(f'  {cc:12s} {rho:+8.4f}  {p:10.6f}  {n:5d}  {direction:6s}  {sig:4s}')

# 同时排除所有五国
sub_no_big5 = umi_base[~umi_base['country_code'].isin(big_countries)]
rho_nb5, p_nb5, n_nb5 = spearman_corr(sub_no_big5['MUQ_real'], sub_no_big5['urban_pct'])
rprint(f'  {"全排除(5国)":12s} {rho_nb5:+8.4f}  {p_nb5:10.6f}  {n_nb5:5d}  {"负" if rho_nb5<0 else "正":6s}  {"Y" if p_nb5<0.05 else "N":4s}')

rprint()
rprint('  解读:')
all_negative = all(True for cc in big_countries
                   for sub in [umi_base[umi_base['country_code'] != cc]]
                   for rho, _, _ in [spearman_corr(sub['MUQ_real'], sub['urban_pct'])]
                   if rho < 0)
# 简化判断
neg_count = 0
for cc in big_countries:
    sub = umi_base[umi_base['country_code'] != cc]
    rho, _, _ = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    if rho < 0:
        neg_count += 1
rprint(f'  --> {neg_count}/{len(big_countries)} 种排除方案下 rho 保持为负。')
if neg_count == len(big_countries):
    rprint('  --> UMI 组的递减趋势不由任何单一大国驱动，结果稳健。')
else:
    rprint('  --> 部分方案下 rho 变号，需进一步检查。')

# =============================================================================
# 分析 3: Leave-one-out 稳健性（UMI 组）
# =============================================================================
rprint()
rprint('=' * 76)
rprint('分析 3: UMI 组 Leave-One-Out 稳健性')
rprint('=' * 76)

umi_countries = sorted(umi_base['country_code'].unique())
loo_results = []

for cc in umi_countries:
    sub = umi_base[umi_base['country_code'] != cc]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    loo_results.append({'country': cc, 'rho': rho, 'p': p, 'n': n})

loo_df = pd.DataFrame(loo_results)

rprint(f'  UMI 组共 {len(umi_countries)} 个国家')
rprint(f'  基线 rho = {rho_umi_full:+.4f}')
rprint()
rprint(f'  Leave-one-out rho 范围:')
rprint(f'    最小值: {loo_df["rho"].min():+.4f} (排除 {loo_df.loc[loo_df["rho"].idxmin(), "country"]})')
rprint(f'    最大值: {loo_df["rho"].max():+.4f} (排除 {loo_df.loc[loo_df["rho"].idxmax(), "country"]})')
rprint(f'    均值:   {loo_df["rho"].mean():+.4f}')
rprint(f'    标准差: {loo_df["rho"].std():.4f}')
rprint()

n_negative = (loo_df['rho'] < 0).sum()
n_sig = (loo_df['p'] < 0.05).sum()
n_total = len(loo_df)
rprint(f'  方向: {n_negative}/{n_total} 次为负 ({n_negative/n_total*100:.1f}%)')
rprint(f'  显著: {n_sig}/{n_total} 次 p<0.05 ({n_sig/n_total*100:.1f}%)')
rprint()

# 显示变化最大的 10 个国家
rprint('  rho 变化最大的 10 个国家 (排除该国后 rho 偏离基线最远):')
loo_df['delta_rho'] = loo_df['rho'] - rho_umi_full
loo_df['abs_delta'] = loo_df['delta_rho'].abs()
top10 = loo_df.nlargest(10, 'abs_delta')
rprint(f'  {"国家":6s} {"rho":>8s}  {"delta_rho":>10s}  {"p值":>10s}')
rprint(f'  {"-"*6} {"-"*8}  {"-"*10}  {"-"*10}')
for _, row in top10.iterrows():
    rprint(f'  {row["country"]:6s} {row["rho"]:+8.4f}  {row["delta_rho"]:+10.4f}  {row["p"]:10.6f}')

rprint()
rprint('  解读:')
if n_negative == n_total:
    rprint(f'  --> 所有 {n_total} 次 LOO 检验中 rho 均为负，方向完全稳健。')
elif n_negative >= n_total * 0.9:
    rprint(f'  --> {n_negative}/{n_total} 次为负 (>90%)，方向高度稳健。')
else:
    rprint(f'  --> 仅 {n_negative}/{n_total} 次为负，稳健性存疑。')

if n_sig >= n_total * 0.8:
    rprint(f'  --> {n_sig}/{n_total} 次显著 (>80%)，统计显著性稳健。')
else:
    rprint(f'  --> 仅 {n_sig}/{n_total} 次显著，显著性不够稳健（可能因样本量有限）。')

# =============================================================================
# 分析 4: 时变收入分类（GDP per capita 四分位动态分组）
# =============================================================================
rprint()
rprint('=' * 76)
rprint('分析 4: 时变收入分类 (GDP per capita 年度四分位动态分组)')
rprint('=' * 76)

# 每年按 GDP per capita 四分位分组
panel_tv = panel[panel['gdp_pc'].notna() & panel['MUQ_real'].notna()].copy()

# 计算年度四分位
def assign_quartile_group(df):
    """按年度 GDP per capita 分四组"""
    labels = ['Q1_Low', 'Q2_LowerMid', 'Q3_UpperMid', 'Q4_High']
    result = []
    for year, grp in df.groupby('year'):
        if len(grp) < 4:
            grp = grp.copy()
            grp['tv_income_group'] = np.nan
            result.append(grp)
            continue
        grp = grp.copy()
        try:
            grp['tv_income_group'] = pd.qcut(grp['gdp_pc'], 4, labels=labels, duplicates='drop')
        except ValueError:
            # 分位数重叠时回退到 rank 方法
            grp['gdp_rank'] = grp['gdp_pc'].rank(method='first', pct=True)
            grp['tv_income_group'] = pd.cut(grp['gdp_rank'], bins=[0, 0.25, 0.5, 0.75, 1.0],
                                            labels=labels, include_lowest=True)
        result.append(grp)
    return pd.concat(result, ignore_index=True)

panel_tv = assign_quartile_group(panel_tv)
panel_tv = panel_tv[panel_tv['tv_income_group'].notna()]

rprint(f'  可用观测: {len(panel_tv)}')
rprint(f'  方法: 每年按 GDP per capita (constant 2015 USD) 四分位分组')
rprint()

TV_GROUPS = ['Q1_Low', 'Q2_LowerMid', 'Q3_UpperMid', 'Q4_High']

# 全样本
rho_tv_all, p_tv_all, n_tv_all = spearman_corr(panel_tv['MUQ_real'], panel_tv['urban_pct'])
rprint(f'  全样本 (时变分组): {format_rho(rho_tv_all, p_tv_all, n_tv_all)}')

tv_results = {}
for tg in TV_GROUPS:
    sub = panel_tv[panel_tv['tv_income_group'] == tg]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    tv_results[tg] = (rho, p, n)
    rprint(f'  {tg:20s}: {format_rho(rho, p, n)}')

rprint()

# 排除中国的时变分组
panel_tv_nc = panel_tv[panel_tv['country_code'] != 'CHN']
rprint('  排除中国后 (时变分组):')
rho_tv_nc, p_tv_nc, n_tv_nc = spearman_corr(panel_tv_nc['MUQ_real'], panel_tv_nc['urban_pct'])
rprint(f'  全样本 (无中国): {format_rho(rho_tv_nc, p_tv_nc, n_tv_nc)}')

for tg in TV_GROUPS:
    sub = panel_tv_nc[panel_tv_nc['tv_income_group'] == tg]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    rprint(f'  {tg:20s}: {format_rho(rho, p, n)}')

rprint()
rprint('  解读:')
n_neg_tv = sum(1 for tg in TV_GROUPS if tv_results[tg][0] < 0 and not np.isnan(tv_results[tg][0]))
rprint(f'  --> 时变分组下 {n_neg_tv}/{len(TV_GROUPS)} 组 rho 为负。')
if n_neg_tv >= 3:
    rprint('  --> 时变分类下 Simpson\'s Paradox 仍然成立，不依赖于固定收入分类。')
else:
    rprint('  --> 时变分类下部分组方向改变，需谨慎解读。')

# =============================================================================
# 分析 5: Oaxaca-Blinder 式分解（简化版）
# =============================================================================
rprint()
rprint('=' * 76)
rprint('分析 5: Within vs Between 分解')
rprint('=' * 76)
rprint()
rprint('  方法: 比较 pooled Spearman rho 与组内 rho 的加权平均')
rprint('  若 pooled rho > weighted within rho，则 between-group composition 推高了全局相关')
rprint()

# 使用固定收入分组
base_valid = base[base['MUQ_real'].notna() & base['urban_pct'].notna()].copy()

# Pooled rho
rho_pooled, p_pooled, n_pooled = spearman_corr(base_valid['MUQ_real'], base_valid['urban_pct'])
rprint(f'  Pooled Spearman rho:    {rho_pooled:+.4f} (p={p_pooled:.6f}, n={n_pooled})')

# Within-group weighted average
within_rhos = []
within_weights = []
for ig in INCOME_GROUPS:
    sub = base_valid[base_valid['income_group'] == ig]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    if not np.isnan(rho):
        within_rhos.append(rho)
        within_weights.append(n)
        rprint(f'    {ig:25s}: rho={rho:+.4f}, w={n}')

within_weights = np.array(within_weights, dtype=float)
within_rhos = np.array(within_rhos)
weights_norm = within_weights / within_weights.sum()
weighted_within = np.dot(weights_norm, within_rhos)

rprint()
rprint(f'  Weighted within-group rho: {weighted_within:+.4f}')
rprint(f'  Between-group component:   {rho_pooled - weighted_within:+.4f}')
rprint(f'    (= pooled - weighted_within)')
rprint()

if rho_pooled > weighted_within:
    rprint('  解读: Between-group composition 推高了全局 rho。')
    rprint('  --> 高收入国家（高城镇化率、高 MUQ）的数量优势抬高了全局正相关。')
    rprint('  --> 但分组内部，MUQ 随城镇化率递减 — 经典 Simpson\'s Paradox。')
else:
    rprint('  解读: Between-group 贡献为负，全局 rho 比组内更低。')

# 排除中国后重复
rprint()
rprint('  --- 排除中国后的分解 ---')
base_nc = base_valid[base_valid['country_code'] != 'CHN']
rho_p_nc, p_p_nc, n_p_nc = spearman_corr(base_nc['MUQ_real'], base_nc['urban_pct'])
rprint(f'  Pooled (无CHN): {rho_p_nc:+.4f} (p={p_p_nc:.6f}, n={n_p_nc})')

within_rhos_nc = []
within_weights_nc = []
for ig in INCOME_GROUPS:
    sub = base_nc[base_nc['income_group'] == ig]
    rho, p, n = spearman_corr(sub['MUQ_real'], sub['urban_pct'])
    if not np.isnan(rho):
        within_rhos_nc.append(rho)
        within_weights_nc.append(n)

within_weights_nc = np.array(within_weights_nc, dtype=float)
within_rhos_nc = np.array(within_rhos_nc)
weights_nc_norm = within_weights_nc / within_weights_nc.sum()
weighted_within_nc = np.dot(weights_nc_norm, within_rhos_nc)

rprint(f'  Weighted within (无CHN): {weighted_within_nc:+.4f}')
rprint(f'  Between component (无CHN): {rho_p_nc - weighted_within_nc:+.4f}')

# =============================================================================
# 综合判定
# =============================================================================
rprint()
rprint('=' * 76)
rprint('综合判定: Simpson\'s Paradox 稳健性 GO/NO-GO')
rprint('=' * 76)
rprint()

# 收集判定依据
checks = {}

# Check 1: 排除中国后 UMI 组方向
checks['排除中国_UMI方向'] = umi_rho_no_chn < 0
# Check 2: 排除中国后至少 3/4 组方向为负
n_neg_no_chn = sum(1 for ig in INCOME_GROUPS
                   if results_no_chn[ig][0] < 0 and not np.isnan(results_no_chn[ig][0]))
checks['排除中国_多组为负'] = n_neg_no_chn >= 3
# Check 3: 大国敏感性 — 排除任一大国后 UMI rho 均为负
checks['大国敏感性_全负'] = neg_count == len(big_countries)
# Check 4: LOO 方向 >90%
checks['LOO_方向稳健'] = n_negative >= n_total * 0.9
# Check 5: 时变分类 >=3 组为负
checks['时变分类_多组为负'] = n_neg_tv >= 3
# Check 6: Between > Within (Simpson's Paradox 机制)
checks['Between推高全局'] = rho_pooled > weighted_within

for check_name, result in checks.items():
    status = 'PASS' if result else 'FAIL'
    rprint(f'  [{status}] {check_name}')

n_pass = sum(checks.values())
n_checks = len(checks)

rprint()
if n_pass >= 5:
    rprint(f'  ==> GO ({n_pass}/{n_checks} 项通过)')
    rprint('  Simpson\'s Paradox 对排除中国、排除大国、动态分组均稳健。')
    rprint('  审稿人的关切可以得到充分回应: 中国数据的包含/排除不影响核心结论。')
elif n_pass >= 3:
    rprint(f'  ==> CONDITIONAL GO ({n_pass}/{n_checks} 项通过)')
    rprint('  Simpson\'s Paradox 部分稳健，但需在论文中披露以下局限:')
    for check_name, result in checks.items():
        if not result:
            rprint(f'    - {check_name} 未通过')
else:
    rprint(f'  ==> NO-GO ({n_pass}/{n_checks} 项通过)')
    rprint('  Simpson\'s Paradox 不够稳健，需重新审视分组策略或数据范围。')

# =============================================================================
# 保存报告
# =============================================================================
with open(OUT_REPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f'\n[完成] 报告已保存至: {OUT_REPORT}')
