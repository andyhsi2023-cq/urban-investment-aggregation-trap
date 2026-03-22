"""
Phase 0 Kill Test: GDP-based MUQ Simpson's Paradox
===================================================
构建 MUQ_GDP = Delta-GDP / GFCF (即 1/ICOR)，完全免疫房价周期。
检验 Simpson's Paradox 是否在此指标下仍然成立。

如果通过 → 论文核心发现稳固
如果失败 → 转投 Nature Cities
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. 加载数据
# ============================================================
print("=" * 70)
print("PHASE 0 KILL TEST: GDP-based MUQ Simpson's Paradox")
print("=" * 70)

# 使用现有全球面板
panel = pd.read_csv('/Users/andy/Desktop/Claude/urban-q-phase-transition/02-data/processed/global_urban_q_panel.csv')

# 同时加载 World Bank 原始数据以获取收入分类
wb = pd.read_csv('/Users/andy/Desktop/Claude/urban-q-phase-transition/02-data/raw/world_bank_all_countries.csv')

print(f"\n全球面板: {len(panel)} 行, {panel['country_code'].nunique()} 国")

# ============================================================
# 2. 构建 GDP-based MUQ
# ============================================================

# 方法 A: 使用 constant 2015 USD GDP (WDI)
# MUQ_GDP_A = Delta(GDP_constant_2015) / GFCF_constant_2015

# 方法 B: 使用 PWT rgdpna
# MUQ_GDP_B = Delta(rgdpna) / (GFCF_implied from rgdpna)

# 方法 C: 使用 current USD 以保持与原始 MUQ 的可比性
# MUQ_GDP_C = Delta(GDP_current) / GFCF_current

# 先用方法 A (constant 2015 USD) 作为主方法
panel = panel.sort_values(['country_code', 'year'])

# 计算 GFCF in constant 2015 USD
panel['gfcf_constant_2015'] = panel['gdp_constant_2015'] * panel['gfcf_pct_gdp'] / 100

# Delta GDP (constant 2015)
panel['delta_gdp_constant'] = panel.groupby('country_code')['gdp_constant_2015'].diff()

# MUQ_GDP = Delta-GDP / GFCF (1/ICOR 的一种变体)
panel['muq_gdp'] = panel['delta_gdp_constant'] / panel['gfcf_constant_2015']

# 方法 B: 使用 PWT rnna (real national accounts GDP)
panel['delta_rgdpna'] = panel.groupby('country_code')['rgdpna'].diff()
# PWT 中的投资 = rgdpna * csh_i (但面板中没有 csh_i，用 gfcf_pct_gdp 代替)
panel['gfcf_rgdpna'] = panel['rgdpna'] * panel['gfcf_pct_gdp'] / 100
panel['muq_gdp_pwt'] = panel['delta_rgdpna'] / panel['gfcf_rgdpna']

# 清洗：去除极端值和无效值
for col in ['muq_gdp', 'muq_gdp_pwt']:
    panel[col] = panel[col].replace([np.inf, -np.inf], np.nan)
    # Winsorise at 1%/99%
    q01 = panel[col].quantile(0.01)
    q99 = panel[col].quantile(0.99)
    panel[col] = panel[col].clip(q01, q99)

print(f"\nMUQ_GDP (WDI constant 2015): {panel['muq_gdp'].notna().sum()} 有效观测")
print(f"MUQ_GDP (PWT rgdpna):        {panel['muq_gdp_pwt'].notna().sum()} 有效观测")
print(f"MUQ_GDP 中位数: {panel['muq_gdp'].median():.4f}")
print(f"MUQ_GDP 均值:   {panel['muq_gdp'].mean():.4f}")

# ============================================================
# 3. 收入组分类
# ============================================================

# 使用 World Bank 收入分类
# 从现有数据中提取国家信息，手动分类
# 使用 WDI 的 region 作为辅助，但需要收入组

# 加载收入组分类 - 使用 PWT 的人均 GDP 作为代理
# World Bank 2024 thresholds (GNI per capita, Atlas method):
# Low: < $1,145; Lower-middle: $1,146-$4,515; Upper-middle: $4,516-$14,005; High: > $14,005

# 我们用人均 GDP (constant 2015 USD) 的最近可用年份作为分类依据
latest = panel.dropna(subset=['gdp_constant_2015', 'total_pop']).copy()
latest['gdp_pc'] = latest['gdp_constant_2015'] / latest['total_pop']

# 取每国最近年份
latest_year = latest.groupby('country_code')['year'].max().reset_index()
latest_year.columns = ['country_code', 'latest_year']
latest = latest.merge(latest_year, on='country_code')
latest = latest[latest['year'] == latest['latest_year']]

# 基于人均 GDP 阈值分组 (constant 2015 USD, 近似 World Bank Atlas method)
# 调整阈值以匹配 WB 分类（constant 2015 USD 大约相当于）
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

# 映射回面板
income_map = latest[['country_code', 'income_group']].drop_duplicates()
panel = panel.merge(income_map, on='country_code', how='left')

# 统计
print("\n收入组分布:")
ig_counts = panel.dropna(subset=['muq_gdp', 'income_group']).groupby('income_group')['country_code'].nunique()
print(ig_counts)

# ============================================================
# 4. Simpson's Paradox 检验
# ============================================================

print("\n" + "=" * 70)
print("SIMPSON'S PARADOX TEST: GDP-based MUQ")
print("=" * 70)

# 4.1 使用 MUQ_GDP (WDI constant 2015)
muq_col = 'muq_gdp'
results = {}

valid = panel.dropna(subset=[muq_col, 'urban_pct', 'income_group']).copy()
print(f"\n有效观测总数: {len(valid)}, 覆盖 {valid['country_code'].nunique()} 国")

# 4.1a 全样本 Spearman
rho_all, p_all = stats.spearmanr(valid['urban_pct'], valid[muq_col])
print(f"\n全样本 (pooled): rho = {rho_all:+.4f}, p = {p_all:.4f}, N = {len(valid)}")

# 4.1b 分收入组 Spearman
print(f"\n{'收入组':<25} {'N':>6} {'国家数':>6} {'rho':>8} {'p-value':>10} {'方向':>6}")
print("-" * 65)

income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']

for ig in income_order:
    sub = valid[valid['income_group'] == ig]
    if len(sub) < 10:
        print(f"{ig:<25} {len(sub):>6} {'--':>6} {'--':>8} {'--':>10} {'--':>6}")
        continue
    rho, p = stats.spearmanr(sub['urban_pct'], sub[muq_col])
    n_countries = sub['country_code'].nunique()
    direction = "DOWN" if rho < 0 else "UP"
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    results[ig] = {'rho': rho, 'p': p, 'n': len(sub), 'n_countries': n_countries}
    print(f"{ig:<25} {len(sub):>6} {n_countries:>6} {rho:>+8.4f} {p:>10.4f}{sig} {direction:>6}")

# 4.2 使用 MUQ_GDP_PWT (PWT rgdpna)
print(f"\n--- PWT rgdpna 版本 ---")
muq_col2 = 'muq_gdp_pwt'
valid2 = panel.dropna(subset=[muq_col2, 'urban_pct', 'income_group']).copy()

rho_all2, p_all2 = stats.spearmanr(valid2['urban_pct'], valid2[muq_col2])
print(f"全样本 (pooled): rho = {rho_all2:+.4f}, p = {p_all2:.4f}, N = {len(valid2)}")

print(f"\n{'收入组':<25} {'N':>6} {'国家数':>6} {'rho':>8} {'p-value':>10} {'方向':>6}")
print("-" * 65)

results_pwt = {}
for ig in income_order:
    sub = valid2[valid2['income_group'] == ig]
    if len(sub) < 10:
        print(f"{ig:<25} {len(sub):>6} {'--':>6} {'--':>8} {'--':>10} {'--':>6}")
        continue
    rho, p = stats.spearmanr(sub['urban_pct'], sub[muq_col2])
    n_countries = sub['country_code'].nunique()
    direction = "DOWN" if rho < 0 else "UP"
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    results_pwt[ig] = {'rho': rho, 'p': p, 'n': len(sub), 'n_countries': n_countries}
    print(f"{ig:<25} {len(sub):>6} {n_countries:>6} {rho:>+8.4f} {p:>10.4f}{sig} {direction:>6}")

# ============================================================
# 5. Within/Between 分解
# ============================================================
print("\n" + "=" * 70)
print("WITHIN/BETWEEN DECOMPOSITION")
print("=" * 70)

# 计算加权 within-group rho
for label, res in [("WDI", results), ("PWT", results_pwt)]:
    total_n = sum(r['n'] for r in res.values())
    weighted_within = sum(r['rho'] * r['n'] / total_n for r in res.values())
    pooled_rho = rho_all if label == "WDI" else rho_all2
    between = pooled_rho - weighted_within
    print(f"\n{label}:")
    print(f"  Pooled rho:          {pooled_rho:+.4f}")
    print(f"  Weighted within-group: {weighted_within:+.4f}")
    print(f"  Between-group:       {between:+.4f}")

# ============================================================
# 6. 城镇化阶段分析
# ============================================================
print("\n" + "=" * 70)
print("URBANISATION STAGE ANALYSIS (GDP-based MUQ)")
print("=" * 70)

valid['urb_stage'] = pd.cut(valid['urban_pct'], bins=[0, 30, 50, 70, 100],
                            labels=['S1:<30%', 'S2:30-50%', 'S3:50-70%', 'S4:>70%'])

for ig in income_order:
    sub = valid[valid['income_group'] == ig]
    if len(sub) < 10:
        continue
    print(f"\n{ig}:")
    stage_stats = sub.groupby('urb_stage', observed=True)['muq_gdp'].agg(['count', 'median', 'mean', 'std'])
    for stage, row in stage_stats.iterrows():
        if row['count'] > 0:
            print(f"  {stage}: N={int(row['count']):>4}, median={row['median']:>8.4f}, mean={row['mean']:>8.4f}")
    # Kruskal-Wallis test
    groups = [g['muq_gdp'].dropna().values for _, g in sub.groupby('urb_stage', observed=True) if len(g) > 5]
    if len(groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*groups)
        print(f"  Kruskal-Wallis: H={kw_stat:.2f}, p={kw_p:.4f}")

# ============================================================
# 7. 与原始 MUQ 的对比
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON: Original MUQ vs GDP-based MUQ")
print("=" * 70)

# 原始 MUQ 的 Simpson's Paradox (从已有结果复现)
valid_orig = panel.dropna(subset=['muq', 'urban_pct', 'income_group']).copy()

print(f"\n{'指标':<20} {'收入组':<25} {'rho':>8} {'p':>10} {'N':>6}")
print("-" * 75)

for muq_label, muq_c, valid_df in [("Original MUQ", "muq", valid_orig),
                                     ("GDP-based MUQ", "muq_gdp", valid)]:
    for ig in income_order:
        sub = valid_df[valid_df['income_group'] == ig]
        if len(sub) < 10:
            continue
        rho, p = stats.spearmanr(sub['urban_pct'], sub[muq_c])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{muq_label:<20} {ig:<25} {rho:>+8.4f} {p:>10.4f}{sig} {len(sub):>6}")

# ============================================================
# 8. Leave-One-Out 稳健性 (Upper Middle Income)
# ============================================================
print("\n" + "=" * 70)
print("LEAVE-ONE-OUT ROBUSTNESS: Upper Middle Income (GDP-based MUQ)")
print("=" * 70)

umi = valid[valid['income_group'] == 'Upper middle income'].copy()
umi_countries = umi['country_code'].unique()

loo_results = []
for c in umi_countries:
    sub = umi[umi['country_code'] != c]
    if len(sub) < 10:
        continue
    rho, p = stats.spearmanr(sub['urban_pct'], sub['muq_gdp'])
    loo_results.append({'excluded': c, 'rho': rho, 'p': p})

loo_df = pd.DataFrame(loo_results)
n_negative = (loo_df['rho'] < 0).sum()
n_sig = (loo_df['p'] < 0.05).sum()
print(f"UMI 国家数: {len(umi_countries)}")
print(f"LOO iterations: {len(loo_df)}")
print(f"  rho < 0: {n_negative}/{len(loo_df)} ({100*n_negative/len(loo_df):.1f}%)")
print(f"  p < 0.05: {n_sig}/{len(loo_df)} ({100*n_sig/len(loo_df):.1f}%)")
print(f"  rho range: [{loo_df['rho'].min():+.4f}, {loo_df['rho'].max():+.4f}]")
print(f"  rho mean: {loo_df['rho'].mean():+.4f} (SD={loo_df['rho'].std():.4f})")

# ============================================================
# 9. Block Bootstrap (Country-Level Clustering)
# ============================================================
print("\n" + "=" * 70)
print("BLOCK BOOTSTRAP: Country-Clustered P-values")
print("=" * 70)

np.random.seed(42)
n_bootstrap = 5000

for ig in income_order:
    sub = valid[valid['income_group'] == ig].copy()
    if len(sub) < 30:
        continue

    # 原始 rho
    rho_obs, _ = stats.spearmanr(sub['urban_pct'], sub['muq_gdp'])

    # Block bootstrap: resample countries (with replacement), keep all obs per country
    countries = sub['country_code'].unique()
    n_countries = len(countries)

    boot_rhos = []
    for _ in range(n_bootstrap):
        # Resample countries
        boot_countries = np.random.choice(countries, size=n_countries, replace=True)
        # Gather all observations for resampled countries
        boot_data = pd.concat([sub[sub['country_code'] == c] for c in boot_countries], ignore_index=True)
        if len(boot_data) > 10:
            r, _ = stats.spearmanr(boot_data['urban_pct'], boot_data['muq_gdp'])
            boot_rhos.append(r)

    boot_rhos = np.array(boot_rhos)
    # Two-sided p-value: fraction of bootstrap rhos with opposite sign or more extreme
    if rho_obs < 0:
        boot_p = np.mean(boot_rhos >= 0) * 2  # two-sided
    else:
        boot_p = np.mean(boot_rhos <= 0) * 2
    boot_p = min(boot_p, 1.0)

    # Bootstrap SE and 95% CI
    boot_se = np.std(boot_rhos)
    boot_ci_lo = np.percentile(boot_rhos, 2.5)
    boot_ci_hi = np.percentile(boot_rhos, 97.5)

    sig = "***" if boot_p < 0.001 else "**" if boot_p < 0.01 else "*" if boot_p < 0.05 else ""
    print(f"\n{ig}:")
    print(f"  Observed rho: {rho_obs:+.4f}")
    print(f"  Bootstrap SE: {boot_se:.4f}")
    print(f"  Bootstrap 95% CI: [{boot_ci_lo:+.4f}, {boot_ci_hi:+.4f}]")
    print(f"  Bootstrap p-value: {boot_p:.4f}{sig}")
    print(f"  N countries: {n_countries}, N obs: {len(sub)}")

# ============================================================
# 10. 最终判决
# ============================================================
print("\n" + "=" * 70)
print("PHASE 0 VERDICT")
print("=" * 70)

# 检查三个发展中收入组是否都显示负相关
developing_groups = ['Low income', 'Lower middle income', 'Upper middle income']
all_negative = all(results.get(ig, {}).get('rho', 0) < 0 for ig in developing_groups if ig in results)
any_significant = any(results.get(ig, {}).get('p', 1) < 0.05 for ig in developing_groups if ig in results)
n_significant = sum(1 for ig in developing_groups if ig in results and results[ig]['p'] < 0.05)

print(f"\n三个发展中收入组内 rho 均为负: {'YES' if all_negative else 'NO'}")
print(f"至少一组显著 (p<0.05): {'YES' if any_significant else 'NO'}")
print(f"显著的组数: {n_significant}/3")

# Pooled 方向
pooled_positive = rho_all > 0 or abs(rho_all) < 0.02
print(f"Pooled rho 接近零或正: {'YES' if pooled_positive else 'NO'} (rho={rho_all:+.4f})")

if all_negative and any_significant:
    verdict = "PASS"
    detail = "Simpson's Paradox 在 GDP-based MUQ 下成立。论文核心发现稳固。继续 Nature 投稿修改。"
elif all_negative and not any_significant:
    verdict = "MARGINAL"
    detail = "方向一致但显著性不足。需要进一步分析（更大样本、面板方法）。暂不转投。"
elif not all_negative:
    verdict = "FAIL"
    detail = "Simpson's Paradox 在 GDP-based MUQ 下不成立。核心发现仅限于住房价格指标。建议转投 Nature Cities。"
else:
    verdict = "INCONCLUSIVE"
    detail = "结果不明确，需更多分析。"

print(f"\n{'='*30}")
print(f"  VERDICT: {verdict}")
print(f"{'='*30}")
print(f"\n{detail}")

# ============================================================
# 11. 保存结果
# ============================================================
output_path = '/Users/andy/Desktop/Claude/urban-q-phase-transition/03-analysis/models/phase0_gdp_muq_results.txt'
with open(output_path, 'w') as f:
    f.write("PHASE 0 KILL TEST: GDP-based MUQ Simpson's Paradox\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Verdict: {verdict}\n\n")
    f.write(f"WDI Method (constant 2015 USD):\n")
    f.write(f"  Pooled rho: {rho_all:+.4f}, p={p_all:.4f}\n")
    for ig in income_order:
        if ig in results:
            r = results[ig]
            f.write(f"  {ig}: rho={r['rho']:+.4f}, p={r['p']:.4f}, N={r['n']}, countries={r['n_countries']}\n")
    f.write(f"\nPWT Method (rgdpna):\n")
    f.write(f"  Pooled rho: {rho_all2:+.4f}, p={p_all2:.4f}\n")
    for ig in income_order:
        if ig in results_pwt:
            r = results_pwt[ig]
            f.write(f"  {ig}: rho={r['rho']:+.4f}, p={r['p']:.4f}, N={r['n']}, countries={r['n_countries']}\n")
    f.write(f"\nLOO (UMI, GDP-based): {n_negative}/{len(loo_df)} negative, {n_sig}/{len(loo_df)} significant\n")

print(f"\n结果已保存至: {output_path}")
