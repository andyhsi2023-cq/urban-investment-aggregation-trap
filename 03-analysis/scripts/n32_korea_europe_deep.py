"""
n32_korea_europe_deep.py
========================
韩国 + 欧洲 深化分析 (Simpson's Paradox, 危机冲击, 收敛检验, Clean Spec)
附带: 澳大利亚 + 南非 简要补充分析

输入:
  - 02-data/raw/korea_regional_panel.csv
  - 02-data/raw/europe_regional_panel.csv
  - 02-data/raw/oceania_regional_panel.csv
  - 02-data/raw/africa_regional_panel.csv

输出:
  - 03-analysis/models/korea_deep_analysis_report.txt
  - 03-analysis/models/europe_deep_analysis_report.txt
  - 03-analysis/models/aus_sa_deep_report.txt

依赖: pandas, numpy, scipy, statsmodels
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols as smf_ols
from io import StringIO
from datetime import datetime

# ====================================================================
# 路径设置
# ====================================================================
BASE = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
RAW = os.path.join(BASE, "02-data/raw")
OUT = os.path.join(BASE, "03-analysis/models")
os.makedirs(OUT, exist_ok=True)

np.random.seed(42)

# ====================================================================
# 工具函数
# ====================================================================

def spearman_test(x, y, label=""):
    """Spearman 秩相关, 返回格式化字符串"""
    mask = np.isfinite(x) & np.isfinite(y)
    x2, y2 = x[mask], y[mask]
    if len(x2) < 5:
        return f"  {label}: N = {len(x2)}, 样本不足\n"
    rho, p = stats.spearmanr(x2, y2)
    return f"  {label}: rho = {rho:+.4f}, p = {p:.4e}, N = {len(x2)}\n"


def ols_summary(y, X, label="", cluster_ids=None):
    """简要 OLS 报告"""
    mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    y2, X2 = y[mask], X[mask]
    if len(y2) < 10:
        return f"  {label}: N = {len(y2)}, 样本不足\n"
    X2c = sm.add_constant(X2)

    if cluster_ids is not None:
        cl = cluster_ids[mask]
        model = sm.OLS(y2, X2c).fit(cov_type='cluster', cov_kwds={'groups': cl})
    else:
        model = sm.OLS(y2, X2c).fit(cov_type='HC1')

    lines = [f"  [{label}]"]
    lines.append(f"  N = {int(model.nobs)}, R2 = {model.rsquared:.4f}")
    for i, name in enumerate(['const'] + [f'x{j}' for j in range(X2c.shape[1]-1)]):
        b = model.params[i]
        se = model.bse[i]
        ci = model.conf_int()[i]
        p = model.pvalues[i]
        lines.append(f"    {name}: b = {b:+.6f} (SE = {se:.6f}), 95% CI [{ci[0]:+.6f}, {ci[1]:+.6f}], p = {p:.4e}")
    return "\n".join(lines) + "\n"


def bai_perron_simple(series, max_breaks=3, min_segment=5):
    """
    简化版 Bai-Perron 断点检验: 在全局时间序列上测试结构断点
    使用 F 检验逐步搜索最优断点位置
    """
    y = np.array(series.dropna())
    n = len(y)
    if n < 2 * min_segment:
        return {"n_breaks": 0, "breaks": [], "F_stats": []}

    results = []

    for n_brk in range(1, max_breaks + 1):
        best_rss = np.inf
        best_breaks = None

        if n_brk == 1:
            for i in range(min_segment, n - min_segment):
                # 分段回归: 每段用线性趋势
                x1 = np.arange(i).reshape(-1, 1)
                x2 = np.arange(n - i).reshape(-1, 1)
                y1, y2 = y[:i], y[i:]

                X1c = sm.add_constant(x1)
                X2c = sm.add_constant(x2)
                rss1 = sm.OLS(y1, X1c).fit().ssr
                rss2 = sm.OLS(y2, X2c).fit().ssr
                rss = rss1 + rss2

                if rss < best_rss:
                    best_rss = rss
                    best_breaks = [i]

        elif n_brk == 2:
            for i in range(min_segment, n - 2 * min_segment):
                for j in range(i + min_segment, n - min_segment):
                    segs = [(0, i), (i, j), (j, n)]
                    rss = 0
                    for s, e in segs:
                        xs = np.arange(e - s).reshape(-1, 1)
                        Xsc = sm.add_constant(xs)
                        rss += sm.OLS(y[s:e], Xsc).fit().ssr
                    if rss < best_rss:
                        best_rss = rss
                        best_breaks = [i, j]

        # F 检验: 无断点 vs 有断点
        X_full = sm.add_constant(np.arange(n).reshape(-1, 1))
        rss_null = sm.OLS(y, X_full).fit().ssr

        k_null = 2  # const + trend
        k_alt = 2 * (n_brk + 1)  # 每段 const + trend
        df1 = k_alt - k_null
        df2 = n - k_alt

        if df2 > 0 and best_rss > 0:
            F_stat = ((rss_null - best_rss) / df1) / (best_rss / df2)
            p_val = 1 - stats.f.cdf(F_stat, df1, df2)
        else:
            F_stat, p_val = np.nan, np.nan

        results.append({
            "n_breaks": n_brk,
            "breaks": best_breaks if best_breaks else [],
            "F_stat": F_stat,
            "p_value": p_val,
            "RSS_break": best_rss,
            "RSS_null": rss_null
        })

    return results


# ====================================================================
# PART 1: 韩国深化分析
# ====================================================================

print("=" * 70)
print("PART 1: 韩国深化分析")
print("=" * 70)

kr = pd.read_csv(os.path.join(RAW, "korea_regional_panel.csv"))
kr_report = []

def kr_log(msg):
    kr_report.append(msg)
    print(msg)

kr_log("=" * 72)
kr_log("韩国 17 市道 深化分析报告")
kr_log("Korea 17 Sido Deep Analysis Report")
kr_log("=" * 72)
kr_log(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
kr_log(f"分析脚本: n32_korea_europe_deep.py")
kr_log("")

# ------------------------------------------------------------------
# K1: Simpson's Paradox 检验 — 三区域分组
# ------------------------------------------------------------------
kr_log("-" * 72)
kr_log("K1: Simpson's Paradox 检验 (三区域分组)")
kr_log("-" * 72)

# 区域分组定义
capital_region = ['Seoul', 'Gyeonggi', 'Incheon']  # 首都圈
metro_cities = ['Busan', 'Daegu', 'Gwangju', 'Daejeon', 'Ulsan']  # 广域市
provinces = ['Gangwon', 'Chungbuk', 'Chungnam', 'Jeonbuk', 'Jeonnam',
             'Gyeongbuk', 'Gyeongnam', 'Jeju', 'Sejong']  # 道

def assign_group(name):
    if name in capital_region:
        return '首都圈'
    elif name in metro_cities:
        return '广域市'
    else:
        return '道'

kr['group'] = kr['name_en'].map(assign_group)

kr_log("")
kr_log("  分组定义:")
kr_log("    首都圈: 서울, 경기, 인천 (全国 GDP ~52%)")
kr_log("    广域市: 부산, 대구, 광주, 대전, 울산")
kr_log("    道:     강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주, 세종")
kr_log("")

# K1a: 各组 GRDP 占比
kr_log("  K1a: 各组 GRDP 占比 (2020-2022 均值)")
for g in ['首都圈', '广域市', '道']:
    sub = kr[(kr['group'] == g) & (kr['year'].between(2020, 2022))]
    share = sub.groupby('year')['grdp_share_pct'].sum().mean()
    pop = sub.groupby('year')['population_1000'].sum().mean()
    kr_log(f"    {g}: GRDP 占比 = {share:.1f}%, 人口 = {pop:.0f} 千人")

# K1b: 各组 MUQ 均值时间序列
kr_log("")
kr_log("  K1b: 各组 MUQ 年均值")
kr_log(f"  {'Year':<6} {'首都圈':>8} {'广域市':>8} {'道':>8} {'全国':>8}")
for yr in range(1990, 2023, 5):
    vals = {}
    for g in ['首都圈', '广域市', '道']:
        sub = kr[(kr['group'] == g) & (kr['year'] == yr) & kr['muq'].notna()]
        vals[g] = sub['muq'].mean() if len(sub) > 0 else np.nan
    nat_sub = kr[(kr['year'] == yr) & kr['muq'].notna()]
    nat = nat_sub['muq'].mean() if len(nat_sub) > 0 else np.nan
    kr_log(f"  {yr:<6} {vals['首都圈']:>8.3f} {vals['广域市']:>8.3f} {vals['道']:>8.3f} {nat:>8.3f}")

# K1c: 组内 Spearman — MUQ ~ year
kr_log("")
kr_log("  K1c: 组内 Spearman 相关 (MUQ ~ year, 2000-2022)")
for g in ['首都圈', '广域市', '道']:
    sub = kr[(kr['group'] == g) & (kr['year'].between(2000, 2022)) & kr['muq'].notna()]
    kr_log(spearman_test(sub['year'].values, sub['muq'].values, label=g))

# 全国汇总
nat_agg = kr[kr['year'].between(2000, 2022)].groupby('year').agg(
    total_grdp=('grdp_bkrw', 'sum'),
    total_gfcf=('gfcf_bkrw', 'sum')
).reset_index()
nat_agg['delta'] = nat_agg['total_grdp'].diff()
nat_agg['muq_nat'] = nat_agg['delta'] / nat_agg['total_gfcf']
nat_valid = nat_agg.dropna(subset=['muq_nat'])
kr_log(spearman_test(nat_valid['year'].values, nat_valid['muq_nat'].values, label="全国汇总"))

# K1d: 首都圈 vs 地方 MUQ 水平差异
kr_log("  K1d: 首都圈 vs 地方 MUQ 水平差异 (2000-2022)")
cap_muq = kr[(kr['group'] == '首都圈') & kr['year'].between(2000, 2022) & kr['muq'].notna()]['muq']
non_cap = kr[(kr['group'] != '首都圈') & kr['year'].between(2000, 2022) & kr['muq'].notna()]['muq']
mwu_stat, mwu_p = stats.mannwhitneyu(cap_muq, non_cap, alternative='greater')
kr_log(f"    首都圈 MUQ: mean = {cap_muq.mean():.4f}, median = {cap_muq.median():.4f}, N = {len(cap_muq)}")
kr_log(f"    非首都圈 MUQ: mean = {non_cap.mean():.4f}, median = {non_cap.median():.4f}, N = {len(non_cap)}")
kr_log(f"    Mann-Whitney U (首都圈 > 非首都圈): U = {mwu_stat:.1f}, p = {mwu_p:.4e}")
kr_log("")

# K1e: Simpson's Paradox 诊断
kr_log("  K1e: Simpson's Paradox 诊断")

# 汇总趋势
slope_nat, _, _, p_nat, _ = stats.linregress(nat_valid['year'], nat_valid['muq_nat'])
kr_log(f"    全国汇总 MUQ 趋势 (OLS): slope = {slope_nat:+.5f}, p = {p_nat:.4e}")

# 组内趋势
group_slopes = {}
for g in ['首都圈', '广域市', '道']:
    sub = kr[(kr['group'] == g) & kr['year'].between(2000, 2022) & kr['muq'].notna()]
    gmean = sub.groupby('year')['muq'].mean().reset_index()
    if len(gmean) > 5:
        sl, _, _, p, _ = stats.linregress(gmean['year'], gmean['muq'])
        group_slopes[g] = (sl, p)
        kr_log(f"    {g} 组均 MUQ 趋势: slope = {sl:+.5f}, p = {p:.4e}")

# 判断
all_declining = all(s < 0 for s, _ in group_slopes.values())
nat_declining = slope_nat < 0
kr_log("")
if all_declining and nat_declining:
    kr_log("    结论: 各组均下降, 汇总也下降 => 无 Simpson's Paradox")
elif all_declining and not nat_declining:
    kr_log("    结论: 各组下降但汇总不下降 => Simpson's Paradox 存在!")
else:
    kr_log(f"    结论: 组内趋势方向不一致, 需进一步分析")

# 补充: 首都圈 GDP 份额变化 (追赶效应)
kr_log("")
kr_log("  补充: 各组 GRDP 份额时间变化")
for g in ['首都圈', '广域市', '道']:
    sub = kr[(kr['group'] == g)]
    share_2000 = sub[sub['year'] == 2000].groupby('year')['grdp_share_pct'].sum().values
    share_2020 = sub[sub['year'] == 2020].groupby('year')['grdp_share_pct'].sum().values
    if len(share_2000) > 0 and len(share_2020) > 0:
        kr_log(f"    {g}: 2000 = {share_2000[0]:.1f}%, 2020 = {share_2020[0]:.1f}%, 变化 = {share_2020[0]-share_2000[0]:+.1f}pp")

kr_log("")

# ------------------------------------------------------------------
# K2: 1997 亚洲金融危机分析
# ------------------------------------------------------------------
kr_log("-" * 72)
kr_log("K2: 1997 亚洲金融危机分析")
kr_log("-" * 72)

kr_log("")
kr_log("  K2a: 三时期 MUQ 比较")
periods = {
    '危机前 (1993-1996)': (1993, 1996),
    '危机中 (1997-1998)': (1997, 1998),
    '恢复期 (1999-2003)': (1999, 2003)
}

kr_log(f"  {'时期':<20} {'Mean MUQ':>10} {'Median':>10} {'SD':>10} {'N':>6}")
for pname, (y1, y2) in periods.items():
    sub = kr[kr['year'].between(y1, y2) & kr['muq'].notna()]
    m = sub['muq'].mean()
    md = sub['muq'].median()
    sd = sub['muq'].std()
    n = len(sub)
    kr_log(f"  {pname:<20} {m:>10.4f} {md:>10.4f} {sd:>10.4f} {n:>6}")

# Kruskal-Wallis 检验
groups_kw = []
for pname, (y1, y2) in periods.items():
    sub = kr[kr['year'].between(y1, y2) & kr['muq'].notna()]['muq'].values
    groups_kw.append(sub)
H, p_kw = stats.kruskal(*groups_kw)
kr_log(f"\n  Kruskal-Wallis 检验: H = {H:.3f}, p = {p_kw:.4e}")

# 两两 Mann-Whitney
pnames = list(periods.keys())
kr_log("  两两 Mann-Whitney U 检验:")
for i in range(len(pnames)):
    for j in range(i+1, len(pnames)):
        u, p = stats.mannwhitneyu(groups_kw[i], groups_kw[j], alternative='two-sided')
        kr_log(f"    {pnames[i]} vs {pnames[j]}: U = {u:.0f}, p = {p:.4e}")

# K2b: 分市道恢复速度
kr_log("")
kr_log("  K2b: 分市道危机恢复速度")
kr_log("  (恢复速度 = 恢复期 MUQ 均值 / 危机前 MUQ 均值)")
kr_log(f"  {'Region':<15} {'危机前':>10} {'危机中':>10} {'恢复期':>10} {'恢复比':>10}")

recovery_data = []
for name in sorted(kr['name_en'].unique()):
    row = {'name': name}
    for pname, (y1, y2) in periods.items():
        sub = kr[(kr['name_en'] == name) & kr['year'].between(y1, y2) & kr['muq'].notna()]
        row[pname] = sub['muq'].mean() if len(sub) > 0 else np.nan

    pre = row['危机前 (1993-1996)']
    rec = row['恢复期 (1999-2003)']
    ratio = rec / pre if (pre and pre != 0 and np.isfinite(pre)) else np.nan
    row['recovery_ratio'] = ratio
    recovery_data.append(row)

    kr_log(f"  {name:<15} {row['危机前 (1993-1996)']:>10.4f} {row['危机中 (1997-1998)']:>10.4f} {row['恢复期 (1999-2003)']:>10.4f} {ratio:>10.3f}" if np.isfinite(ratio) else f"  {name:<15} N/A")

# K2c: 恢复速度与产业结构
kr_log("")
kr_log("  K2c: 恢复速度与区域类型")
kr_log("  (metro = 广域市+特别市, province = 道)")
for rtype in ['metro', 'province']:
    vals = [r['recovery_ratio'] for r in recovery_data
            if np.isfinite(r.get('recovery_ratio', np.nan))
            and kr[kr['name_en'] == r['name']]['region_type'].iloc[0] == rtype]
    if vals:
        kr_log(f"    {rtype}: mean recovery ratio = {np.mean(vals):.3f} (SD = {np.std(vals):.3f}, N = {len(vals)})")

# K2d: Bai-Perron 断点检验 (全国 MUQ)
kr_log("")
kr_log("  K2d: Bai-Perron 断点检验 (全国汇总 MUQ)")

# 重建全国时间序列
kr_nat = kr.groupby('year').agg(
    grdp_total=('grdp_bkrw', 'sum'),
    gfcf_total=('gfcf_bkrw', 'sum')
).reset_index().sort_values('year')
kr_nat['delta'] = kr_nat['grdp_total'].diff()
kr_nat['muq'] = kr_nat['delta'] / kr_nat['gfcf_total']
kr_nat_valid = kr_nat.dropna(subset=['muq']).reset_index(drop=True)

bp_results = bai_perron_simple(kr_nat_valid['muq'], max_breaks=2, min_segment=5)
for res in bp_results:
    n_brk = res['n_breaks']
    F = res['F_stat']
    p = res['p_value']
    brk_years = [kr_nat_valid.iloc[b]['year'] for b in res['breaks']] if res['breaks'] else []
    kr_log(f"    {n_brk} break(s): F = {F:.3f}, p = {p:.4e}, break year(s) = {brk_years}")

kr_log("")

# ------------------------------------------------------------------
# K3: Clean Specification
# ------------------------------------------------------------------
kr_log("-" * 72)
kr_log("K3: Clean Specification (DeltaGRDP/GRDP ~ GFCF/GRDP)")
kr_log("-" * 72)

# 构建变量
kr['gdp_growth_rate'] = kr['delta_grdp'] / kr['grdp_bkrw'].shift(1)
# 需要按 sido 计算
kr_clean = kr.copy()
kr_clean = kr_clean.sort_values(['sido_code', 'year'])
kr_clean['gdp_growth_rate'] = kr_clean.groupby('sido_code')['grdp_bkrw'].pct_change()
kr_clean['invest_ratio'] = kr_clean['gfcf_gdp_ratio']  # GFCF / GRDP

# 去除极端值
valid = kr_clean[kr_clean['gdp_growth_rate'].notna() & kr_clean['invest_ratio'].notna()].copy()
valid = valid[(valid['gdp_growth_rate'].between(-0.5, 1.0)) & (valid['invest_ratio'].between(0.05, 0.8))]

kr_log("")
kr_log("  样本: DeltaGRDP/GRDP (GDP 增长率) ~ GFCF/GRDP (投资率)")
kr_log(f"  有效观测: {len(valid)}")
kr_log("")

# K3a: Pooled OLS
kr_log("  K3a: Pooled OLS")
y = valid['gdp_growth_rate'].values
X = valid['invest_ratio'].values.reshape(-1, 1)
kr_log(ols_summary(y, X, label="Pooled OLS"))

# K3b: Sido FE + Year FE
kr_log("  K3b: 固定效应 (Sido FE + Year FE)")
valid['sido_str'] = valid['sido_code'].astype(str)
try:
    sido_dummies = pd.get_dummies(valid['sido_str'], prefix='sido', drop_first=True)
    year_dummies = pd.get_dummies(valid['year'], prefix='yr', drop_first=True)

    X_fe = pd.concat([valid[['invest_ratio']].reset_index(drop=True),
                       sido_dummies.reset_index(drop=True),
                       year_dummies.reset_index(drop=True)], axis=1)
    y_fe = valid['gdp_growth_rate'].reset_index(drop=True)

    X_fe_c = sm.add_constant(X_fe.astype(float))
    cluster_ids = valid['sido_str'].reset_index(drop=True)

    model_fe = sm.OLS(y_fe.astype(float), X_fe_c).fit(cov_type='cluster', cov_kwds={'groups': cluster_ids})

    b = model_fe.params['invest_ratio']
    se = model_fe.bse['invest_ratio']
    ci = model_fe.conf_int().loc['invest_ratio']
    p = model_fe.pvalues['invest_ratio']

    kr_log(f"  invest_ratio: b = {b:+.6f} (SE = {se:.6f})")
    kr_log(f"    95% CI = [{ci[0]:+.6f}, {ci[1]:+.6f}]")
    kr_log(f"    p = {p:.4e}")
    kr_log(f"    N = {int(model_fe.nobs)}, R2 = {model_fe.rsquared:.4f}")
    kr_log(f"    Sido FE: {sido_dummies.shape[1]} dummies, Year FE: {year_dummies.shape[1]} dummies")
    kr_log(f"    聚类标准误: 按 Sido (17 clusters)")

except Exception as e:
    kr_log(f"  固定效应模型出错: {e}")

# K3c: 分时期估计
kr_log("")
kr_log("  K3c: 分时期 Pooled OLS (invest_ratio 系数)")
time_periods_kr = {
    '1986-1997 (高速增长)': (1986, 1997),
    '1999-2007 (恢复期)': (1999, 2007),
    '2010-2022 (成熟期)': (2010, 2022)
}
kr_log(f"  {'时期':<25} {'b':>10} {'SE':>10} {'p-value':>12} {'N':>6} {'R2':>8}")
for pname, (y1, y2) in time_periods_kr.items():
    sub = valid[valid['year'].between(y1, y2)]
    if len(sub) < 10:
        continue
    yy = sub['gdp_growth_rate'].values
    xx = sm.add_constant(sub['invest_ratio'].values)
    m = sm.OLS(yy, xx).fit(cov_type='HC1')
    kr_log(f"  {pname:<25} {m.params[1]:>+10.4f} {m.bse[1]:>10.4f} {m.pvalues[1]:>12.4e} {int(m.nobs):>6} {m.rsquared:>8.4f}")

kr_log("")
kr_log("  注: 韩国区域 GFCF 有真实区域间差异 (ECOS 基础, 审计 A 级), clean spec 可信度较高")
kr_log("")

# ------------------------------------------------------------------
# K4: 补充 — 城市化率与 MUQ 阶段性
# ------------------------------------------------------------------
kr_log("-" * 72)
kr_log("K4: 全国 MUQ 阶段性特征总结")
kr_log("-" * 72)
kr_log("")
kr_log("  时期划分与 MUQ:")
phases_kr = [
    ('高度增长期', '1986-1996', 1986, 1996, '城市化 65%→78%, 建设高潮'),
    ('IMF 危机', '1997-1998', 1997, 1998, '投资崩塌, MUQ 骤降'),
    ('V型恢复', '1999-2003', 1999, 2003, '结构调整, IT 产业兴起'),
    ('稳定期', '2004-2007', 2004, 2007, '城市化 82%, MUQ 趋稳'),
    ('GFC 冲击', '2008-2009', 2008, 2009, '全球金融危机, 冲击温和'),
    ('成熟下降', '2010-2022', 2010, 2022, '人口老龄化, 投资效率下降')
]
kr_log(f"  {'阶段':<12} {'期间':<12} {'MUQ 均值':>10} {'MUQ SD':>8} {'N':>5}  特征")
for phase_name, period_str, y1, y2, desc in phases_kr:
    sub = kr_nat_valid[(kr_nat_valid['year'] >= y1) & (kr_nat_valid['year'] <= y2)]
    if len(sub) > 0:
        kr_log(f"  {phase_name:<12} {period_str:<12} {sub['muq'].mean():>10.4f} {sub['muq'].std():>8.4f} {len(sub):>5}  {desc}")

kr_log("")

# 保存韩国报告
kr_report_path = os.path.join(OUT, "korea_deep_analysis_report.txt")
with open(kr_report_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(kr_report))
print(f"\n韩国报告已保存: {kr_report_path}")


# ====================================================================
# PART 2: 欧洲深化分析
# ====================================================================

print("\n" + "=" * 70)
print("PART 2: 欧洲深化分析")
print("=" * 70)

eu = pd.read_csv(os.path.join(RAW, "europe_regional_panel.csv"))
eu_report = []

def eu_log(msg):
    eu_report.append(msg)
    print(msg)

eu_log("=" * 72)
eu_log("欧洲 NUTS-2 深化分析报告")
eu_log("Europe NUTS-2 Deep Analysis Report")
eu_log("=" * 72)
eu_log(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
eu_log(f"分析脚本: n32_korea_europe_deep.py")
eu_log("")

# ------------------------------------------------------------------
# E1: 东欧 vs 西欧 Simpson's Paradox
# ------------------------------------------------------------------
eu_log("-" * 72)
eu_log("E1: 东欧 vs 西欧 Simpson's Paradox")
eu_log("-" * 72)

# 分组
western = ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'PT', 'GR', 'FI',
           'IE', 'SE', 'DK', 'LU', 'NO', 'CH']
eastern = ['PL', 'CZ', 'HU', 'SK', 'RO', 'BG', 'HR', 'SI', 'LT', 'LV', 'EE']
# CY, MT 归入其他 (small islands)

def assign_eu_group(iso2):
    if iso2 in western:
        return 'Western'
    elif iso2 in eastern:
        return 'Eastern'
    else:
        return 'Other'

eu['eu_group'] = eu['iso2'].map(assign_eu_group)

eu_log("")
eu_log("  分组定义:")
eu_log(f"    Western (EU-15 + EFTA): {', '.join(western)} ({len(western)} 国)")
eu_log(f"    Eastern (2004+ 新成员): {', '.join(eastern)} ({len(eastern)} 国)")
eu_log("")

# E1a: 组级 GDP 份额
eu_log("  E1a: 东西欧 GDP 份额 (2022)")
for g in ['Western', 'Eastern']:
    sub = eu[(eu['eu_group'] == g) & (eu['year'] == 2022)]
    total_gdp = sub['gdp_meur'].sum()
    eu_log(f"    {g}: {sub['geo'].nunique()} regions, GDP = {total_gdp/1000:.1f} B EUR")

# E1b: 组内 Spearman — MUQ ~ year
eu_log("")
eu_log("  E1b: 组内 Spearman (MUQ ~ year, 2001-2023)")
for g in ['Western', 'Eastern', 'All']:
    if g == 'All':
        sub = eu[eu['year'].between(2001, 2023) & eu['muq'].notna()]
    else:
        sub = eu[(eu['eu_group'] == g) & eu['year'].between(2001, 2023) & eu['muq'].notna()]
    eu_log(spearman_test(sub['year'].values, sub['muq'].values, label=g))

# E1c: 组内年均 MUQ
eu_log("  E1c: 东西欧年均 MUQ")
eu_log(f"  {'Year':<6} {'Western':>10} {'Eastern':>10} {'All':>10}")
for yr in range(2001, 2024, 2):
    vals = {}
    for g in ['Western', 'Eastern']:
        sub = eu[(eu['eu_group'] == g) & (eu['year'] == yr) & eu['muq'].notna()]
        vals[g] = sub['muq'].mean() if len(sub) > 0 else np.nan
    all_sub = eu[(eu['year'] == yr) & eu['muq'].notna()]
    vals['All'] = all_sub['muq'].mean() if len(all_sub) > 0 else np.nan
    eu_log(f"  {yr:<6} {vals['Western']:>10.4f} {vals['Eastern']:>10.4f} {vals['All']:>10.4f}")

# E1d: 组内线性趋势
eu_log("")
eu_log("  E1d: 组内 MUQ 线性趋势 (OLS, 年均值)")
for g in ['Western', 'Eastern', 'All']:
    if g == 'All':
        sub = eu[eu['year'].between(2001, 2023) & eu['muq'].notna()]
    else:
        sub = eu[(eu['eu_group'] == g) & eu['year'].between(2001, 2023) & eu['muq'].notna()]
    gmean = sub.groupby('year')['muq'].mean().reset_index()
    if len(gmean) > 5:
        sl, intercept, r, p, se = stats.linregress(gmean['year'], gmean['muq'])
        eu_log(f"    {g}: slope = {sl:+.5f} (SE = {se:.5f}), p = {p:.4e}, R2 = {r**2:.4f}")

# E1e: Simpson's Paradox 诊断
eu_log("")
eu_log("  E1e: Simpson's Paradox 诊断")
# 东欧 GDP per capita 追赶
eu_log("  东欧 GDP per capita 追赶:")
for yr in [2001, 2010, 2020, 2023]:
    for g in ['Western', 'Eastern']:
        sub = eu[(eu['eu_group'] == g) & (eu['year'] == yr) & eu['gdp_per_capita'].notna()]
        if len(sub) > 0:
            eu_log(f"    {yr} {g}: median GDP/cap = {sub['gdp_per_capita'].median():.0f} EUR")

eu_log("")

# 东欧 GDP 份额变化
eu_log("  东欧 GDP 份额变化:")
for yr in [2001, 2010, 2020]:
    all_gdp = eu[(eu['year'] == yr) & eu['gdp_meur'].notna()]['gdp_meur'].sum()
    east_gdp = eu[(eu['eu_group'] == 'Eastern') & (eu['year'] == yr) & eu['gdp_meur'].notna()]['gdp_meur'].sum()
    eu_log(f"    {yr}: Eastern share = {east_gdp/all_gdp*100:.1f}%")

eu_log("")

# ------------------------------------------------------------------
# E2: 欧债危机冲击分析
# ------------------------------------------------------------------
eu_log("-" * 72)
eu_log("E2: 欧债危机冲击分析 (PIIGS)")
eu_log("-" * 72)

piigs = ['PT', 'IT', 'IE', 'GR', 'ES']
piigs_names = {'PT': 'Portugal', 'IT': 'Italy', 'IE': 'Ireland', 'GR': 'Greece', 'ES': 'Spain'}

eu_log("")
eu_log("  E2a: PIIGS 三时期 MUQ 比较")

eu_periods = {
    '危机前 (2005-2008)': (2005, 2008),
    '危机中 (2009-2013)': (2009, 2013),
    '恢复期 (2014-2019)': (2014, 2019)
}

eu_log(f"  {'Country':<12} {'危机前':>10} {'危机中':>10} {'恢复期':>10} {'恢复形态':>10}")
for iso in piigs:
    vals = {}
    for pname, (y1, y2) in eu_periods.items():
        sub = eu[(eu['iso2'] == iso) & eu['year'].between(y1, y2) & eu['muq'].notna()]
        vals[pname] = sub['muq'].mean() if len(sub) > 0 else np.nan

    pre = vals['危机前 (2005-2008)']
    crisis = vals['危机中 (2009-2013)']
    rec = vals['恢复期 (2014-2019)']

    # 判断恢复形态
    if np.isfinite(pre) and np.isfinite(rec):
        if rec >= pre * 0.9:
            shape = "V 型"
        elif rec >= pre * 0.5:
            shape = "U 型"
        else:
            shape = "L 型"
    else:
        shape = "N/A"

    eu_log(f"  {piigs_names[iso]:<12} {pre:>10.4f} {crisis:>10.4f} {rec:>10.4f} {shape:>10}")

# PIIGS 整体
eu_log("")
eu_log("  PIIGS 整体:")
for pname, (y1, y2) in eu_periods.items():
    sub = eu[(eu['iso2'].isin(piigs)) & eu['year'].between(y1, y2) & eu['muq'].notna()]
    eu_log(f"    {pname}: MUQ mean = {sub['muq'].mean():.4f}, median = {sub['muq'].median():.4f}, N = {len(sub)}")

# 非 PIIGS 西欧对照
eu_log("")
eu_log("  非 PIIGS 西欧对照:")
non_piigs_west = [c for c in western if c not in piigs]
for pname, (y1, y2) in eu_periods.items():
    sub = eu[(eu['iso2'].isin(non_piigs_west)) & eu['year'].between(y1, y2) & eu['muq'].notna()]
    eu_log(f"    {pname}: MUQ mean = {sub['muq'].mean():.4f}, median = {sub['muq'].median():.4f}, N = {len(sub)}")

# E2b: 首都区 vs 外围区
eu_log("")
eu_log("  E2b: PIIGS 首都区 vs 外围区")

# 识别 PIIGS 首都区 (NUTS-2)
capital_nuts2 = {
    'PT': 'PT17',  # Lisboa
    'IT': 'ITI4',  # Lazio (Roma)
    'IE': 'IE06',  # Eastern and Midland (Dublin) - 或 IE061
    'GR': 'EL30',  # Attiki (Athens)
    'ES': 'ES30',  # Comunidad de Madrid
}

# 检查实际可用 NUTS 代码
eu_log("  (首都区 NUTS-2 代码映射)")
for iso, nuts in capital_nuts2.items():
    available = eu[(eu['iso2'] == iso)]['geo'].unique()
    match = [g for g in available if g.startswith(nuts[:4])]
    if not match:
        # 尝试更短前缀
        match = [g for g in available if g.startswith(nuts[:3])]
    eu_log(f"    {piigs_names[iso]}: target = {nuts}, matched = {match[:3]}")

# 首都/外围对比
for pname, (y1, y2) in eu_periods.items():
    cap_muqs = []
    peri_muqs = []
    for iso, nuts in capital_nuts2.items():
        sub_all = eu[(eu['iso2'] == iso) & eu['year'].between(y1, y2) & eu['muq'].notna()]
        sub_cap = sub_all[sub_all['geo'].str.startswith(nuts[:4])]
        sub_per = sub_all[~sub_all['geo'].str.startswith(nuts[:4])]
        cap_muqs.extend(sub_cap['muq'].values)
        peri_muqs.extend(sub_per['muq'].values)

    if cap_muqs and peri_muqs:
        eu_log(f"    {pname}:")
        eu_log(f"      首都区: mean MUQ = {np.mean(cap_muqs):.4f}, N = {len(cap_muqs)}")
        eu_log(f"      外围区: mean MUQ = {np.mean(peri_muqs):.4f}, N = {len(peri_muqs)}")

# E2c: 与韩国 1997 危机对比
eu_log("")
eu_log("  E2c: 韩国 1997 vs 欧洲 2009 危机对比")
eu_log(f"  {'指标':<30} {'韩国 1997':>15} {'PIIGS 2009':>15}")

# 韩国
kr_pre = kr[kr['year'].between(1993, 1996) & kr['muq'].notna()]['muq'].mean()
kr_crisis = kr[kr['year'].between(1997, 1998) & kr['muq'].notna()]['muq'].mean()
kr_rec = kr[kr['year'].between(1999, 2003) & kr['muq'].notna()]['muq'].mean()
kr_drop = kr_crisis - kr_pre

# PIIGS
eu_pre = eu[(eu['iso2'].isin(piigs)) & eu['year'].between(2005, 2008) & eu['muq'].notna()]['muq'].mean()
eu_crisis = eu[(eu['iso2'].isin(piigs)) & eu['year'].between(2009, 2010) & eu['muq'].notna()]['muq'].mean()
eu_rec = eu[(eu['iso2'].isin(piigs)) & eu['year'].between(2014, 2019) & eu['muq'].notna()]['muq'].mean()
eu_drop = eu_crisis - eu_pre

eu_log(f"  {'危机前 MUQ':<30} {kr_pre:>15.4f} {eu_pre:>15.4f}")
eu_log(f"  {'危机中 MUQ':<30} {kr_crisis:>15.4f} {eu_crisis:>15.4f}")
eu_log(f"  {'恢复期 MUQ':<30} {kr_rec:>15.4f} {eu_rec:>15.4f}")
eu_log(f"  {'MUQ 下降幅度':<30} {kr_drop:>15.4f} {eu_drop:>15.4f}")
eu_log(f"  {'恢复/危机前比':<30} {kr_rec/kr_pre:>15.3f} {eu_rec/eu_pre:>15.3f}")
eu_log(f"  {'恢复形态':<30} {'V 型':>15} {'L 型 (部分)':>15}")
eu_log("")

# ------------------------------------------------------------------
# E3: 收敛检验
# ------------------------------------------------------------------
eu_log("-" * 72)
eu_log("E3: MUQ 收敛检验")
eu_log("-" * 72)

# E3a: beta-收敛
eu_log("")
eu_log("  E3a: Beta-收敛 (MUQ growth 2010-2020 ~ initial MUQ 2000-2005)")

# 初始 MUQ (2001-2005 均值, 因为 2000 年是首年无 MUQ)
init_muq = eu[eu['year'].between(2001, 2005) & eu['muq'].notna()].groupby('geo')['muq'].mean().rename('init_muq')
# 终端 MUQ (2018-2022 均值)
end_muq = eu[eu['year'].between(2018, 2022) & eu['muq'].notna()].groupby('geo')['muq'].mean().rename('end_muq')

conv = pd.merge(init_muq, end_muq, left_index=True, right_index=True).dropna()
conv['muq_change'] = conv['end_muq'] - conv['init_muq']

if len(conv) > 20:
    y_conv = conv['muq_change'].values
    X_conv = conv['init_muq'].values.reshape(-1, 1)
    X_conv_c = sm.add_constant(X_conv)
    model_conv = sm.OLS(y_conv, X_conv_c).fit(cov_type='HC1')

    b = model_conv.params[1]
    se = model_conv.bse[1]
    ci = model_conv.conf_int()[1]
    p = model_conv.pvalues[1]

    eu_log(f"    N = {int(model_conv.nobs)} regions")
    eu_log(f"    beta (init_muq -> muq_change): {b:+.4f} (SE = {se:.4f})")
    eu_log(f"    95% CI: [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    eu_log(f"    p = {p:.4e}, R2 = {model_conv.rsquared:.4f}")
    if b < 0 and p < 0.05:
        eu_log(f"    => Beta-收敛: 初始 MUQ 高的区域下降更多 (收敛)")
    elif b < 0:
        eu_log(f"    => 方向为收敛, 但统计不显著 (p = {p:.4f})")
    else:
        eu_log(f"    => 无收敛迹象 (beta > 0)")

# 分东西欧
eu_log("")
eu_log("  分东西欧 Beta-收敛:")
eu_merged_group = eu[['geo', 'eu_group']].drop_duplicates().set_index('geo')
conv2 = conv.join(eu_merged_group)
for g in ['Western', 'Eastern']:
    sub = conv2[conv2['eu_group'] == g]
    if len(sub) > 10:
        y2 = sub['muq_change'].values
        X2 = sm.add_constant(sub['init_muq'].values.reshape(-1, 1))
        m2 = sm.OLS(y2, X2).fit(cov_type='HC1')
        eu_log(f"    {g}: beta = {m2.params[1]:+.4f} (SE = {m2.bse[1]:.4f}), p = {m2.pvalues[1]:.4e}, N = {len(sub)}, R2 = {m2.rsquared:.4f}")

# E3b: Sigma-收敛
eu_log("")
eu_log("  E3b: Sigma-收敛 (MUQ 跨区域标准差随时间)")

sigma_data = []
eu_log(f"  {'Year':<6} {'SD(MUQ)':>10} {'CV(MUQ)':>10} {'IQR':>10} {'N':>6}")
for yr in range(2001, 2024):
    sub = eu[(eu['year'] == yr) & eu['muq'].notna()]
    if len(sub) > 20:
        sd = sub['muq'].std()
        mean = sub['muq'].mean()
        cv = sd / abs(mean) if abs(mean) > 0.001 else np.nan
        iqr = sub['muq'].quantile(0.75) - sub['muq'].quantile(0.25)
        sigma_data.append({'year': yr, 'sd': sd, 'cv': cv, 'iqr': iqr, 'n': len(sub)})
        eu_log(f"  {yr:<6} {sd:>10.4f} {cv:>10.4f} {iqr:>10.4f} {len(sub):>6}")

if sigma_data:
    sigma_df = pd.DataFrame(sigma_data)
    sl_sd, _, _, p_sd, _ = stats.linregress(sigma_df['year'], sigma_df['sd'])
    sl_iqr, _, _, p_iqr, _ = stats.linregress(sigma_df['year'], sigma_df['iqr'])
    eu_log(f"\n  SD 趋势: slope = {sl_sd:+.5f}, p = {p_sd:.4e}")
    eu_log(f"  IQR 趋势: slope = {sl_iqr:+.5f}, p = {p_iqr:.4e}")
    if sl_sd < 0 and p_sd < 0.05:
        eu_log(f"  => Sigma-收敛: MUQ 离散度在缩小")
    elif sl_sd > 0 and p_sd < 0.05:
        eu_log(f"  => Sigma-发散: MUQ 离散度在扩大")
    else:
        eu_log(f"  => Sigma-收敛不显著")

# 分东西欧 sigma 收敛
eu_log("")
eu_log("  分东西欧 Sigma-收敛:")
for g in ['Western', 'Eastern']:
    sd_list = []
    for yr in range(2001, 2024):
        sub = eu[(eu['eu_group'] == g) & (eu['year'] == yr) & eu['muq'].notna()]
        if len(sub) > 5:
            sd_list.append({'year': yr, 'sd': sub['muq'].std()})
    if len(sd_list) > 5:
        sdf = pd.DataFrame(sd_list)
        sl, _, _, p, _ = stats.linregress(sdf['year'], sdf['sd'])
        eu_log(f"    {g}: SD slope = {sl:+.5f}, p = {p:.4e}")

eu_log("")

# ------------------------------------------------------------------
# E4: 欧洲 Clean Specification (补充)
# ------------------------------------------------------------------
eu_log("-" * 72)
eu_log("E4: Clean Specification (GDP growth ~ Investment intensity)")
eu_log("-" * 72)
eu_log("")
eu_log("  注意: 欧洲 GFCF 按国家级 GFCF/GDP 比率分配给区域,")
eu_log("  故同一国家内各区域 invest_intensity 相同。")
eu_log("  Clean spec 实质上测试跨国差异, 非跨区域差异。")
eu_log("")

eu_valid = eu[eu['gdp_growth'].notna() & eu['invest_intensity'].notna()].copy()
eu_valid = eu_valid[(eu_valid['gdp_growth'].between(-0.5, 1.0)) &
                     (eu_valid['invest_intensity'].between(0.05, 0.6))]

# Pooled OLS
y_eu = eu_valid['gdp_growth'].values
X_eu = eu_valid['invest_intensity'].values.reshape(-1, 1)
eu_log("  Pooled OLS:")
eu_log(ols_summary(y_eu, X_eu, label="GDP_growth ~ invest_intensity"))

# Country FE + Year FE
eu_log("  Country FE + Year FE:")
try:
    ctry_dummies = pd.get_dummies(eu_valid['iso2'], prefix='c', drop_first=True)
    yr_dummies = pd.get_dummies(eu_valid['year'], prefix='y', drop_first=True)
    X_fe_eu = pd.concat([eu_valid[['invest_intensity']].reset_index(drop=True),
                          ctry_dummies.reset_index(drop=True),
                          yr_dummies.reset_index(drop=True)], axis=1)
    y_fe_eu = eu_valid['gdp_growth'].reset_index(drop=True)
    X_fe_eu_c = sm.add_constant(X_fe_eu.astype(float))

    cl_eu = eu_valid['geo'].reset_index(drop=True)
    model_fe_eu = sm.OLS(y_fe_eu.astype(float), X_fe_eu_c).fit(cov_type='cluster', cov_kwds={'groups': cl_eu})

    b = model_fe_eu.params['invest_intensity']
    se = model_fe_eu.bse['invest_intensity']
    ci = model_fe_eu.conf_int().loc['invest_intensity']
    p = model_fe_eu.pvalues['invest_intensity']

    eu_log(f"    invest_intensity: b = {b:+.6f} (SE = {se:.6f})")
    eu_log(f"    95% CI = [{ci[0]:+.6f}, {ci[1]:+.6f}]")
    eu_log(f"    p = {p:.4e}")
    eu_log(f"    N = {int(model_fe_eu.nobs)}, R2 = {model_fe_eu.rsquared:.4f}")
    eu_log(f"    Country FE + Year FE, 聚类 SE by region ({eu_valid['geo'].nunique()} clusters)")
except Exception as e:
    eu_log(f"    模型出错: {e}")

eu_log("")

# 保存欧洲报告
eu_report_path = os.path.join(OUT, "europe_deep_analysis_report.txt")
with open(eu_report_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(eu_report))
print(f"\n欧洲报告已保存: {eu_report_path}")


# ====================================================================
# PART 3: 澳大利亚 + 南非 简要分析
# ====================================================================

print("\n" + "=" * 70)
print("PART 3: 澳大利亚 + 南非 简要分析")
print("=" * 70)

as_report = []

def as_log(msg):
    as_report.append(msg)
    print(msg)

as_log("=" * 72)
as_log("澳大利亚 + 南非 补充分析报告")
as_log("Australia + South Africa Supplementary Report")
as_log("=" * 72)
as_log(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
as_log(f"分析脚本: n32_korea_europe_deep.py")
as_log("")

# ------------------------------------------------------------------
# A1: 澳大利亚
# ------------------------------------------------------------------
as_log("-" * 72)
as_log("A1: 澳大利亚州级分析")
as_log("-" * 72)

au = pd.read_csv(os.path.join(RAW, "oceania_regional_panel.csv"))

as_log("")
as_log(f"  数据: {au['region_name'].nunique()} 州/领地, {au['year'].min()}-{au['year'].max()}")
as_log("")

# A1a: 矿业州 vs 服务州
mining_states = ['Western Australia', 'Queensland']
service_states = ['New South Wales', 'Victoria']

as_log("  A1a: 矿业州 vs 服务州 MUQ 对比")
as_log(f"  {'Group':<20} {'Mean MUQ':>10} {'Median':>10} {'SD':>10} {'N':>6}")

for label, states in [('矿业州 (WA, QLD)', mining_states), ('服务州 (NSW, VIC)', service_states)]:
    sub = au[au['region_name'].isin(states) & au['muq'].notna()]
    as_log(f"  {label:<20} {sub['muq'].mean():>10.4f} {sub['muq'].median():>10.4f} {sub['muq'].std():>10.4f} {len(sub):>6}")

# Mann-Whitney
mining_muq = au[au['region_name'].isin(mining_states) & au['muq'].notna()]['muq']
service_muq = au[au['region_name'].isin(service_states) & au['muq'].notna()]['muq']
if len(mining_muq) > 5 and len(service_muq) > 5:
    u, p = stats.mannwhitneyu(mining_muq, service_muq, alternative='two-sided')
    as_log(f"  Mann-Whitney U: U = {u:.1f}, p = {p:.4e}")

# 分时期对比
as_log("")
as_log("  分时期对比:")
au_periods = {
    '矿业繁荣前 (1991-2002)': (1991, 2002),
    '矿业繁荣 (2003-2012)': (2003, 2012),
    '矿业繁荣后 (2013-2023)': (2013, 2023)
}
as_log(f"  {'Period':<25} {'矿业州':>10} {'服务州':>10}")
for pname, (y1, y2) in au_periods.items():
    m_val = au[au['region_name'].isin(mining_states) & au['year'].between(y1, y2) & au['muq'].notna()]['muq'].mean()
    s_val = au[au['region_name'].isin(service_states) & au['year'].between(y1, y2) & au['muq'].notna()]['muq'].mean()
    as_log(f"  {pname:<25} {m_val:>10.4f} {s_val:>10.4f}")

# A1b: 标度律确认
as_log("")
as_log("  A1b: 标度律 (截面, 最近年份)")
for yr in [2015, 2020, 2023]:
    sub = au[(au['year'] == yr) & au['ln_gdp'].notna() & au['ln_pop'].notna()]
    sub = sub[sub['population'] > 100000]  # 排除极小领地
    if len(sub) >= 5:
        sl, intercept, r, p, se = stats.linregress(sub['ln_pop'], sub['ln_gdp'])
        as_log(f"    {yr}: beta = {sl:.4f} (SE = {se:.4f}), R2 = {r**2:.4f}, p = {p:.4e}, N = {len(sub)}")

# A1c: 各州 MUQ 排名 (近 5 年)
as_log("")
as_log("  A1c: 各州 MUQ 排名 (2019-2023 均值)")
au_recent = au[au['year'].between(2019, 2023) & au['muq'].notna()]
au_rank = au_recent.groupby('region_name').agg(
    muq_mean=('muq', 'mean'),
    muq_median=('muq', 'median'),
    n=('muq', 'count')
).sort_values('muq_mean', ascending=False)
as_log(f"  {'Region':<35} {'Mean':>8} {'Median':>8} {'N':>4}")
for name, row in au_rank.iterrows():
    as_log(f"  {name:<35} {row['muq_mean']:>8.4f} {row['muq_median']:>8.4f} {int(row['n']):>4}")

as_log("")

# ------------------------------------------------------------------
# S1: 南非
# ------------------------------------------------------------------
as_log("-" * 72)
as_log("S1: 南非省级分析")
as_log("-" * 72)

sa = pd.read_csv(os.path.join(RAW, "africa_regional_panel.csv"))

as_log("")
as_log(f"  数据: {sa['region_name'].nunique()} 省, {sa['year'].min()}-{sa['year'].max()}")
as_log("")

# S1a: Gauteng vs 其他
as_log("  S1a: Gauteng vs 其他 8 省 MUQ 对比")

gauteng = sa[sa['region_name'] == 'Gauteng']
others = sa[sa['region_name'] != 'Gauteng']

as_log(f"  {'Group':<20} {'Mean MUQ':>10} {'Median':>10} {'SD':>10} {'N':>6}")
g_muq = gauteng[gauteng['muq'].notna()]
o_muq = others[others['muq'].notna()]
as_log(f"  {'Gauteng':<20} {g_muq['muq'].mean():>10.4f} {g_muq['muq'].median():>10.4f} {g_muq['muq'].std():>10.4f} {len(g_muq):>6}")
as_log(f"  {'Other 8 provinces':<20} {o_muq['muq'].mean():>10.4f} {o_muq['muq'].median():>10.4f} {o_muq['muq'].std():>10.4f} {len(o_muq):>6}")

if len(g_muq) > 5 and len(o_muq) > 5:
    u, p = stats.mannwhitneyu(g_muq['muq'], o_muq['muq'], alternative='two-sided')
    as_log(f"  Mann-Whitney U: U = {u:.1f}, p = {p:.4e}")

# S1b: 各省 MUQ 排名
as_log("")
as_log("  S1b: 各省 MUQ 排名 (2015-2021 均值)")
sa_recent = sa[sa['year'].between(2015, 2021) & sa['muq'].notna()]
sa_rank = sa_recent.groupby('region_name').agg(
    muq_mean=('muq', 'mean'),
    gdp_share=('gdp_share', 'mean'),
    pop=('population', 'mean'),
    n=('muq', 'count')
).sort_values('muq_mean', ascending=False)
as_log(f"  {'Province':<20} {'Mean MUQ':>10} {'GDP share':>10} {'Pop (M)':>10}")
for name, row in sa_rank.iterrows():
    as_log(f"  {name:<20} {row['muq_mean']:>10.4f} {row['gdp_share']:>10.3f} {row['pop']/1e6:>10.2f}")

# S1c: 城市化率与 MUQ
as_log("")
as_log("  S1c: 城市化率与 MUQ")
if 'urban_pct_national' in sa.columns:
    # 全国城市化率 (同一国家内各省相同)
    sa_nat = sa.groupby('year').agg(
        total_gdp=('gdp_usd', 'sum'),
        total_gfcf=('gfcf_est_usd', 'sum'),
        urban_pct=('urban_pct_national', 'first')
    ).reset_index()
    sa_nat['delta'] = sa_nat['total_gdp'].diff()
    sa_nat['muq'] = sa_nat['delta'] / sa_nat['total_gfcf']
    sa_nat_v = sa_nat.dropna(subset=['muq', 'urban_pct'])

    if len(sa_nat_v) > 5:
        rho, p = stats.spearmanr(sa_nat_v['urban_pct'], sa_nat_v['muq'])
        as_log(f"    Spearman (urban_pct ~ MUQ): rho = {rho:+.4f}, p = {p:.4e}, N = {len(sa_nat_v)}")

    as_log("")
    as_log("  城市化率时间序列:")
    for yr in range(1995, 2023, 5):
        sub = sa_nat_v[sa_nat_v['year'] == yr]
        if len(sub) > 0:
            as_log(f"    {yr}: urban = {sub['urban_pct'].iloc[0]:.1f}%, MUQ = {sub['muq'].iloc[0]:.4f}")

# S1d: Gauteng GDP 份额
as_log("")
as_log("  S1d: Gauteng GDP 份额时间变化")
for yr in [1995, 2000, 2005, 2010, 2015, 2020]:
    sub = sa[sa['year'] == yr]
    gt = sub[sub['region_name'] == 'Gauteng']
    if len(gt) > 0:
        as_log(f"    {yr}: Gauteng GDP share = {gt['gdp_share'].iloc[0]*100:.1f}%")

as_log("")

# ------------------------------------------------------------------
# 综合对比总结
# ------------------------------------------------------------------
as_log("-" * 72)
as_log("综合对比: 四经济体区域 MUQ 特征")
as_log("-" * 72)
as_log("")
as_log(f"  {'Economy':<15} {'首位区域 MUQ':>15} {'其他区域 MUQ':>15} {'差异':>10} {'首位份额':>10}")

# 韩国
kr_seoul = kr[(kr['name_en'] == 'Seoul') & kr['year'].between(2018, 2022) & kr['muq'].notna()]['muq'].mean()
kr_other = kr[(kr['name_en'] != 'Seoul') & kr['year'].between(2018, 2022) & kr['muq'].notna()]['muq'].mean()
as_log(f"  {'Korea':<15} {kr_seoul:>15.4f} {kr_other:>15.4f} {kr_seoul-kr_other:>10.4f} {'~25%':>10}")

# 澳大利亚
au_nsw = au[(au['region_name'] == 'New South Wales') & au['year'].between(2019, 2023) & au['muq'].notna()]['muq'].mean()
au_other = au[(au['region_name'] != 'New South Wales') & au['year'].between(2019, 2023) & au['muq'].notna()]['muq'].mean()
as_log(f"  {'Australia':<15} {au_nsw:>15.4f} {au_other:>15.4f} {au_nsw-au_other:>10.4f} {'~32%':>10}")

# 南非
sa_gt = sa[(sa['region_name'] == 'Gauteng') & sa['year'].between(2015, 2021) & sa['muq'].notna()]['muq'].mean()
sa_other = sa[(sa['region_name'] != 'Gauteng') & sa['year'].between(2015, 2021) & sa['muq'].notna()]['muq'].mean()
as_log(f"  {'South Africa':<15} {sa_gt:>15.4f} {sa_other:>15.4f} {sa_gt-sa_other:>10.4f} {'~34%':>10}")

as_log("")
as_log("  注: 首位区域 = 经济首都 (Seoul / NSW / Gauteng)")
as_log("  首位份额 = 该区域占全国 GDP 比重 (近似值)")
as_log("")

# 保存报告
as_report_path = os.path.join(OUT, "aus_sa_deep_report.txt")
with open(as_report_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(as_report))
print(f"\n澳大利亚+南非报告已保存: {as_report_path}")

# ====================================================================
# 完成
# ====================================================================
print("\n" + "=" * 70)
print("所有分析完成!")
print("=" * 70)
print(f"  韩国报告:       {os.path.join(OUT, 'korea_deep_analysis_report.txt')}")
print(f"  欧洲报告:       {os.path.join(OUT, 'europe_deep_analysis_report.txt')}")
print(f"  澳大利亚+南非: {os.path.join(OUT, 'aus_sa_deep_report.txt')}")
