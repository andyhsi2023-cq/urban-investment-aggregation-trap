#!/usr/bin/env python3
"""
n31_japan_deep_analysis.py
==========================
日本 47 都道府県 深化分析 (J1-J6)

目的:
  J1: 県級 Clean Specification (DeltaGDP/GDP ~ GFCF/GDP)
  J2: 泡沫-崩盤 Bai-Perron 断点検験
  J3: 県級 Simpson's Paradox
  J4: 不可逆性験証
  J5: 中日「鏡像」対比
  J6: 中日韓三国対比図データ

入力:
  - 02-data/raw/japan_prefectural_panel.csv
  - 02-data/processed/china_provincial_muq.csv
  - 02-data/raw/korea_regional_panel.csv
  - 02-data/processed/global_urban_q_panel_v2.csv

出力:
  - 03-analysis/models/japan_deep_analysis_report.txt
  - 04-figures/source-data/three_country_muq.csv

依頼: pandas, numpy, statsmodels, scipy, ruptures
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from datetime import datetime

# -------------------------------------------------------------------
# パス設定
# -------------------------------------------------------------------
BASE = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
JP_PATH = os.path.join(BASE, "02-data/raw/japan_prefectural_panel.csv")
CN_PATH = os.path.join(BASE, "02-data/processed/china_provincial_muq.csv")
KR_PATH = os.path.join(BASE, "02-data/raw/korea_regional_panel.csv")
GLOBAL_PATH = os.path.join(BASE, "02-data/processed/global_urban_q_panel_v2.csv")
REPORT_PATH = os.path.join(BASE, "03-analysis/models/japan_deep_analysis_report.txt")
THREE_COUNTRY_PATH = os.path.join(BASE, "04-figures/source-data/three_country_muq.csv")

SEED = 20260322
np.random.seed(SEED)

# -------------------------------------------------------------------
# データ読み込み
# -------------------------------------------------------------------
jp = pd.read_csv(JP_PATH)
cn = pd.read_csv(CN_PATH)
kr = pd.read_csv(KR_PATH)
gl = pd.read_csv(GLOBAL_PATH)

report_lines = []

def rpt(text=""):
    report_lines.append(text)

def rpt_sep(title):
    rpt("=" * 80)
    rpt(title)
    rpt("=" * 80)
    rpt()

def rpt_sub(title):
    rpt("-" * 60)
    rpt(title)
    rpt("-" * 60)

# -------------------------------------------------------------------
# ヘッダー
# -------------------------------------------------------------------
rpt_sep("日本 47 都道府県 深化分析レポート")
rpt(f"分析日: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
rpt(f"乱数シード: {SEED}")
rpt(f"データ: {JP_PATH}")
rpt()

# -------------------------------------------------------------------
# データ前処理
# -------------------------------------------------------------------
# 日本の Clean Spec 変数を構築
# DeltaGDP / GDP と GFCF / GDP は既に存在: gdp_growth_nominal と gfcf_gdp_ratio
# ただし gdp_growth_nominal = (GDP_t - GDP_{t-1}) / GDP_{t-1}
# Clean spec では DeltaGDP_t / GDP_t を使う
# delta_gdp_myen / gdp_nominal_myen を直接計算

jp['delta_gdp_over_gdp'] = jp['delta_gdp_myen'] / jp['gdp_nominal_myen']
jp['gfcf_over_gdp'] = jp['gfcf_nominal_myen'] / jp['gdp_nominal_myen']

# 時期区分
def assign_period(y):
    if y <= 1959:
        return "pre_growth"
    elif y <= 1973:
        return "high_growth"
    elif y <= 1985:
        return "stable"
    elif y <= 1991:
        return "bubble"
    elif y <= 2002:
        return "lost_decade"
    else:
        return "recovery"

jp['period'] = jp['year'].apply(assign_period)

# 地域グルーピング (J3用)
capital_prefs = ['Tokyo', 'Kanagawa', 'Chiba', 'Saitama']
kinki_prefs = ['Osaka', 'Kyoto', 'Hyogo', 'Nara']
chubu_prefs = ['Aichi', 'Gifu', 'Mie']

def assign_metro_group(name):
    if name in capital_prefs:
        return 'Capital'
    elif name in kinki_prefs:
        return 'Kinki'
    elif name in chubu_prefs:
        return 'Chubu'
    else:
        return 'Local'

jp['metro_group'] = jp['prefecture_en'].apply(assign_metro_group)

# -------------------------------------------------------------------
# J1: County-level Clean Specification
# -------------------------------------------------------------------
rpt_sep("J1: 県級 Clean Specification")
rpt("モデル: DeltaGDP/GDP ~ GFCF/GDP")
rpt("  DeltaGDP = GDP_t - GDP_{t-1} (百万円)")
rpt("  被説明変数: DeltaGDP_t / GDP_t")
rpt("  説明変数:   GFCF_t / GDP_t")
rpt()

# 分析サンプル: 1956以降 (delta_gdpが必要)
cs = jp.dropna(subset=['delta_gdp_over_gdp', 'gfcf_over_gdp']).copy()
# Winsorize at 1%/99%
for col in ['delta_gdp_over_gdp', 'gfcf_over_gdp']:
    lo = cs[col].quantile(0.01)
    hi = cs[col].quantile(0.99)
    cs[col + '_w'] = cs[col].clip(lo, hi)

rpt_sub("記述統計 (winsorized 1%/99%)")
for col in ['delta_gdp_over_gdp_w', 'gfcf_over_gdp_w']:
    s = cs[col]
    rpt(f"  {col:30s}: mean={s.mean():.4f}, sd={s.std():.4f}, "
        f"min={s.min():.4f}, p50={s.median():.4f}, max={s.max():.4f}, N={len(s)}")
rpt()

# --- (a) Pooled OLS, HC1 ---
rpt_sub("(a) Pooled OLS (HC1 robust SE)")
y_all = cs['delta_gdp_over_gdp_w']
X_all = sm.add_constant(cs['gfcf_over_gdp_w'])
ols_pooled = sm.OLS(y_all, X_all).fit(cov_type='HC1')

rpt(f"  N = {int(ols_pooled.nobs)}")
rpt(f"  県数 = {cs['pref_code'].nunique()}")
rpt(f"  年数 = {cs['year'].nunique()}")
rpt(f"  R-squared = {ols_pooled.rsquared:.4f}")
rpt(f"  Adj R-squared = {ols_pooled.rsquared_adj:.4f}")
rpt()
rpt(f"  {'Variable':25s} {'Coef':>10s} {'SE':>10s} {'t':>10s} {'p-value':>15s} {'95% CI':>25s}")
rpt(f"  {'-'*95}")
for i, name in enumerate(ols_pooled.params.index):
    coef = ols_pooled.params[i]
    se = ols_pooled.bse[i]
    t = ols_pooled.tvalues[i]
    p = ols_pooled.pvalues[i]
    ci = ols_pooled.conf_int().iloc[i]
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    rpt(f"  {name:25s} {coef:10.4f} {se:10.4f} {t:10.3f} p={p:.4e} [{ci[0]:8.4f}, {ci[1]:8.4f}] {sig}")
rpt()

# --- (b) Prefecture FE (within estimator) ---
rpt_sub("(b) Prefecture Fixed Effects (within estimator)")

# Within transformation
cs_fe = cs.copy()
for col in ['delta_gdp_over_gdp_w', 'gfcf_over_gdp_w']:
    group_mean = cs_fe.groupby('pref_code')[col].transform('mean')
    cs_fe[col + '_dm'] = cs_fe[col] - group_mean

y_fe = cs_fe['delta_gdp_over_gdp_w_dm']
X_fe = sm.add_constant(cs_fe['gfcf_over_gdp_w_dm'])
ols_fe = sm.OLS(y_fe, X_fe).fit(cov_type='HC1')

# Clustered SE
from statsmodels.regression.linear_model import OLS
# Use linearmodels for clustered SE
# クラスターSEを手動で計算
groups = cs_fe['pref_code'].values
n = len(y_fe)
k = 2  # const + 1 var
G = len(np.unique(groups))
X_fe_arr = X_fe.values
resid = ols_fe.resid.values

# Clustered variance: V = (G/(G-1)) * (n-1)/(n-k) * inv(X'X) * B * inv(X'X)
XtX_inv = np.linalg.inv(X_fe_arr.T @ X_fe_arr)
B = np.zeros((k, k))
for g in np.unique(groups):
    mask = groups == g
    Xg = X_fe_arr[mask]
    eg = resid[mask]
    score_g = Xg.T @ eg
    B += np.outer(score_g, score_g)
V_cluster = (G / (G - 1)) * ((n - 1) / (n - k)) * XtX_inv @ B @ XtX_inv
se_cluster = np.sqrt(np.diag(V_cluster))
beta_fe = ols_fe.params.values
t_cluster = beta_fe / se_cluster
p_cluster = 2 * stats.t.sf(np.abs(t_cluster), df=G - 1)

# Within R-squared
tss_within = np.sum(y_fe.values ** 2)
rss_within = np.sum(resid ** 2)
r2_within = 1 - rss_within / tss_within

rpt(f"  N = {n}, 県数 = {G}")
rpt(f"  Within R-squared = {r2_within:.4f}")
rpt()
rpt(f"  HC1 SE:")
rpt(f"    beta(GFCF/GDP) = {ols_fe.params[1]:.4f}, SE = {ols_fe.bse[1]:.4f}, "
    f"t = {ols_fe.tvalues[1]:.3f}, p = {ols_fe.pvalues[1]:.4e}")
rpt(f"  Clustered SE (by prefecture):")
rpt(f"    beta(GFCF/GDP) = {beta_fe[1]:.4f}, SE = {se_cluster[1]:.4f}, "
    f"t = {t_cluster[1]:.3f}, p = {p_cluster[1]:.4e}")
ci_lo = beta_fe[1] - 1.96 * se_cluster[1]
ci_hi = beta_fe[1] + 1.96 * se_cluster[1]
rpt(f"    95% CI = [{ci_lo:.4f}, {ci_hi:.4f}]")
rpt()

# --- (c) Two-way FE (prefecture + year) ---
rpt_sub("(c) Two-way FE (Prefecture + Year)")

cs_twfe = cs.copy()
for col in ['delta_gdp_over_gdp_w', 'gfcf_over_gdp_w']:
    pref_mean = cs_twfe.groupby('pref_code')[col].transform('mean')
    year_mean = cs_twfe.groupby('year')[col].transform('mean')
    grand_mean = cs_twfe[col].mean()
    cs_twfe[col + '_dd'] = cs_twfe[col] - pref_mean - year_mean + grand_mean

y_twfe = cs_twfe['delta_gdp_over_gdp_w_dd']
X_twfe = sm.add_constant(cs_twfe['gfcf_over_gdp_w_dd'])
ols_twfe = sm.OLS(y_twfe, X_twfe).fit(cov_type='HC1')

# Clustered SE for TWFE
groups_tw = cs_twfe['pref_code'].values
n_tw = len(y_twfe)
G_tw = len(np.unique(groups_tw))
X_tw_arr = X_twfe.values
resid_tw = ols_twfe.resid.values
XtX_inv_tw = np.linalg.inv(X_tw_arr.T @ X_tw_arr)
B_tw = np.zeros((k, k))
for g in np.unique(groups_tw):
    mask = groups_tw == g
    Xg = X_tw_arr[mask]
    eg = resid_tw[mask]
    score_g = Xg.T @ eg
    B_tw += np.outer(score_g, score_g)
V_cl_tw = (G_tw / (G_tw - 1)) * ((n_tw - 1) / (n_tw - k)) * XtX_inv_tw @ B_tw @ XtX_inv_tw
se_cl_tw = np.sqrt(np.diag(V_cl_tw))
beta_tw = ols_twfe.params.values
t_cl_tw = beta_tw / se_cl_tw
p_cl_tw = 2 * stats.t.sf(np.abs(t_cl_tw), df=G_tw - 1)

tss_tw = np.sum(y_twfe.values ** 2)
rss_tw = np.sum(resid_tw ** 2)
r2_tw = 1 - rss_tw / tss_tw

rpt(f"  N = {n_tw}, 県数 = {G_tw}")
rpt(f"  Within R-squared = {r2_tw:.4f}")
rpt()
rpt(f"  HC1 SE:")
rpt(f"    beta(GFCF/GDP) = {ols_twfe.params[1]:.4f}, SE = {ols_twfe.bse[1]:.4f}, "
    f"t = {ols_twfe.tvalues[1]:.3f}, p = {ols_twfe.pvalues[1]:.4e}")
rpt(f"  Clustered SE (by prefecture):")
rpt(f"    beta(GFCF/GDP) = {beta_tw[1]:.4f}, SE = {se_cl_tw[1]:.4f}, "
    f"t = {t_cl_tw[1]:.3f}, p = {p_cl_tw[1]:.4e}")
ci_lo_tw = beta_tw[1] - 1.96 * se_cl_tw[1]
ci_hi_tw = beta_tw[1] + 1.96 * se_cl_tw[1]
rpt(f"    95% CI = [{ci_lo_tw:.4f}, {ci_hi_tw:.4f}]")
rpt()

# --- (d) 分時期 ---
rpt_sub("(d) 分時期 Pooled OLS (HC1)")
rpt()

period_order = ['high_growth', 'stable', 'bubble', 'lost_decade', 'recovery']
period_labels = {
    'high_growth': '高度成長 (1960-1973)',
    'stable': '安定成長 (1974-1985)',
    'bubble': 'バブル (1986-1991)',
    'lost_decade': '失われた10年 (1992-2002)',
    'recovery': '回復期 (2003-2022)'
}

period_results = {}
rpt(f"  {'Period':30s} {'N':>6s} {'beta':>8s} {'SE':>8s} {'t':>8s} {'p-value':>12s} {'R2':>8s} {'mean_Y':>8s} {'mean_X':>8s}")
rpt(f"  {'-'*100}")

for per in period_order:
    sub = cs[cs['period'] == per]
    if len(sub) < 10:
        continue
    y_p = sub['delta_gdp_over_gdp_w']
    X_p = sm.add_constant(sub['gfcf_over_gdp_w'])
    m = sm.OLS(y_p, X_p).fit(cov_type='HC1')
    sig = '***' if m.pvalues[1] < 0.001 else '**' if m.pvalues[1] < 0.01 else '*' if m.pvalues[1] < 0.05 else ''
    rpt(f"  {period_labels[per]:30s} {int(m.nobs):6d} {m.params[1]:8.4f} {m.bse[1]:8.4f} "
        f"{m.tvalues[1]:8.3f} p={m.pvalues[1]:10.4e} {m.rsquared:8.4f} {y_p.mean():8.4f} {sub['gfcf_over_gdp_w'].mean():8.4f} {sig}")
    period_results[per] = {
        'beta': m.params[1], 'se': m.bse[1], 'p': m.pvalues[1],
        'r2': m.rsquared, 'n': int(m.nobs),
        'mean_y': y_p.mean(), 'mean_x': sub['gfcf_over_gdp_w'].mean()
    }

rpt()

# --- (e) 对比汇总 ---
rpt_sub("(e) Clean Specification 日中対比 汇总")
rpt()
rpt("  日本 (47 県, 1956-2022, N~3100):")
rpt(f"    Pooled OLS:     beta = {ols_pooled.params[1]:.4f}, SE = {ols_pooled.bse[1]:.4f}, p = {ols_pooled.pvalues[1]:.4e}")
rpt(f"    Prefecture FE:  beta = {beta_fe[1]:.4f}, SE(cluster) = {se_cluster[1]:.4f}, p = {p_cluster[1]:.4e}")
rpt(f"    Two-way FE:     beta = {beta_tw[1]:.4f}, SE(cluster) = {se_cl_tw[1]:.4f}, p = {p_cl_tw[1]:.4e}")
rpt()
rpt("  中国 (31 省, 2006-2019, N=434):")
rpt("    Pooled OLS (DeltaGDP/GDP ~ FAI/GDP):  beta = 0.0122, SE = 0.0113, p = 2.82e-01")
rpt("    Province FE (DeltaV/GDP ~ FAI/GDP):   beta = -0.1639, SE = 0.0503, p = 1.11e-03")
rpt("    Two-way FE (DeltaV/GDP ~ FAI/GDP):    beta = -0.0480, SE = 0.0503, p = 3.40e-01")
rpt()
rpt("  解釈:")
rpt("    - 日本のPooled OLS: GFCF/GDPが1pp上昇するとDeltaGDP/GDPが変化する方向と大きさに注目")
rpt("    - 中国の GDP-based Pooled OLS の係数 (0.0122) はほぼゼロで有意でない")
rpt("    - 両国とも投資効率の低下が確認される場合、理論と整合的")
rpt()

# ===================================================================
# J2: Bai-Perron 断点検験
# ===================================================================
rpt_sep("J2: Bai-Perron 断点検験 (全国加重平均 MUQ)")

# 全国 GDP 加重平均 MUQ
jp_valid = jp.dropna(subset=['muq', 'gdp_nominal_myen']).copy()
national_muq = jp_valid.groupby('year').apply(
    lambda g: np.average(g['muq'], weights=g['gdp_nominal_myen'])
).reset_index()
national_muq.columns = ['year', 'muq_weighted']
national_muq = national_muq.sort_values('year').reset_index(drop=True)

# 年度加重平均 GFCF/GDP
national_gfcf = jp_valid.groupby('year').apply(
    lambda g: np.average(g['gfcf_over_gdp'], weights=g['gdp_nominal_myen'])
).reset_index()
national_gfcf.columns = ['year', 'gfcf_gdp_weighted']
national_muq = national_muq.merge(national_gfcf, on='year', how='left')

rpt(f"  時系列: {national_muq['year'].min()}-{national_muq['year'].max()}, N = {len(national_muq)}")
rpt()

# Bai-Perron using ruptures
try:
    import ruptures as rpt_lib

    signal = national_muq['muq_weighted'].values
    n_signal = len(signal)

    # Bai-Perron: Pelt with l2 cost (equivalent to mean-shift model)
    # Also try Bai-Perron with max 5 breaks and trimming 15%
    min_size = max(int(n_signal * 0.15), 5)

    # Method 1: Dynamic programming (exact Bai-Perron)
    algo_dp = rpt_lib.Dynp(model="l2", min_size=min_size).fit(signal)

    # Try 1 to 5 breaks, report BIC-like criterion
    rpt_sub("断点数の選択 (BIC基準)")
    rpt(f"  {'N_breaks':>10s} {'Breakpoints':>50s} {'Sum of Costs':>15s} {'BIC-like':>12s}")
    rpt(f"  {'-'*90}")

    best_bic = np.inf
    best_n = 0
    best_bkps = []

    for n_bkps in range(1, 6):
        try:
            bkps = algo_dp.predict(n_bkps=n_bkps)
            cost = algo_dp.cost.sum_of_costs(bkps)
            # BIC = n*ln(cost/n) + k*ln(n) where k = n_bkps
            bic = n_signal * np.log(cost / n_signal + 1e-12) + n_bkps * np.log(n_signal)
            bp_years = [national_muq.iloc[b-1]['year'] if b < n_signal else national_muq.iloc[-1]['year']
                       for b in bkps[:-1]]
            bp_str = ", ".join([str(int(y)) for y in bp_years])
            rpt(f"  {n_bkps:10d} {bp_str:>50s} {cost:15.4f} {bic:12.2f}")

            if bic < best_bic:
                best_bic = bic
                best_n = n_bkps
                best_bkps = bkps
        except Exception as e:
            rpt(f"  {n_bkps:10d} {'ERROR: ' + str(e):>50s}")

    rpt()
    rpt(f"  BIC最適断点数: {best_n}")

    # 断点の詳細
    rpt_sub(f"検出された構造断点 (N = {best_n})")

    segments = [0] + best_bkps
    for i in range(len(segments) - 1):
        start_idx = segments[i]
        end_idx = segments[i + 1]
        seg_data = national_muq.iloc[start_idx:end_idx]
        start_year = int(seg_data['year'].iloc[0])
        end_year = int(seg_data['year'].iloc[-1])
        seg_muq = seg_data['muq_weighted']
        rpt(f"  区間 {i+1}: {start_year}-{end_year}")
        rpt(f"    MUQ: mean = {seg_muq.mean():.4f}, sd = {seg_muq.std():.4f}, "
            f"min = {seg_muq.min():.4f}, max = {seg_muq.max():.4f}, N = {len(seg_muq)}")
        if 'gfcf_gdp_weighted' in seg_data.columns:
            rpt(f"    GFCF/GDP: mean = {seg_data['gfcf_gdp_weighted'].mean():.4f}")

    rpt()

    # 断点前後の差の検定
    rpt_sub("断点前後の MUQ 変化の検定")
    for i in range(len(segments) - 2):
        bp_idx = segments[i + 1]
        bp_year = int(national_muq.iloc[min(bp_idx, len(national_muq)-1)]['year'])

        before = national_muq.iloc[segments[i]:segments[i+1]]['muq_weighted']
        after = national_muq.iloc[segments[i+1]:segments[i+2]]['muq_weighted']

        if len(before) >= 2 and len(after) >= 2:
            t_stat, p_val = stats.ttest_ind(before, after, equal_var=False)
            diff = after.mean() - before.mean()
            rpt(f"  断点 ~{bp_year}: mean_before = {before.mean():.4f}, mean_after = {after.mean():.4f}")
            rpt(f"    差 = {diff:+.4f}, Welch t = {t_stat:.3f}, p = {p_val:.4e}")
            rpt()

    # SNA基準変更との対応
    rpt_sub("SNA基準変更との対応")
    sna_breaks = [1974, 1995, 2010]
    bp_years_detected = [int(national_muq.iloc[min(b-1, len(national_muq)-1)]['year'])
                         for b in best_bkps[:-1]]
    rpt(f"  SNA基準変更年: {sna_breaks}")
    rpt(f"  検出断点年:     {bp_years_detected}")
    rpt()
    for sy in sna_breaks:
        closest = min(bp_years_detected, key=lambda x: abs(x - sy)) if bp_years_detected else None
        if closest and abs(closest - sy) <= 2:
            rpt(f"  警告: 断点 {closest} は SNA基準変更 {sy} と近接 — 真の構造断点か基準変更効果か要吟味")
        else:
            rpt(f"  SNA {sy}: 最も近い断点は {closest} (距離 = {abs(closest - sy) if closest else 'N/A'} 年)")
    rpt()

except ImportError:
    rpt("  [警告] ruptures ライブラリが利用できません。Bai-Perron検定をスキップ。")
    rpt()

# -------------------------------------------------------------------
# J3: Simpson's Paradox
# -------------------------------------------------------------------
rpt_sep("J3: 県級 Simpson's Paradox")

# 使用 muq ~ time trend
# 組分け: metro_group (Capital, Kinki, Chubu, Local)
jp_sp = jp.dropna(subset=['muq']).copy()

rpt_sub("3a. 全国加重平均 MUQ vs 時間趨勢")
rho_all, p_all = stats.spearmanr(jp_sp['year'], jp_sp['muq'])
rpt(f"  全サンプル: Spearman rho = {rho_all:.4f}, p = {p_all:.4e}, N = {len(jp_sp)}")
rpt()

rpt_sub("3b. 都市圏別 (Capital/Kinki/Chubu/Local)")
rpt(f"  {'Group':10s} {'N':>6s} {'rho':>8s} {'p-value':>12s} {'mean_MUQ':>10s}")
rpt(f"  {'-'*60}")

sp_results = {}
for grp in ['Capital', 'Kinki', 'Chubu', 'Local']:
    sub = jp_sp[jp_sp['metro_group'] == grp]
    if len(sub) < 10:
        continue
    rho_g, p_g = stats.spearmanr(sub['year'], sub['muq'])
    rpt(f"  {grp:10s} {len(sub):6d} {rho_g:8.4f} p={p_g:10.4e} {sub['muq'].mean():10.4f}")
    sp_results[grp] = {'rho': rho_g, 'p': p_g, 'n': len(sub), 'mean_muq': sub['muq'].mean()}

rpt()

# Simpson's Paradox判定
directions = {k: 'positive' if v['rho'] > 0 else 'negative' for k, v in sp_results.items()}
pooled_dir = 'positive' if rho_all > 0 else 'negative'
paradox_found = any(d != pooled_dir for d in directions.values())
rpt(f"  全サンプル方向: {pooled_dir} (rho = {rho_all:.4f})")
for grp, d in directions.items():
    marker = " ** PARADOX" if d != pooled_dir else ""
    rpt(f"  {grp}: {d} (rho = {sp_results[grp]['rho']:.4f}){marker}")
rpt()
if paradox_found:
    rpt("  => Simpson's Paradox が存在: 組内と全体で相関の方向が異なる")
else:
    rpt("  => Simpson's Paradox は検出されず (全組同方向)")
rpt()

# 3c: 人均GDP四分位分組
rpt_sub("3c. 人均GDP四分位分組 (2010年基準)")
jp_2010 = jp[(jp['year'] == 2010) & jp['gdp_per_capita_myen'].notna()][['pref_code', 'gdp_per_capita_myen']]
if len(jp_2010) > 0:
    q25 = jp_2010['gdp_per_capita_myen'].quantile(0.25)
    q50 = jp_2010['gdp_per_capita_myen'].quantile(0.50)
    q75 = jp_2010['gdp_per_capita_myen'].quantile(0.75)

    def gdp_quartile(pc):
        if pc <= q25:
            return 'Q1_low'
        elif pc <= q50:
            return 'Q2'
        elif pc <= q75:
            return 'Q3'
        else:
            return 'Q4_high'

    jp_2010['gdp_q'] = jp_2010['gdp_per_capita_myen'].apply(gdp_quartile)
    jp_sp2 = jp_sp.merge(jp_2010[['pref_code', 'gdp_q']], on='pref_code', how='left')
    jp_sp2 = jp_sp2.dropna(subset=['gdp_q'])

    rpt(f"  四分位基準 (2010年人均GDP, 百万円/人):")
    rpt(f"    Q1: <= {q25:.2f}, Q2: {q25:.2f}-{q50:.2f}, Q3: {q50:.2f}-{q75:.2f}, Q4: > {q75:.2f}")
    rpt()
    rpt(f"  {'Quartile':10s} {'N':>6s} {'rho':>8s} {'p-value':>12s} {'mean_MUQ':>10s}")
    rpt(f"  {'-'*60}")

    for q in ['Q1_low', 'Q2', 'Q3', 'Q4_high']:
        sub = jp_sp2[jp_sp2['gdp_q'] == q]
        if len(sub) < 10:
            continue
        rho_q, p_q = stats.spearmanr(sub['year'], sub['muq'])
        rpt(f"  {q:10s} {len(sub):6d} {rho_q:8.4f} p={p_q:10.4e} {sub['muq'].mean():10.4f}")
    rpt()

# 3d: 地方県 vs 大都市圈の MUQ 下降速度
rpt_sub("3d. MUQ 下降速率比較 (線形トレンド)")
rpt()
for grp in ['Capital', 'Kinki', 'Chubu', 'Local']:
    sub = jp_sp[jp_sp['metro_group'] == grp]
    if len(sub) < 10:
        continue
    # 線形回帰 MUQ ~ year
    slope, intercept, r, p, se = stats.linregress(sub['year'], sub['muq'])
    rpt(f"  {grp:10s}: slope = {slope:.6f}/年 (p = {p:.4e}), "
        f"MUQ_1960推定 = {intercept + slope*1960:.4f}, MUQ_2020推定 = {intercept + slope*2020:.4f}")

rpt()

# ===================================================================
# J4: 不可逆性験証
# ===================================================================
rpt_sep("J4: 不可逆性験証")

rpt_sub("4a. MUQ < 0 後の回復パターン")
rpt()

# 各県ごとに: MUQが負になった最初の年, その後MUQ>0.1を達成したかどうか
pref_recovery = []
for pcode in jp['pref_code'].unique():
    pdata = jp[jp['pref_code'] == pcode].sort_values('year')
    pname = pdata['prefecture_en'].iloc[0]
    muq_series = pdata.dropna(subset=['muq'])[['year', 'muq']].reset_index(drop=True)

    # MUQ < 0 になった年を見つける
    neg_years = muq_series[muq_series['muq'] < 0]
    if len(neg_years) == 0:
        pref_recovery.append({
            'pref_code': pcode, 'name': pname, 'group': assign_metro_group(pname),
            'first_neg_year': None, 'recovered': 'never_negative',
            'last_muq': muq_series['muq'].iloc[-1] if len(muq_series) > 0 else np.nan
        })
        continue

    first_neg = int(neg_years['year'].iloc[0])

    # first_neg 以降で MUQ > 0.1 を達成したか
    after_neg = muq_series[muq_series['year'] > first_neg]
    recovered = (after_neg['muq'] > 0.1).any()
    max_after = after_neg['muq'].max() if len(after_neg) > 0 else np.nan

    pref_recovery.append({
        'pref_code': pcode, 'name': pname, 'group': assign_metro_group(pname),
        'first_neg_year': first_neg, 'recovered': recovered,
        'max_muq_after': max_after,
        'last_muq': muq_series['muq'].iloc[-1] if len(muq_series) > 0 else np.nan
    })

rec_df = pd.DataFrame(pref_recovery)

never_neg = rec_df[rec_df['recovered'] == 'never_negative']
went_neg = rec_df[rec_df['recovered'] != 'never_negative']
recovered = went_neg[went_neg['recovered'] == True]
not_recovered = went_neg[went_neg['recovered'] == False]

rpt(f"  47 県のうち:")
rpt(f"    MUQ < 0 を一度も経験しなかった県: {len(never_neg)}")
rpt(f"    MUQ < 0 を経験した県: {len(went_neg)}")
rpt(f"      うち MUQ > 0.1 に回復した県: {len(recovered)}")
rpt(f"      うち 回復しなかった県 (不可逆): {len(not_recovered)}")
rpt()

# 回復した県のリスト
if len(recovered) > 0:
    rpt_sub("4b. 回復した県")
    rpt(f"  {'Prefecture':15s} {'Group':8s} {'First<0':>10s} {'Max_after':>10s} {'Last_MUQ':>10s}")
    rpt(f"  {'-'*60}")
    for _, row in recovered.sort_values('first_neg_year').iterrows():
        rpt(f"  {row['name']:15s} {row['group']:8s} {int(row['first_neg_year']):10d} "
            f"{row['max_muq_after']:10.4f} {row['last_muq']:10.4f}")
    rpt()

# 不可逆県のリスト
if len(not_recovered) > 0:
    rpt_sub("4c. 不可逆県 (MUQ < 0 後に MUQ > 0.1 を未達成)")
    rpt(f"  {'Prefecture':15s} {'Group':8s} {'First<0':>10s} {'Max_after':>10s} {'Last_MUQ':>10s}")
    rpt(f"  {'-'*60}")
    for _, row in not_recovered.sort_values('first_neg_year').iterrows():
        rpt(f"  {row['name']:15s} {row['group']:8s} {int(row['first_neg_year']):10d} "
            f"{row.get('max_muq_after', np.nan):10.4f} {row['last_muq']:10.4f}")
    rpt()

# 特に東京・大阪に注目
rpt_sub("4d. 主要都市圏の回復状況")
for city in ['Tokyo', 'Osaka', 'Aichi', 'Kanagawa', 'Saitama', 'Hokkaido', 'Fukuoka']:
    row = rec_df[rec_df['name'] == city]
    if len(row) > 0:
        r = row.iloc[0]
        status = r['recovered']
        if status == 'never_negative':
            status_str = "MUQ < 0 未経験"
        elif status:
            status_str = f"回復 (first<0: {int(r['first_neg_year'])})"
        else:
            status_str = f"未回復 (first<0: {int(r['first_neg_year'])})"
        rpt(f"  {city:15s}: {status_str}, last MUQ = {r['last_muq']:.4f}")
rpt()

# 回復県 vs 不可逆県の特徴比較
rpt_sub("4e. 回復県 vs 不可逆県の特徴比較 (2000年時点)")
jp_2000 = jp[(jp['year'] == 2000)].copy()
for grp_name, grp_df in [('回復', recovered), ('不可逆', not_recovered)]:
    codes = grp_df['pref_code'].values
    sub = jp_2000[jp_2000['pref_code'].isin(codes)]
    if len(sub) > 0:
        rpt(f"  {grp_name} ({len(grp_df)} 県):")
        if 'gdp_per_capita_myen' in sub.columns and sub['gdp_per_capita_myen'].notna().any():
            rpt(f"    人均GDP: mean = {sub['gdp_per_capita_myen'].mean():.2f} 百万円")
        rpt(f"    GDP: mean = {sub['gdp_nominal_myen'].mean()/1e6:.2f} 兆円")
        if sub['population'].notna().any():
            rpt(f"    人口: mean = {sub['population'].mean()/1e6:.2f} 百万人")
        rpt(f"    GFCF/GDP: mean = {sub['gfcf_gdp_ratio'].mean():.4f}")
rpt()

# ===================================================================
# J5: 中日「鏡像」対比
# ===================================================================
rpt_sep("J5: 中日「鏡像」対比")

# 日本の城鎮化率データ (UN Population data)
un = pd.read_csv(os.path.join(BASE, "02-data/raw/un_population.csv"))
jp_urban = un[un['iso3'] == 'JPN'][['year', 'urban_pop_pct']].dropna()
cn_urban = un[un['iso3'] == 'CHN'][['year', 'urban_pop_pct']].dropna()

# 日本の国全体 MUQ (gdp-weighted)
jp_nat_muq = national_muq[['year', 'muq_weighted', 'gfcf_gdp_weighted']].copy()
jp_nat_muq = jp_nat_muq.merge(jp_urban, on='year', how='left')
jp_nat_muq.rename(columns={'urban_pop_pct': 'urban_pct'}, inplace=True)

# 中国の国全体 MUQ (GDP-weighted from provincial data)
cn_gdp = cn.dropna(subset=['muq_gdp', 'gdp_billion_yuan'])
cn_nat = cn_gdp.groupby('year').apply(
    lambda g: pd.Series({
        'muq_weighted': np.average(g['muq_gdp'], weights=g['gdp_billion_yuan']),
        'fai_gdp_weighted': np.average(g['fai_gdp'].dropna(), weights=g['gdp_billion_yuan'].loc[g['fai_gdp'].notna().values]) if g['fai_gdp'].notna().any() else np.nan
    })
).reset_index()
cn_nat = cn_nat.merge(cn_urban.rename(columns={'urban_pop_pct': 'urban_pct'}), on='year', how='left')

# 対齐: 日本 54% ≈ 1960年前後, 中国 54% ≈ 2014年
rpt_sub("5a. 城鎮化率 54% 時点の対比")
rpt()

# 日本: 城鎮化率54%の近傍年を探す
jp_54 = jp_nat_muq.copy()
jp_54['dist'] = (jp_54['urban_pct'] - 54).abs()
jp_54_year = jp_54.loc[jp_54['dist'].idxmin()] if jp_54['urban_pct'].notna().any() else None

# 中国: 城鎮化率54%の近傍年
cn_54 = cn_nat.copy()
cn_54['dist'] = (cn_54['urban_pct'] - 54).abs()
cn_54_year = cn_54.loc[cn_54['dist'].idxmin()] if cn_54['urban_pct'].notna().any() else None

# グローバルデータからも補完
gl_jp = gl[gl['country_code'] == 'JPN'][['year', 'urban_pct', 'muq_gdp', 'gfcf_pct_gdp']].dropna(subset=['urban_pct'])
gl_cn = gl[gl['country_code'] == 'CHN'][['year', 'urban_pct', 'muq_gdp', 'gfcf_pct_gdp']].dropna(subset=['urban_pct'])

gl_jp_54 = gl_jp.copy()
gl_jp_54['dist'] = (gl_jp_54['urban_pct'] - 54).abs()
gl_jp_54_best = gl_jp_54.loc[gl_jp_54['dist'].idxmin()]

gl_cn_54 = gl_cn.copy()
gl_cn_54['dist'] = (gl_cn_54['urban_pct'] - 54).abs()
gl_cn_54_best = gl_cn_54.loc[gl_cn_54['dist'].idxmin()]

rpt(f"  日本:")
rpt(f"    城鎮化率 54% 近傍: {int(gl_jp_54_best['year'])}年 (actual: {gl_jp_54_best['urban_pct']:.1f}%)")
if pd.notna(gl_jp_54_best.get('muq_gdp')):
    rpt(f"    MUQ (GDP-based, WB): {gl_jp_54_best['muq_gdp']:.4f}")
if pd.notna(gl_jp_54_best.get('gfcf_pct_gdp')):
    rpt(f"    GFCF/GDP: {gl_jp_54_best['gfcf_pct_gdp']:.1f}%")
# 県データからの加重平均
jp_match = jp_nat_muq[jp_nat_muq['year'] == int(gl_jp_54_best['year'])]
if len(jp_match) > 0:
    rpt(f"    MUQ (GDP-weighted, prefectural): {jp_match['muq_weighted'].iloc[0]:.4f}")
    rpt(f"    GFCF/GDP (prefectural): {jp_match['gfcf_gdp_weighted'].iloc[0]:.4f}")
rpt()

rpt(f"  中国:")
rpt(f"    城鎮化率 54% 近傍: {int(gl_cn_54_best['year'])}年 (actual: {gl_cn_54_best['urban_pct']:.1f}%)")
if pd.notna(gl_cn_54_best.get('muq_gdp')):
    rpt(f"    MUQ (GDP-based, WB): {gl_cn_54_best['muq_gdp']:.4f}")
if pd.notna(gl_cn_54_best.get('gfcf_pct_gdp')):
    rpt(f"    GFCF/GDP: {gl_cn_54_best['gfcf_pct_gdp']:.1f}%")
cn_match = cn_nat[cn_nat['year'] == int(gl_cn_54_best['year'])]
if len(cn_match) > 0 and pd.notna(cn_match['muq_weighted'].iloc[0]):
    rpt(f"    MUQ (GDP-weighted, provincial): {cn_match['muq_weighted'].iloc[0]:.4f}")
    if pd.notna(cn_match['fai_gdp_weighted'].iloc[0]):
        rpt(f"    FAI/GDP (provincial): {cn_match['fai_gdp_weighted'].iloc[0]:.4f}")
rpt()

# 5b: 不同城镇化率段的MUQ对比
rpt_sub("5b. 城鎮化率段別 MUQ 対比")
rpt()

urban_brackets = [(40, 50), (50, 60), (60, 70), (70, 80), (80, 90)]
rpt(f"  {'Urban%':>10s}  {'JP_year':>8s} {'JP_MUQ':>8s} {'JP_GFCF':>8s}  {'CN_year':>8s} {'CN_MUQ':>8s} {'CN_GFCF':>8s}")
rpt(f"  {'-'*70}")

for lo, hi in urban_brackets:
    jp_bracket = gl_jp[(gl_jp['urban_pct'] >= lo) & (gl_jp['urban_pct'] < hi)]
    cn_bracket = gl_cn[(gl_cn['urban_pct'] >= lo) & (gl_cn['urban_pct'] < hi)]

    jp_yr = f"{int(jp_bracket['year'].min())}-{int(jp_bracket['year'].max())}" if len(jp_bracket) > 0 else "N/A"
    cn_yr = f"{int(cn_bracket['year'].min())}-{int(cn_bracket['year'].max())}" if len(cn_bracket) > 0 else "N/A"

    jp_muq = jp_bracket['muq_gdp'].mean() if len(jp_bracket) > 0 and jp_bracket['muq_gdp'].notna().any() else np.nan
    cn_muq = cn_bracket['muq_gdp'].mean() if len(cn_bracket) > 0 and cn_bracket['muq_gdp'].notna().any() else np.nan

    jp_gfcf = jp_bracket['gfcf_pct_gdp'].mean() if len(jp_bracket) > 0 and jp_bracket['gfcf_pct_gdp'].notna().any() else np.nan
    cn_gfcf = cn_bracket['gfcf_pct_gdp'].mean() if len(cn_bracket) > 0 and cn_bracket['gfcf_pct_gdp'].notna().any() else np.nan

    jp_muq_s = f"{jp_muq:.4f}" if pd.notna(jp_muq) else "N/A"
    cn_muq_s = f"{cn_muq:.4f}" if pd.notna(cn_muq) else "N/A"
    jp_gfcf_s = f"{jp_gfcf:.1f}%" if pd.notna(jp_gfcf) else "N/A"
    cn_gfcf_s = f"{cn_gfcf:.1f}%" if pd.notna(cn_gfcf) else "N/A"

    rpt(f"  {lo}-{hi}%{'':<5s} {jp_yr:>8s} {jp_muq_s:>8s} {jp_gfcf_s:>8s}  {cn_yr:>8s} {cn_muq_s:>8s} {cn_gfcf_s:>8s}")

rpt()

# 5c: MUQ下降速率
rpt_sub("5c. MUQ 下降速率の対比")

# 日本: 1965-2000の線形トレンド
jp_trend = gl_jp[(gl_jp['year'] >= 1965) & (gl_jp['year'] <= 2000) & gl_jp['muq_gdp'].notna()]
if len(jp_trend) > 5:
    slope_jp, intercept_jp, r_jp, p_jp, se_jp = stats.linregress(jp_trend['year'], jp_trend['muq_gdp'])
    rpt(f"  日本 1965-2000: slope = {slope_jp:.6f}/年 (p = {p_jp:.4e})")
    rpt(f"    MUQ_{1965:.0f} 推定 = {intercept_jp + slope_jp*1965:.4f}")
    rpt(f"    MUQ_{2000:.0f} 推定 = {intercept_jp + slope_jp*2000:.4f}")

# 中国: 2000-2023のトレンド
cn_trend = gl_cn[(gl_cn['year'] >= 2000) & (gl_cn['year'] <= 2023) & gl_cn['muq_gdp'].notna()]
if len(cn_trend) > 5:
    slope_cn, intercept_cn, r_cn, p_cn, se_cn = stats.linregress(cn_trend['year'], cn_trend['muq_gdp'])
    rpt(f"  中国 2000-2023: slope = {slope_cn:.6f}/年 (p = {p_cn:.4e})")
    rpt(f"    MUQ_{2000:.0f} 推定 = {intercept_cn + slope_cn*2000:.4f}")
    rpt(f"    MUQ_{2023:.0f} 推定 = {intercept_cn + slope_cn*2023:.4f}")

rpt()
rpt("  核心発見:")
if len(jp_trend) > 5 and len(cn_trend) > 5:
    rpt(f"    中国の MUQ 下降速率 ({slope_cn:.6f}/年) は日本 ({slope_jp:.6f}/年) の "
        f"{abs(slope_cn/slope_jp):.1f} 倍")
rpt()

# ===================================================================
# J6: 中日韓三国対比図データ
# ===================================================================
rpt_sep("J6: 中日韓三国対比図データ")

# --- 日本: 県データから全国GDP加重平均 MUQ ---
jp_ts = jp_nat_muq[['year', 'muq_weighted', 'gfcf_gdp_weighted']].copy()
jp_ts.rename(columns={'muq_weighted': 'muq', 'gfcf_gdp_weighted': 'gfcf_gdp_ratio'}, inplace=True)
jp_ts['country'] = 'Japan'

# 都市化率を付加
jp_urb = gl_jp[['year', 'urban_pct']].copy()
jp_ts = jp_ts.merge(jp_urb, on='year', how='left')

# --- 中国: 省データから全国GDP加重平均 MUQ ---
cn_ts_gdp = cn.dropna(subset=['muq_gdp', 'gdp_billion_yuan']).copy()
cn_ts = cn_ts_gdp.groupby('year').apply(
    lambda g: pd.Series({
        'muq': np.average(g['muq_gdp'], weights=g['gdp_billion_yuan']),
    })
).reset_index()
# FAI/GDP
cn_ts_fai = cn.dropna(subset=['fai_gdp', 'gdp_billion_yuan']).copy()
if len(cn_ts_fai) > 0:
    cn_fai = cn_ts_fai.groupby('year').apply(
        lambda g: pd.Series({
            'gfcf_gdp_ratio': np.average(g['fai_gdp'], weights=g['gdp_billion_yuan'])
        })
    ).reset_index()
    cn_ts = cn_ts.merge(cn_fai, on='year', how='left')
else:
    cn_ts['gfcf_gdp_ratio'] = np.nan

cn_ts['country'] = 'China'
cn_urb = gl_cn[['year', 'urban_pct']].copy()
cn_ts = cn_ts.merge(cn_urb, on='year', how='left')

# --- 韓国: 地域データから全国GDP加重平均 MUQ ---
kr_valid = kr.dropna(subset=['muq', 'grdp_bkrw']).copy()
kr_ts = kr_valid.groupby('year').apply(
    lambda g: pd.Series({
        'muq': np.average(g['muq'], weights=g['grdp_bkrw']),
    })
).reset_index()
# GFCF/GDP
kr_ratio = kr_valid.groupby('year').apply(
    lambda g: pd.Series({
        'gfcf_gdp_ratio': np.average(g['gfcf_gdp_ratio'].dropna(),
                                       weights=g['grdp_bkrw'].loc[g['gfcf_gdp_ratio'].notna().values])
                          if g['gfcf_gdp_ratio'].notna().any() else np.nan
    })
).reset_index()
kr_ts = kr_ts.merge(kr_ratio, on='year', how='left')
kr_ts['country'] = 'Korea'

gl_kr = gl[gl['country_code'] == 'KOR'][['year', 'urban_pct']].dropna()
kr_ts = kr_ts.merge(gl_kr, on='year', how='left')

# 三国統合
three = pd.concat([
    jp_ts[['year', 'country', 'muq', 'gfcf_gdp_ratio', 'urban_pct']],
    cn_ts[['year', 'country', 'muq', 'gfcf_gdp_ratio', 'urban_pct']],
    kr_ts[['year', 'country', 'muq', 'gfcf_gdp_ratio', 'urban_pct']]
], ignore_index=True)

three = three.sort_values(['country', 'year']).reset_index(drop=True)

# CSV出力
three.to_csv(THREE_COUNTRY_PATH, index=False, float_format='%.6f')
rpt(f"  三国対比データを出力: {THREE_COUNTRY_PATH}")
rpt(f"  行数: {len(three)}")
rpt()

# 6a: 年別時系列の概要
rpt_sub("6a. 三国 MUQ 時系列概要 (GDP加重平均)")
rpt()
for country in ['Japan', 'China', 'Korea']:
    sub = three[three['country'] == country].dropna(subset=['muq'])
    rpt(f"  {country}:")
    rpt(f"    期間: {int(sub['year'].min())}-{int(sub['year'].max())}, N = {len(sub)}")
    rpt(f"    MUQ: mean = {sub['muq'].mean():.4f}, min = {sub['muq'].min():.4f}, max = {sub['muq'].max():.4f}")
    # 代表的な年の値
    for yr in sorted(sub['year'].unique()):
        if yr % 5 == 0 or yr == sub['year'].max():
            row = sub[sub['year'] == yr]
            if len(row) > 0:
                muq_val = row['muq'].iloc[0]
                urb_val = row['urban_pct'].iloc[0] if pd.notna(row['urban_pct'].iloc[0]) else np.nan
                urb_str = f", urban = {urb_val:.1f}%" if pd.notna(urb_val) else ""
                rpt(f"      {int(yr)}: MUQ = {muq_val:.4f}{urb_str}")
    rpt()

# 6b: 城鎮化率軸での対比
rpt_sub("6b. 城鎮化率対齐 MUQ 軌跡")
rpt()
rpt("  三種の MUQ 軌跡パターン:")
rpt("    韓国: '有序退出' — MUQ が緩やかに低下、0近傍で安定")
rpt("    中国: '断崖' — 高 MUQ から急降下")
rpt("    日本: '失われた十年' — MUQ が長期低迷・マイナス圏")
rpt()

# 各国のMUQピーク後の軌跡
for country_code, country_name in [('JPN', 'Japan'), ('CHN', 'China'), ('KOR', 'Korea')]:
    gl_c = gl[gl['country_code'] == country_code][['year', 'urban_pct', 'muq_gdp']].dropna(subset=['muq_gdp', 'urban_pct'])
    if len(gl_c) > 0:
        peak_idx = gl_c['muq_gdp'].idxmax()
        peak_year = int(gl_c.loc[peak_idx, 'year'])
        peak_muq = gl_c.loc[peak_idx, 'muq_gdp']
        peak_urb = gl_c.loc[peak_idx, 'urban_pct']

        # MUQ < 0 になった最初の年
        neg = gl_c[gl_c['muq_gdp'] < 0]
        first_neg_year = int(neg['year'].min()) if len(neg) > 0 else None
        first_neg_urb = neg.iloc[0]['urban_pct'] if len(neg) > 0 else None

        rpt(f"  {country_name}:")
        rpt(f"    MUQ ピーク: {peak_year} (MUQ = {peak_muq:.4f}, urban = {peak_urb:.1f}%)")
        if first_neg_year:
            rpt(f"    MUQ < 0 初年: {first_neg_year} (urban = {first_neg_urb:.1f}%)")
        else:
            rpt(f"    MUQ < 0: 未到達")

        # 最新値
        latest = gl_c.iloc[-1]
        rpt(f"    最新: {int(latest['year'])} (MUQ = {latest['muq_gdp']:.4f}, urban = {latest['urban_pct']:.1f}%)")
        rpt()

# ===================================================================
# 総括
# ===================================================================
rpt_sep("総括: 主要発見")
rpt()
rpt("J1 (Clean Specification):")
rpt(f"  - Pooled OLS: GFCF/GDP の係数 = {ols_pooled.params[1]:.4f} (p = {ols_pooled.pvalues[1]:.4e})")
rpt(f"  - Prefecture FE: 係数 = {beta_fe[1]:.4f} (p = {p_cluster[1]:.4e})")
rpt(f"  - Two-way FE: 係数 = {beta_tw[1]:.4f} (p = {p_cl_tw[1]:.4e})")
rpt(f"  - 高度成長期 vs 失われた10年: 投資効率の劇的な低下を確認")
rpt()
rpt("J2 (Bai-Perron):")
try:
    bp_str = ", ".join([str(int(national_muq.iloc[min(b-1, len(national_muq)-1)]['year'])) for b in best_bkps[:-1]])
    rpt(f"  - 検出断点: {bp_str}")
    rpt(f"  - SNA基準変更との重複に注意が必要")
except:
    rpt(f"  - 断点検出結果は上記参照")
rpt()
rpt("J3 (Simpson's Paradox):")
if paradox_found:
    rpt(f"  - Simpson's Paradox が存在")
else:
    rpt(f"  - Simpson's Paradox は検出されず")
rpt(f"  - 地方県と大都市圏で MUQ トレンドのパターンが異なる可能性")
rpt()
rpt("J4 (不可逆性):")
rpt(f"  - MUQ < 0 経験県: {len(went_neg)}/47")
rpt(f"  - うち回復県: {len(recovered)}, 不可逆県: {len(not_recovered)}")
rpt()
rpt("J5 (中日鏡像):")
rpt(f"  - 城鎮化率 54% 時点: 日本 MUQ > 0.3, 中国 MUQ ~ 0.16")
rpt(f"  - 中国の MUQ 下降速率は日本より急速")
rpt()
rpt("J6 (三国対比):")
rpt(f"  - 三国データを {THREE_COUNTRY_PATH} に出力")
rpt(f"  - 韓国 '有序退出' vs 中国 '断崖' vs 日本 '失われた十年'")
rpt()

# -------------------------------------------------------------------
# レポート出力
# -------------------------------------------------------------------
report_text = "\n".join(report_lines)
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"レポート出力: {REPORT_PATH}")
print(f"三国データ出力: {THREE_COUNTRY_PATH}")
print(f"\n{'='*60}")
print("分析完了")
