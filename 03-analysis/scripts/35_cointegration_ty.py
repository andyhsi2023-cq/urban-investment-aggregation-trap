"""
35_cointegration_ty.py
目的: 中国城市Q与投资率(GFCF/GDP)的协整检验与Toda-Yamamoto因果检验
输入: china_q_adjusted.csv, china_national_real_data_v2.csv
输出: cointegration_ty_report.txt
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.api import VAR
from scipy import stats
import warnings, os
warnings.filterwarnings("ignore")

BASE = "/Users/andy/Desktop/Claude/urban-q-phase-transition"
OUT = f"{BASE}/03-analysis/models/cointegration_ty_report.txt"

# ── 数据准备 ──
q_df = pd.read_csv(f"{BASE}/03-analysis/models/china_q_adjusted.csv")
raw_df = pd.read_csv(f"{BASE}/02-data/raw/china_national_real_data_v2.csv")

# 合并：取 Q_weighted 和投资率
raw_df["inv_gdp"] = raw_df["fai_total_100m"] / raw_df["gdp_100m"]  # FAI/GDP
raw_df["gfcf_gdp"] = raw_df["wb_gfcf_pct_gdp"] / 100.0            # GFCF/GDP

df = q_df[["year", "Q_weighted"]].merge(
    raw_df[["year", "inv_gdp", "gfcf_gdp"]], on="year", how="inner"
).dropna().sort_values("year").reset_index(drop=True)

# 选择投资率指标：优先 GFCF/GDP，缺失过多则用 FAI/GDP
inv_col = "gfcf_gdp" if df["gfcf_gdp"].notna().sum() >= 15 else "inv_gdp"
inv_label = "GFCF/GDP" if inv_col == "gfcf_gdp" else "FAI/GDP"
df = df[["year", "Q_weighted", inv_col]].dropna().reset_index(drop=True)
df.columns = ["year", "Q", "I"]

lines = []
def log(s=""):
    lines.append(s)
    print(s)

log("=" * 60)
log("协整检验与 Toda-Yamamoto 因果检验报告")
log("=" * 60)
log(f"样本: {int(df['year'].min())}–{int(df['year'].max())}, N={len(df)}")
log(f"Q 指标: Q_weighted (加权城市Q)")
log(f"投资指标: {inv_label}")
log()

# ── Part A: ADF 单位根检验 ──
log("─" * 60)
log("Part A: ADF 单位根检验")
log("─" * 60)

def adf_test(series, name, maxlag=None):
    """ADF检验，返回结果字典"""
    if maxlag is None:
        maxlag = max(1, int(np.floor((len(series) - 1) ** (1/3))))
    res = adfuller(series, maxlag=maxlag, autolag="AIC")
    return {"name": name, "stat": res[0], "pval": res[1], "lags": res[2],
            "crit": res[4]}

for var, label in [("Q", "Q_weighted"), ("I", inv_label)]:
    s = df[var].values
    # 水平值
    r = adf_test(s, f"{label} (level)")
    log(f"  {r['name']:30s}  ADF={r['stat']:7.3f}  p={r['pval']:.4f}  lags={r['lags']}")
    # 一阶差分
    r = adf_test(np.diff(s), f"{label} (1st diff)")
    log(f"  {r['name']:30s}  ADF={r['stat']:7.3f}  p={r['pval']:.4f}  lags={r['lags']}")
log()

# 判断积分阶数
def get_integration_order(series, maxlag=None):
    p_level = adfuller(series, maxlag=maxlag or max(1, int(len(series)**(1/3))),
                       autolag="AIC")[1]
    if p_level < 0.05:
        return 0
    p_diff = adfuller(np.diff(series),
                      maxlag=maxlag or max(1, int((len(series)-1)**(1/3))),
                      autolag="AIC")[1]
    return 1 if p_diff < 0.05 else 2

d_Q = get_integration_order(df["Q"].values)
d_I = get_integration_order(df["I"].values)
d_max = max(d_Q, d_I, 1)  # Toda-Yamamoto 的 d_max
log(f"积分阶数: Q ~ I({d_Q}), {inv_label} ~ I({d_I})")
log(f"d_max = {d_max}")
log()

# ── Part B: Toda-Yamamoto 因果检验 ──
log("─" * 60)
log("Part B: Toda-Yamamoto Granger 因果检验")
log("─" * 60)

# 确定最优滞后阶数 p (AIC)
data_var = df[["Q", "I"]].values
max_p = min(4, len(df) // 4)  # 小样本限制
model_select = VAR(data_var)
aic_vals = {}
for p in range(1, max_p + 1):
    try:
        res = model_select.fit(p)
        aic_vals[p] = res.aic
    except:
        pass

p_opt = min(aic_vals, key=aic_vals.get)
log(f"VAR 滞后阶数选择 (AIC):")
for p, a in sorted(aic_vals.items()):
    marker = " <-- 最优" if p == p_opt else ""
    log(f"  p={p}: AIC={a:.4f}{marker}")
log()

# 估计 VAR(p + d_max)
p_aug = p_opt + d_max
log(f"Toda-Yamamoto: p={p_opt}, d_max={d_max}, 估计 VAR({p_aug})")

var_model = VAR(data_var)
var_result = var_model.fit(p_aug)

# Wald 检验函数
def wald_test_ty(var_result, p_opt, d_max, cause_idx, effect_idx, var_names):
    """
    对 VAR(p+d_max) 中前 p 阶的因果系数做 Wald 检验
    cause_idx: 原因变量在 VAR 中的列索引 (0 or 1)
    effect_idx: 结果变量的方程索引 (0 or 1)
    """
    # 获取效果方程的系数和协方差
    k = var_result.neqs  # 变量数 = 2
    params = var_result.params  # shape: (1+k*p_aug, k) — 含截距
    sigma = var_result.sigma_u   # 残差协方差

    # 效果方程的系数（含截距）
    eq_params = params[:, effect_idx]

    # 构建约束矩阵 R: 检验前 p_opt 阶中 cause 变量的系数 = 0
    n_params = len(eq_params)  # 1 + k * p_aug
    R = np.zeros((p_opt, n_params))
    for j in range(p_opt):
        # 参数排列: [const, y1_L1, y2_L1, y1_L2, y2_L2, ...]
        coef_idx = 1 + j * k + cause_idx
        R[j, coef_idx] = 1.0

    # Wald = (R*beta)' * inv(R * Cov * R') * (R*beta)
    # 使用 OLS 协方差估计
    T = var_result.nobs
    # 从 statsmodels VAR 获取参数协方差
    # var_result.cov_params 不一定直接可用，手动计算
    X = np.column_stack([np.ones(T)] +
                        [data_var[p_aug-i-1:T+p_aug-i-1] for i in range(p_aug)])
    # 简化：直接用残差估计
    resid = var_result.resid[:, effect_idx]
    s2 = np.sum(resid**2) / (T - n_params)
    XtX_inv = np.linalg.inv(X.T @ X)
    cov_beta = s2 * XtX_inv

    Rb = R @ eq_params
    RCR = R @ cov_beta @ R.T
    try:
        W = Rb.T @ np.linalg.inv(RCR) @ Rb
    except np.linalg.LinAlgError:
        W = Rb.T @ np.linalg.pinv(RCR) @ Rb

    p_value = 1 - stats.chi2.cdf(W, df=p_opt)

    cause_name = var_names[cause_idx]
    effect_name = var_names[effect_idx]
    return {"direction": f"{cause_name} -> {effect_name}",
            "wald": W, "df": p_opt, "pval": p_value}

var_names = ["Q", inv_label]
log()

# 双向检验
for cause_idx, effect_idx in [(0, 1), (1, 0)]:
    r = wald_test_ty(var_result, p_opt, d_max, cause_idx, effect_idx, var_names)
    sig = "***" if r["pval"] < 0.01 else "**" if r["pval"] < 0.05 else "*" if r["pval"] < 0.10 else ""
    log(f"  {r['direction']:25s}  Wald={r['wald']:8.3f}  df={r['df']}  "
        f"p={r['pval']:.4f} {sig}")

log()
log("─" * 60)
log("Part C: 结论")
log("─" * 60)

# 自动判断
results = []
for cause_idx, effect_idx in [(0, 1), (1, 0)]:
    r = wald_test_ty(var_result, p_opt, d_max, cause_idx, effect_idx, var_names)
    results.append(r)

for r in results:
    if r["pval"] < 0.05:
        log(f"  {r['direction']}: 拒绝原假设 (p={r['pval']:.4f})，存在因果关系")
    elif r["pval"] < 0.10:
        log(f"  {r['direction']}: 边际显著 (p={r['pval']:.4f})，弱因果证据")
    else:
        log(f"  {r['direction']}: 不拒绝原假设 (p={r['pval']:.4f})，无因果关系证据")

# 因果方向总结
q_to_i = results[0]["pval"] < 0.10
i_to_q = results[1]["pval"] < 0.10
if q_to_i and i_to_q:
    log("\n  => 双向因果 (feedback loop)")
elif q_to_i:
    log(f"\n  => 单向因果: Q -> {inv_label}")
elif i_to_q:
    log(f"\n  => 单向因果: {inv_label} -> Q")
else:
    log("\n  => 未检测到显著因果关系")

log()
log("注: * p<0.10, ** p<0.05, *** p<0.01")
log(f"注: 小样本 (N={len(df)}) 下检验力有限，结果需谨慎解读")

# 写入报告
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n报告已保存: {OUT}")
