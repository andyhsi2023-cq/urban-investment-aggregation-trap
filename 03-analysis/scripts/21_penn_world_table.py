"""
21_penn_world_table.py
======================
目的：下载并处理 Penn World Table (PWT) 10.01 数据，提取人力资本指数、
     资本存量、GDP 等核心变量，计算资本-产出比和人均资本。

数据来源：
  - PWT 10.01 (Groningen Growth and Development Centre)
  - 备用：World Bank Human Capital Index

输出：
  - penn_world_table.csv — PWT 核心变量面板数据
  - pwt_data_summary.txt — 数据覆盖范围与描述性统计摘要

依赖包：pandas, numpy, openpyxl, requests
"""

import pandas as pd
import numpy as np
import requests
import io
import sys
import time
from pathlib import Path
from datetime import datetime

# ============================================================
# 0. 路径设置
# ============================================================

PROJECT_DIR = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
RAW_DIR = PROJECT_DIR / "02-data/raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = RAW_DIR / "penn_world_table.csv"
OUTPUT_SUMMARY = RAW_DIR / "pwt_data_summary.txt"
CACHE_FILE = RAW_DIR / "pwt1001_cache.xlsx"

# 需要提取的变量
# 注意：PWT 10.01 变量定义（来自 Stata variable labels）:
#   rkna = Capital services at constant 2017 national prices (2017=1) — 是指数，不是水平值
#   rnna = Capital stock at constant 2017 national prices (in mil. 2017US$) — 这是资本存量水平值
#   rgdpna = Real GDP at constant 2017 national prices (in mil. 2017US$)
TARGET_VARS = [
    "countrycode", "country", "year",
    "hc",       # Human capital index (基于受教育年限和教育回报率)
    "cn",       # Capital stock at current PPPs (million 2017US$)
    "ck",       # Capital services levels at current PPPs (USA=1)
    "rgdpna",   # Real GDP at constant 2017 national prices (million 2017US$)
    "rnna",     # Capital stock at constant 2017 national prices (million 2017US$) — 资本存量水平值
    "rkna",     # Capital services index at constant 2017 national prices (2017=1)
    "pop",      # Population (millions)
    "emp",      # Number of persons engaged (millions)
    "avh",      # Average annual hours worked
    "ctfp",     # TFP level at current PPPs (USA=1)
    "rtfpna",   # TFP at constant national prices (2017=1)
]

# 额外可能有用的变量（用于计算投资率）
EXTRA_VARS = [
    "csh_i",    # Share of gross capital formation at current PPPs
    "delta",    # Depreciation rate of capital stock
    "labsh",    # Share of labour compensation in GDP at current national prices
    "irr",      # Real internal rate of return
    "rgdpe",    # Expenditure-side real GDP at chained PPPs (million 2017US$)
    "rgdpo",    # Output-side real GDP at chained PPPs (million 2017US$)
]

# ============================================================
# 1. 下载 PWT 数据
# ============================================================

def download_pwt():
    """尝试多个源下载 PWT 10.01 数据，返回 DataFrame"""

    # 文件 ID 来自 Dataverse API 查询 (doi:10.34894/QT5BCC)
    # 354098 = pwt1001.dta (主表, 3.3MB), 354095 = pwt1001.xlsx (主表, 6.4MB)
    # 354099 = pwt1001_na_data.dta (仅国民账户子集，不含 hc/rkna 等)
    urls = [
        ("Dataverse main (stata)", "https://dataverse.nl/api/access/datafile/354098", "dta"),
        ("Dataverse main (xlsx)", "https://dataverse.nl/api/access/datafile/354095", "xlsx"),
        ("RUG official (xlsx)", "https://www.rug.nl/ggdc/docs/pwt1001.xlsx", "xlsx"),
    ]

    # 如果缓存文件存在，直接读取
    cache_dta = RAW_DIR / "pwt1001_cache.dta"
    if cache_dta.exists() and cache_dta.stat().st_size > 2_000_000:
        print(f"[INFO] 发现 Stata 缓存文件: {cache_dta}")
        try:
            df = pd.read_stata(cache_dta)
            if df.shape[1] > 30:  # 主表应有 50+ 列
                print(f"[INFO] 从 Stata 缓存读取成功: {df.shape[0]} 行, {df.shape[1]} 列")
                return df
            else:
                print(f"[WARN] 缓存文件列数过少 ({df.shape[1]})，可能不是主表，重新下载")
        except Exception as e:
            print(f"[WARN] Stata 缓存读取失败: {e}")

    if CACHE_FILE.exists() and CACHE_FILE.stat().st_size > 2_000_000:
        print(f"[INFO] 发现 Excel 缓存文件: {CACHE_FILE}")
        try:
            df = pd.read_excel(CACHE_FILE, sheet_name="Data", engine="openpyxl")
            if df.shape[1] > 30:
                print(f"[INFO] 从 Excel 缓存读取成功: {df.shape[0]} 行, {df.shape[1]} 列")
                return df
        except Exception as e:
            print(f"[WARN] Excel 缓存读取失败: {e}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    for name, url, fmt in urls:
        print(f"\n[INFO] 尝试下载: {name}")
        print(f"       URL: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
            print(f"       HTTP {resp.status_code}, 大小: {len(resp.content) / 1024:.0f} KB")

            if resp.status_code != 200:
                print(f"[WARN] HTTP {resp.status_code}，跳过")
                continue

            if len(resp.content) < 10000:
                print(f"[WARN] 文件过小 ({len(resp.content)} bytes)，可能不是数据文件")
                # 检查是否为 HTML 错误页面
                try:
                    text_preview = resp.content[:500].decode("utf-8", errors="ignore")
                    if "<html" in text_preview.lower():
                        print(f"[WARN] 返回了 HTML 页面，跳过")
                        continue
                except:
                    pass

            if fmt == "xlsx":
                # 保存缓存
                with open(CACHE_FILE, "wb") as f:
                    f.write(resp.content)
                print(f"[INFO] 已缓存到: {CACHE_FILE}")

                # 读取 Data sheet
                try:
                    df = pd.read_excel(
                        io.BytesIO(resp.content),
                        sheet_name="Data",
                        engine="openpyxl"
                    )
                except Exception:
                    # 某些版本 sheet 名称可能不同，尝试第一个 sheet
                    df = pd.read_excel(
                        io.BytesIO(resp.content),
                        sheet_name=0,
                        engine="openpyxl"
                    )

                print(f"[INFO] 读取成功: {df.shape[0]} 行, {df.shape[1]} 列")
                return df

            elif fmt == "dta":
                # Stata 格式
                cache_dta = RAW_DIR / "pwt1001_cache.dta"
                with open(cache_dta, "wb") as f:
                    f.write(resp.content)
                print(f"[INFO] 已缓存到: {cache_dta}")

                df = pd.read_stata(io.BytesIO(resp.content))
                print(f"[INFO] 读取成功: {df.shape[0]} 行, {df.shape[1]} 列")
                return df

        except requests.exceptions.Timeout:
            print(f"[WARN] 下载超时，跳过")
        except requests.exceptions.ConnectionError as e:
            print(f"[WARN] 连接失败: {e}")
        except Exception as e:
            print(f"[WARN] 处理失败: {e}")

    return None


# ============================================================
# 2. World Bank 备用数据
# ============================================================

def fetch_world_bank_fallback():
    """如果 PWT 下载完全失败，使用 World Bank API 获取替代数据"""

    print("\n" + "=" * 60)
    print("[FALLBACK] PWT 下载全部失败，启用 World Bank 备用方案")
    print("=" * 60)

    # World Bank API v2 (JSON format)
    base_url = "https://api.worldbank.org/v2/country/all/indicator"

    indicators = {
        "HD.HCI.OVRL": "human_capital_index",
        "NY.ADJ.NNTY.PC.CD": "adj_nni_per_capita",
        "NY.GDP.MKTP.CD": "gdp_current_usd",
        "NY.GDP.MKTP.KD": "gdp_constant_usd",
        "SP.POP.TOTL": "population",
        "NE.GDI.FTOT.ZS": "gross_fixed_capital_pct_gdp",
        "SE.ADT.LITR.ZS": "literacy_rate",
        "SE.SCH.LIFE": "expected_schooling_years",
    }

    all_data = []

    for indicator_code, var_name in indicators.items():
        print(f"\n[INFO] 获取 World Bank 指标: {indicator_code} ({var_name})")

        try:
            url = (
                f"{base_url}/{indicator_code}"
                f"?format=json&per_page=20000&date=1960:2023"
            )
            resp = requests.get(url, timeout=60)

            if resp.status_code != 200:
                print(f"[WARN] HTTP {resp.status_code}，跳过 {indicator_code}")
                continue

            data = resp.json()

            if not isinstance(data, list) or len(data) < 2:
                print(f"[WARN] 无数据返回，跳过 {indicator_code}")
                continue

            records = data[1]
            print(f"       获取 {len(records)} 条记录")

            for rec in records:
                if rec.get("value") is not None:
                    all_data.append({
                        "countrycode": rec["countryiso3code"],
                        "country": rec["country"]["value"],
                        "year": int(rec["date"]),
                        "indicator": var_name,
                        "value": float(rec["value"]),
                    })

        except Exception as e:
            print(f"[WARN] 获取失败: {e}")

    if not all_data:
        print("[ERROR] World Bank 备用方案也失败了")
        return None

    # 转为宽表
    df_long = pd.DataFrame(all_data)
    df_wide = df_long.pivot_table(
        index=["countrycode", "country", "year"],
        columns="indicator",
        values="value"
    ).reset_index()
    df_wide.columns.name = None

    # 计算人均 GDP
    if "gdp_constant_usd" in df_wide.columns and "population" in df_wide.columns:
        df_wide["gdp_per_capita"] = df_wide["gdp_constant_usd"] / df_wide["population"]

    print(f"\n[INFO] World Bank 备用数据: {df_wide.shape[0]} 行, {df_wide.shape[1]} 列")
    print(f"       国家数: {df_wide['countrycode'].nunique()}")
    print(f"       年份范围: {df_wide['year'].min()} - {df_wide['year'].max()}")

    return df_wide


# ============================================================
# 3. 数据处理
# ============================================================

def process_pwt(df):
    """处理 PWT 原始数据，提取目标变量并计算衍生指标"""

    # 统一列名为小写
    df.columns = [c.lower().strip() for c in df.columns]

    print(f"\n[INFO] PWT 原始数据列名 ({len(df.columns)} 列):")
    print(f"       {list(df.columns)}")

    # 筛选可用的目标变量
    available = [v for v in TARGET_VARS if v in df.columns]
    extra_avail = [v for v in EXTRA_VARS if v in df.columns]
    missing = [v for v in TARGET_VARS if v not in df.columns]

    print(f"\n[INFO] 目标变量匹配:")
    print(f"       可用 ({len(available)}): {available}")
    print(f"       额外 ({len(extra_avail)}): {extra_avail}")
    if missing:
        print(f"       缺失 ({len(missing)}): {missing}")

    # 选取变量
    select_cols = available + extra_avail
    df_out = df[select_cols].copy()

    # 基本统计
    n_countries = df_out["countrycode"].nunique()
    year_min = df_out["year"].min()
    year_max = df_out["year"].max()
    n_rows = len(df_out)

    print(f"\n[INFO] 数据覆盖范围:")
    print(f"       国家/地区数: {n_countries}")
    print(f"       时间跨度: {year_min} - {year_max}")
    print(f"       总行数: {n_rows}")

    # ----------------------------------------------------------
    # 确保数值精度：float32 -> float64
    # ----------------------------------------------------------
    numeric_cols = df_out.select_dtypes(include=["float32"]).columns
    if len(numeric_cols) > 0:
        print(f"\n[INFO] 将 {len(numeric_cols)} 个 float32 列转换为 float64 以保证精度")
        for col in numeric_cols:
            df_out[col] = df_out[col].astype(np.float64)

    # ----------------------------------------------------------
    # 计算衍生变量
    # 注意：rnna = 资本存量水平值 (million 2017US$)
    #       rkna = 资本服务指数 (2017=1)，不是水平值
    # ----------------------------------------------------------

    # 资本-产出比 K/Y = rnna / rgdpna （使用资本存量水平值）
    if "rnna" in df_out.columns and "rgdpna" in df_out.columns:
        df_out["ky_ratio"] = df_out["rnna"] / df_out["rgdpna"]
        # 排除极端值
        df_out.loc[df_out["ky_ratio"] > 20, "ky_ratio"] = np.nan
        df_out.loc[df_out["ky_ratio"] < 0, "ky_ratio"] = np.nan
        valid_ky = df_out["ky_ratio"].dropna()
        print(f"\n[INFO] 资本-产出比 K/Y (rnna/rgdpna):")
        print(f"       均值: {valid_ky.mean():.2f}")
        print(f"       中位数: {valid_ky.median():.2f}")
        print(f"       范围: {valid_ky.min():.2f} - {valid_ky.max():.2f}")

    # 人均资本 k = rnna / pop （单位：million 2017US$ / million people = US$ per capita）
    if "rnna" in df_out.columns and "pop" in df_out.columns:
        df_out["k_per_capita"] = df_out["rnna"] / df_out["pop"]
        valid_k = df_out["k_per_capita"].dropna()
        print(f"\n[INFO] 人均资本 k (rnna/pop, US$ per capita):")
        print(f"       均值: {valid_k.mean():,.0f}")
        print(f"       中位数: {valid_k.median():,.0f}")

    # 人均 GDP = rgdpna / pop
    if "rgdpna" in df_out.columns and "pop" in df_out.columns:
        df_out["gdp_per_capita"] = df_out["rgdpna"] / df_out["pop"]

    # 投资率
    # 方法1：csh_i = 投资占 GDP 份额（直接来自 PWT）
    if "csh_i" in df_out.columns:
        df_out["investment_rate"] = df_out["csh_i"]
        print(f"\n[INFO] 投资率 (csh_i):")
        print(f"       均值: {df_out['investment_rate'].mean():.3f}")

    # 方法2：从 ΔK + δK 反推投资（使用 PWT 提供的 delta 或假设 5%）
    if "rnna" in df_out.columns and "rgdpna" in df_out.columns:
        df_out = df_out.sort_values(["countrycode", "year"])

        df_out["rnna_lag"] = df_out.groupby("countrycode")["rnna"].shift(1)

        # 使用 PWT 提供的折旧率 delta，如不可用则假设 5%
        if "delta" in df_out.columns:
            dep_rate = df_out["delta"].fillna(0.05)
            print(f"\n[INFO] 使用 PWT 提供的折旧率 (delta):")
            print(f"       均值: {df_out['delta'].mean():.4f}")
        else:
            dep_rate = 0.05

        df_out["investment_implied"] = (
            df_out["rnna"] - df_out["rnna_lag"] + dep_rate * df_out["rnna_lag"]
        )
        df_out["investment_rate_implied"] = df_out["investment_implied"] / df_out["rgdpna"]

        # 清理不合理值
        df_out.loc[df_out["investment_rate_implied"] < -0.5, "investment_rate_implied"] = np.nan
        df_out.loc[df_out["investment_rate_implied"] > 1.0, "investment_rate_implied"] = np.nan

        valid_ir = df_out["investment_rate_implied"].dropna()
        print(f"\n[INFO] 隐含投资率 (ΔK + δK)/Y:")
        print(f"       均值: {valid_ir.mean():.3f}")
        print(f"       中位数: {valid_ir.median():.3f}")

        # 清除临时列
        df_out.drop(columns=["rnna_lag"], inplace=True)

    return df_out, {
        "n_countries": n_countries,
        "year_min": int(year_min),
        "year_max": int(year_max),
        "n_rows": n_rows,
        "available_vars": available,
        "extra_vars": extra_avail,
        "missing_vars": missing,
    }


# ============================================================
# 4. 生成摘要报告
# ============================================================

def write_summary(df, meta, output_path, source="PWT 10.01"):
    """生成数据摘要报告"""

    lines = []
    lines.append("=" * 70)
    lines.append(f"Penn World Table 数据摘要报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"数据来源: {source}")
    lines.append("=" * 70)

    lines.append(f"\n## 1. 数据覆盖范围")
    lines.append(f"   国家/地区数: {meta['n_countries']}")
    lines.append(f"   时间跨度: {meta['year_min']} - {meta['year_max']}")
    lines.append(f"   总观测数: {meta['n_rows']}")

    lines.append(f"\n## 2. 变量清单")
    lines.append(f"   已提取 ({len(meta['available_vars'])}): {', '.join(meta['available_vars'])}")
    if meta['extra_vars']:
        lines.append(f"   额外变量 ({len(meta['extra_vars'])}): {', '.join(meta['extra_vars'])}")
    if meta['missing_vars']:
        lines.append(f"   缺失变量 ({len(meta['missing_vars'])}): {', '.join(meta['missing_vars'])}")

    lines.append(f"\n## 3. 关键变量描述性统计")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col == "year":
            continue
        s = df[col].dropna()
        if len(s) == 0:
            continue
        lines.append(f"\n   {col}:")
        lines.append(f"     N (非缺失): {len(s)}")
        lines.append(f"     均值: {s.mean():.4f}")
        lines.append(f"     标准差: {s.std():.4f}")
        lines.append(f"     最小值: {s.min():.4f}")
        lines.append(f"     25%: {s.quantile(0.25):.4f}")
        lines.append(f"     中位数: {s.median():.4f}")
        lines.append(f"     75%: {s.quantile(0.75):.4f}")
        lines.append(f"     最大值: {s.max():.4f}")
        lines.append(f"     缺失率: {df[col].isna().mean():.1%}")

    # 关键国家数据概览
    lines.append(f"\n## 4. 关键国家最新数据 (2019)")
    key_countries = ["CHN", "JPN", "USA", "GBR", "DEU", "FRA", "KOR", "IND", "BRA"]
    show_cols = ["countrycode", "country", "year", "hc", "rnna", "rgdpna", "pop",
                 "ky_ratio", "k_per_capita", "gdp_per_capita", "delta"]
    show_cols = [c for c in show_cols if c in df.columns]

    df_2019 = df[(df["year"] == 2019) & (df["countrycode"].isin(key_countries))].copy()
    if len(df_2019) == 0:
        # 尝试最新可用年份
        latest_year = df[df["countrycode"].isin(key_countries)]["year"].max()
        df_2019 = df[(df["year"] == latest_year) & (df["countrycode"].isin(key_countries))].copy()
        lines.append(f"   (2019年数据不可用，使用最新年份 {latest_year})")

    if len(df_2019) > 0:
        for _, row in df_2019[show_cols].iterrows():
            lines.append(f"\n   {row.get('country', row.get('countrycode', 'N/A'))} ({row.get('countrycode', '')}):")
            if "hc" in row and pd.notna(row["hc"]):
                lines.append(f"     人力资本指数 (hc): {row['hc']:.3f}")
            if "rnna" in row and pd.notna(row["rnna"]):
                lines.append(f"     资本存量 (rnna): {row['rnna']:,.0f} million 2017US$")
            if "rgdpna" in row and pd.notna(row["rgdpna"]):
                lines.append(f"     实际GDP (rgdpna): {row['rgdpna']:,.0f} million 2017US$")
            if "pop" in row and pd.notna(row["pop"]):
                lines.append(f"     人口 (pop): {row['pop']:.2f} million")
            if "ky_ratio" in row and pd.notna(row["ky_ratio"]):
                lines.append(f"     资本-产出比 (K/Y): {row['ky_ratio']:.2f}")
            if "k_per_capita" in row and pd.notna(row["k_per_capita"]):
                lines.append(f"     人均资本: {row['k_per_capita']:,.0f} US$")
            if "gdp_per_capita" in row and pd.notna(row["gdp_per_capita"]):
                lines.append(f"     人均GDP: {row['gdp_per_capita']:,.0f} US$")

    # 中国时序概览
    lines.append(f"\n## 5. 中国资本-产出比演变")
    if "ky_ratio" in df.columns:
        df_chn = df[df["countrycode"] == "CHN"][["year", "ky_ratio", "k_per_capita", "hc"]].dropna(subset=["ky_ratio"])
        if len(df_chn) > 0:
            for _, row in df_chn.iterrows():
                hc_str = f"  hc={row['hc']:.3f}" if pd.notna(row.get("hc")) else ""
                kpc_str = f"  k_per_capita={row['k_per_capita']:,.0f}" if pd.notna(row.get("k_per_capita")) else ""
                lines.append(f"   {int(row['year'])}: K/Y = {row['ky_ratio']:.3f}{kpc_str}{hc_str}")

    lines.append(f"\n{'=' * 70}")
    lines.append(f"报告结束")
    lines.append(f"{'=' * 70}")

    text = "\n".join(lines)
    output_path.write_text(text, encoding="utf-8")
    print(f"\n[INFO] 摘要报告已保存: {output_path}")
    return text


# ============================================================
# 5. 主流程
# ============================================================

def main():
    print("=" * 70)
    print("21_penn_world_table.py — PWT 10.01 数据获取与处理")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 第一步：尝试下载 PWT
    df_raw = download_pwt()

    if df_raw is not None:
        # PWT 下载成功，处理数据
        print("\n[SUCCESS] PWT 数据下载成功")

        df_processed, meta = process_pwt(df_raw)

        # 保存 CSV
        df_processed.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        print(f"\n[INFO] 处理后数据已保存: {OUTPUT_CSV}")
        print(f"       大小: {OUTPUT_CSV.stat().st_size / 1024:.0f} KB")

        # 生成摘要
        summary = write_summary(df_processed, meta, OUTPUT_SUMMARY, source="PWT 10.01")

    else:
        # PWT 下载全部失败，使用 World Bank 备用
        print("\n[WARN] PWT 所有下载源均失败")

        df_wb = fetch_world_bank_fallback()

        if df_wb is not None:
            output_csv_wb = RAW_DIR / "penn_world_table_wb_proxy.csv"
            output_summary_wb = RAW_DIR / "pwt_data_summary_wb_proxy.txt"

            df_wb.to_csv(output_csv_wb, index=False, encoding="utf-8-sig")
            print(f"\n[INFO] World Bank 备用数据已保存: {output_csv_wb}")

            meta_wb = {
                "n_countries": df_wb["countrycode"].nunique(),
                "year_min": int(df_wb["year"].min()),
                "year_max": int(df_wb["year"].max()),
                "n_rows": len(df_wb),
                "available_vars": [c for c in df_wb.columns if c not in ["countrycode", "country", "year"]],
                "extra_vars": [],
                "missing_vars": ["hc", "cn", "ck", "rkna", "rgdpna", "emp", "avh", "ctfp"],
            }

            write_summary(df_wb, meta_wb, output_summary_wb, source="World Bank API (proxy)")

            print(f"\n[IMPORTANT] 使用了 World Bank 备用数据，不是 PWT 原始数据。")
            print(f"            文件名包含 'wb_proxy' 标识。")
            print(f"            建议后续手动下载 PWT 10.01 替换。")
        else:
            print("\n[ERROR] PWT 和 World Bank 备用方案均失败。")
            print("        请手动下载 PWT 10.01:")
            print("        https://www.rug.nl/ggdc/productivity/pwt/")
            sys.exit(1)

    print("\n[DONE] 脚本执行完毕")


if __name__ == "__main__":
    main()
