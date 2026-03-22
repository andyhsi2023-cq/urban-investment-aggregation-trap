"""
22_bis_un_data.py
=================
目的：获取住宅房地产价格指数（OECD）和人口年龄结构数据（World Bank / UN）
输入：在线 API（OECD SDMX-JSON, World Bank API, UN Data Portal API）
输出：
  - 02-data/raw/bis_property_prices.csv   — OECD 住房价格指数（~52 国家）
  - 02-data/raw/un_population.csv         — 全球人口数据（~200+ 国家）
  - 02-data/raw/data_acquisition_report.txt — 数据获取报告
依赖：pandas, requests, json, gzip
"""

import pandas as pd
import numpy as np
import requests
import json
import gzip
import io
import os
import time
from datetime import datetime

# === 路径配置 ===
RAW_DIR = "/Users/andy/Desktop/Claude/urban-q-phase-transition/02-data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

TIMEOUT = 60
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# 获取报告
report_lines = []
report_lines.append(f"数据获取报告 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("=" * 60)


def log(msg):
    print(msg, flush=True)
    report_lines.append(msg)


def try_download(url, description, **kwargs):
    """尝试下载 URL，返回 response 或 None"""
    log(f"\n尝试下载: {description}")
    log(f"  URL: {url[:120]}{'...' if len(url) > 120 else ''}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, **kwargs)
        resp.raise_for_status()
        log(f"  状态: 成功 (HTTP {resp.status_code}, {len(resp.content):,} bytes)")
        return resp
    except requests.exceptions.Timeout:
        log(f"  状态: 失败 — 超时 ({TIMEOUT}s)")
    except requests.exceptions.HTTPError as e:
        log(f"  状态: 失败 — HTTP {e.response.status_code}")
    except requests.exceptions.ConnectionError as e:
        log(f"  状态: 失败 — 连接错误: {str(e)[:100]}")
    except Exception as e:
        log(f"  状态: 失败 — {type(e).__name__}: {str(e)[:100]}")
    return None


# ============================================================
# 部分 1：OECD 住宅房地产价格指数
# ============================================================
log("\n" + "=" * 60)
log("部分 1：OECD 住宅房地产价格指数")
log("=" * 60)

bis_df = None

# --- 方案 A: OECD SDMX-JSON API (旧版 stats.oecd.org) ---
# 这个端点在首次测试中返回了 1.8MB 数据
resp = try_download(
    "https://stats.oecd.org/sdmx-json/data/HOUSE_PRICES/..Q..?"
    "startTime=1970&endTime=2024&dimensionAtObservation=allDimensions",
    "OECD SDMX-JSON API (HOUSE_PRICES, 季度数据)"
)

if resp is not None:
    try:
        raw = resp.json()
        structures = raw['data']['structures'][0]
        datasets = raw['data']['dataSets'][0]

        # 解析维度
        series_dims = structures['dimensions']['series']
        obs_dims = structures['dimensions']['observation']

        # 维度映射：索引 -> 值
        dim_maps = {}
        for dim in series_dims:
            dim_maps[dim['id']] = {
                str(i): v['id'] for i, v in enumerate(dim['values'])
            }
            dim_maps[dim['id'] + '_name'] = {
                str(i): v['name'] for i, v in enumerate(dim['values'])
            }

        time_map = {
            str(i): v['id'] for i, v in enumerate(obs_dims[0]['values'])
        }

        # 维度顺序：REF_AREA, FREQ, MEASURE, UNIT_MEASURE
        dim_order = [d['id'] for d in series_dims]
        log(f"  维度顺序: {dim_order}")
        log(f"  国家数: {len(dim_maps['REF_AREA'])}")
        log(f"  时间点数: {len(time_map)}")

        # 解析所有 series
        rows = []
        series = datasets['series']
        for series_key, series_data in series.items():
            # series_key 格式: "0:0:1:0" -> 对应各维度的索引
            key_parts = series_key.split(':')
            dim_values = {}
            for i, dim_id in enumerate(dim_order):
                dim_values[dim_id] = dim_maps[dim_id].get(key_parts[i], key_parts[i])
                dim_values[dim_id + '_name'] = dim_maps.get(dim_id + '_name', {}).get(key_parts[i], '')

            # 解析观测值
            for time_idx, obs_value in series_data.get('observations', {}).items():
                period = time_map.get(time_idx, time_idx)
                value = obs_value[0] if isinstance(obs_value, list) else obs_value
                row = {
                    'country_code': dim_values.get('REF_AREA', ''),
                    'country_name': dim_values.get('REF_AREA_name', ''),
                    'frequency': dim_values.get('FREQ', ''),
                    'measure': dim_values.get('MEASURE', ''),
                    'measure_name': dim_values.get('MEASURE_name', ''),
                    'unit': dim_values.get('UNIT_MEASURE', ''),
                    'period': period,
                    'value': value
                }
                rows.append(row)

        bis_df = pd.DataFrame(rows)
        bis_df['value'] = pd.to_numeric(bis_df['value'], errors='coerce')
        log(f"  解析完成: {bis_df.shape[0]:,} 条观测, {bis_df['country_code'].nunique()} 个国家")
        log(f"  指标类型: {bis_df['measure'].unique().tolist()}")
        log(f"  时间范围: {bis_df['period'].min()} ~ {bis_df['period'].max()}")
        log(f"  国家列表: {sorted(bis_df['country_code'].unique())}")

    except Exception as e:
        log(f"  解析失败: {type(e).__name__}: {e}")
        bis_df = None

# --- 方案 B: BIS 直接下载（备用） ---
if bis_df is None:
    for url, desc in [
        ("https://www.bis.org/statistics/pp/pp_long.csv", "BIS pp_long.csv"),
        ("https://www.bis.org/statistics/pp_selected.csv", "BIS pp_selected.csv"),
        ("https://data.bis.org/api/v2/data/dataflow/BIS/WS_SPP/1.0?format=csv&startPeriod=1970&endPeriod=2024",
         "BIS SDMX API"),
    ]:
        resp = try_download(url, desc)
        if resp is not None:
            try:
                bis_df = pd.read_csv(io.StringIO(resp.text))
                log(f"  解析成功: {bis_df.shape}")
                break
            except Exception as e:
                log(f"  解析失败: {e}")

# --- 保存 BIS/OECD 数据 ---
if bis_df is not None:
    outpath = os.path.join(RAW_DIR, "bis_property_prices.csv")
    bis_df.to_csv(outpath, index=False)
    log(f"\n已保存房价数据: {outpath}")
    log(f"  总行数: {bis_df.shape[0]:,}")
    log(f"  国家数: {bis_df['country_code'].nunique()}")

    # 生成摘要
    summary = bis_df.groupby(['country_code', 'measure']).agg(
        n_obs=('value', 'count'),
        min_period=('period', 'min'),
        max_period=('period', 'max')
    ).reset_index()
    log(f"\n  各国数据覆盖摘要 (前20行):")
    log(summary.head(20).to_string())
else:
    log("\n所有房价数据源均获取失败。")
    log("建议手动下载:")
    log("  1. https://www.bis.org/statistics/pp.htm -> Property prices CSV")
    log("  2. https://data-explorer.oecd.org/ -> 搜索 House Prices")
    log(f"  保存至: {os.path.join(RAW_DIR, 'bis_property_prices.csv')}")


# ============================================================
# 部分 2：人口数据（World Bank API + UN Data Portal）
# ============================================================
log("\n" + "=" * 60)
log("部分 2：人口年龄结构数据")
log("=" * 60)

# --- 方案 A: World Bank API ---
# World Bank 数据覆盖 200+ 国家，数据来源即 UN WPP
log("\n使用 World Bank API 获取人口数据...")

# 需要获取的指标
wb_indicators = {
    'SP.POP.TOTL': 'total_population',
    'SP.POP.0014.TO.ZS': 'pop_0_14_pct',
    'SP.POP.1564.TO.ZS': 'pop_15_64_pct',
    'SP.POP.65UP.TO.ZS': 'pop_65plus_pct',
    'SP.DYN.TFRT.IN': 'tfr',
    'SP.POP.GROW': 'pop_growth_rate',
    'SP.DYN.LE00.IN': 'life_expectancy',
    'SP.DYN.CDRT.IN': 'crude_death_rate',
    'SP.DYN.CBRT.IN': 'crude_birth_rate',
    'SP.POP.DPND': 'dependency_ratio',
    'SP.POP.DPND.OL': 'old_dependency_ratio',
    'SP.POP.DPND.YG': 'young_dependency_ratio',
    'SP.URB.TOTL.IN.ZS': 'urban_pop_pct',
}

# 获取国家列表（只要国家，不要聚合区域）
log("\n获取国家列表...")
countries_url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
resp = try_download(countries_url, "World Bank 国家列表")
country_info = {}
if resp is not None:
    cdata = resp.json()
    for c in cdata[1]:
        # 排除聚合区域（region.id == "NA" 表示国家）
        # 实际上 World Bank 用 aggregates 标记
        if c.get('region', {}).get('id', '') != 'NA':
            # 这是非聚合区域（即国家）
            pass
        # 保存所有，稍后按 ISO3 筛选
        country_info[c['id']] = {
            'iso3': c['id'],
            'iso2': c.get('iso2Code', ''),
            'name': c['name'],
            'region': c.get('region', {}).get('value', ''),
            'income_level': c.get('incomeLevel', {}).get('value', ''),
            'lending_type': c.get('lendingType', {}).get('value', ''),
        }
    log(f"  获取到 {len(country_info)} 个国家/地区")

# 逐个指标获取数据
all_data = {}  # {indicator_name: DataFrame}

for wb_code, col_name in wb_indicators.items():
    log(f"\n获取指标: {col_name} ({wb_code})")

    # World Bank API 每页最多 32767 条
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{wb_code}"
           f"?format=json&per_page=20000&date=1960:2024")
    resp = try_download(url, f"World Bank {col_name}")

    if resp is None:
        log(f"  跳过指标 {col_name}")
        continue

    try:
        data = resp.json()
        page_info = data[0]
        records = data[1] if len(data) > 1 else []

        total_pages = page_info.get('pages', 1)
        total_records = page_info.get('total', 0)
        log(f"  总记录数: {total_records}, 页数: {total_pages}")

        # 如果有多页，获取后续页面
        all_records = list(records) if records else []
        for page in range(2, total_pages + 1):
            page_url = url + f"&page={page}"
            resp2 = requests.get(page_url, headers=HEADERS, timeout=TIMEOUT)
            if resp2.status_code == 200:
                pdata = resp2.json()
                if len(pdata) > 1 and pdata[1]:
                    all_records.extend(pdata[1])
            time.sleep(0.3)  # 礼貌性延迟

        # 解析为 DataFrame
        rows = []
        for r in all_records:
            if r is None:
                continue
            rows.append({
                'iso3': r.get('countryiso3code', ''),
                'country_code': r.get('country', {}).get('id', ''),
                'year': int(r['date']) if r.get('date') else None,
                col_name: r.get('value'),
            })

        df = pd.DataFrame(rows)
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        df = df.dropna(subset=[col_name])

        n_countries = df['iso3'].nunique()
        year_range = f"{df['year'].min():.0f} ~ {df['year'].max():.0f}" if len(df) > 0 else "N/A"
        log(f"  有效数据: {len(df):,} 条, {n_countries} 个国家, {year_range}")

        all_data[col_name] = df[['iso3', 'country_code', 'year', col_name]]

    except Exception as e:
        log(f"  解析失败: {type(e).__name__}: {e}")

    time.sleep(0.5)  # API 礼貌性延迟

# --- 合并所有指标 ---
if all_data:
    log("\n--- 合并人口指标 ---")

    # 高效合并：先转长格式再 pivot，避免反复 outer merge
    long_frames = []
    for col_name, df in all_data.items():
        temp = df[['iso3', 'country_code', 'year', col_name]].copy()
        temp = temp.rename(columns={col_name: 'value'})
        temp['indicator'] = col_name
        long_frames.append(temp)

    long_df = pd.concat(long_frames, ignore_index=True)
    log(f"  长格式合并: {long_df.shape[0]:,} 行")

    # 转宽格式
    merged = long_df.pivot_table(
        index=['iso3', 'country_code', 'year'],
        columns='indicator',
        values='value',
        aggfunc='first'
    ).reset_index()
    merged.columns.name = None  # 移除 MultiIndex 名称
    log(f"  宽格式: {merged.shape[0]:,} 行, {merged.shape[1]} 列")

    # 补充国家名称和区域信息
    if country_info:
        info_df = pd.DataFrame(country_info.values())
        merged = merged.merge(
            info_df[['iso3', 'name', 'region', 'income_level']],
            on='iso3',
            how='left'
        )
        # 重排列
        id_cols = ['iso3', 'country_code', 'name', 'region', 'income_level', 'year']
        data_cols = [c for c in merged.columns if c not in id_cols]
        merged = merged[id_cols + data_cols]

    # 排除区域聚合（保留真正的国家）
    # World Bank 聚合区域的 ISO3 通常不是标准3字母代码
    # 或者用 region 列来判断
    if 'region' in merged.columns:
        # 有 region 信息的是国家，聚合区域通常没有 region
        # 但更可靠的方法是排除已知聚合代码
        aggregate_codes = {
            'WLD', 'HIC', 'LIC', 'LMC', 'LMY', 'MIC', 'UMC',
            'EAS', 'ECS', 'LCN', 'MEA', 'NAC', 'SAS', 'SSF',
            'EMU', 'EUU', 'OED', 'ARB', 'CSS', 'FCS', 'HPC',
            'IBD', 'IBT', 'IDA', 'IDB', 'IDX', 'INX', 'LDC',
            'LTE', 'MNA', 'OSS', 'PRE', 'PSS', 'PST', 'SSA',
            'SST', 'TEA', 'TEC', 'TLA', 'TMN', 'TSA', 'TSS',
            'AFE', 'AFW', 'CEB', 'EAP', 'EAR', 'ECR',
            'LAC', 'LCR', 'MEI',
        }
        before = merged['iso3'].nunique()
        merged_countries = merged[~merged['iso3'].isin(aggregate_codes)].copy()
        after = merged_countries['iso3'].nunique()
        log(f"排除聚合区域: {before} -> {after} 个国家/地区")
    else:
        merged_countries = merged.copy()

    # 计算额外指标
    if 'pop_15_64_pct' in merged_countries.columns:
        merged_countries['working_age_pct'] = merged_countries['pop_15_64_pct']
    if 'pop_65plus_pct' in merged_countries.columns:
        merged_countries['aging_rate'] = merged_countries['pop_65plus_pct']

    # 排序
    merged_countries = merged_countries.sort_values(['iso3', 'year']).reset_index(drop=True)

    n_countries = merged_countries['iso3'].nunique()
    n_years = merged_countries['year'].nunique()
    year_range = f"{merged_countries['year'].min():.0f} ~ {merged_countries['year'].max():.0f}"

    log(f"\n最终人口数据集:")
    log(f"  国家/地区数: {n_countries}")
    log(f"  年份范围: {year_range}")
    log(f"  年份数: {n_years}")
    log(f"  总行数: {merged_countries.shape[0]:,}")
    log(f"  列: {list(merged_countries.columns)}")

    # 各指标覆盖率
    log(f"\n  各指标非空率:")
    for col in merged_countries.columns:
        if col not in ['iso3', 'country_code', 'name', 'region', 'income_level', 'year']:
            pct = merged_countries[col].notna().mean() * 100
            log(f"    {col}: {pct:.1f}%")

    # 保存
    outpath = os.path.join(RAW_DIR, "un_population.csv")
    merged_countries.to_csv(outpath, index=False)
    log(f"\n已保存人口数据: {outpath}")

    # 额外尝试: UN Data Portal API 获取中位年龄（World Bank 没有此指标）
    log("\n--- 补充: UN Data Portal 中位年龄数据 ---")
    log("注意: UN Data Portal 数据接口需要认证 (HTTP 401)")
    log("中位年龄 (MedianAgePop, indicator #67) 需手动从以下来源获取:")
    log("  1. https://population.un.org/dataportal/ -> Median age")
    log("  2. 或手动下载 WPP2024 Excel/CSV 文件")
    log("  3. 下载页面: https://population.un.org/wpp/Download/")
else:
    log("\n所有人口数据源均获取失败。")
    log("建议手动下载:")
    log("  1. https://data.worldbank.org/indicator/SP.POP.TOTL")
    log("  2. https://population.un.org/wpp/Download/")


# ============================================================
# 写入数据获取报告
# ============================================================
log("\n" + "=" * 60)
log("数据获取总结")
log("=" * 60)

if bis_df is not None:
    log(f"[成功] 房价数据: {bis_df.shape[0]:,} 条, {bis_df['country_code'].nunique()} 国家")
else:
    log("[失败] 房价数据: 需手动下载")

if all_data:
    log(f"[成功] 人口数据: {merged_countries.shape[0]:,} 条, {n_countries} 国家")
    log(f"       指标数: {len(all_data)}")
else:
    log("[失败] 人口数据: 需手动下载")

report_path = os.path.join(RAW_DIR, "data_acquisition_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n{'=' * 60}")
print(f"报告已保存: {report_path}")
print(f"{'=' * 60}")
