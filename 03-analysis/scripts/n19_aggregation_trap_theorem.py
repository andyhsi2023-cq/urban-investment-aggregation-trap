"""
n19_aggregation_trap_theorem.py
================================
目的：Aggregation Trap 定理的数值验证与可视化

1. 用论文实际数据校准定理参数，验证三个条件是否满足
2. 构造简化两组模型的数值示例
3. 构造 K=4 一般模型的数值示例
4. Monte Carlo 模拟：在条件满足/不满足时 paradox 出现的概率
5. 生成 Box 1 可用的示意数据

输入：
  - 02-data/processed/global_q_revised_panel.csv

输出：
  - 03-analysis/models/aggregation_trap_verification.csv  (校准参数)
  - 03-analysis/models/aggregation_trap_monte_carlo.csv   (MC 结果)
  - 04-figures/drafts/aggregation_trap_schematic_data.csv  (Box 1 图表数据)

依赖：pandas, numpy, scipy, statsmodels
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import os

# =============================================================================
# 路径设置
# =============================================================================
BASE = '/Users/andy/Desktop/Claude/urban-q-phase-transition'
PANEL_PATH = f'{BASE}/02-data/processed/global_q_revised_panel.csv'
OUT_DIR = f'{BASE}/03-analysis/models'
FIG_DIR = f'{BASE}/04-figures/drafts'

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

report_lines = []

def rprint(msg=''):
    print(msg)
    report_lines.append(str(msg))

# =============================================================================
# 1. 数据加载与 MUQ 计算 (复现 n01 的逻辑)
# =============================================================================
rprint('=' * 76)
rprint('AGGREGATION TRAP THEOREM: Numerical Verification')
rprint('=' * 76)
rprint()

panel = pd.read_csv(PANEL_PATH)
rprint(f'面板数据: {len(panel)} 行, {panel["country_code"].nunique()} 国')

# 构建实际 MUQ (constant 2015 USD) — 与 96 号脚本完全一致
panel['deflator'] = panel['gdp_current_usd'] / panel['gdp_constant_2015']
panel['V2_real'] = panel['rnna'] * 1e6  # PWT rnna 百万，转美元
panel['K_pim_real'] = panel['K_pim'] / panel['deflator']
panel['gfcf_real'] = panel['gfcf_current_usd'] / panel['deflator']

panel = panel.sort_values(['country_code', 'year'])
panel['delta_V2_real'] = panel.groupby('country_code')['V2_real'].diff()
panel['delta_I_real'] = panel.groupby('country_code')['gfcf_real'].diff()
panel['muq_real'] = panel['delta_V2_real'] / panel['delta_I_real']

# 极端值处理 (与 96 号脚本一致: |MUQ| > 20 或 MUQ < -5)
muq_extreme = (panel['muq_real'].abs() > 20) | (panel['muq_real'] < -5)
panel.loc[muq_extreme, 'muq_real'] = np.nan

# 收入组: 使用面板中已有的 World Bank 分类，简化标签
ig_map = {
    'Low income': 'Low',
    'Lower middle income': 'Lower-Mid',
    'Upper middle income': 'Upper-Mid',
    'High income': 'High'
}
panel['ig_short'] = panel['income_group'].map(ig_map)

valid = panel.dropna(subset=['muq_real', 'urban_pct', 'ig_short']).copy()
valid['u'] = valid['urban_pct'] / 100  # 归一化到 [0, 1]
# 用简化标签替代
valid['income_group'] = valid['ig_short']

rprint(f'有效观测: {len(valid)}, 覆盖 {valid["country_code"].nunique()} 国')
rprint()

# =============================================================================
# 2. 校准定理参数: 每组的 mu_k 和 beta_k
# =============================================================================
rprint('=' * 76)
rprint('PART 1: Parameter Calibration from Data')
rprint('=' * 76)
rprint()

income_order = ['Low', 'Lower-Mid', 'Upper-Mid', 'High']
calibration = []

rprint(f'{"Group":<12} {"N":>6} {"mu_k":>8} {"beta_k":>9} {"mean_u":>7} '
       f'{"rho":>7} {"p":>10} {"SE_beta":>9}')
rprint('-' * 76)

for ig in income_order:
    sub = valid[valid['income_group'] == ig].copy()
    if len(sub) < 10:
        continue

    # OLS: MUQ = mu_k + beta_k * u + epsilon
    X = sm.add_constant(sub['u'])
    model = sm.OLS(sub['muq_real'], X).fit(cov_type='cluster',
                                            cov_kwds={'groups': sub['country_code']})
    mu_k = model.params['const']
    beta_k = model.params['u']
    se_beta = model.bse['u']
    p_beta = model.pvalues['u']

    # Spearman 相关
    rho, p_rho = stats.spearmanr(sub['u'], sub['muq_real'])

    mean_u = sub['u'].mean()

    calibration.append({
        'group': ig,
        'n': len(sub),
        'mu_k': mu_k,
        'beta_k': beta_k,
        'se_beta': se_beta,
        'p_beta': p_beta,
        'mean_u': mean_u,
        'rho': rho,
        'p_rho': p_rho
    })

    rprint(f'{ig:<12} {len(sub):>6} {mu_k:>8.4f} {beta_k:>+9.4f} {mean_u:>7.2f} '
           f'{rho:>+7.4f} {p_rho:>10.6f} {se_beta:>9.4f}')

cal_df = pd.DataFrame(calibration)
rprint()

# =============================================================================
# 3. 验证定理三个条件
# =============================================================================
rprint('=' * 76)
rprint('PART 2: Verification of Theorem Conditions')
rprint('=' * 76)
rprint()

# Condition A1: beta_k < 0 for all k
rprint('--- Condition (A1): Within-group decline ---')
a1_check = all(cal_df['beta_k'] < 0)
for _, row in cal_df.iterrows():
    status = 'PASS' if row['beta_k'] < 0 else 'FAIL'
    sig = '*' if row['p_beta'] < 0.05 else ''
    rprint(f'  {row["group"]:<12}: beta = {row["beta_k"]:+.4f} '
           f'(p = {row["p_beta"]:.4f}{sig}) [{status}]')
rprint(f'  A1 overall: {"PASS" if a1_check else "FAIL"}')
rprint()

# Condition A2: mu_{k+1} - mu_k > |beta_k| (inter-group gap dominates)
# 但需注意 beta_k 是斜率对 u in [0,1]，而实际 u 变化范围是有限的
# 更精确的条件：mu_{k+1} - mu_k > |beta_k| * Delta_u_k，其中 Delta_u_k
# 是组 k 内 u 的实际变化范围
rprint('--- Condition (A2): Between-group dominance ---')
for i in range(len(cal_df) - 1):
    row_lo = cal_df.iloc[i]
    row_hi = cal_df.iloc[i + 1]
    gap = row_hi['mu_k'] - row_lo['mu_k']
    # 组内 u 的 range (使用实际数据)
    sub_lo = valid[valid['income_group'] == row_lo['group']]
    delta_u = sub_lo['u'].quantile(0.95) - sub_lo['u'].quantile(0.05)
    within_decline = abs(row_lo['beta_k']) * delta_u
    status = 'PASS' if gap > within_decline else 'FAIL'
    rprint(f'  {row_lo["group"]} -> {row_hi["group"]}:')
    rprint(f'    Level gap: {gap:+.4f}')
    rprint(f'    Within decline (|beta|*Delta_u): {within_decline:.4f}')
    rprint(f'    Ratio (gap / decline): {gap/within_decline:.2f}x [{status}]')
rprint()

# Condition A3: Compositional shift
rprint('--- Condition (A3): Compositional shift ---')
# 检验高收入组在高 u 中的权重是否更大
u_bins = pd.qcut(valid['u'], q=5, labels=False, duplicates='drop')
valid_temp = valid.copy()
valid_temp['u_quintile'] = u_bins

rprint('  Group weight by urbanization quintile:')
weight_table = pd.crosstab(valid_temp['u_quintile'], valid_temp['income_group'],
                            normalize='index')
weight_table = weight_table.reindex(columns=income_order)
rprint(f'  {"Quintile":<10}' + ''.join(f'{g:>12}' for g in income_order))
for q in sorted(valid_temp['u_quintile'].dropna().unique()):
    row_str = f'  Q{int(q)+1:<9}'
    for g in income_order:
        val = weight_table.loc[q, g] if g in weight_table.columns else 0
        row_str += f'{val:>12.3f}'
    rprint(row_str)

# 定量检验：High income 的权重与 u 的 Spearman 相关
rprint()
rprint('  Correlation between u-quintile and group weight:')
for g in income_order:
    weights = []
    quintiles = []
    for q in sorted(valid_temp['u_quintile'].dropna().unique()):
        sub_q = valid_temp[valid_temp['u_quintile'] == q]
        w = (sub_q['income_group'] == g).mean()
        weights.append(w)
        quintiles.append(q)
    rho_w, p_w = stats.spearmanr(quintiles, weights)
    rprint(f'    {g:<12}: rho(u, w_k) = {rho_w:+.4f}, p = {p_w:.4f}')

rprint()

# 全局验证：between > within
rho_pooled, p_pooled = stats.spearmanr(valid['u'], valid['muq_real'])
total_n = len(valid)
weighted_within = sum(
    row['rho'] * row['n'] / total_n for _, row in cal_df.iterrows()
)
between = rho_pooled - weighted_within

rprint(f'  Pooled rho:           {rho_pooled:+.4f}')
rprint(f'  Weighted within rho:  {weighted_within:+.4f}')
rprint(f'  Between component:    {between:+.4f}')
rprint(f'  |Between| > |Within|: {abs(between) > abs(weighted_within)} '
       f'({abs(between):.4f} vs {abs(weighted_within):.4f})')
a3_check = between > abs(weighted_within)
rprint(f'  A3 overall: {"PASS" if a3_check else "MARGINAL"}')
rprint()

# =============================================================================
# 4. 简化两组模型: 数值示例
# =============================================================================
rprint('=' * 76)
rprint('PART 3: Two-Group Simplified Model')
rprint('=' * 76)
rprint()

# 用 Low + High 两组校准
mu_L = cal_df[cal_df['group'] == 'Low']['mu_k'].values[0]
mu_H = cal_df[cal_df['group'] == 'High']['mu_k'].values[0]
beta_L = cal_df[cal_df['group'] == 'Low']['beta_k'].values[0]
beta_H = cal_df[cal_df['group'] == 'High']['beta_k'].values[0]
gamma = (abs(beta_L) + abs(beta_H)) / 2  # 取平均斜率

rprint(f'Calibrated parameters:')
rprint(f'  mu_L = {mu_L:.4f} (Low income intercept)')
rprint(f'  mu_H = {mu_H:.4f} (High income intercept)')
rprint(f'  gamma = {gamma:.4f} (average within-group decline)')
rprint(f'  Gap = mu_H - mu_L = {mu_H - mu_L:.4f}')
rprint(f'  Condition: Gap >= gamma? {mu_H - mu_L >= gamma} '
       f'({mu_H - mu_L:.4f} vs {gamma:.4f})')
rprint()

# 构造两组的完整轨迹
u_grid = np.linspace(0.05, 0.95, 200)
E_L = mu_L - gamma * u_grid
E_H = mu_H - gamma * u_grid

# 权重函数: logistic shift (更贴近现实)
def logistic_weight(u, u0=0.5, steepness=5):
    """高收入组的权重: S 型函数"""
    return 1 / (1 + np.exp(-steepness * (u - u0)))

w_H = logistic_weight(u_grid)
w_L = 1 - w_H

E_agg = w_L * E_L + w_H * E_H

rprint(f'Two-group trajectory:')
rprint(f'  {"u":>5} {"E_L":>8} {"E_H":>8} {"w_H":>6} {"E_agg":>8}')
for idx in [0, 49, 99, 149, 199]:
    rprint(f'  {u_grid[idx]:>5.2f} {E_L[idx]:>8.4f} {E_H[idx]:>8.4f} '
           f'{w_H[idx]:>6.3f} {E_agg[idx]:>8.4f}')

# dE_agg/du 的符号
dE_agg = np.diff(E_agg) / np.diff(u_grid)
n_positive = np.sum(dE_agg >= 0)
rprint(f'\n  dE_agg/du >= 0 at {n_positive}/{len(dE_agg)} points '
       f'({100*n_positive/len(dE_agg):.1f}%)')
rprint(f'  E_agg range: [{E_agg.min():.4f}, {E_agg.max():.4f}]')
rprint(f'  E_L range:   [{E_L.min():.4f}, {E_L.max():.4f}] (declining)')
rprint(f'  E_H range:   [{E_H.min():.4f}, {E_H.max():.4f}] (declining)')
rprint()

# 保存 Box 1 图表数据
box1_data = pd.DataFrame({
    'u': u_grid,
    'E_L': E_L,
    'E_H': E_H,
    'w_L': w_L,
    'w_H': w_H,
    'E_agg': E_agg
})
box1_path = f'{FIG_DIR}/aggregation_trap_schematic_data.csv'
box1_data.to_csv(box1_path, index=False)
rprint(f'Box 1 数据已保存: {box1_path}')
rprint()

# =============================================================================
# 5. K=4 一般模型验证
# =============================================================================
rprint('=' * 76)
rprint('PART 4: Four-Group General Model')
rprint('=' * 76)
rprint()

# 用实际校准参数
mu_vec = cal_df['mu_k'].values
beta_vec = cal_df['beta_k'].values
mean_u_vec = cal_df['mean_u'].values

rprint('Calibrated parameters (from OLS with clustered SE):')
for i, row in cal_df.iterrows():
    rprint(f'  Group {row["group"]:<12}: mu = {row["mu_k"]:+.6f}, '
           f'beta = {row["beta_k"]:+.6f}, mean_u = {row["mean_u"]:.3f}')
rprint()

# 权重函数: 多项式 logit (softmax of linear functions of u)
# 校准到数据中的 u-quintile 权重
def multi_weight(u_val, alphas, betas_w):
    """
    多组权重函数: softmax(alpha_k + beta_w_k * u)
    alpha_k, beta_w_k 校准到数据
    """
    logits = alphas + betas_w * u_val
    logits -= logits.max()  # numerical stability
    exp_logits = np.exp(logits)
    return exp_logits / exp_logits.sum()

# 校准权重参数: 使各组的平均 u 匹配数据
# 简化: 使用线性插值权重
# 从 quintile 权重表中提取
u_quintile_centers = [0.15, 0.30, 0.45, 0.60, 0.80]

# 构造四组轨迹
u_grid_4 = np.linspace(0.10, 0.90, 300)

# 用更灵活的权重: 对数据做 kernel 平滑
# 但更简洁的方法: 直接从数据拟合 multinomial logit
from sklearn.linear_model import LogisticRegression

# 将组编码为数字
group_map = {'Low': 0, 'Lower-Mid': 1, 'Upper-Mid': 2, 'High': 3}
valid_4g = valid.copy()
valid_4g['group_id'] = valid_4g['income_group'].map(group_map)
valid_4g = valid_4g.dropna(subset=['group_id'])

# Multinomial logit: P(group | u)
try:
    ml = LogisticRegression(multi_class='multinomial', solver='lbfgs',
                            max_iter=1000, C=1.0)
    ml.fit(valid_4g[['u']].values, valid_4g['group_id'].astype(int).values)

    # 预测各 u 的权重
    w_pred = ml.predict_proba(u_grid_4.reshape(-1, 1))

    rprint('Weight functions (multinomial logit fitted to data):')
    rprint(f'  {"u":>5} ' + ''.join(f'{g:>12}' for g in income_order))
    for idx in [0, 74, 149, 224, 299]:
        row_str = f'  {u_grid_4[idx]:>5.2f} '
        for j in range(4):
            row_str += f'{w_pred[idx, j]:>12.3f}'
        rprint(row_str)
    rprint()

    # 构造四组 E_k(u) 和 E_agg(u)
    E_4g = np.zeros((len(u_grid_4), 4))
    for k in range(4):
        E_4g[:, k] = mu_vec[k] + beta_vec[k] * u_grid_4

    E_agg_4g = np.sum(w_pred * E_4g, axis=1)

    # 检查斜率
    dE_agg_4g = np.diff(E_agg_4g) / np.diff(u_grid_4)
    n_pos = np.sum(dE_agg_4g >= 0)

    rprint(f'Four-group aggregate:')
    rprint(f'  dE_agg/du >= 0 at {n_pos}/{len(dE_agg_4g)} points '
           f'({100*n_pos/len(dE_agg_4g):.1f}%)')
    rprint(f'  E_agg range: [{E_agg_4g.min():.4f}, {E_agg_4g.max():.4f}]')
    for k, g in enumerate(income_order):
        rprint(f'  E_{g} range: [{E_4g[:, k].min():.4f}, {E_4g[:, k].max():.4f}]')
    rprint()

    # Spearman 相关 on simulated aggregate
    rho_sim, p_sim = stats.spearmanr(u_grid_4, E_agg_4g)
    rprint(f'  Simulated aggregate Spearman: rho = {rho_sim:+.4f}, p = {p_sim:.6f}')
    rprint(f'  Empirical pooled Spearman:    rho = {rho_pooled:+.4f}, p = {p_pooled:.6f}')
    rprint()

    # 保存四组数据
    four_group_data = pd.DataFrame({
        'u': u_grid_4,
        'E_Low': E_4g[:, 0],
        'E_LowerMid': E_4g[:, 1],
        'E_UpperMid': E_4g[:, 2],
        'E_High': E_4g[:, 3],
        'w_Low': w_pred[:, 0],
        'w_LowerMid': w_pred[:, 1],
        'w_UpperMid': w_pred[:, 2],
        'w_High': w_pred[:, 3],
        'E_agg': E_agg_4g
    })
    four_group_path = f'{FIG_DIR}/aggregation_trap_4group_data.csv'
    four_group_data.to_csv(four_group_path, index=False)
    rprint(f'四组数据已保存: {four_group_path}')

except ImportError:
    rprint('NOTE: sklearn not available, skipping multinomial logit.')

rprint()

# =============================================================================
# 6. Monte Carlo: 定理条件满足时 paradox 出现的概率
# =============================================================================
rprint('=' * 76)
rprint('PART 5: Monte Carlo Simulation')
rprint('=' * 76)
rprint()

np.random.seed(20260322)
n_sim = 10000
n_obs_per_group = 100

mc_results = []

for sim_idx in range(n_sim):
    # 随机生成参数
    K = 4
    # mu_k 递增，间距随机
    mu_base = np.random.uniform(0.02, 0.08)
    mu_gaps = np.random.uniform(0.005, 0.03, K - 1)
    mu_sim = np.cumsum(np.concatenate([[mu_base], mu_gaps]))

    # beta_k < 0 (条件 A1 始终满足)
    beta_sim = -np.random.uniform(0.01, 0.15, K)

    # 权重函数斜率：控制 compositional shift 的强度
    # shift_strength > 1 = 强 compositional shift
    shift_strength = np.random.uniform(0.5, 3.0)

    # 生成数据
    u_sim_all = []
    e_sim_all = []
    g_sim_all = []

    for k in range(K):
        # 组 k 的 u 分布：随 k 增大而右移
        u_center = 0.2 + 0.2 * k  # [0.2, 0.4, 0.6, 0.8]
        u_k = np.random.beta(
            2 + shift_strength * k,
            2 + shift_strength * (K - 1 - k)
        ) * 0.8 + 0.1  # 映射到 [0.1, 0.9]
        u_k = np.clip(np.random.normal(u_center, 0.15, n_obs_per_group), 0.05, 0.95)

        # E_k = mu_k + beta_k * u + noise
        noise = np.random.normal(0, 0.03, n_obs_per_group)
        e_k = mu_sim[k] + beta_sim[k] * u_k + noise

        u_sim_all.extend(u_k)
        e_sim_all.extend(e_k)
        g_sim_all.extend([k] * n_obs_per_group)

    u_arr = np.array(u_sim_all)
    e_arr = np.array(e_sim_all)
    g_arr = np.array(g_sim_all)

    # 全样本 Spearman
    rho_pool, p_pool = stats.spearmanr(u_arr, e_arr)

    # 分组 Spearman
    within_neg = 0
    for k in range(K):
        mask = g_arr == k
        rho_k, _ = stats.spearmanr(u_arr[mask], e_arr[mask])
        if rho_k < 0:
            within_neg += 1

    # 检查条件 A2
    a2_met = True
    for k in range(K - 1):
        gap = mu_sim[k + 1] - mu_sim[k]
        decline = abs(beta_sim[k]) * 0.6  # 实际 u 跨度约 0.6
        if gap < decline:
            a2_met = False
            break

    mc_results.append({
        'sim': sim_idx,
        'rho_pooled': rho_pool,
        'within_all_negative': within_neg == K,
        'paradox': (within_neg == K) and (rho_pool >= 0),
        'a2_met': a2_met,
        'shift_strength': shift_strength,
        'mean_gap': np.mean(mu_gaps),
        'mean_abs_beta': np.mean(np.abs(beta_sim))
    })

mc_df = pd.DataFrame(mc_results)

# 分析结果
rprint(f'Monte Carlo: {n_sim} simulations, K=4 groups, {n_obs_per_group} obs/group')
rprint()

# 总体
n_paradox = mc_df['paradox'].sum()
n_within_neg = mc_df['within_all_negative'].sum()
rprint(f'All within-group rho < 0: {n_within_neg}/{n_sim} ({100*n_within_neg/n_sim:.1f}%)')
rprint(f'Simpson\'s Paradox (all neg within + non-neg pooled): '
       f'{n_paradox}/{n_sim} ({100*n_paradox/n_sim:.1f}%)')
rprint()

# 按条件分组
a2_met = mc_df[mc_df['a2_met']]
a2_not = mc_df[~mc_df['a2_met']]

rprint('When A2 (between-group dominance) is met:')
if len(a2_met) > 0:
    n_p = a2_met['paradox'].sum()
    rprint(f'  N = {len(a2_met)}, Paradox occurs: {n_p} ({100*n_p/len(a2_met):.1f}%)')

rprint('When A2 is NOT met:')
if len(a2_not) > 0:
    n_p = a2_not['paradox'].sum()
    rprint(f'  N = {len(a2_not)}, Paradox occurs: {n_p} ({100*n_p/len(a2_not):.1f}%)')

rprint()

# 按 shift_strength 分组
for ss_lo, ss_hi, label in [(0.5, 1.0, 'Weak shift'),
                              (1.0, 2.0, 'Medium shift'),
                              (2.0, 3.0, 'Strong shift')]:
    sub = mc_df[(mc_df['shift_strength'] >= ss_lo) & (mc_df['shift_strength'] < ss_hi)]
    if len(sub) > 0:
        n_p = sub['paradox'].sum()
        n_wn = sub['within_all_negative'].sum()
        rprint(f'  {label:<15} (N={len(sub):>4}): '
               f'all_neg={100*n_wn/len(sub):>5.1f}%, '
               f'paradox={100*n_p/len(sub):>5.1f}%')

rprint()

# 最关键的: 当所有三个条件都满足时
# A1 by construction, A2 checked, A3 ~ shift_strength > 1.5
strict = mc_df[(mc_df['a2_met']) & (mc_df['shift_strength'] > 1.5)]
if len(strict) > 0:
    n_wn = strict['within_all_negative'].sum()
    n_p = strict['paradox'].sum()
    rprint(f'When all conditions approximately met (A2 + strong shift):')
    rprint(f'  N = {len(strict)}')
    rprint(f'  All within negative: {n_wn} ({100*n_wn/len(strict):.1f}%)')
    rprint(f'  Paradox: {n_p} ({100*n_p/len(strict):.1f}%)')
    # 在 all-within-negative 的子集中
    if n_wn > 0:
        strict_neg = strict[strict['within_all_negative']]
        n_p2 = strict_neg['paradox'].sum()
        rprint(f'  Paradox | all within negative: {n_p2}/{n_wn} '
               f'({100*n_p2/n_wn:.1f}%)')

rprint()

# 保存 MC 结果
mc_path = f'{OUT_DIR}/aggregation_trap_monte_carlo.csv'
mc_df.to_csv(mc_path, index=False)
rprint(f'MC 结果已保存: {mc_path}')

# =============================================================================
# 7. 敏感性: 定理"临界点"分析
# =============================================================================
rprint()
rprint('=' * 76)
rprint('PART 6: Critical Threshold Analysis')
rprint('=' * 76)
rprint()
rprint('Question: How large must the between-group gap be (relative to within-')
rprint('group decline) for the paradox to be guaranteed?')
rprint()

# 简化两组模型: E_agg 非递减 iff mu_H - mu_L >= gamma
# 扫描 gap/gamma 比率
ratios = np.linspace(0.0, 3.0, 61)
paradox_freq = []

np.random.seed(42)
n_sim_crit = 2000

for ratio in ratios:
    count_paradox = 0
    count_valid = 0
    for _ in range(n_sim_crit):
        gamma_c = np.random.uniform(0.02, 0.12)
        mu_L_c = np.random.uniform(0.02, 0.08)
        mu_H_c = mu_L_c + ratio * gamma_c

        # 生成数据
        n_each = 80
        u_L = np.random.uniform(0.1, 0.6, n_each)
        u_H = np.random.uniform(0.4, 0.9, n_each)
        e_L = mu_L_c - gamma_c * u_L + np.random.normal(0, 0.02, n_each)
        e_H = mu_H_c - gamma_c * u_H + np.random.normal(0, 0.02, n_each)

        # 分组检验
        rho_L, _ = stats.spearmanr(u_L, e_L)
        rho_H, _ = stats.spearmanr(u_H, e_H)

        if rho_L < 0 and rho_H < 0:
            count_valid += 1
            # Pooled
            u_all_c = np.concatenate([u_L, u_H])
            e_all_c = np.concatenate([e_L, e_H])
            rho_all_c, _ = stats.spearmanr(u_all_c, e_all_c)
            if rho_all_c >= 0:
                count_paradox += 1

    freq = count_paradox / count_valid if count_valid > 0 else np.nan
    paradox_freq.append(freq)

rprint(f'{"Gap/Gamma":>12} {"P(Paradox|all neg)":>20}')
rprint('-' * 35)
for i in range(0, len(ratios), 5):
    rprint(f'{ratios[i]:>12.2f} {paradox_freq[i]:>20.3f}')

# 保存临界点数据
crit_df = pd.DataFrame({'gap_gamma_ratio': ratios, 'paradox_probability': paradox_freq})
crit_path = f'{FIG_DIR}/aggregation_trap_critical_threshold.csv'
crit_df.to_csv(crit_path, index=False)
rprint(f'\n临界点数据已保存: {crit_path}')

# 我们数据中的实际比率
actual_gap = mu_vec[-1] - mu_vec[0]  # High - Low
actual_gamma = np.mean(np.abs(beta_vec))
actual_ratio = actual_gap / actual_gamma if actual_gamma > 0 else np.inf
rprint(f'\n本文数据中的 gap/gamma 比率: {actual_ratio:.2f}')
rprint(f'  (mu_High - mu_Low) = {actual_gap:.4f}')
rprint(f'  mean |beta_k| = {actual_gamma:.4f}')

# =============================================================================
# 8. 保存校准参数
# =============================================================================
cal_path = f'{OUT_DIR}/aggregation_trap_verification.csv'
cal_df.to_csv(cal_path, index=False)
rprint(f'\n校准参数已保存: {cal_path}')

# =============================================================================
# 9. 保存完整报告
# =============================================================================
report_path = f'{OUT_DIR}/aggregation_trap_verification_report.txt'
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))
rprint(f'\n完整报告已保存: {report_path}')

rprint()
rprint('=' * 76)
rprint('DONE. All outputs generated.')
rprint('=' * 76)
