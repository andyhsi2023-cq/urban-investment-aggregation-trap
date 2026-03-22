"""
20_world_bank_data.py
=====================
目的：从 World Bank Open Data API 批量获取跨国宏观经济与人口指标数据
输入：World Bank API v2
输出：
  - 02-data/raw/world_bank_all_countries.csv（完整面板数据）
  - 02-data/processed/world_bank_usable_panel.csv（筛选后可用国家面板）
  - 02-data/raw/world_bank_data_summary.txt（数据摘要报告）
依赖：requests, pandas, time
"""

import requests
import pandas as pd
import time
import sys
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
PROJECT_ROOT = Path("/Users/andy/Desktop/Claude/urban-q-phase-transition")
RAW_DIR = PROJECT_ROOT / "02-data" / "raw"
PROC_DIR = PROJECT_ROOT / "02-data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 指标定义
# ============================================================
INDICATORS = {
    "NY.GDP.MKTP.CD":     "GDP (current US$)",
    "NY.GDP.MKTP.KD":     "GDP (constant 2015 US$)",
    "NE.GDI.FTOT.ZS":     "Gross fixed capital formation (% of GDP)",
    "NE.GDI.FTOT.CD":     "Gross fixed capital formation (current US$)",
    "NE.CON.GOVT.ZS":     "General government final consumption expenditure (% of GDP)",
    "NV.SRV.TOTL.ZS":     "Services, value added (% of GDP)",
    "NV.IND.TOTL.ZS":     "Industry (including construction), value added (% of GDP)",
    "NV.AGR.TOTL.ZS":     "Agriculture, forestry, and fishing, value added (% of GDP)",
    "SP.URB.TOTL.IN.ZS":  "Urban population (% of total population)",
    "SP.URB.TOTL":         "Urban population",
    "SP.POP.TOTL":         "Population, total",
    "SP.POP.1564.TO.ZS":  "Population ages 15-64 (% of total population)",
    "SP.POP.65UP.TO.ZS":  "Population ages 65 and above (% of total population)",
}

# ============================================================
# API 配置
# ============================================================
BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/{indicator}"
COUNTRY_URL = "https://api.worldbank.org/v2/country"
PER_PAGE = 20000
MAX_RETRIES = 3
RETRY_DELAY = 3  # 秒


def api_get(url, params, timeout=60):
    """带重试机制的 API 请求"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"    [重试 {attempt}/{MAX_RETRIES}] 请求失败: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                print(f"    [错误] 请求彻底失败")
                return None


def get_country_set():
    """
    从 World Bank Country API 获取真实国家列表（排除聚合体）。
    返回 dict: {iso2_code: {'iso3': ..., 'name': ..., 'region': ...}}
    """
    print("获取 World Bank 国家列表...")
    params = {"format": "json", "per_page": 500}
    data = api_get(COUNTRY_URL, params)
    if data is None or len(data) < 2:
        print("[错误] 无法获取国家列表")
        sys.exit(1)

    countries = {}
    for entry in data[1]:
        # 排除聚合体（region 为 'Aggregates' 的条目）
        if entry["region"]["value"] == "Aggregates":
            continue
        iso2 = entry["iso2Code"]
        iso3 = entry["id"]  # World Bank 'id' 字段是 ISO alpha-3
        name = entry["name"]
        region = entry["region"]["value"]
        countries[iso2] = {"iso3": iso3, "name": name, "region": region}

    print(f"  真实国家/地区数量: {len(countries)}")
    return countries


def fetch_indicator(indicator_code, country_iso2_set):
    """
    从 World Bank API 获取某一指标的全部数据，仅保留真实国家。
    返回 list of dict: [{'country_iso2', 'country_iso3', 'country_name', 'year', 'value'}, ...]
    """
    url = BASE_URL.format(indicator=indicator_code)
    params = {
        "date": "1960:2023",
        "format": "json",
        "per_page": PER_PAGE,
        "page": 1,
    }

    all_records = []
    page = 1

    while True:
        params["page"] = page
        data = api_get(url, params)

        if data is None or len(data) < 2 or data[1] is None:
            break

        metadata = data[0]
        records = data[1]
        total = metadata.get("total", 0)
        pages = metadata.get("pages", 1)

        if page == 1:
            print(f"    总记录数: {total}, 总页数: {pages}")

        for rec in records:
            iso2 = rec.get("country", {}).get("id", "")
            # 只保留真实国家
            if iso2 not in country_iso2_set:
                continue

            country_name = rec.get("country", {}).get("value", "")
            iso3 = rec.get("countryiso3code", "")
            year_str = rec.get("date", "")
            value = rec.get("value")

            all_records.append({
                "country_iso2": iso2,
                "country_iso3": iso3,
                "country_name": country_name,
                "year": int(year_str) if year_str else None,
                "value": value,
            })

        if page >= pages:
            break
        page += 1
        time.sleep(0.5)

    return all_records


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("World Bank Open Data 批量获取脚本")
    print(f"指标数量: {len(INDICATORS)}")
    print(f"时间范围: 1960-2023")
    print("=" * 60)

    # 0. 获取真实国家列表
    country_map = get_country_set()
    country_iso2_set = set(country_map.keys())

    # 1. 逐指标获取数据
    indicator_dfs = {}

    for i, (code, desc) in enumerate(INDICATORS.items(), 1):
        print(f"\n[{i}/{len(INDICATORS)}] 获取: {code} -- {desc}")
        records = fetch_indicator(code, country_iso2_set)
        print(f"    有效记录数: {len(records)}")

        if records:
            df = pd.DataFrame(records)
            df = df.rename(columns={"value": code})
            indicator_dfs[code] = df

        # 指标间等待，避免限速
        if i < len(INDICATORS):
            time.sleep(1)

    if not indicator_dfs:
        print("[错误] 未获取到任何数据，退出")
        sys.exit(1)

    # 2. 合并为宽格式面板
    print("\n" + "=" * 60)
    print("合并数据为宽格式面板...")

    merge_keys = ["country_iso2", "country_iso3", "country_name", "year"]
    merged = None
    for code, df in indicator_dfs.items():
        subset = df[merge_keys + [code]].copy()
        if merged is None:
            merged = subset
        else:
            merged = merged.merge(subset, on=merge_keys, how="outer")

    # 排序、去重
    merged = merged.sort_values(["country_iso3", "year"]).reset_index(drop=True)
    merged = merged.drop_duplicates(subset=["country_iso3", "year"]).reset_index(drop=True)

    # 转换数据类型
    for code in INDICATORS:
        if code in merged.columns:
            merged[code] = pd.to_numeric(merged[code], errors="coerce")

    # 补充 region 信息
    merged["region"] = merged["country_iso2"].map(
        lambda x: country_map.get(x, {}).get("region", "")
    )

    # 重新排列列顺序
    id_cols = ["country_iso3", "country_iso2", "country_name", "region", "year"]
    ind_cols = [c for c in INDICATORS if c in merged.columns]
    merged = merged[id_cols + ind_cols]

    # 3. 统计信息
    all_countries = sorted(merged["country_iso3"].unique())
    n_countries = len(all_countries)
    year_range = (int(merged["year"].min()), int(merged["year"].max()))

    print(f"国家/地区数量: {n_countries}")
    print(f"年份范围: {year_range[0]}-{year_range[1]}")
    print(f"总行数: {len(merged)}")

    # 各指标覆盖率
    coverage = {}
    for code in INDICATORS:
        if code in merged.columns:
            non_null = int(merged[code].notna().sum())
            total = len(merged)
            pct = non_null / total * 100
            # 也计算有多少国家至少有1个非空值
            n_cty = int(merged[merged[code].notna()]["country_iso3"].nunique())
            coverage[code] = {
                "non_null": non_null,
                "total": total,
                "pct": pct,
                "n_countries": n_cty,
            }
            print(f"  {code}: {non_null}/{total} ({pct:.1f}%), {n_cty} 个国家")

    # 4. 筛选可用国家
    print("\n" + "=" * 60)
    print("筛选可用国家（2000-2020 期间，GDP/GFCF/城镇化率各 >=15 年有数据）...")

    core_indicators = ["NY.GDP.MKTP.CD", "NE.GDI.FTOT.ZS", "SP.URB.TOTL.IN.ZS"]
    period_mask = (merged["year"] >= 2000) & (merged["year"] <= 2020)
    period_df = merged[period_mask].copy()

    usable_countries = []
    for cc in all_countries:
        cc_data = period_df[period_df["country_iso3"] == cc]
        ok = True
        for ind in core_indicators:
            if ind not in cc_data.columns:
                ok = False
                break
            n_valid = int(cc_data[ind].notna().sum())
            if n_valid < 15:
                ok = False
                break
        if ok:
            usable_countries.append(cc)

    n_usable = len(usable_countries)
    print(f"可用国家数量: {n_usable}")

    # 获取可用国家名称
    country_names = (
        merged[merged["country_iso3"].isin(usable_countries)]
        .drop_duplicates("country_iso3")[["country_iso3", "country_name", "region"]]
        .sort_values("country_iso3")
    )

    print("\n可用国家列表:")
    for _, row in country_names.iterrows():
        print(f"  {row['country_iso3']}  {row['country_name']}  [{row['region']}]")

    # 5. 保存数据
    print("\n" + "=" * 60)
    print("保存数据...")

    # 5a. 完整数据
    out_all = RAW_DIR / "world_bank_all_countries.csv"
    merged.to_csv(out_all, index=False)
    print(f"  完整数据: {out_all} ({len(merged)} 行)")

    # 5b. 筛选后可用国家面板
    usable_df = merged[merged["country_iso3"].isin(usable_countries)].copy()
    out_usable = PROC_DIR / "world_bank_usable_panel.csv"
    usable_df.to_csv(out_usable, index=False)
    print(f"  可用国家面板: {out_usable} ({len(usable_df)} 行)")

    # 5c. 数据摘要报告
    summary_path = RAW_DIR / "world_bank_data_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("World Bank Open Data 数据摘要报告\n")
        f.write(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"数据来源: World Bank Open Data API v2\n")
        f.write(f"时间范围: {year_range[0]}-{year_range[1]}\n")
        f.write(f"国家/地区总数: {n_countries}\n")
        f.write(f"总行数 (country-year): {len(merged)}\n\n")

        f.write("指标覆盖率:\n")
        f.write("-" * 60 + "\n")
        for code, desc in INDICATORS.items():
            if code in coverage:
                c = coverage[code]
                f.write(f"  {code}\n")
                f.write(f"    {desc}\n")
                f.write(f"    有效值: {c['non_null']}/{c['total']} ({c['pct']:.1f}%)")
                f.write(f", 覆盖 {c['n_countries']} 个国家\n\n")

        f.write("=" * 60 + "\n")
        f.write("可用国家筛选标准:\n")
        f.write("  - GDP (NY.GDP.MKTP.CD): 2000-2020 期间 >= 15 年有数据\n")
        f.write("  - GFCF (NE.GDI.FTOT.ZS): 2000-2020 期间 >= 15 年有数据\n")
        f.write("  - 城镇化率 (SP.URB.TOTL.IN.ZS): 2000-2020 期间 >= 15 年有数据\n\n")
        f.write(f"可用国家数量: {n_usable}\n\n")

        f.write("可用国家列表:\n")
        f.write("-" * 60 + "\n")
        for _, row in country_names.iterrows():
            f.write(f"  {row['country_iso3']}  {row['country_name']}")
            f.write(f"  [{row['region']}]\n")

        # 按区域统计
        f.write("\n" + "=" * 60 + "\n")
        f.write("按区域统计可用国家数量:\n")
        f.write("-" * 60 + "\n")
        region_counts = country_names["region"].value_counts().sort_index()
        for region, count in region_counts.items():
            f.write(f"  {region}: {count}\n")

    print(f"  摘要报告: {summary_path}")
    print("\n" + "=" * 60)
    print("全部完成!")


if __name__ == "__main__":
    main()
