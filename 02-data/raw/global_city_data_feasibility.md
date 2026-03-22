# 全球城市级数据可行性普查报告

**项目**: Urban Q Phase Transition
**撰写日期**: 2026-03-22
**撰写人**: data-analyst
**目的**: 评估 14 个优先国家城市级数据的可获得性，识别"低垂果实"，规划全球城市面板构建路线

---

## 目录

- [Part 1: 全球城市级数据普查](#part-1-全球城市级数据普查)
- [Part 2: 历史时间序列数据源](#part-2-历史时间序列数据源)
- [Part 3: 可直接获取的"低垂果实"](#part-3-可直接获取的低垂果实)
- [Part 4: 日本深度评估](#part-4-日本深度评估)
- [Part 5: 构建"全球城市面板"的可行性](#part-5-构建全球城市面板的可行性)

---

## Part 1: 全球城市级数据普查

### 数据可得性总览矩阵

| 国家 | 空间单元 | 单元数 | GDP/经济产出 | 固定资产投资/GFCF | 房价/资产价值 | 人口 | 建成区面积 | 可构建 Urban Q? | 综合评级 |
|------|---------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 日本 | 都道府県 | 47 | A | B+ | A | A | B | **可行** | **A** |
| 韩国 | 広域市/道 | 17 | A | B | B+ | A | B | **可行** | **A-** |
| 英国 | LAD / NUTS-3 | 382/179 | A | C | A | A | C | **部分可行** | **B+** |
| 德国 | Kreise | 401 | A | C | B | A | C | **部分可行** | **B** |
| 巴西 | Municipios | 5,570 | B+ | D | D | A | C | **困难** | **C+** |
| 印度 | Districts / UA | 640/53 | C | D | D | A | D | **极困难** | **D+** |
| 印度尼西亚 | Kabupaten/Kota | 514 | B | D | D | A | D | **极困难** | **D** |
| 越南 | 省级 | 63 | B+ | C | D | A | C | **困难** | **C** |
| 墨西哥 | Municipios / ZM | 2,469/74 | B | D | C | A | C | **困难** | **C** |
| 土耳其 | 省级 (Il) | 81 | B+ | C | B | A | C | **部分可行** | **B-** |
| 泰国 | 府级 (Changwat) | 77 | B+ | D | D | A | D | **极困难** | **D+** |
| 尼日利亚 | 州级 (State) | 36+FCT | C | D | D | C | D | **不可行** | **D** |
| 南非 | Municipality | 257 | B | D | C | A | D | **困难** | **C-** |
| 俄罗斯 | 联邦主体 | 85 | B+ | C | C | A | C | **部分可行** | **B-** |

**评级标准**:
- A: 长时序(>30年)、公开可下载、口径一致
- B: 中等时序(15-30年)、公开但需整理
- C: 短时序(<15年)或需大量拼接
- D: 基本不可得或极度碎片化

---

### 1.1 日本 (Japan) — 47 都道府県

**空间单元**: 47 都道府県 (prefectures)
**城市化轨迹**: 1950 年 ~37% -> 2025 年 ~92%，完整覆盖从初期到成熟期

#### 城市 GDP / 经济产出
- **来源**: 内閣府「県民経済計算」(Prefectural Accounts / SNA)
- **URL**: https://www.esri.cao.go.jp/jp/sna/sonota/kenmin/kenmin_top.html
- **时间跨度**: 1955-present (68SNA: 1955-1974; 93SNA: 1975-2010; 08SNA: 2001-present)
- **最早年份**: 1955
- **最新年份**: 2021 (08SNA 基准，约滞后 3 年发布)
- **变量**: 県内総生産 (Gross Prefectural Product, GPP)，名义/实际
- **获取方式**: 内閣府网站 Excel 下载; e-Stat 数据库
- **免费**: 是
- **质量评级**: **A**
- **备注**: 需拼接三套 SNA 基准。68SNA 和 93SNA 的衔接年份（1975, 2001）有重叠期可做比率链接。

#### 固定资产投资 / 资本形成
- **来源 1**: 県民経済計算中的「県内総固定資本形成」(Prefectural GFCF)
  - 时间跨度: 1975-present (93SNA 基准起)
  - 含住宅、非住宅、公共投资分项
  - 质量评级: **B+**
- **来源 2**: 国土交通省「建設総合統計」都道府県別
  - 时间跨度: 1960-present
  - 含建設投資額（住宅・非住宅・土木）× 47 県
  - URL: https://www.mlit.go.jp/sogoseisaku/jouhouka/sosei_jouhouka_tk_000007.html
  - 质量评级: **B+**
- **来源 3**: e-Stat「建築着工統計」都道府県別
  - 時間: 1951-present (年度)
  - 含着工建築物の床面積・工事費予定額 by 県
  - URL: https://www.e-stat.go.jp/ > 建築着工統計調査
  - 質量: **A** (長時序、月次あり)
- **免费**: 是
- **备注**: 県民経済計算的 GFCF 是最佳选择，但仅从 1975 年起。1955-1974 需用建設総合統計补充。

#### 房价 / 资产价值
- **来源 1**: 国土交通省「地価公示」(Official Land Prices)
  - 時間: 1970-present (年度)
  - 47 県の用途別（住宅、商業、工業）平均地価
  - URL: https://www.land.mlit.go.jp/webland/
  - 免費: 是
  - 質量: **A**
- **来源 2**: 国土交通省「都道府県地価調査」
  - 時間: 1975-present
  - 各県独自調査、7月1日基準
  - 免費: 是
- **来源 3**: 日本不動産研究所「市街地価格指数」(JREI Urban Land Price Index)
  - 時間: 1936-present (6大都市), 1955-present (全国)
  - URL: https://www.reinet.or.jp/ (部分公開、完整需付費)
  - 質量: **A** (最長時序)
- **来源 4**: 不動産経済研究所 — マンション市場動向（新築分譲マンション平均価格 by 地域）
  - 主に首都圏・近畿圏、1970s-present
- **备注**: 地価公示 + 建物価格で V(t) の代理変数を構築可能。

#### 人口
- **来源**: 総務省「国勢調査」(Population Census, 5年ごと) + 「人口推計」(年度推計)
- **時間**: 1920-present (Census), 年度推計 1950-present
- **URL**: https://www.e-stat.go.jp/ > 国勢調査
- **免費**: 是
- **質量**: **A**

#### 建成区面積
- **来源 1**: 国土交通省「都市計画区域、市街化区域」面積
  - 時間: 1968-present
  - 都市計画区域内 DID (人口集中地区) 面積 by 県
  - URL: https://www.mlit.go.jp/toshi/city_plan/
  - 質量: **B**
- **来源 2**: 総務省「国勢調査」DID (Densely Inhabited District) 面積
  - 時間: 1960-present (5年ごと)
  - URL: e-Stat
  - 質量: **B+** (5年間隔需插値)
- **来源 3**: MODIS / Landsat 衛星遥感 — Global Urban Footprint, GHSL
  - 時間: 1975-present (GHSL), 2000-present (MODIS)
  - 質量: **B** (空間分解能に制約)

#### Urban Q 構築可能性: **可行**
- V(t): 地価公示（1970-）× 建物面積（建築着工統計累計）で構築
- I(t) / K(t): 県民経済計算 GFCF（1975-）または建設総合統計（1960-）
- 可比時間窗口: **1975-2021** (47年、47県 = 最大 2,209 obs)
- 拡張窗口: **1960-2021** (62年、但 1960-1974 のV側は地価指数×面積で近似)

---

### 1.2 韩国 (South Korea) — 17 広域市/道

**空间单元**: 8 道 + 6 広域市 + 1 特別市(首爾) + 1 特別自治市(世宗) + 1 特別自治道(濟州) = 17 単位
**城市化轨迹**: 1960 年 ~28% -> 2025 年 ~81%

#### 城市 GDP / 经济产出
- **来源**: 韓国銀行 (BOK)「地域別 GRDP」(Regional GDP)
- **URL**: https://ecos.bok.or.kr/ > 국민계정 > 지역별경제활동별GRDP
- **時間**: 1985-present (16 市道), 2010-present (世宗市分離後 17 単位)
- **免費**: 是
- **質量**: **A**

#### 固定資産投資 / GFCF
- **来源 1**: BOK 地域所得統計 — 地域別 총固定자본형성
  - 時間: 2010-present (17 市道)
  - 質量: **B** (短時序)
- **来源 2**: KOSIS「건설업조사」(Construction Survey) 시도별
  - 時間: 1990-present
  - 含建設工事完成額 by 시도
  - URL: https://kosis.kr/
  - 質量: **B**
- **来源 3**: KOSIS「건축물현황」(Building Statistics) 시도별 착공/허가
  - 時間: 1990-present
  - 質量: **B**
- **免費**: 是

#### 房価 / 資産価値
- **来源 1**: 韓国不動産院 (KREB)「全国住宅価格動向調査」시도별
  - 時間: 2003-present (月次), 1986-present (首爾のみ KB国民銀行指数)
  - URL: https://www.reb.or.kr/
  - 質量: **B+**
- **来源 2**: KOSIS「주택가격동향」시도별 매매가격지수
  - 時間: 2012-present (改訂系列)
  - 質量: **B**
- **来源 3**: 国土交通部「공시지가」(Official Land Prices) 시도별
  - 時間: 1990-present
  - URL: https://www.realtyprice.kr/
  - 質量: **B+**
- **免費**: 是

#### 人口
- **来源**: KOSIS「주민등록인구」시도별
- **時間**: 1966-present (Census), 1992-present (住民登録月次)
- **免費**: 是
- **質量**: **A**

#### 建成区面積
- **来源 1**: KOSIS「도시계획현황」시도별 都市地域面積
  - 時間: 2000-present
  - 質量: **B**
- **来源 2**: 衛星遙感 (GHSL, Landsat)
  - 質量: **B**

#### Urban Q 構築可能性: **可行**
- V(t): 住宅価格指数(2003-) × 住宅存量(KOSIS) + 地價(1990-)
- K(t): 地域別 GFCF(2010-) 或建設工事額(1990-)
- 可比窗口: **2003-2023** (20年、17市道 = 340 obs)
- 拡張: 用建設額回溯至 1990，但 V 側在 2003 前不够稳健

---

### 1.3 英国 (United Kingdom) — LAD / NUTS-3

**空间单元**: 382 Local Authority Districts (LADs) 或 179 NUTS-3 regions
**城市化轨迹**: 1950 年 ~79% -> 2025 年 ~84% (已高度城市化)

#### 城市 GDP / 经济产出
- **来源**: ONS「Regional GVA (Balanced)」
- **URL**: https://www.ons.gov.uk/economy/grossvalueaddedgva
- **時間**: 1998-present (NUTS-3 / LAD)
- **免費**: 是
- **質量**: **A**
- **備注**: 1998 年前有 NUTS-1/NUTS-2 級 GVA (1971-), 但 NUTS-3 仅 1998 起

#### 固定資産投資
- **来源**: ONS 不提供 LAD 級 GFCF
- **替代 1**: ONS「Construction Output」by region (NUTS-1, 9 regions)
  - 時間: 2010-present (一致系列)
  - 質量: **C** (空間粒度不足)
- **替代 2**: BEIS (現 DESNZ)「Sub-national energy statistics」— 建築能耗作為存量代理
  - 質量: **C**
- **替代 3**: Planning applications data (建築許可) — LAD 級
  - 時間: 2006-present
  - URL: https://www.gov.uk/government/statistical-data-sets/
  - 質量: **C** (許可數≠投資額)
- **免費**: 是
- **質量**: **C** (LAD 級 GFCF 基本不可得)

#### 房価 / 資産価値
- **来源 1**: ONS / HM Land Registry「House Price Statistics for Small Areas」
  - 時間: 1995-present (LAD 級中位数房価)
  - URL: https://www.ons.gov.uk/peoplepopulationandcommunity/housing/
  - 質量: **A**
- **来源 2**: Land Registry「Price Paid Data」(逐筆交易)
  - 時間: 1995-present
  - URL: https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads
  - 質量: **A** (微觀數據、可聚合到任何空間單元)
- **来源 3**: VOA (Valuation Office Agency)「Council Tax Valuations」
  - 含物業估值分布
  - 質量: **B**
- **免費**: 是

#### 人口
- **来源**: ONS「Mid-year Population Estimates」LAD 級
- **時間**: 1981-present (LAD), 1971-present (county)
- **免費**: 是
- **質量**: **A**

#### 建成区面積
- **来源 1**: ONS/DLUHC「Land Use Statistics」
  - 時間: 2005, 2018, 2022 (不規則)
  - 質量: **C**
- **来源 2**: Ordnance Survey 基礎地図 + GHSL 遙感
  - 質量: **B**

#### Urban Q 構築可能性: **部分可行**
- V(t): House Price Data (1995-) × housing stock estimates — LAD 級可行
- K(t): **主要瓶頸** — LAD 級 GFCF 不可得。只能用 NUTS-1 級建設產出做粗略配分
- 推薦方案: 放弃 LAD 級 K(t)，改用 **NUTS-1 (9 regions)** 或 **NUTS-2 (40 regions)** 分析
- 可比窗口: **1998-2023** (NUTS-3 GVA + LAD house prices)
- 替代方案: 全國級 Urban Q 使用 ONS National Balance Sheet (1995-) — 非常稳健

---

### 1.4 德国 (Germany) — 401 Kreise

**空间单元**: 401 Kreise (含 Kreisfreie Stadte), 或 NUTS-3 (401 units)
**城市化轨迹**: 1960 年 ~72% (西德) -> 2025 年 ~77%

#### 城市 GDP / 经济产出
- **来源**: Statistische Amter des Bundes und der Lander「VGR der Lander」
  - Kreise-level BIP (GDP): Bruttoinlandsprodukt zu Marktpreisen
  - URL: https://www.statistikportal.de/de/vgrdl
  - 時間: 2000-present (Kreise), 1991-present (Bundeslander / NUTS-1)
  - 免費: 是
  - 質量: **A**

#### 固定資産投資
- **来源**: VGR der Lander 不提供 Kreise 級 GFCF
- **替代**: Bundeslander (16 州) 級 Bruttoanlageinvestitionen
  - 時間: 1991-present
  - 質量: **C** (空間粒度不足)
- **備注**: Kreise 級投資數據基本不可得。德國統計系統在市/县級不單獨統計 GFCF

#### 房価 / 資産価値
- **来源 1**: bulwiengesa AG — Immobilienindex (覆蓋 127 城市)
  - 時間: 1975-present
  - 付費: 是 (學術授權可協商)
  - 質量: **A** (但付費)
- **来源 2**: Deutsche Bundesbank — Wohnimmobilienpreisindex
  - 時間: 2004-present (127 城市)
  - URL: https://www.bundesbank.de/en/statistics/sets-of-indicators/
  - 免費: 是
  - 質量: **B+**
- **来源 3**: Destatis「Hauskaufwerte」(House purchase values, Kreise 級)
  - 時間: 2015-present (新系列)
  - 免費: 是
  - 質量: **B** (時序太短)
- **来源 4**: vdpResearch「vdp-Immobilienpreisindex」(基於抵押貸款數據)
  - 時間: 2003-present (全國); Kreise 級 2010-present
  - URL: https://www.vdpresearch.de/
  - 免費: 部分
  - 質量: **B**

#### 人口
- **来源**: Destatis / Statistische Landesamter — Bevolkerung Kreise 級
- **時間**: 1990-present (統一後), 西德 Kreise 1970-
- **免費**: 是, via GENESIS-Online
- **質量**: **A**

#### 建成区面積
- **来源**: Destatis「Flachenerhebung」(Land use survey) Kreise 級
  - 時間: 1992-present
  - 含 Siedlungs- und Verkehrsflache (Settlement and transport area)
  - URL: GENESIS-Online (33111-0003)
  - 免費: 是
  - 質量: **B** (2016 年有方法論斷裂)

#### Urban Q 構築可能性: **部分可行**
- V(t): Kreise 級房価 (2004-) × housing stock (Zensus 2011/2022 基準) — 可行但短
- K(t): **主要瓶頸** — Kreise 級 GFCF 不可得
- 推薦方案: 改用 **Bundeslander (16 州)** 分析 (1991-present, GFCF 可得)
- 替代: 全國級使用 Destatis VGR Anlagevermogen (1991-, 西德 1950-)

---

### 1.5 巴西 (Brazil) — 5,570 Municipios

**空间单元**: 5,570 municipios, 或按 IBGE 定義的 mesorregiao (137) / microrregiao (558)
**城市化轨迹**: 1950 年 ~36% -> 2025 年 ~88%

#### 城市 GDP
- **来源**: IBGE「PIB dos Municipios」(Municipal GDP)
- **URL**: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088-produto-interno-bruto-dos-municipios.html
- **時間**: 2002-present (年度、全部 5,570 市)
- **早期**: 1999-2001 有舊方法論版本
- **免費**: 是
- **質量**: **B+** (municipio 定義變更需concordance table)

#### 固定資産投資
- **来源**: IBGE 不提供 municipio 級 GFCF
- **替代 1**: IBGE「Pesquisa Anual da Industria da Construcao」(Annual Construction Survey) — 全國/大區級
  - 質量: **D** (無 municipio 分解)
- **替代 2**: CAGED / RAIS 就業數據中的建設業就業 by municipio — 作為投資代理
  - 時間: 2003-present
  - 質量: **D** (弱代理)
- **免費**: 是
- **質量**: **D**

#### 房価
- **来源 1**: FipeZap Index (主要城市房価指数)
  - 覆蓋: ~50 個主要城市
  - 時間: 2008-present
  - URL: https://www.fipe.org.br/
  - 質量: **C** (覆蓋不全)
- **来源 2**: BIS Residential Property Prices (全國級)
  - 時間: 2001-present
  - 質量: **C** (僅全國)
- **免費**: 部分

#### 人口
- **来源**: IBGE「Censos Demograficos」+ 年度估計
- **時間**: 1940-present (Census, 10年), municipio 年度估計 2001-present
- **URL**: https://www.ibge.gov.br/
- **免費**: 是
- **質量**: **A**

#### 建成区面積
- **来源**: IBGE「Areas Urbanizadas do Brasil」
  - 時間: 2005, 2015, 2019 (不規則)
  - 質量: **C**
- **来源**: MapBiomas (遙感)
  - 時間: 1985-present (年度)
  - URL: https://mapbiomas.org/
  - 質量: **B** (覆蓋好但需GIS處理)

#### Urban Q 構築可能性: **困難**
- K(t) 完全缺失於 municipio 級別，是最大障礙
- 推薦: 全國級分析可行 (IBGE SNA + BIS 房価)
- 巴西最大價值: 5,570 個 municipio 的截面分析（GDP, 人口, 城市化程度）

---

### 1.6 印度 (India) — 640 Districts / 53 Urban Agglomerations

**空间单元**: 640 districts (Census 2011) 或 53 Million Plus Urban Agglomerations (UAs)
**城市化轨迹**: 1951 年 ~17% -> 2025 年 ~36% (仍處早期)

#### 城市 GDP
- **来源 1**: CSO / MoSPI「State Domestic Product」(SDP) — 36 州/聯邦直轄區
  - 時間: 1960-present (舊系列), 2011-present (新基準年)
  - URL: https://mospi.gov.in/
  - 質量: **B** (州級可得，district 級不可得)
- **来源 2**: District-level estimates — 極少数州有
  - Andhra Pradesh, Karnataka, Tamil Nadu 部分提供 district GDP
  - 質量: **D** (覆蓋極不完整)
- **学術来源**: Indicus Analytics / CMIE (Centre for Monitoring Indian Economy)
  - CMIE 提供 district-level 經濟指標 (付費)
  - URL: https://www.cmie.com/
  - 質量: **C** (付費、方法論不完全透明)

#### 固定資産投資
- **来源**: 不可得（district 級）
- **替代**: Annual Survey of Industries (ASI) — 工業投資 by state
  - 時間: 1959-present (state 級)
  - 質量: **D** (僅工業、非建設)

#### 房価
- **来源 1**: National Housing Bank「RESIDEX」(Residential Housing Price Index)
  - 覆蓋: ~50 城市
  - 時間: 2007-present
  - URL: https://residex.nhb.org.in/
  - 質量: **C** (覆蓋有限)
- **来源 2**: PropEquity / MagicBricks — 商業數據 (付費)
  - 質量: **D**

#### 人口
- **来源**: Census of India (10年一次: 1951, 1961, ..., 2011)
  - District / UA 級詳細數據
  - 時間: 1951-2011 (2021 Census 因 COVID 延遲至 2026?)
  - URL: https://censusindia.gov.in/
  - 質量: **A** (10年間隔)

#### 建成区面積
- **来源**: Census Town 分類 + 遙感 (GHSL)
  - 質量: **D**

#### Urban Q 構築可能性: **極困難**
- district 級 GDP 和投資均不可得
- 推薦: **州級 (36 units)** 分析可部分可行 (SDP + ASI), 但 V(t) 依然薄弱
- 印度主要價值: 城市化率仍低(~36%)，可作為"早期階段"的觀察點（全國級）

---

### 1.7 印度尼西亚 (Indonesia) — 514 Kabupaten/Kota

**空间单元**: 38 省, 514 kabupaten/kota (regencies/cities)
**城市化轨迹**: 1960 年 ~15% -> 2025 年 ~58%

#### 城市 GDP
- **来源**: BPS (Statistics Indonesia)「PDRB Kabupaten/Kota」(Regency/City GRDP)
- **URL**: https://www.bps.go.id/
- **時間**: 2010-present (2010 基準年), 部分省 2000-
- **免費**: 是 (但需逐省下載)
- **質量**: **B**

#### 固定資産投資
- **来源**: BPS 不提供 kabupaten 級 GFCF
- **替代**: BPS「Survei Konstruksi」(Construction Survey) — 全國/省級
  - 質量: **D**

#### 房価
- **来源**: Bank Indonesia「Residential Property Price Survey」
  - 覆蓋: 18 個主要城市
  - 時間: 2002-present
  - URL: https://www.bi.go.id/
  - 質量: **C** (覆蓋有限)

#### 人口
- **来源**: BPS Census + 年度估計
  - 時間: 1971-present (Census), kabupaten 級
  - 質量: **A**

#### Urban Q 構築可能性: **極困難**
- 與印度類似，kabupaten 級 GFCF 和房価均不可得
- 推薦: **省級 (38 units)** 或全國級分析
- 印尼主要價值: 城市化率 ~58%，正處於 Urban Q 理論預測的轉折區間

---

### 1.8 越南 (Vietnam) — 63 省級

**空间单元**: 63 省/直轄市
**城市化轨迹**: 1986 年 ~20% -> 2025 年 ~39%

#### 城市 GDP
- **来源**: GSO (General Statistics Office)「GRDP」省級
- **URL**: https://www.gso.gov.vn/
- **時間**: 2005-present (63 省), 部分 1995-
- **免費**: 是
- **質量**: **B+**

#### 固定資産投資
- **来源**: GSO「Social Investment Capital」省級
  - 時間: 2000-present
  - 含建設投資分項
  - URL: https://www.gso.gov.vn/ > Statistical Yearbook
  - 質量: **C** (口径変更多)
- **免費**: 是

#### 房価
- **来源**: 極度碎片化。僅河内、胡志明市有商業指數
  - 質量: **D**

#### 人口
- **来源**: GSO Census (1989, 1999, 2009, 2019) + 年度估計
  - 省級可得
  - 質量: **A**

#### Urban Q 構築可能性: **困難**
- GDP 和投資省級可得，但房価幾乎不可得
- 越南主要價值: 城市化率 ~39%，非常接近"起飛前"，可提供早期階段的觀察

---

### 1.9 墨西哥 (Mexico) — 74 Zonas Metropolitanas / 2,469 Municipios

**空间单元**: 2,469 municipios, 或 74 zonas metropolitanas (metropolitan zones, 更實用)
**城市化轨迹**: 1950 年 ~43% -> 2025 年 ~81%

#### 城市 GDP
- **来源**: INEGI「PIB por Entidad Federativa」(State GDP, 32 states)
  - 時間: 1993-present
  - URL: https://www.inegi.org.mx/
  - 質量: **B+** (州級)
- **来源 2**: INEGI「Censos Economicos」— municipio 級經濟活動 (5年一次)
  - 時間: 1999, 2004, 2009, 2014, 2019
  - 質量: **B** (5年間隔)

#### 固定資産投資
- **来源**: 不可得（municipio 級）
- **替代**: INEGI Censos Economicos 中的「formacion bruta de capital fijo」by municipio (5年)
  - 質量: **D** (間隔太長)

#### 房価
- **来源 1**: SHF (Sociedad Hipotecaria Federal)「Indice SHF de Precios de la Vivienda」
  - 時間: 2005-present (全國), 部分 municipio
  - URL: https://www.gob.mx/shf
  - 質量: **C**
- **来源 2**: Conavi/Infonavit 住房價格數據
  - 質量: **C**

#### 人口
- **来源**: INEGI Census (1990, 2000, 2010, 2020) + 年度 Encuestas
  - municipio 級可得
  - 質量: **A**

#### Urban Q 構築可能性: **困難**
- 州級 (32) 可部分可行 (GDP + 建設數據), 但 V(t) 弱
- 墨西哥主要價值: 74 個都市區可做截面分析

---

### 1.10 土耳其 (Turkey) — 81 省 (Il)

**空间单元**: 81 il (provinces)
**城市化轨迹**: 1960 年 ~32% -> 2025 年 ~77%

#### 城市 GDP
- **来源**: TURKSTAT「Il bazinda gayri safi katma deger」(Provincial GVA)
- **URL**: https://data.tuik.gov.tr/
- **時間**: 2004-present (81 il)
- **免費**: 是
- **質量**: **B+**

#### 固定資産投資
- **来源**: TURKSTAT「Il bazinda sabit sermaye yatirimi」— 部分可得
  - 公共投資 by il: 2006-present
  - 私人投資: 不可得 (il 級)
  - 質量: **C**

#### 房価
- **来源 1**: CBRT (Central Bank)「Residential Property Price Index」il 級
  - 時間: 2010-present
  - URL: https://evds2.tcmb.gov.tr/
  - 免費: 是
  - 質量: **B**
- **来源 2**: TURKSTAT「Konut Satis Istatistikleri」(Housing Sales) il 級
  - 時間: 2013-present
  - 質量: **B**

#### 人口
- **来源**: TURKSTAT「Adrese Dayali Nufus Kayit Sistemi」(ADNKS)
  - 時間: 2007-present (年度、il 級)
  - Census: 1927-2000 (10年)
  - 質量: **A**

#### Urban Q 構築可能性: **部分可行**
- V(t): 房價指數(2010-) × 住宅存量 — 可行但時序短
- K(t): 公共投資可得，私人需估算
- 可比窗口: **2010-2023** (短、但 81 省提供足夠截面變異)
- 土耳其主要價值: 城市化從 32% 到 77% 的完整中等收入國家軌跡

---

### 1.11 泰国 (Thailand) — 77 府 (Changwat)

**空间单元**: 76 changwat + Bangkok = 77 units
**城市化轨迹**: 1960 年 ~13% -> 2025 年 ~53%

#### 城市 GDP
- **来源**: NESDC (National Economic and Social Development Council)「GPP」(Gross Provincial Product)
- **URL**: https://www.nesdc.go.th/
- **時間**: 1995-present (77 changwat)
- **免費**: 是
- **質量**: **B+**

#### 固定資産投資
- **来源**: 不可得（changwat 級）
- **替代**: NESDC 僅提供全國 GFCF
  - 質量: **D**

#### 房価
- **来源**: Bank of Thailand「Housing Price Index」— 僅 Bangkok 及周邊
  - 時間: 2008-present
  - 質量: **D** (僅首都)

#### 人口
- **来源**: NSO「Population Census」+ 住民登録
  - 時間: 1960-present (Census), changwat 年度估計
  - 質量: **A**

#### Urban Q 構築可能性: **極困難**
- changwat 級 GFCF 和房價均不可得

---

### 1.12 尼日利亚 (Nigeria) — 36+1 州

**空间单元**: 36 states + FCT (Abuja)
**城市化轨迹**: 1960 年 ~15% -> 2025 年 ~54%

#### 城市 GDP
- **来源**: NBS (National Bureau of Statistics)「State GDP」— 不規則發布
  - 時間: 2013-present (有斷裂)
  - 質量: **C**

#### 固定資産投資
- **来源**: 不可得
- **質量**: **D**

#### 房価
- **来源**: 極度碎片化。僅 Lagos 有零散商業數據
  - 質量: **D**

#### 人口
- **来源**: NPC Census (1991, 2006), NBS 估計
  - 質量: **C** (人口數據本身存爭議)

#### Urban Q 構築可能性: **不可行**

---

### 1.13 南非 (South Africa) — 257 Municipalities

**空间单元**: 257 municipalities (8 metros + 44 district municipalities + 205 local municipalities)
**城市化轨迹**: 1960 年 ~47% -> 2025 年 ~69%

#### 城市 GDP
- **来源**: Stats SA「GDP by Metropolitan Area」(8 metros only)
  - 時間: 2010-present
  - 質量: **C** (僅8個都市區)
- **来源 2**: IHS Markit「Regional eXplorer」— municipality 級 GDP (付費)
  - 時間: 1995-present
  - 質量: **B** (但付費)
- **来源 3**: Quantec — municipality 級數據 (付費)
  - 質量: **B** (但付費)

#### 固定資産投資
- **来源**: 不可得 (municipality 級)
- **替代**: Stats SA 全國 GFCF only
  - 質量: **D**

#### 房価
- **来源**: FNB House Price Index (全國/省級)
  - 時間: 2001-present
  - 質量: **C**
- **来源 2**: Lightstone Property — municipality 級 (付費)
  - 質量: **B** (但付費)

#### Urban Q 構築可能性: **困難**
- 免費數據不支持 municipality 級 Urban Q
- 付費數據 (IHS Markit + Lightstone) 可能支持 8 metros 的分析

---

### 1.14 俄罗斯 (Russia) — 85 联邦主体

**空间单元**: 85 federal subjects (含 Crimea/Sevastopol 後為 85)
**城市化轨迹**: 1959 年 ~52% -> 2025 年 ~75%

#### 城市 GDP
- **来源**: Rosstat「VRP」(Gross Regional Product) 联邦主体級
- **URL**: https://rosstat.gov.ru/ > National Accounts > Regional Accounts
- **時間**: 1998-present
- **免費**: 是
- **質量**: **B+**

#### 固定資産投資
- **来源**: Rosstat「投資 в основной капитал」(Fixed Capital Investment) 联邦主体級
  - 時間: 1998-present
  - URL: https://rosstat.gov.ru/
  - 免費: 是
  - 質量: **B** (含建設投資分項)

#### 房価
- **来源 1**: Rosstat「средние цены на рынке жилья」(Average housing prices) 联邦主体級
  - 時間: 2000-present
  - 含一次市場/二次市場分別
  - URL: https://rosstat.gov.ru/
  - 免費: 是
  - 質量: **B**
- **来源 2**: Rosreestr (Federal Registration Service) — 交易數據
  - 質量: **C** (獲取困難)

#### 人口
- **来源**: Rosstat Census (2002, 2010, 2021) + 年度估計
  - 联邦主体級: 1990-present
  - 質量: **A**

#### 建成区面積
- **来源**: Rosstat「Жилищный фонд」(Housing stock) 联邦主体級
  - 時間: 2000-present
  - 質量: **B**

#### Urban Q 構築可能性: **部分可行**
- V(t): 住宅価格(2000-) × 住宅存量面積(2000-) — 可行
- K(t): 固定資本投資(1998-) 中建設分項 — 可行
- 可比窗口: **2000-2023** (24年、85 联邦主体 = ~2,000 obs)
- **注意**: 地緣政治因素可能影響數據可得性和國際合作

---

## Part 2: 历史时间序列数据源

### 2.1 发达国家城市化初期数据 (覆盖城市化率 30-50% 时期)

| 国家 | 城市化率达到 30% 的年份 | 达到 50% 的年份 | GDP 数据最早年份 | 投資数据最早年份 | 可覆盖初期? |
|------|:---:|:---:|:---:|:---:|:---:|
| 美国 | ~1880 | ~1920 | 1929 (BEA) | 1929 (BEA) | 部分 (从50%) |
| 英国 | ~1800 | ~1850 | 1948 (ONS) | 1965 (ONS GFCF) | 否 (已超80%) |
| 日本 | ~1935 | ~1960 | 1955 (SNA) | 1955 (SNA GFCF) | **是 (从37%)** |
| 德国(西) | ~1880 | ~1900 | 1950 (Destatis) | 1950 (Destatis) | 否 (已超70%) |
| 韩国 | ~1965 | ~1977 | 1953 (BOK) | 1970 (BOK GFCF) | **是 (从28%)** |
| 巴西 | ~1950 | ~1965 | 2002 (municipio) | N/A | 否 (municipio級) |
| 中国 | ~1995 | ~2010 | 1978 (NBS) | 1987 (NBS) | **是 (从18%)** |
| 土耳其 | ~1960 | ~1985 | 2004 (il 級) | N/A | 否 (il級) |

**结论**: 能覆盖城市化从 30-40% 到 80-90% 完整轨迹的国家级数据:
1. **日本**: 1955-present, 城市化 37% -> 92% (**最优**)
2. **韩国**: 1970-present, 城市化 41% -> 81% (**次优**)
3. **中国**: 1978-present, 城市化 18% -> 67% (**核心案例, 正在进行中**)

### 2.2 Maddison Project Database

- **最新版本**: Maddison Project Database 2023 (MPD 2023)
- **URL**: https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023
- **覆盖**: 169 个国家/地区
- **时间跨度**:
  - 西欧主要国家: 1 AD - 2022 (英法德意荷等)
  - 日本: 730 AD - 2022
  - 中国: 1 AD - 2022
  - 美国: 1800 - 2022
  - 韩国: 1911 - 2022
  - 巴西: 1850 - 2022
  - 印度: 1 AD - 2022
  - 全覆盖(169国): 1950 - 2022
- **变量**: GDP per capita (2011 USD PPP), Population
- **限制**: 仅国家级、仅 GDP (无投资/房价)
- **对本项目的价值**: 可确定各国城市化加速期的经济背景，但无法直接用于计算 Urban Q

### 2.3 Mitchell Historical Statistics

- **全名**: Brian R. Mitchell, "International Historical Statistics" (4th ed, Palgrave)
- **覆盖**: 全球所有主要国家
- **时间跨度**: 约 1750-2010 (因国因指标而異)
- **相关变量**:
  - National accounts: GDP 组分 (含 GFCF) — 多数国家从 1950s 起
  - Construction: 建筑许可、住宅竣工 — 部分国家从 1920s 起
  - Prices: 消费者价格指数、批发价格指数 — 很早
  - Population: 城市人口 — 19世纪起
- **获取方式**: 通过大学图书馆电子版 (Palgrave Connect)
- **对本项目的价值**: **中等** — 可补充 1950-1970 年代部分国家的投资数据，但格式为 PDF/表格需手动提取

### 2.4 UN World Urbanization Prospects

- **最新版本**: WUP 2024 Revision
- **URL**: https://population.un.org/wup/
- **覆盖**: 全球所有国家 + 主要 urban agglomerations (>300,000 人口)
- **时间跨度**:
  - 国家级城市化率: **1950-2050** (含预测)
  - Urban agglomeration 人口: **1950-2035** (含预测)
  - 全球覆盖: 233 个国家/地区
  - Urban agglomerations: 1,860+ (人口>30万)
- **变量**: 总人口、城市人口、城市化率、各 agglomeration 人口
- **免费**: 是、完全公开
- **对本项目的价值**: **核心数据源** — 提供 1950-present 所有国家的城市化率，是构建 "城市化阶段" 维度的基础

### 2.5 Penn World Table (PWT)

- **最新版本**: PWT 10.01
- **URL**: https://www.rug.nl/ggdc/productivity/pwt/
- **覆盖**: 183 个国家
- **时间跨度**: **1950-2019** (PWT 10.01)
- **关键变量及覆盖**:

| 变量 | 含义 | 覆盖 |
|------|------|------|
| `rgdpna` | Real GDP (国民账户基准) | 1950-2019, ~180国 |
| `rkna` | Capital stock (国民账户PPP) | 1950-2019, ~150国 |
| `cn` | Capital stock (current PPPs) | 1950-2019 |
| `ck` | Capital stock (constant PPPs) | 1950-2019 |
| `csh_i` | Investment share of GDP | 1950-2019 |
| `delta` | Depreciation rate | 1950-2019 |
| `pop` | Population | 1950-2019 |

- **限制**: 资本存量是总量 (含机器设备、知识产权)，非仅建筑
- **对本项目的价值**: **高** — 提供 1950 年起全球可比的资本存量和投资率数据。虽是总量而非建筑专项，但可通过 OECD GFCF by asset type 比率进行调整

### 2.6 其他历史数据源

#### OECD Historical Statistics
- **覆盖**: OECD 成员国 (38 国)
- **相关系列**:
  - GFCF by asset type (dwellings, other buildings): 1970-present for most
  - National Balance Sheet (非金融资产): 1995-present for most
- **URL**: https://stats.oecd.org/ (将迁移至 OECD.Stat Explorer)
- **价值**: 1970-present 的建筑投资分项是最标准化的跨国可比数据

#### BIS Residential Property Prices
- **覆盖**: 60+ 国家/地区
- **时间跨度**: 因国而异，最早至 1970 (部分发达国家)
- **URL**: https://www.bis.org/statistics/pp.htm
- **变量**: Residential property price indices (名义/实际)
- **价值**: **高** — 提供跨国可比的房价指数，可作为 V(t) 的增长率参考

#### World Bank WDI
- **覆盖**: 217 国
- **关键变量**: GFCF/GDP ratio (`NE.GDI.FTOT.ZS`), 1960-present
- **价值**: 提供 1960 年起几乎所有国家的投资/GDP 比率

### 2.7 各国城市化初期数据可得性总结

能够从**城市化率 < 50%** 时期开始覆盖的国家级时间序列:

| 国家 | 达到50%的年份 | GDP数据起始 | 投资数据起始 | 可用数据起始时的城市化率 | 评价 |
|------|:---:|:---:|:---:|:---:|:---:|
| 中国 | ~2010 | 1978 | 1987 (FAI) | 18% (1978) | 完整覆盖全过程 |
| 韩国 | ~1977 | 1953 | 1970 (GFCF) | 41% (1970) | 基本覆盖 |
| 日本 | ~1960 | 1955 | 1955 (SNA) | 37% (1955) | 非常完整 |
| 巴西 | ~1965 | 1947 (全国) | 1947 (全国GFCF) | 36% (1950) | 全国级可行 |
| 印度 | 尚未达到 | 1951 (全国) | 1951 (全国) | 17% (1951) | 极早期阶段 |
| 印度尼西亚 | ~2015 | 1967 (全国) | 1967 | 15% (1960) | 全国级可行 |
| 土耳其 | ~1985 | 1968 (全国) | 1968 | 32% (1960) | 全国级可行 |
| 墨西哥 | ~1965 | 1950 (全国) | 1960 (全国) | 43% (1950) | 全国级可行 |
| 越南 | 尚未达到 | 1986 (全国) | 1986 | 20% (1986) | 极早期 |
| 泰国 | ~2020 | 1960 (全国) | 1960 | 13% (1960) | 非常完整 |

---

## Part 3: 可直接获取的"低垂果实"

### 优先级 1: 1-3 天内可完成下载和初步清洗

#### 3.1 日本都道府県 GDP + 地価 (最高优先级)

| 项目 | 详情 |
|------|------|
| **数据源** | e-Stat「県民経済計算」+ 国土交通省「地価公示」 |
| **URL** | https://www.e-stat.go.jp/ ; https://www.land.mlit.go.jp/webland/ |
| **下载方式** | CSV/Excel 直接下载 (e-Stat API 也可用) |
| **预计行数** | 47県 × 60年 = ~2,800 行 (GDP), 47県 × 55年 = ~2,600 行 (地価) |
| **变量清单** | 県名、年度、県内総生産(名義/実質)、産業別付加価値、人口、用途別地価(住宅/商業/工業) |
| **工作量** | 1-2 天 (含三套SNA基準拼接) |
| **价值** | 可直接构建 47 県 × ~50年 的面板 |

#### 3.2 BIS 房価指数 — 60+ 国家 (已部分获取)

| 项目 | 详情 |
|------|------|
| **数据源** | BIS Residential Property Prices |
| **URL** | https://www.bis.org/statistics/pp.htm |
| **下载方式** | CSV 一键下载 (单文件) |
| **预计行数** | ~60国 × ~50年 = ~3,000 行 |
| **变量清单** | country, date, nominal_index, real_index |
| **工作量** | 0.5 天 (已有 `bis_property_prices.csv`，需更新和扩展) |
| **价值** | 全球房价变动的长时序可比数据 |

#### 3.3 Penn World Table 资本存量 (已获取，需深度处理)

| 项目 | 详情 |
|------|------|
| **数据源** | PWT 10.01 |
| **URL** | https://www.rug.nl/ggdc/productivity/pwt/ |
| **下载方式** | Stata (.dta) / Excel 下载 |
| **预计行数** | ~183国 × 70年 = ~12,800 行 |
| **变量清单** | country, year, rgdpna, rkna, cn, ck, csh_i, delta, pop |
| **工作量** | 0.5 天 (已有 `penn_world_table.csv`，需合并建筑投资比率) |
| **价值** | 1950-2019 全球资本存量的基础 |

#### 3.4 OECD GFCF by Asset Type

| 项目 | 详情 |
|------|------|
| **数据源** | OECD.Stat > National Accounts > Capital Formation |
| **URL** | https://stats.oecd.org/ > SNA Table 8 |
| **下载方式** | CSV 下载 (OECD API: SDMX) |
| **预计行数** | ~38国 × ~50年 × 4资产类型 = ~7,600 行 |
| **变量清单** | country, year, asset_type (dwellings/other_buildings/machinery/IP), gfcf_current, gfcf_constant |
| **工作量** | 1 天 |
| **价值** | **关键** — 提供建筑投资占总投资的比率，用于从 PWT 总资本存量中提取建筑存量 |

#### 3.5 World Bank WDI 扩展变量 (已部分获取)

| 项目 | 详情 |
|------|------|
| **数据源** | World Bank WDI |
| **URL** | https://data.worldbank.org/ (API: https://api.worldbank.org/v2/) |
| **下载方式** | API (JSON/CSV) 或 Bulk download |
| **预计行数** | ~217国 × 60年 = ~13,000 行 |
| **新增变量** | `BX.GSR.GNFS.CD` (出口), `BN.CAB.XOKA.GD.ZS` (经常账户), `FP.CPI.TOTL` (CPI), `NY.GDP.PCAP.PP.KD` (GDP per capita PPP) |
| **工作量** | 0.5 天 (API 自動化) |

#### 3.6 UN World Urbanization Prospects

| 项目 | 详情 |
|------|------|
| **数据源** | UN WUP 2024 |
| **URL** | https://population.un.org/wup/ |
| **下载方式** | Excel/CSV 直接下载 |
| **预计行数** | ~233国 × 75年 = ~17,500 行 (国家级), ~1,860 agglom × 85年 = ~158,000 行 (城市级) |
| **变量清单** | country/agglomeration, year, population, urban_pct |
| **工作量** | 0.5 天 |
| **价值** | 1950-present 全球城市化率 + 1,860+ 城市 agglomeration 人口 |

#### 3.7 韩国 BOK / KOSIS 数据

| 项目 | 详情 |
|------|------|
| **数据源** | Bank of Korea ECOS + KOSIS |
| **URL** | https://ecos.bok.or.kr/ ; https://kosis.kr/ |
| **下载方式** | Web 下载 (ECOS API 可用、需申请 key) |
| **预计行数** | 17 市道 × 40年 = ~680 行 (GRDP), 17 × 30年 = ~510 (地価) |
| **变量清单** | 시도, year, GRDP, population, housing_price_index, land_price_index |
| **工作量** | 1-2 天 |

#### 3.8 Rosstat 俄罗斯联邦主体数据

| 项目 | 详情 |
|------|------|
| **数据源** | Rosstat — Regiony Rossii |
| **URL** | https://rosstat.gov.ru/folder/210/document/13204 |
| **下载方式** | Excel 下载 (俄语界面) |
| **预计行数** | 85 联邦主体 × 25年 = ~2,125 行 |
| **变量清单** | region, year, GRP, population, fixed_investment, housing_price, housing_stock_m2 |
| **工作量** | 2-3 天 (俄语界面、需翻译) |

### 优先级 2: 1-2 周内可完成

| 数据集 | 工作量 | 价值 |
|--------|--------|------|
| 德国 Bundeslander (16州) GDP + GFCF + 房价 | 3-5 天 | 中 |
| 土耳其 81 il GVA + 房价 | 2-3 天 | 中 |
| 英国 NUTS-3 GVA + LAD 房价 | 2-3 天 | 高 (V側) |
| Eurostat NUTS-3 GDP (欧盟全部) | 3-5 天 | 高 (大样本截面) |

### 优先级 3: 需 1 个月+

| 数据集 | 障碍 | 备注 |
|--------|------|------|
| 巴西 municipio 投资数据 | 基本不存在 | 可能需放弃 |
| 印度 district GDP | 仅少数邦有 | 范围有限 |
| 日本 68SNA-93SNA-08SNA 完整拼接 | 技术复杂 | 高回报但耗时 |
| 全球卫星遥感建成区 (GHSL) | 需 GIS 技术 | 可外包 |

### 总结: 3 天速赢方案

**Day 1**:
1. 下载 BIS 房价指数最新版 (0.5h)
2. 下载 OECD GFCF by asset type (2h)
3. 下载 UN WUP 2024 (1h)
4. 更新 WDI 扩展变量 (1h)

**Day 2**:
5. 下载日本 e-Stat 県民経済計算 + 地価公示 (4h)
6. 开始拼接日本三套 SNA (4h)

**Day 3**:
7. 下载韩国 ECOS GRDP + 地价 (3h)
8. 合并所有数据源、初步质量检查 (5h)

**预期产出**: 覆盖 ~60 国 × 50+ 年的国家级面板 + 日本 47 県 × 50 年 + 韩国 17 市道 × 30 年 的城市级面板

---

## Part 4: 日本深度评估

### 4.1 为什么日本是最有价值的第三个国家案例

日本在 Urban Q 研究中具有不可替代的地位:

1. **完整的城市化轨迹**: 1950 年 37% -> 1975 年 76% -> 2025 年 92%，覆盖从初期加速到饱和的全过程
2. **泡沫-崩盘自然实验**: 1985-1991 資産バブル + 1991-2005 失われた十年，提供了 Urban Q > 1 急剧上升再崩溃至 Q < 1 的清晰案例
3. **数据质量极高**: 日本統計制度是亚洲最完善的，数据可追溯至 1950s
4. **政策对照**: 日本的经验对中国当前状况具有直接参考价值
5. **已有研究对照**: Piketty & Zucman (2014), Knoll et al. (2017) 等均使用日本数据

### 4.2 都道府県級数据详细评估

#### 4.2.1 GDP (県内総生産)

| 数据系列 | 时间跨度 | 基准年 | 备注 |
|---------|---------|--------|------|
| 68SNA 県民所得統計 | 1955-1974 | 1965年基準 | 旧体系、定義異なる |
| 93SNA 県民経済計算 | 1975-2010 | 1995/2000年基準 | 中間体系 |
| 08SNA 県民経済計算 | 2001-2021 | 2015年基準 | 現行体系 |

**拼接方法**:
- 93SNA 与 08SNA 有重叠期 (2001-2010)，可用比率链接 (ratio splicing)
- 68SNA 与 93SNA 重叠期 (1975)，同样用比率链接
- 学术先例: Fukao et al. (2015) "Regional Inequality and Industrial Structure in Japan" 已完成类似拼接
- **预计拼接后覆盖**: 47 県 × 67 年 (1955-2021) = 3,149 观测

**数据质量**: 内閣府公式統計、经过多次修訂、方法论文档完整。**A 级**。

#### 4.2.2 固定資本形成 (GFCF)

| 数据源 | 时间跨度 | 空间 | 分项 |
|--------|---------|------|------|
| 県民経済計算 GFCF | 1975-2021 | 47県 | 住宅/非住宅/公共 |
| 建設総合統計 (建設投資額) | 1960-present | 47県 | 住宅/非住宅/土木 |
| 建築着工統計 (着工床面積・工事費) | 1951-present | 47県 | 居住/非居住、用途別 |

**最佳策略**:
- 主系列: 県民経済計算 GFCF (1975-2021) — SNA 口径、可与 GDP 直接比较
- 延伸: 建築着工統計の工事費予定額 (1951-1974) — 以建設総合統計做交叉验证
- 新建 vs 維持修繕: 建設総合統計 (1960-present) 明确区分

**数据质量**: **B+** (1975 前需用非 SNA 数据近似)

#### 4.2.3 地価・資産価値

| 数据源 | 时间跨度 | 空间 | 変数 |
|--------|---------|------|------|
| 地価公示 | 1970-present | 47県 × 用途別 | 住宅地/商業地/工業地 平均地価 (円/m2) |
| 都道府県地価調査 | 1975-present | 47県 | 同上 (7月基準) |
| 市街地価格指数 (JREI) | 1955-present | 6大都市/全国 | 住宅/商業/工業/全用途 指数 |
| 固定資産税評価額 | 1960-present | 市町村 → 県集計 | 土地+建物 課税標準額 |

**V(t) 構築方法**:

方法 A: 地価 × 宅地面積 + 建物価値
```
V_land(t, i) = 用途別地価(t, i) × 用途別宅地面積(t, i)
V_building(t, i) = 建築着工統計累計から PIM で推計
V(t, i) = V_land(t, i) + V_building(t, i)
```

方法 B: SNA 非金融資産残高 × 地価指数調整
```
V_sna(t) = 内閣府 SNA 全国非金融資産 (1994-)
V(t, i) = V_sna(t) × [地価(t,i) / 地価(t,全国)] × [建物面積(t,i) / 建物面積(t,全国)]
```

方法 C: 固定資産税評価額の補正
```
V(t, i) = 固定資産税課税標準額(t, i) × 補正係数(t)
```
補正係数 = 市場価格 / 固定資産税評価額 (全国平均で年次推計)

**推薦**: 方法 A を主分析、方法 B と C で感度分析。

**数据質量**: 地価公示 **A**、構築後の V(t) **B+** (推計を含むため)

#### 4.2.4 人口

- 国勢調査 (5年ごと): 1920-present
- 人口推計 (年度): 1950-present
- 住民基本台帳: 1968-present
- **47 県 × 75 年 = 完全にカバー**
- 質量: **A**

#### 4.2.5 建成区面積

- DID (人口集中地区) 面積: 1960-present (5年ごと、国勢調査)
- 都市計画区域内市街化区域: 1968-present
- **中間年の線形插値が必要**
- 質量: **B+**

### 4.3 都道府県級 Urban Q 構築: 具体方案

#### 核心面板仕様

| 項目 | 仕様 |
|------|------|
| 空間単位 | 47 都道府県 |
| 時間範囲 | 1975-2021 (主分析) / 1960-2021 (拡張) |
| 観測数 | 2,209 (主) / 2,914 (拡張) |
| V(t,i) | 地価公示 × 宅地面積 + PIM建物価値 |
| K(t,i) | 県民経済計算 GFCF (1975-) / 建設総合統計 (1960-) |
| Q(t,i) | V(t,i) / Cumulative K(t,i) with depreciation |
| 控制変数 | 人口、県内GDP、産業構造、DID面積 |

#### 可能な分析

1. **泡沫前後の Q 動態**: 47 県の Q(t) が 1985-91 にどう発散し、その後収束したか
2. **大都市 vs 地方の乖離**: 東京圏・大阪圏 vs 地方県の Q 軌跡の違い
3. **人口減少の影響**: 2000 年代以降、人口減少県で Q はどう動いたか
4. **中国との比較**: 日本の Q=1 交差時点 vs 中国の 2012.6 年

### 4.4 与中国/美国数据的可比性

| 比較項目 | 日本 | 中国 | 美国 |
|---------|------|------|------|
| V(t) 口径 | 地価×面積+建物PIM | 社科院NBS/住宅面積×均価 | BEA Fixed Assets (current-cost net stock) |
| K(t) 口径 | SNA GFCF 累計 | FAI 累計 | BEA GFCF 累計 |
| 空間単位 | 47 県 | 290+ 地級市 | 380+ MSAs |
| 時間範囲 | 1960-2021 | 1987-2024 | 1929-2024 |
| 城市化範囲 | 37%-92% | 18%-67% | 64%-83% |
| 数据質量 | A | B+ | A |

**可比性分析**:
- **共通の Q 構築法**: 三国均可使用 "不動産総市值 / 累計建設投資" 作為 Q 的操作化定義
- **V(t) 的口径差異**: 美国 BEA 提供 current-cost net stock (近似市場価値); 日本需構築; 中国需推計 — 三者方法不同但概念一致
- **K(t) 的可比性**: 三国均有 SNA 框架下的 GFCF 建築投資系列，可比性較高
- **核心挑戰**: 土地所有制差異（中国土地国有 vs 日美私有），影響 V(t) 中土地価値的計入方式
- **建議**: 同時報告含/不含土地価値的 Q 值，做感度分析

### 4.5 日本数据获取优先操作清单

| 步骤 | 数据 | 来源 | 工作量 |
|------|------|------|--------|
| 1 | 47県 地価公示 (1970-2024) | land.mlit.go.jp | 0.5天 |
| 2 | 47県 県民経済計算 GDP+GFCF (08SNA, 2001-2021) | e-Stat | 0.5天 |
| 3 | 47県 県民経済計算 GDP+GFCF (93SNA, 1975-2010) | e-Stat | 0.5天 |
| 4 | 47県 建築着工統計 (1965-2024) | e-Stat | 0.5天 |
| 5 | 47県 人口 (1950-2024) | e-Stat 国勢調査+推計 | 0.5天 |
| 6 | 47県 DID面積 (1960-2020) | e-Stat | 0.5天 |
| 7 | SNA基準年拼接 (68SNA/93SNA/08SNA) | 手動計算 | 1天 |
| 8 | V(t) 構築 (地価×面積+建物PIM) | スクリプト作成 | 1天 |
| 9 | 品質檢査・文書化 | — | 1天 |
| **合計** | | | **~6天** |

---

## Part 5: 構建"全球城市面板"的可行性

### 5.1 最可行的国家组合

基于 Part 1 的评估，推荐以下三层结构:

#### Tier 1: 城市级面板 (Urban Q 可直接计算)
| 国家 | 单元 | 数量 | 时间 | 城市化覆盖 | 工作量 |
|------|------|------|------|-----------|--------|
| 中国 | 地级市 | 290+ | 1998-2024 | 33%-67% | 已完成 |
| 美国 | MSAs | 380+ | 1969-2024 | 74%-83% | 已大部分完成 |
| 日本 | 都道府県 | 47 | 1975-2021 | 76%-92% | ~6天 |
| 韩国 | 市道 | 17 | 2003-2023 | 82%-82% | ~3天 |
| **小计** | | **734+** | | 33%-92% | ~9天 |

#### Tier 2: 准城市级面板 (V 或 K 需代理变量)
| 国家 | 单元 | 数量 | 时间 | 工作量 |
|------|------|------|------|--------|
| 英国 | NUTS-1/2 | 12/40 | 1998-2023 | ~3天 |
| 德国 | Bundeslander | 16 | 1991-2023 | ~3天 |
| 俄罗斯 | 联邦主体 | 85 | 2000-2023 | ~5天 |
| 土耳其 | Il | 81 | 2010-2023 | ~3天 |
| **小计** | | **194-222** | | ~14天 |

#### Tier 3: 全国级面板 (长时序、广覆盖)
| 国家集合 | 数量 | 时间 | 变量 | 工作量 |
|----------|------|------|------|--------|
| OECD 国家 | 38 | 1970-2023 | GDP, GFCF by asset, 房价 | ~5天 |
| 全球 (PWT+WDI+BIS) | 100-150 | 1950-2019 | GDP, K, 投资率, 城市化率 | ~5天 |
| **小计** | **150** | | | ~10天 |

### 5.2 最可行的"10+ 国家、50+ 年、1000+ 城市"方案

**目标**: 10+ 国家、50+ 年时间跨度、1000+ 城市级观测单元

**推荐组合**:

| 层级 | 国家 | 单元数 | 最长时间 | 贡献 |
|------|------|--------|---------|------|
| 核心三国 | 中国 | 290 | 1998-2024 (27年) | 快速城市化+过热 |
| | 美国 | 380 | 1969-2024 (56年) | 成熟经济体 |
| | 日本 | 47 | 1975-2021 (47年) | 泡沫-崩盘 |
| 补充 | 韩国 | 17 | 2003-2023 (21年) | 快速追赶 |
| | 俄罗斯 | 85 | 2000-2023 (24年) | 转型经济体 |
| | 土耳其 | 81 | 2010-2023 (14年) | 中等收入 |
| | 英国 | 40 (NUTS-2) | 1998-2023 (26年) | 去工业化 |
| | 德国 | 16 | 1991-2023 (33年) | 统一后转型 |
| 全国级 | OECD 38国 | 38 | 1970-2023 (54年) | 广覆盖 |
| | 非OECD 60+ | 60 | 1960-2023 (64年) | 发展中国家 |
| **合计** | **10+ 国家** | **~1,054 城市级 + ~100 国家级** | | |

**时间跨度**: 如果含全国级数据，可覆盖 1950-2024 (75 年); 城市级核心面板覆盖 1975-2024 (50 年)

### 5.3 预计总工作量

| 阶段 | 内容 | 工作量 |
|------|------|--------|
| Phase A | 全国级数据整合 (PWT+WDI+BIS+OECD+UN) | 1-2 周 |
| Phase B | 日本都道府県面板构建 | 1 周 |
| Phase C | 韩国市道面板构建 | 0.5 周 |
| Phase D | 英德俄土区域面板 | 2-3 周 |
| Phase E | 数据质量审计、文档化 | 1 周 |
| Phase F | 合并、标准化、最终面板 | 1 周 |
| **总计** | | **6-8 周 (1名全职RA)** |

如果 PI 投入 2 名 RA 并行，可压缩至 **3-4 周**。

### 5.4 这个数据集本身是否具有独立发表价值?

**答案: 是的，具有高度独立发表价值。**

#### 5.4.1 数据论文 (Data Descriptor) 目标期刊

| 期刊 | IF | 类型 | 可行性 |
|------|:---:|------|:---:|
| **Scientific Data** (Nature) | ~6 | Data Descriptor | **高** |
| **Data in Brief** (Elsevier) | ~1.5 | Data Article | 高 |
| **Earth System Science Data** | ~11 | 地球系统数据 | 中 (需空间组分) |
| **Journal of Open Humanities Data** | — | 开放数据 | 中 |

#### 5.4.2 发表价值论证

**独特性**: 目前不存在一个覆盖多国城市级、长时序、同时包含 GDP/投资/资产价值/人口/建成区的统一面板数据集。最接近的是:
- OECD Regional Statistics: 仅 OECD 国家、变量有限
- Global Human Settlement Layer (GHSL): 仅物理空间、无经济变量
- World Bank WDI: 仅国家级

**差异化**: 本数据集的核心创新是将 **经济变量 (V, K, Q)** 与 **空间变量 (建成区、人口密度)** 在城市级别进行匹配，这在现有公开数据集中尚无先例。

**引用潜力**: 城市经济学、房地产金融、发展经济学、空间经济学等领域的研究者都可能使用此数据集。保守估计年引用 20-50 次。

#### 5.4.3 建议的数据论文标题

> "A Global Urban Panel Dataset: Economic Output, Capital Investment, and Asset Values across 1,000+ Cities in 10 Countries, 1960-2024"

#### 5.4.4 数据仓库与 DOI

- 首选: **Zenodo** (CERN, 免费、支持大文件、自动 DOI)
- 备选: **Figshare** (Nature 旗下)
- 版本控制: 初始版本 v1.0, 后续可更新
- 许可: CC BY 4.0

### 5.5 建议的实施路线图

```
Week 1-2: Phase A (全国级) + Phase B (日本)
Week 3:   Phase C (韩国) + Phase D 启动 (英德)
Week 4:   Phase D 继续 (俄土)
Week 5:   Phase E (审计) + Phase F (合并)
Week 6:   Data Descriptor 论文撰写
```

**里程碑**:
- M1 (Week 2): 日本 47 県面板完成、全国级面板完成 -> **可立即用于 Nature 主论文**
- M2 (Week 4): 全部城市级面板完成 -> 分析就绪
- M3 (Week 6): Data Descriptor 论文初稿 -> 可平行投稿 Scientific Data

---

## 附录 A: 数据源 URL 汇总

| 国家 | 数据源 | URL |
|------|--------|-----|
| 全球 | Penn World Table 10.01 | https://www.rug.nl/ggdc/productivity/pwt/ |
| 全球 | World Bank WDI | https://data.worldbank.org/ |
| 全球 | UN World Urbanization Prospects | https://population.un.org/wup/ |
| 全球 | BIS Property Prices | https://www.bis.org/statistics/pp.htm |
| 全球 | Maddison Project Database | https://www.rug.nl/ggdc/historicaldevelopment/maddison/ |
| OECD | OECD.Stat (SNA Tables) | https://stats.oecd.org/ |
| 日本 | e-Stat (総務省統計局) | https://www.e-stat.go.jp/ |
| 日本 | 内閣府 SNA | https://www.esri.cao.go.jp/jp/sna/ |
| 日本 | 国土交通省 地価公示 | https://www.land.mlit.go.jp/webland/ |
| 日本 | 国土交通省 建設総合統計 | https://www.mlit.go.jp/sogoseisaku/jouhouka/ |
| 韩国 | BOK ECOS | https://ecos.bok.or.kr/ |
| 韩国 | KOSIS | https://kosis.kr/ |
| 韩国 | 韓国不動産院 | https://www.reb.or.kr/ |
| 英国 | ONS | https://www.ons.gov.uk/ |
| 英国 | HM Land Registry | https://www.gov.uk/government/organisations/land-registry |
| 德国 | Destatis GENESIS-Online | https://www-genesis.destatis.de/ |
| 德国 | VGR der Lander | https://www.statistikportal.de/de/vgrdl |
| 巴西 | IBGE | https://www.ibge.gov.br/ |
| 印度 | MoSPI | https://mospi.gov.in/ |
| 印度 | CMIE (付费) | https://www.cmie.com/ |
| 印度尼西亚 | BPS | https://www.bps.go.id/ |
| 越南 | GSO | https://www.gso.gov.vn/ |
| 墨西哥 | INEGI | https://www.inegi.org.mx/ |
| 土耳其 | TURKSTAT | https://data.tuik.gov.tr/ |
| 泰国 | NESDC | https://www.nesdc.go.th/ |
| 南非 | Stats SA | https://www.statssa.gov.za/ |
| 俄罗斯 | Rosstat | https://rosstat.gov.ru/ |

## 附录 B: 项目现有数据资产清单

以下数据已存在于 `02-data/raw/` 目录中:

| 文件 | 覆盖 | 状态 |
|------|------|------|
| `world_bank_all_countries.csv` | ~217国, 1960-2024 | 已获取, 需扩展变量 |
| `penn_world_table.csv` | ~183国, 1950-2019 | 已获取, 含 K stock |
| `bis_property_prices.csv` | ~60国 房价指数 | 已获取, 需更新 |
| `oecd_gfcf_by_asset.csv` | OECD 国家 GFCF 分资产类型 | 已获取 |
| `japan_urban_q_data.csv` | 日本全国级 1960-2024 | 已获取, 含插值 |
| `japan_prefecture_data.csv` | 47県 截面数据 | 已获取, 需扩展为面板 |
| `us_msa_data.csv` | 380+ MSAs 截面数据 | 已获取, 需扩展为面板 |
| `brazil_municipio_data.csv` | 5,570 municipios (2023) | 已获取, 仅截面 |
| `eu_nuts3_data.csv` | 欧盟 NUTS-3 GDP | 已获取, 仅截面 |
| `china_national_real_data_v2.csv` | 中国全国级 | 已获取 |
| `china_provincial_real_data.csv` | 中国省级 | 已获取 |

**最大缺口**: 日本县级面板 (时间序列)、韩国市道面板、英德区域面板、俄罗斯联邦主体面板

## 附录 C: Urban Q 構築に必要な最小変数セット

构建城市级 Urban Q 需要以下最小变量集:

```
V(t, i) = 不動産資産総市場価値
         = f(房價指数, 住宅存量面積, 地價)

K(t, i) = 累計建設投資 (含折旧调整)
         = Σ GFCF_construction(τ, i) × (1 - δ)^(t-τ)  for τ = t0 to t

Q(t, i) = V(t, i) / K(t, i)
```

对每个国家，需确认:
1. V 的分子: 房价/地价 × 存量面积，或 SNA 非金融资产残高
2. K 的分母: GFCF 中建筑/建設分項 (非総 GFCF)
3. 折旧率 δ: 可从 PWT 或各国 SNA 获取 (通常建筑 2-3%/年)

---

*报告结束。下一步行动请参照 Part 3 的 "3天速赢方案" 和 Part 4 的日本操作清单。*
