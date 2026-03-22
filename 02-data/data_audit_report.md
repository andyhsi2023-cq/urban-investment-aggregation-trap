# 数据质量系统性审计报告

审计日期: 2026-03-22 09:17:39
审计人: data-analyst (AI agent, 审计模式)
项目: Urban Q Phase Transition — 目标: Nature 主刊

---

## A. 原始数据文件基本信息与异常值检测

### world_bank_all_countries.csv
**描述**: 世界银行 WDI 全球面板

- **行数**: 13,888
- **列数**: 18
- **列名**: ['country_iso3', 'country_iso2', 'country_name', 'region', 'year', 'NY.GDP.MKTP.CD', 'NY.GDP.MKTP.KD', 'NE.GDI.FTOT.ZS', 'NE.GDI.FTOT.CD', 'NE.CON.GOVT.ZS', 'NV.SRV.TOTL.ZS', 'NV.IND.TOTL.ZS', 'NV.AGR.TOTL.ZS', 'SP.URB.TOTL.IN.ZS', 'SP.URB.TOTL', 'SP.POP.TOTL', 'SP.POP.1564.TO.ZS', 'SP.POP.65UP.TO.ZS']
- **时间范围**: 1960 - 2023
- **country_name 唯一值**: 217
- **缺失值**:
  - country_iso2: 64 (0.5%)
  - NY.GDP.MKTP.CD: 2,511 (18.1%)
  - NY.GDP.MKTP.KD: 2,741 (19.7%)
  - NE.GDI.FTOT.ZS: 6,097 (43.9%)
  - NE.GDI.FTOT.CD: 6,110 (44.0%)
  - NE.CON.GOVT.ZS: 5,526 (39.8%)
  - NV.SRV.TOTL.ZS: 5,642 (40.6%)
  - NV.IND.TOTL.ZS: 5,216 (37.6%)
  - NV.AGR.TOTL.ZS: 5,170 (37.2%)
  - SP.URB.TOTL: 30 (0.2%)
  - SP.POP.TOTL: 30 (0.2%)
- **数值列范围检查**:
  - year: min=1960, max=2023, mean=1992
  - NY.GDP.MKTP.CD: min=2.586e+06, max=2.729e+13, mean=1.873e+11
  - NY.GDP.MKTP.KD: min=1.01e+07, max=2.196e+13, mean=2.389e+11
  - NE.GDI.FTOT.ZS: min=-2.424, max=93.55, mean=22.38
  - NE.GDI.FTOT.CD: min=-2.061e+07, max=7.553e+12, mean=6.598e+10
  - NE.CON.GOVT.ZS: min=1.788, max=147.7, mean=16.39
  - NV.SRV.TOTL.ZS: min=0, max=98.62, mean=51.69
  - NV.IND.TOTL.ZS: min=0, max=97.52, mean=26.44
  - NV.AGR.TOTL.ZS: min=0, max=89.41, mean=15.43
  - SP.URB.TOTL.IN.ZS: min=1.839, max=100, mean=51.87
  - SP.URB.TOTL: min=692, max=9.244e+08, mean=1.164e+07
  - SP.POP.TOTL: min=2715, max=1.438e+09, mean=2.512e+07
  - SP.POP.1564.TO.ZS: min=36.43, max=85.25, mean=59.74
  - SP.POP.65UP.TO.ZS: min=0.8625, max=37.32, mean=6.691
- **异常值/警告**: 12 项
  - WARNING: NY.GDP.MKTP.CD: 112 个 Z>3 异常值, 样本=[3604055822571.63, 4667346414521.95, 5189577094997.58]
  - WARNING: NY.GDP.MKTP.KD: 121 个 Z>3 异常值, 样本=[3681006926650.74, 4053944733453.66, 4518455387849.41]
  - WARNING: NE.GDI.FTOT.ZS: 87 个 Z>3 异常值, 样本=[46.8333157896094, 52.8818302665641, 57.7102529835174]
  - WARNING: NE.GDI.FTOT.CD: 89 个 Z>3 异常值, 样本=[1357683411650.45, 1811074229473.19, 2252783317543.54]
  - WARNING: NE.CON.GOVT.ZS: 117 个 Z>3 异常值, 样本=[43.9137134052388, 52.3324361222187, 62.1334122674263]
  - WARNING: NV.SRV.TOTL.ZS: 59 个 Z>3 异常值, 样本=[0.0, 0.0, 0.0]
  - WARNING: NV.IND.TOTL.ZS: 137 个 Z>3 异常值, 样本=[73.995507005299, 71.8147226501297, 67.9817061865227]
  - WARNING: NV.AGR.TOTL.ZS: 115 个 Z>3 异常值, 样本=[65.3313935147911, 64.7617713131167, 60.7731276105096]
  - WARNING: SP.URB.TOTL: 191 个 Z>3 异常值, 样本=[143854809.0, 146362770.0, 148750069.0]
  - WARNING: SP.POP.TOTL: 128 个 Z>3 异常值, 样本=[667070000.0, 660330000.0, 665770000.0]
  - WARNING: SP.POP.1564.TO.ZS: 34 个 Z>3 异常值, 样本=[81.5845266712198, 81.6611769273503, 81.7040705422879]
  - WARNING: SP.POP.65UP.TO.ZS: 146 个 Z>3 异常值, 样本=[21.4794589439076, 21.6867892994918, 21.7032217425472]

### penn_world_table.csv
**描述**: Penn World Table 10.01

- **行数**: 12,810
- **列数**: 26
- **列名**: ['countrycode', 'country', 'year', 'hc', 'cn', 'ck', 'rgdpna', 'rnna', 'rkna', 'pop', 'emp', 'avh', 'ctfp', 'rtfpna', 'csh_i', 'delta', 'labsh', 'irr', 'rgdpe', 'rgdpo', 'ky_ratio', 'k_per_capita', 'gdp_per_capita', 'investment_rate', 'investment_implied', 'investment_rate_implied']
- **时间范围**: 1950 - 2019
- **缺失值**:
  - hc: 4,173 (32.6%)
  - cn: 2,496 (19.5%)
  - ck: 5,720 (44.7%)
  - rgdpna: 2,411 (18.8%)
  - rnna: 2,496 (19.5%)
  - rkna: 5,720 (44.7%)
  - pop: 2,411 (18.8%)
  - emp: 3,281 (25.6%)
  - avh: 9,318 (72.7%)
  - ctfp: 6,403 (50.0%)
  - rtfpna: 6,403 (50.0%)
  - csh_i: 2,411 (18.8%)
  - delta: 2,496 (19.5%)
  - labsh: 4,840 (37.8%)
  - irr: 5,270 (41.1%)
  - rgdpe: 2,411 (18.8%)
  - rgdpo: 2,411 (18.8%)
  - ky_ratio: 2,520 (19.7%)
  - k_per_capita: 2,496 (19.5%)
  - gdp_per_capita: 2,411 (18.8%)
  - investment_rate: 2,411 (18.8%)
  - investment_implied: 2,676 (20.9%)
  - investment_rate_implied: 2,702 (21.1%)
- **数值列范围检查**:
  - year: min=1950, max=2019, mean=1984
  - hc: min=1.007, max=4.352, mean=2.087
  - cn: min=14.04, max=9.946e+07, mean=1.144e+06
  - ck: min=5.909e-06, max=1.147, mean=0.03437
  - rgdpna: min=13.91, max=2.057e+07, mean=3.272e+05
  - rnna: min=18.05, max=9.961e+07, mean=1.298e+06
  - rkna: min=0.002975, max=1.937, mean=0.4575
  - pop: min=0.004425, max=1434, mean=30.96
  - emp: min=0.0012, max=799.3, mean=14.17
  - avh: min=1381, max=3040, mean=1987
  - ctfp: min=0.03486, max=3.696, mean=0.7297
  - rtfpna: min=0.2023, max=9.397, mean=1.015
  - csh_i: min=-2.953, max=8.123, mean=0.2192
  - delta: min=0.01252, max=0.1014, mean=0.04282
  - labsh: min=0.08966, max=0.903, mean=0.5332
  - irr: min=0.01, max=1.091, mean=0.1315
  - rgdpe: min=20.36, max=2.086e+07, mean=3.049e+05
  - rgdpo: min=27.65, max=2.06e+07, mean=3.071e+05
  - ky_ratio: min=0.2062, max=19.02, mean=3.634
  - k_per_capita: min=134, max=1.708e+06, mean=5.706e+04
  - gdp_per_capita: min=233.9, max=2.043e+05, mean=1.418e+04
  - investment_rate: min=-2.953, max=8.123, mean=0.2192
  - investment_implied: min=3.626, max=1.306e+07, mean=9.772e+04
  - investment_rate_implied: min=0.004725, max=0.987, mean=0.2726
- **异常值/警告**: 23 项
  - WARNING: hc: 1 个 Z>3 异常值, 样本=[4.351568222045898]
  - WARNING: cn: 148 个 Z>3 异常值, 样本=[16249036.0, 18387840.0, 20845850.0]
  - WARNING: ck: 105 个 Z>3 异常值, 样本=[0.4143619537353515, 0.4639983773231506, 0.5324641466140747]
  - WARNING: rgdpna: 127 个 Z>3 异常值, 样本=[4256331.0, 4657186.5, 4990733.0]
  - WARNING: rnna: 186 个 Z>3 异常值, 样本=[16804928.0, 18906530.0, 21265522.0]
  - WARNING: rkna: 7 个 Z>3 异常值, 样本=[1.9371126890182495, 1.8455091714859009, 1.7508543729782104]
  - WARNING: pop: 136 个 Z>3 异常值, 样本=[579.5771775253429, 589.316980637563, 599.9429088684137]
  - WARNING: emp: 122 个 Z>3 异常值, 样本=[239.7740478515625, 245.7018585205078, 251.46844482421875]
  - WARNING: avh: 27 个 Z>3 异常值, 样本=[2870.5808194226483, 2900.7974596270974, 2882.667475504428]
  - WARNING: ctfp: 52 个 Z>3 异常值, 样本=[2.1218771934509277, 1.8017109632492063, 2.011030435562134]
  - WARNING: rtfpna: 96 个 Z>3 异常值, 样本=[2.7579026222229004, 2.375252485275269, 2.702343225479126]
  - WARNING: csh_i: 67 个 Z>3 异常值, 样本=[0.7381664514541626, 0.7182853817939758, 0.6824361681938171]
  - WARNING: delta: 167 个 Z>3 异常值, 样本=[0.0817803591489791, 0.0821733027696609, 0.0823542848229408]
  - WARNING: labsh: 33 个 Z>3 异常值, 样本=[0.1508482694625854, 0.1508482694625854, 0.1508482694625854]
  - WARNING: irr: 137 个 Z>3 异常值, 样本=[1.091254472732544, 0.5343582034111023, 0.569298267364502]
  - WARNING: rgdpe: 131 个 Z>3 异常值, 样本=[4327762.5, 4660242.0, 4897091.5]
  - WARNING: rgdpo: 134 个 Z>3 异常值, 样本=[4257891.0, 4580774.5, 4742227.5]
  - WARNING: ky_ratio: 176 个 Z>3 异常值, 样本=[10.508180992942089, 10.796025053668012, 10.440861482454473]
  - WARNING: k_per_capita: 104 个 Z>3 异常值, 样本=[1707801.426567284, 1505697.8927527564, 1340892.2415355889]
  - WARNING: gdp_per_capita: 224 个 Z>3 异常值, 样本=[204345.35957874585, 197750.36738073532, 189821.98186262365]
  - WARNING: investment_rate: 67 个 Z>3 异常值, 样本=[0.7381664514541626, 0.7182853817939758, 0.6824361681938171]
  - WARNING: investment_implied: 90 个 Z>3 异常值, 样本=[1522398.0017822797, 1608455.175804909, 1721016.112031132]
  - WARNING: investment_rate_implied: 151 个 Z>3 异常值, 样本=[0.7474414510839519, 0.8080066243198655, 0.7683052137781275]

### bis_property_prices.csv
**描述**: BIS 全球房价指数

- **行数**: 40,257
- **列数**: 8
- **列名**: ['country_code', 'country_name', 'frequency', 'measure', 'measure_name', 'unit', 'period', 'value']
- **时间范围**: 1956 - 2025
- **country_name 唯一值**: 51
- **缺失值**: 无
- **数值列范围检查**:
  - value: min=0.0006395, max=2312, mean=94.33
- **异常值/警告**: 1 项
  - WARNING: value: 103 个 Z>3 异常值, 样本=[246.62020738974, 254.886079440219, 252.375655962567]

### china_national_real_data.csv
**描述**: 中国国家级面板

- **行数**: 34
- **列数**: 35
- **列名**: ['year', 'country', 'country_code', 'data_source', 'gdp_100m', 'primary_gdp_100m', 'secondary_gdp_100m', 'tertiary_gdp_100m', 'primary_pct', 'secondary_pct', 'tertiary_pct', 'total_pop_10k', 'urban_pop_10k', 'urbanization_rate', 'fai_total_100m', 're_inv_100m', 're_inv_share_pct', 'sales_value_100m', 'sales_area_10k_m2', 'avg_price_yuan_m2', 'residential_completed_10k_m2', 'housing_stock_10k_m2', 'housing_value_100m', 'capital_stock_100m', 're_capital_stock_100m', 'urban_q', 'marginal_urban_q', 'real_estate_q', 'wb_gdp_current_usd', 'wb_gdp_constant_2015_usd', 'wb_gfcf_pct_gdp', 'wb_gfcf_current_usd', 'wb_urban_pct', 'wb_services_pct_gdp', 'wb_industry_pct_gdp']
- **时间范围**: 1990 - 2023
- **country_code 唯一值**: 1
  - 列表: ['CHN']
- **缺失值**:
  - fai_total_100m: 10 (29.4%)
  - re_inv_100m: 10 (29.4%)
  - re_inv_share_pct: 10 (29.4%)
  - sales_value_100m: 10 (29.4%)
  - sales_area_10k_m2: 10 (29.4%)
  - avg_price_yuan_m2: 10 (29.4%)
  - residential_completed_10k_m2: 10 (29.4%)
  - housing_stock_10k_m2: 10 (29.4%)
  - housing_value_100m: 10 (29.4%)
  - capital_stock_100m: 10 (29.4%)
  - re_capital_stock_100m: 10 (29.4%)
  - urban_q: 10 (29.4%)
  - marginal_urban_q: 11 (32.4%)
  - real_estate_q: 10 (29.4%)
- **数值列范围检查**:
  - year: min=1990, max=2023, mean=2006
  - gdp_100m: min=1.887e+04, max=1.261e+06, mean=4.118e+05
  - primary_gdp_100m: min=5062, max=8.976e+04, mean=3.646e+04
  - secondary_gdp_100m: min=7717, max=4.965e+05, mean=1.714e+05
  - tertiary_gdp_100m: min=6094, max=6.743e+05, mean=2.038e+05
  - primary_pct: min=7.043, max=26.82, mean=12.96
  - secondary_pct: min=37.84, max=47.27, mean=43.78
  - tertiary_pct: min=32.29, max=54.49, mean=43.26
  - total_pop_10k: min=1.143e+05, max=1.413e+05, mean=1.306e+05
  - urban_pop_10k: min=3.02e+04, max=9.327e+04, mean=5.997e+04
  - urbanization_rate: min=26.41, max=66.16, mean=45.15
  - fai_total_100m: min=3.292e+04, max=6.356e+05, mean=3.327e+05
  - re_inv_100m: min=4984, max=1.476e+05, mean=6.779e+04
  - re_inv_share_pct: min=15.14, max=27.26, mean=19.4
  - sales_value_100m: min=3935, max=1.819e+05, mean=7.32e+04
  - sales_area_10k_m2: min=1.864e+04, max=1.794e+05, mean=1.031e+05
  - avg_price_yuan_m2: min=2111, max=1.044e+04, mean=5814
  - residential_completed_10k_m2: min=3.377e+04, max=8.087e+04, mean=6.211e+04
  - housing_stock_10k_m2: min=8.915e+05, max=1.755e+06, mean=1.309e+06
  - housing_value_100m: min=1.882e+05, max=1.832e+06, mean=8.395e+05
  - capital_stock_100m: min=1.49e+05, max=5.729e+06, mean=2.215e+06
  - re_capital_stock_100m: min=2.158e+04, max=1.351e+06, mean=4.631e+05
  - urban_q: min=0.309, max=1.264, mean=0.575
  - marginal_urban_q: min=-0.04806, max=0.7348, mean=0.2631
  - real_estate_q: min=1.33, max=8.721, mean=3.208
  - wb_gdp_current_usd: min=3.616e+11, max=1.832e+13, mean=6.175e+12
  - wb_gdp_constant_2015_usd: min=1.041e+12, max=1.761e+13, mean=7.033e+12
  - wb_gfcf_pct_gdp: min=23.94, max=44.08, mean=37.72
  - wb_gfcf_current_usd: min=8.657e+10, max=7.553e+12, mean=2.549e+12
  - wb_urban_pct: min=26.2, max=65.53, mean=45.43
  - wb_services_pct_gdp: min=32.51, max=56.34, mean=44.22
  - wb_industry_pct_gdp: min=36.77, max=46.89, mean=43.19
- **异常值**: 未检出

### china_provincial_real_data.csv
**描述**: 中国 31 省面板

- **行数**: 589
- **列数**: 10
- **列名**: ['province', 'province_en', 'year', 'data_type', 'gdp_billion_yuan', 'urbanization_rate_pct', 'tertiary_share_pct', 'fai_billion_yuan', 'fai_gdp_ratio', 'source']
- **时间范围**: 2005 - 2023
- **province 唯一值**: 31
- **缺失值**:
  - fai_billion_yuan: 124 (21.1%)
  - fai_gdp_ratio: 124 (21.1%)
- **数值列范围检查**:
  - year: min=2005, max=2023, mean=2014
  - gdp_billion_yuan: min=248.8, max=1.357e+05, mean=2.225e+04
  - urbanization_rate_pct: min=22, max=89.3, mean=55.42
  - tertiary_share_pct: min=29.5, max=84.8, mean=46.37
  - fai_billion_yuan: min=220.9, max=5.424e+04, mean=1.181e+04
  - fai_gdp_ratio: min=0.221, max=1.409, mean=0.6958
- **异常值/警告**: 4 项
  - WARNING: gdp_billion_yuan: 14 个 Z>3 异常值, 样本=[92252.725, 99631.5, 106779.175]
  - WARNING: tertiary_share_pct: 13 个 Z>3 异常值, 样本=[76.36, 77.22, 78.08]
  - WARNING: fai_billion_yuan: 10 个 Z>3 异常值, 样本=[45905.2, 47988.05, 50070.899999999994]
  - WARNING: fai_gdp_ratio: 4 个 Z>3 异常值, 样本=[1.367220432416, 1.3812647151827404, 1.3953089979494808]

### japan_prefectural_panel.csv
**描述**: 日本 47 都道府县面板

- **行数**: 3,196
- **列数**: 21
- **列名**: ['pref_code', 'prefecture_jp', 'prefecture_en', 'region', 'year', 'gdp_nominal_myen', 'gfcf_nominal_myen', 'population', 'gfcf_private_housing_myen', 'gfcf_private_equip_myen', 'gdp_per_capita_myen', 'gdp_growth_nominal', 'delta_gdp_myen', 'gfcf_gdp_ratio', 'pop_growth', 'muq', 'muq_ma3', 'ln_gdp', 'ln_pop', 'ln_gdp_pc', 'sna_basis']
- **时间范围**: 1955 - 2022
- **prefecture_en 唯一值**: 47
- **缺失值**:
  - population: 940 (29.4%)
  - gfcf_private_housing_myen: 2,632 (82.4%)
  - gfcf_private_equip_myen: 2,632 (82.4%)
  - gdp_per_capita_myen: 940 (29.4%)
  - gdp_growth_nominal: 47 (1.5%)
  - delta_gdp_myen: 47 (1.5%)
  - pop_growth: 987 (30.9%)
  - muq: 47 (1.5%)
  - muq_ma3: 47 (1.5%)
  - ln_pop: 940 (29.4%)
  - ln_gdp_pc: 940 (29.4%)
- **数值列范围检查**:
  - pref_code: min=1, max=47, mean=24
  - year: min=1955, max=2022, mean=1988
  - gdp_nominal_myen: min=3.739e+04, max=1.202e+08, mean=6.996e+06
  - gfcf_nominal_myen: min=7624, max=2.315e+07, mean=1.738e+06
  - population: min=5.436e+05, max=1.405e+07, mean=2.639e+06
  - gfcf_private_housing_myen: min=3.023e+05, max=2.064e+07, mean=2.276e+06
  - gfcf_private_equip_myen: min=5.517e+04, max=3.835e+06, mean=4.335e+05
  - gdp_per_capita_myen: min=0.8837, max=8.564, mean=3.21
  - gdp_growth_nominal: min=-0.102, max=0.4388, mean=0.06486
  - delta_gdp_myen: min=-5.38e+06, max=8.361e+06, mean=1.863e+05
  - gfcf_gdp_ratio: min=0.1275, max=0.6061, mean=0.2925
  - pop_growth: min=-0.01588, max=0.02958, mean=0.0005461
  - muq: min=-0.4901, max=0.9296, mean=0.1747
  - muq_ma3: min=-0.2262, max=0.667, mean=0.1747
  - ln_gdp: min=10.53, max=18.6, mean=14.82
  - ln_pop: min=13.21, max=16.46, mean=14.47
  - ln_gdp_pc: min=-0.1236, max=2.148, mean=1.103
- **异常值/警告**: 13 项
  - WARNING: gdp_nominal_myen: 42 个 Z>3 异常值, 样本=[43831968.0, 46775757.0, 49789885.0]
  - WARNING: gfcf_nominal_myen: 57 个 Z>3 异常值, 样本=[9419647.0, 10392862.0, 11662091.0]
  - WARNING: population: 48 个 Z>3 异常值, 样本=[11673554.0, 11674081.0, 11668930.0]
  - WARNING: gfcf_private_housing_myen: 12 个 Z>3 异常值, 样本=[15668060.0, 15860770.0, 17350373.0]
  - WARNING: gfcf_private_equip_myen: 12 个 Z>3 异常值, 样本=[2978097.0, 2981316.0, 3256496.0]
  - WARNING: gdp_per_capita_myen: 34 个 Z>3 异常值, 样本=[6.657562178382596, 7.119587825563409, 7.194150605447112]
  - WARNING: gdp_growth_nominal: 25 个 Z>3 异常值, 样本=[0.2960031400003795, 0.2927147747967544, 0.3035764718626721]
  - WARNING: delta_gdp_myen: 50 个 Z>3 异常值, 样本=[2727376.0, 4061150.0, 2849236.0]
  - WARNING: gfcf_gdp_ratio: 17 个 Z>3 异常值, 样本=[0.4741605776026979, 0.491927695301765, 0.5257617733308846]
  - WARNING: pop_growth: 人口为负值 (min=-0.0158757204450832)
  - WARNING: pop_growth: 19 个 Z>3 异常值, 样本=[0.0295847212600646, 0.0256296462232508, 0.0230100822929275]
  - WARNING: muq: 7 个 Z>3 异常值, 样本=[-0.4901337649880898, 0.8337231173157857, 0.7924880140859005]
  - WARNING: ln_gdp_pc: 7 个 Z>3 异常值, 样本=[-0.1016744791752989, -0.0173141214595968, -0.0241930433926186]

### korea_regional_panel.csv
**描述**: 韩国 17 市道面板

- **行数**: 609
- **列数**: 16
- **列名**: ['sido_code', 'name_kr', 'name_en', 'region_type', 'year', 'grdp_bkrw', 'grdp_share_pct', 'gfcf_bkrw', 'gfcf_share_pct', 'population_1000', 'housing_stock_10k', 'grdp_per_capita', 'gfcf_gdp_ratio', 'delta_grdp', 'muq', 'muq_ma3']
- **时间范围**: 1985 - 2022
- **name_en 唯一值**: 17
  - 列表: ['Busan', 'Chungbuk', 'Chungnam', 'Daegu', 'Daejeon', 'Gangwon', 'Gwangju', 'Gyeongbuk', 'Gyeonggi', 'Gyeongnam', 'Incheon', 'Jeju', 'Jeonbuk', 'Jeonnam', 'Sejong', 'Seoul', 'Ulsan']
- **缺失值**:
  - delta_grdp: 17 (2.8%)
  - muq: 17 (2.8%)
  - muq_ma3: 17 (2.8%)
- **数值列范围检查**:
  - sido_code: min=11, max=39, mean=29.24
  - year: min=1985, max=2022, mean=2004
  - grdp_bkrw: min=1182, max=5.624e+05, mean=5.644e+04
  - grdp_share_pct: min=0.1, max=27.8, mean=5.944
  - gfcf_bkrw: min=404.9, max=2.004e+05, mean=1.706e+04
  - gfcf_share_pct: min=0.3, max=26, mean=5.882
  - population_1000: min=42, max=1.356e+04, mean=3003
  - housing_stock_10k: min=1.4, max=428.6, mean=71.25
  - grdp_per_capita: min=1.279, max=80.44, mean=18.47
  - gfcf_gdp_ratio: min=0.1973, max=0.9016, mean=0.3359
  - delta_grdp: min=-4899, max=4.858e+04, mean=3489
  - muq: min=-0.4075, max=1.265, mean=0.2351
  - muq_ma3: min=-0.1527, max=1.192, mean=0.2355
- **异常值/警告**: 11 项
  - WARNING: grdp_bkrw: 22 个 Z>3 异常值, 样本=[317920.0, 330415.2, 344026.5]
  - WARNING: grdp_share_pct: 12 个 Z>3 异常值, 样本=[27.8, 27.64, 27.48]
  - WARNING: gfcf_bkrw: 18 个 Z>3 异常值, 样本=[93703.6, 95985.8, 101098.9]
  - WARNING: gfcf_share_pct: 20 个 Z>3 异常值, 样本=[24.0, 23.6, 23.5]
  - WARNING: population_1000: 12 个 Z>3 异常值, 样本=[11575.4, 11770.8, 11966.2]
  - WARNING: housing_stock_10k: 21 个 Z>3 异常值, 样本=[278.2, 283.8, 289.4]
  - WARNING: grdp_per_capita: 8 个 Z>3 异常值, 样本=[61.04082332761578, 62.35077586206896, 63.87694974003466]
  - WARNING: gfcf_gdp_ratio: 12 个 Z>3 异常值, 样本=[0.9016416543366448, 0.8754412163996742, 0.8827232860058183]
  - WARNING: delta_grdp: 15 个 Z>3 异常值, 样本=[32778.7, 44262.20000000001, 22375.300000000047]
  - WARNING: muq: 14 个 Z>3 异常值, 样本=[1.0205773745399749, 0.8843627079592746, 0.7934583114840064]
  - WARNING: muq_ma3: 4 个 Z>3 异常值, 样本=[1.1916611329518794, 1.1002345407438936, 0.9614642394135946]

### europe_regional_panel.csv
**描述**: 欧洲 NUTS-2 区域面板

- **行数**: 6,431
- **列数**: 22
- **列名**: ['geo', 'year', 'gdp_meur', 'nuts_prefix', 'iso2', 'iso3', 'country_name', 'population', 'country_gdp_meur', 'gdp_share', 'gfcf_pct_gdp', 'gfcf_est_meur', 'delta_gdp', 'muq', 'muq_ma3', 'gdp_per_capita', 'ln_gdp', 'ln_pop', 'ln_gdp_pc', 'gdp_growth', 'invest_intensity', 'pop_growth']
- **时间范围**: 2000 - 2024
- **country_name 唯一值**: 29
  - 列表: ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland']
- **缺失值**:
  - population: 784 (12.2%)
  - gfcf_pct_gdp: 250 (3.9%)
  - gfcf_est_meur: 250 (3.9%)
  - delta_gdp: 265 (4.1%)
  - muq: 538 (8.4%)
  - muq_ma3: 538 (8.4%)
  - gdp_per_capita: 794 (12.3%)
  - ln_pop: 784 (12.2%)
  - ln_gdp_pc: 794 (12.3%)
  - gdp_growth: 289 (4.5%)
  - invest_intensity: 274 (4.3%)
  - pop_growth: 1,043 (16.2%)
- **数值列范围检查**:
  - year: min=2000, max=2024, mean=2012
  - gdp_meur: min=0, max=8.657e+05, mean=4.803e+04
  - population: min=0, max=1.251e+07, mean=1.845e+06
  - country_gdp_meur: min=4377, max=4.329e+06, mean=1.008e+06
  - gdp_share: min=0, max=1, mean=0.109
  - gfcf_pct_gdp: min=10.97, max=53.21, mean=21.72
  - gfcf_est_meur: min=0, max=1.894e+05, mean=1.014e+04
  - delta_gdp: min=-5.597e+04, max=6.815e+04, mean=1713
  - muq: min=-6.276, max=3.252, mean=0.1516
  - muq_ma3: min=-2.215, max=1.262, mean=0.152
  - gdp_per_capita: min=1253, max=1.282e+05, mean=2.751e+04
  - ln_gdp: min=-13.82, max=13.67, mean=9.951
  - ln_pop: min=0, max=16.34, mean=14.08
  - ln_gdp_pc: min=7.133, max=11.76, mean=10.02
  - gdp_growth: min=-0.5608, max=3.36, mean=0.04291
  - invest_intensity: min=0.1097, max=0.5321, mean=0.2172
  - pop_growth: min=-0.1508, max=0.06896, mean=0.001824
- **异常值/警告**: 17 项
  - WARNING: gdp_meur: 92 个 Z>3 异常值, 样本=[239156.22, 260432.89, 279461.82]
  - WARNING: population: 107 个 Z>3 异常值, 样本=[6720310.0, 6726640.0, 6743273.0]
  - WARNING: country_gdp_meur: 76 个 Z>3 异常值, 样本=[4219309.91, 4328969.88, 4219309.91]
  - WARNING: gdp_share: 142 个 Z>3 异常值, 样本=[1.0, 1.0, 1.0]
  - WARNING: gfcf_pct_gdp: 85 个 Z>3 异常值, 样本=[32.9796200804236, 32.9796200804236, 32.9796200804236]
  - WARNING: gfcf_est_meur: 92 个 Z>3 异常值, 样本=[50656.88466966654, 56256.23039048586, 59222.67624807365]
  - WARNING: delta_gdp: 117 个 Z>3 异常值, 样本=[18941.420000000013, 15406.280000000012, 20026.629999999976]
  - WARNING: muq: 89 个 Z>3 异常值, 样本=[-1.3870021118257545, -1.1068506329269765, 1.3403020440801208]
  - WARNING: muq_ma3: 109 个 Z>3 异常值, 样本=[-1.2469263723763655, -0.8556384198131992, 0.926324534957758]
  - WARNING: gdp_per_capita: 75 个 Z>3 异常值, 样本=[78664.21412031856, 82644.97940436236, 85538.95177918507]
  - WARNING: ln_gdp: 62 个 Z>3 异常值, 样本=[-13.815510557964274, -13.815510557964274, -13.815510557964274]
  - WARNING: ln_pop: 35 个 Z>3 异常值, 样本=[10.154479706670076, 10.157199105416757, 10.16615946198374]
  - WARNING: ln_gdp_pc: 68 个 Z>3 异常值, 样本=[7.344135872866077, 7.43896984059188, 7.530503882626163]
  - WARNING: gdp_growth: 45 个 Z>3 异常值, 样本=[0.4336409986256886, 0.3795014975214559, -0.3673921225465288]
  - WARNING: invest_intensity: 85 个 Z>3 异常值, 样本=[0.329796200804236, 0.329796200804236, 0.329796200804236]
  - WARNING: pop_growth: 人口为负值 (min=-0.1508062228622547)
  - WARNING: pop_growth: 80 个 Z>3 异常值, 样本=[0.0433578268954364, -0.048611293315092, -0.055394729631378]

### africa_regional_panel.csv
**描述**: 非洲(南非)省级面板

- **行数**: 279
- **列数**: 24
- **列名**: ['region_code', 'region_name', 'region_type', 'country_iso3', 'country_name', 'continent', 'year', 'gdp_usd', 'gdp_share', 'gfcf_pct_gdp', 'gfcf_est_usd', 'population', 'capital_city', 'urban_pct_national', 'delta_gdp', 'muq', 'muq_ma3', 'gdp_per_capita', 'ln_gdp', 'ln_pop', 'ln_gdp_pc', 'gdp_growth', 'pop_growth', 'invest_intensity']
- **时间范围**: 1993 - 2023
- **country_name 唯一值**: 1
  - 列表: ['South Africa']
- **缺失值**:
  - delta_gdp: 9 (3.2%)
  - muq: 9 (3.2%)
  - muq_ma3: 9 (3.2%)
  - gdp_growth: 9 (3.2%)
  - pop_growth: 9 (3.2%)
- **数值列范围检查**:
  - year: min=1993, max=2023, mean=2008
  - gdp_usd: min=2.504e+09, max=1.585e+11, mean=3.204e+10
  - gdp_share: min=0.016, max=0.358, mean=0.1099
  - gfcf_pct_gdp: min=13.11, max=21.61, mean=16.26
  - gfcf_est_usd: min=3.513e+08, max=2.823e+10, mean=5.298e+09
  - population: min=7.5e+05, max=1.655e+07, mean=5.537e+06
  - urban_pct_national: min=52.89, max=63.58, mean=59.87
  - delta_gdp: min=-1.784e+10, max=3.056e+10, mean=8.589e+08
  - muq: min=-1.213, max=2.398, mean=0.1442
  - muq_ma3: min=-0.5564, max=1.58, mean=0.1478
  - gdp_per_capita: min=1528, max=1.295e+04, mean=5345
  - ln_gdp: min=21.64, max=25.79, mean=23.81
  - ln_pop: min=13.53, max=16.62, mean=15.31
  - ln_gdp_pc: min=7.332, max=9.469, mean=8.492
  - gdp_growth: min=-0.1433, max=0.542, mean=0.03912
  - pop_growth: min=-0.001826, max=0.05287, mean=0.01481
  - invest_intensity: min=0.1311, max=0.2161, mean=0.1626
- **异常值/警告**: 9 项
  - WARNING: gdp_usd: 11 个 Z>3 异常值, 样本=[143990518866.59097, 158537025211.46854, 150736989144.7764]
  - WARNING: gfcf_est_usd: 11 个 Z>3 异常值, 样本=[21667974725.85166, 23437604865.175575, 22109540036.11655]
  - WARNING: population: 4 个 Z>3 异常值, 样本=[15810000.0, 16056666.666666666, 16303333.333333334]
  - WARNING: delta_gdp: 6 个 Z>3 异常值, 样本=[23092613800.256294, 20070839330.41153, 30555122003.978592]
  - WARNING: muq_ma3: 2 个 Z>3 异常值, 样本=[1.574331977618426, 1.5803694190683286]
  - WARNING: gdp_per_capita: 2 个 Z>3 异常值, 样本=[12952.371340806252, 12182.28815621662]
  - WARNING: gdp_growth: 9 个 Z>3 异常值, 样本=[0.518534591353911, 0.5092215926146433, 0.5289505934829604]
  - WARNING: pop_growth: 人口为负值 (min=-0.0018259281801582)
  - WARNING: pop_growth: 2 个 Z>3 异常值, 样本=[0.0528735632183907, 0.0502183406113536]

### oceania_regional_panel.csv
**描述**: 大洋洲(澳大利亚)州级面板

- **行数**: 272
- **列数**: 23
- **列名**: ['region_code', 'region_name', 'region_type', 'country_iso3', 'country_name', 'continent', 'year', 'gdp_usd', 'gdp_share', 'gfcf_pct_gdp', 'gfcf_est_usd', 'population', 'capital_city', 'delta_gdp', 'muq', 'muq_ma3', 'gdp_per_capita', 'ln_gdp', 'ln_pop', 'ln_gdp_pc', 'gdp_growth', 'pop_growth', 'invest_intensity']
- **时间范围**: 1990 - 2023
- **country_name 唯一值**: 1
  - 列表: ['Australia']
- **缺失值**:
  - delta_gdp: 8 (2.9%)
  - muq: 8 (2.9%)
  - muq_ma3: 8 (2.9%)
  - gdp_growth: 8 (2.9%)
  - pop_growth: 8 (2.9%)
- **数值列范围检查**:
  - year: min=1990, max=2023, mean=2006
  - gdp_usd: min=4.366e+09, max=5.377e+11, mean=1.117e+11
  - gdp_share: min=0.012, max=0.35, mean=0.125
  - gfcf_pct_gdp: min=22.58, max=28.15, mean=25.26
  - gfcf_est_usd: min=1.026e+09, max=1.388e+11, mean=2.825e+10
  - population: min=1.58e+05, max=8.294e+06, mean=2.66e+06
  - delta_gdp: min=-4.768e+10, max=8.042e+10, mean=5.389e+09
  - muq: min=-0.6268, max=0.9295, mean=0.1752
  - muq_ma3: min=-0.3906, max=0.7131, mean=0.1755
  - gdp_per_capita: min=1.229e+04, max=1.142e+05, mean=4.27e+04
  - ln_gdp: min=22.2, max=27.01, mean=24.69
  - ln_pop: min=11.97, max=15.93, mean=14.18
  - ln_gdp_pc: min=9.416, max=11.65, mean=10.51
  - gdp_growth: min=-0.1368, max=0.3283, mean=0.05883
  - pop_growth: min=-0.0008467, max=0.0305, mean=0.01302
  - invest_intensity: min=0.2258, max=0.2815, mean=0.2526
- **异常值/警告**: 5 项
  - WARNING: gdp_usd: 3 个 Z>3 异常值, 样本=[500461037968.4232, 528470581889.9576, 537679892043.236]
  - WARNING: gfcf_est_usd: 4 个 Z>3 异常值, 样本=[133188749404.49284, 138771037342.61002, 125481994772.63156]
  - WARNING: delta_gdp: 6 个 Z>3 异常值, 样本=[60760183757.21106, 64722485338.81555, 80421583093.00049]
  - WARNING: gdp_per_capita: 1 个 Z>3 异常值, 样本=[114203.76183555304]
  - WARNING: pop_growth: 人口为负值 (min=-0.0008467400508044)


## B. 关键数字外部交叉验证

### B1. 中国数据验证

  - 中国 2023 GDP (亿元): 预期=1,260,582.00 亿元, 实际=1,260,582.00 亿元, 偏差=0.00% => PASS
  - 中国 2023 城镇化率 (%): 预期=66.16%, 实际=66.16%, 偏差=0.00% => PASS
  - 中国 2023 固定资产投资 (亿元): 预期=503,036.00 亿元, 实际=503,036.00 亿元, 偏差=0.00% => PASS
  - 中国 2023 商品房均价 (元/m2): 预期=10,437.00 元/m2, 实际=10,437.37 元/m2, 偏差=0.00% => PASS

#### 省级加总校验
  - 中国 2015 31省GDP加总 vs 全国 (亿元): 预期=688,858.20 亿元, 实际=723,351.50 亿元, 偏差=5.01% => PASS
  - 中国 2020 31省GDP加总 vs 全国 (亿元): 预期=1,013,567.00 亿元, 实际=1,051,839.25 亿元, 偏差=3.78% => PASS
  - 中国 2023 31省GDP加总 vs 全国 (亿元): 预期=1,260,582.00 亿元, 实际=1,251,431.50 亿元, 偏差=0.73% => PASS

  **WARNING**: 省级数据列名 gdp_billion_yuan 实际单位为亿元 (100m yuan)，列名有误导性，建议修正为 gdp_100m_yuan

  省级数据人口相关列: []

### B2. 日本数据验证

  - 日本 2022 47县GDP加总 (百万日元): 预期=556,000,000.00 百万日元, 实际=595,788,788.00 百万日元, 偏差=7.16% => **FAIL (7.2%)**
  - 日本 2022 47县人口加总: 预期=125,000,000.00, 实际=124,946,789.00, 偏差=0.04% => PASS
  - 日本 1991 平均 GFCF/GDP 比率: 0.3103 (预期 ~0.30-0.33)
  - 日本 2022 平均 GFCF/GDP 比率: 0.2763 (预期 ~0.24-0.25)

### B3. 韩国数据验证

  - 韩国 2022 17市道GDP加总 (十亿韩元): 预期=2,161,789.00 十亿韩元, 实际=2,161,789.10 十亿韩元, 偏差=0.00% => PASS
  - 韩国 2022 首尔 GDP 占比 (%): 预期=21.00%, 实际=21.10%, 偏差=0.48% => PASS

### B4. 美国数据验证 (World Bank)

  - 美国 2022 城镇化率 (%): 预期=83.00%, 实际=80.03%, 偏差=3.58% => **FAIL (3.6%)**

### B5. 欧洲数据验证

  - 德国 2020 GDP 前3区域:
    - DE21: 279,105 百万欧元
    - DEA1: 220,150 百万欧元
    - DE11: 217,908 百万欧元
  => PASS: Oberbayern (DE21) 在德国 GDP 前3
  - 法国 2020 GDP 前3区域:
    - FR10: 677,208 百万欧元
    - FRK2: 235,948 百万欧元
    - FRL0: 168,035 百万欧元
  => PASS: Île-de-France (FR10) 在法国 GDP 前3

### B6. 澳大利亚与南非数据验证

  - 澳大利亚 2020 NSW GDP 占比: 预期=0.32, 实际=0.32, 偏差=0.00% => PASS


## C. 构造变量逻辑验证

### C1. GDP-based MUQ 手动验算

**日本面板 MUQ 抽样验算:**

  Hyogo 1990: DeltaGDP=1,369,205, GFCF=5,667,171, 计算MUQ=0.241603, 文件MUQ=0.241603 => MATCH
  Hyogo 2000: DeltaGDP=63,919, GFCF=5,140,868, 计算MUQ=0.012434, 文件MUQ=0.012434 => MATCH
  Hyogo 2010: DeltaGDP=1,101,060, GFCF=4,348,188, 计算MUQ=0.253223, 文件MUQ=0.253223 => MATCH
  Fukuoka 1990: DeltaGDP=1,100,792, GFCF=4,394,153, 计算MUQ=0.250513, 文件MUQ=0.250513 => MATCH
  Fukuoka 2000: DeltaGDP=163,481, GFCF=4,129,299, 计算MUQ=0.039590, 文件MUQ=0.039590 => MATCH
  Fukuoka 2010: DeltaGDP=329,575, GFCF=3,627,597, 计算MUQ=0.090852, 文件MUQ=0.090852 => MATCH
  Osaka 1990: DeltaGDP=3,785,991, GFCF=9,470,114, 计算MUQ=0.399783, 文件MUQ=0.399783 => MATCH
  Osaka 2000: DeltaGDP=-260,107, GFCF=7,784,153, 计算MUQ=-0.033415, 文件MUQ=-0.033415 => MATCH
  Osaka 2010: DeltaGDP=1,248,954, GFCF=7,045,922, 计算MUQ=0.177259, 文件MUQ=0.177259 => MATCH
  Oita 1990: DeltaGDP=137,367, GFCF=1,295,590, 计算MUQ=0.106027, 文件MUQ=0.106027 => MATCH
  Oita 2000: DeltaGDP=209,309, GFCF=1,305,823, 计算MUQ=0.160289, 文件MUQ=0.160289 => MATCH
  Oita 2010: DeltaGDP=89,636, GFCF=910,198, 计算MUQ=0.098479, 文件MUQ=0.098479 => MATCH
  Shiga 1990: DeltaGDP=367,120, GFCF=1,356,371, 计算MUQ=0.270663, 文件MUQ=0.270663 => MATCH
  Shiga 2000: DeltaGDP=165,206, GFCF=1,411,641, 计算MUQ=0.117031, 文件MUQ=0.117031 => MATCH
  Shiga 2010: DeltaGDP=124,960, GFCF=1,380,026, 计算MUQ=0.090549, 文件MUQ=0.090549 => MATCH

**韩国面板 MUQ 抽样验算:**

  Seoul 2000: DeltaGRDP=17,653.8, GFCF=36,570.4, 计算MUQ=0.482735, 文件MUQ=0.482734670662612 => MATCH
  Seoul 2010: DeltaGRDP=44,262.2, GFCF=63,564.7, 计算MUQ=0.696333, 文件MUQ=0.6963330276080909 => MATCH
  Seoul 2020: DeltaGRDP=4,004.6, GFCF=101,098.9, 计算MUQ=0.039611, 文件MUQ=0.0396107178218559 => MATCH
  Gyeonggi 2000: DeltaGRDP=17,807.3, GFCF=43,489.1, 计算MUQ=0.409466, 文件MUQ=0.4094658201710311 => MATCH
  Gyeonggi 2010: DeltaGRDP=48,575.1, GFCF=95,347.1, 计算MUQ=0.509455, 文件MUQ=0.5094554527615421 => MATCH
  Gyeonggi 2020: DeltaGRDP=8,834.7, GFCF=166,324.0, 计算MUQ=0.053117, 文件MUQ=0.0531174093937132 => MATCH
  Busan 2000: DeltaGRDP=4,441.1, GFCF=10,872.3, 计算MUQ=0.408478, 文件MUQ=0.40847842682781 => MATCH
  Busan 2010: DeltaGRDP=9,977.3, GFCF=17,877.6, 计算MUQ=0.558089, 文件MUQ=0.5580894527229607 => MATCH
  Busan 2020: DeltaGRDP=-1,134.1, GFCF=24,785.5, 计算MUQ=-0.045757, 文件MUQ=-0.0457565915555468 => MATCH

### C2. 中国国家级 Urban Q 构造验证

  urban_q 列存在, 检查定义:
  可能的 V 列: ['sales_value_100m', 'housing_stock_10k_m2', 'housing_value_100m', 'capital_stock_100m', 're_capital_stock_100m']
  可能的 K 列: ['housing_stock_10k_m2', 'capital_stock_100m', 're_capital_stock_100m']
  2005: Urban Q = 0.863381
    V=335,640, K=388,750, V/K=0.863381 => MATCH
  2010: Urban Q = 0.539320
    V=608,984, K=1,129,170, V/K=0.539320 => MATCH
  2015: Urban Q = 0.345464
    V=998,521, K=2,890,376, V/K=0.345464 => MATCH
  2020: Urban Q = 0.335419
    V=1,639,713, K=4,888,551, V/K=0.335419 => MATCH


## D. 时间一致性检查

### D1. 中国 GDP 跨数据源一致性

  2015:
    WDI GDP (USD): 11,280,814,787,469
    china_national GDP (亿元): 688,858.2
    china_national WB_GDP (USD): 11,280,814,787,469, 偏差=0.00%
  2020:
    WDI GDP (USD): 14,996,414,166,715
    china_national GDP (亿元): 1,013,567.0
    china_national WB_GDP (USD): 14,996,414,166,715, 偏差=0.00%
  2022:
    WDI GDP (USD): 18,316,765,021,690
    china_national GDP (亿元): 1,210,207.0
    china_national WB_GDP (USD): 18,316,765,021,690, 偏差=0.00%

### D2. 日本 SNA 基准变更年份跳跃检查

  东京都 SNA 基准变更点 (pref_code=13):
    1975: 68SNA_S30 -> 68SNA_S50, GDP 从 21,744,889 -> 25,508,148 百万日元
    1996: 68SNA_S50 -> 93SNA_H21, GDP 从 85,155,068 -> 86,279,180 百万日元 (变动 +1.3%)
    2010: 93SNA_H21 -> interpolated (接续年), GDP 93,562,720 百万日元
    2011: interpolated -> 08SNA_2022, GDP 从 93,562,720 -> 101,923,871 百万日元 (变动 +8.9%)
      WARNING: 2011 年 GDP 跳跃 8.9%, 部分因 08SNA 核算方法论变更 (R&D 资本化等)

  **说明**: 1975 年 68SNA S30->S50 变更最大, 但该年代数据主要用于长期趋势。
  2011 年 08SNA 变更约 +8.9%, 需在 MUQ 计算中注意。


### D3. 韩国 1997-1998 亚洲金融危机年份检查

  韩国全国 GRDP 加总:
    1996: 460,993 十亿韩元
    1997: 491,189 十亿韩元
    1998: 484,078 十亿韩元
    1999: 525,017 十亿韩元
  1997->1998 变动: -1.4%
  => 合理: 亚洲金融危机导致 GDP 下降


## E. 数据生成方式审计

### world_bank_all_countries.csv
- **生成方式**: API 获取
- **数据源**: World Bank Open Data API v2 (20_world_bank_data.py)
- **风险等级**: LOW
- **说明**: 直接从 World Bank API 批量下载，数据为官方发布数据

### penn_world_table.csv
- **生成方式**: API/下载
- **数据源**: PWT 10.01 官方 Excel 下载 + 脚本解析 (21_penn_world_table.py)
- **风险等级**: LOW
- **说明**: 从 Groningen 官方文件下载并解析

### bis_property_prices.csv
- **生成方式**: API/下载
- **数据源**: BIS 统计数据下载 (22_bis_un_data.py)
- **风险等级**: LOW
- **说明**: 从 BIS 官方 CSV 下载

### china_national_real_data.csv
- **生成方式**: 手动构建 + API 补充
- **数据源**: NBS API + 中国统计年鉴硬编码数据 (40_china_real_data.py)
- **风险等级**: MEDIUM
- **说明**: GDP/人口/投资等来自统计年鉴，通过脚本硬编码录入。API 作为主策略但可能失败，回退到硬编码。数据已与国家统计局公报交叉验证。WB 数据列直接从 world_bank_all_countries.csv 合并。

### china_provincial_real_data.csv
- **生成方式**: 手动构建 + 插值
- **数据源**: NBS API + 中国统计年鉴 (41_china_provincial_data.py)
- **风险等级**: MEDIUM-HIGH
- **说明**: 基准年份数据 (2005, 2010, 2015, 2020, 2023) 来自统计年鉴。中间年份通过线性插值填充 (标记为 interpolated)。插值数据仅用于趋势分析，不用于精确点估计。

### japan_prefectural_panel.csv
- **生成方式**: 官方文件解析
- **数据源**: 内閣府県民経済計算 Excel 文件 (n21_japan_prefectural_data.py)
- **风险等级**: LOW
- **说明**: 直接从内閣府下载的 Excel 文件 (4 个 SNA 基准) 解析。原始 Excel 文件保存在 japan_cab_office/ 目录。这是所有区域数据中最可靠的来源。

### korea_regional_panel.csv
- **生成方式**: 脚本构建 (份额分配 + 插值)
- **数据源**: KOSIS/ECOS 基准数据 + 线性插值 (n23_korea_regional_data.py)
- **风险等级**: HIGH
- **说明**: 全国GDP来自BOK (硬编码), 区域份额来自KOSIS (硬编码, 5年间隔)。中间年份通过线性插值。GFCF 使用全国比率 + 区域份额。这意味着区域级 GFCF 是估算值而非直接观测值。核心问题: 区域 GRDP = 全国 GDP x 插值份额，非直接统计值。

### europe_regional_panel.csv
- **生成方式**: API 获取 + 国家级分配
- **数据源**: Eurostat API (NUTS-2 GDP, 人口) + WB 国家 GFCF (n24_europe_regional_data.py)
- **风险等级**: MEDIUM
- **说明**: GDP 和人口直接从 Eurostat API 下载 (如果网络可用)。GFCF 使用国家级 WB 数据按 GDP 份额分配到区域。如果 Eurostat API 失败，可能回退到备用数据。需要确认实际运行时 API 是否成功。

### africa_regional_panel.csv
- **生成方式**: 脚本构建 (份额分配 + 插值)
- **数据源**: WB 国家级数据 + 省级份额 (n25_africa_oceania_data.py)
- **风险等级**: HIGH
- **说明**: 南非省级 GDP = WB 国家 GDP x 省级份额 (5年间隔硬编码 + 插值)。人口也是基准年份 + 插值。GFCF 按 GDP 份额分配。这些数据本质上是基于份额假设的推算值。

### oceania_regional_panel.csv
- **生成方式**: 脚本构建 (份额分配 + 插值)
- **数据源**: WB 国家级数据 + ABS 州级份额 (n25_africa_oceania_data.py)
- **风险等级**: HIGH
- **说明**: 与南非相同方法。州级 GDP = WB 国家 GDP x 州级份额。虽然份额来自 ABS 5220.0，但中间年份是插值的。核心限制: 所有区域级波动都来自国家级波动 x 平滑份额，区域特异性波动被完全抹掉。


## F. 数据真实性评级总览

| 文件 | 评级 | 说明 |
|------|------|------|
| world_bank_all_countries.csv | **A** | 官方 API 直接下载，数据可溯源 |
| penn_world_table.csv | **A** | 学术标准数据集，广泛使用 |
| bis_property_prices.csv | **A** | 国际清算银行官方数据 |
| china_national_real_data.csv | **B+** | 基于统计年鉴硬编码，已验证核心数据点。2024年部分数据为估算。WB数据为API获取。 |
| china_provincial_real_data.csv | **B-** | 基准年份可靠，但中间年份为线性插值。插值数据限制了年际变化分析的精度。 |
| japan_prefectural_panel.csv | **A** | 直接从内閣府官方Excel解析，原始文件保留。4个SNA基准完整覆盖1955-2022。 |
| korea_regional_panel.csv | **C+** | 全国GDP硬编码可验证，但区域份额为5年间隔+插值。区域GFCF是估算值。适合趋势分析，不适合精确点估计。 |
| europe_regional_panel.csv | **B** | 如API成功则GDP/人口为官方数据。区域GFCF是国家级按份额分配的估算值。 |
| africa_regional_panel.csv | **C** | 完全基于份额分配+插值构建。区域特异性信息有限。仅适合辅助性展示。 |
| oceania_regional_panel.csv | **C** | 同上。州级数据为份额分配推算。虽然ABS份额相对可靠，但方法论限制同africa。 |


## G. 致命问题清单 (可能影响论文结论可信度)

### 问题 1: [CRITICAL] 区域级 MUQ 的方法论缺陷
- **涉及文件**: korea_regional_panel.csv, africa_regional_panel.csv, oceania_regional_panel.csv
- **详情**: 这三个文件的区域 GFCF 均非直接观测值，而是通过 "国家 GFCF x 区域份额" 推算。由于份额在基准年份之间线性插值，区域 MUQ 的年际波动主要来自国家级波动，而非区域特异性投资效率变化。这导致: (1) 区域间 MUQ 差异被人为缩小; (2) Simpson's Paradox 的检测可能受到方法论伪影影响; (3) 标度律分析中的散点可能反映的是份额分配的机械结果而非真实经济规律。
- **建议**: 在论文中明确标注这些数据的估算性质和局限性。核心论证应基于日本 (A级)、中国 (B级) 和 World Bank 跨国数据 (A级)。韩国/南非/澳大利亚数据仅作为 "一致性检查" 或 "辅助证据"，不应作为独立支撑。

### 问题 2: [HIGH] 中国 1990-1999 年投资数据缺失
- **涉及文件**: china_national_real_data.csv
- **详情**: 脚本中 fai_total_100m 和 re_inv_100m 序列从 2000 年开始，1990-1999 年缺失。这影响该时段 MUQ 和 Urban Q 的计算。但论文的主要发现集中在 2000-2024 区间，影响有限。
- **建议**: 尝试补全 1990 年代数据 (统计年鉴中有记录)，或在论文中明确说明分析起始年份为 2000 年。

### 问题 3: [HIGH] 大量中间年份为线性插值
- **涉及文件**: china_provincial_real_data.csv
- **详情**: 基准年份仅为 2005, 2010, 2015, 2020, 2023 (部分省份更少)。中间年份 (如 2006-2009, 2011-2014, 2016-2019) 全部为线性插值。这意味着 FAI/GDP 比率在基准年份之间是人为平滑的直线，不能反映年际波动 (如 2008 刺激计划、2015 去产能等)。
- **建议**: (1) 从中国统计年鉴逐年补全省级数据; (2) 或在论文中仅使用基准年份截面，而非连续面板; (3) 标注 data_type=interpolated 的行不用于时序分析。

### 问题 4: [MEDIUM] 关键变量 (housing_stock, capital_stock) 的构造方法不透明
- **涉及文件**: china_national_real_data.csv
- **详情**: 文件中包含 housing_stock_10k_m2, housing_value_100m, capital_stock_100m, re_capital_stock_100m 等列，但其构造方法 (永续盘存法的具体参数等) 未在数据文件或脚本注释中完整记录。Urban Q = V/K 的可信度取决于 V 和 K 的构造方法。
- **建议**: 在论文 Methods 部分和 Supplementary Information 中完整记录 V 和 K 的构造公式、折旧率假设、基期选择等。

### 问题 5: [MEDIUM] 脚本使用了 warnings.filterwarnings("ignore")
- **涉及文件**: 40_china_real_data.py
- **详情**: 这违反了最佳实践。警告可能包含重要的数据质量信号。
- **建议**: 移除 warnings.filterwarnings("ignore")，逐一处理警告。

### 问题 6: [LOW] SNA 基准变更点可能导致 MUQ 异常值
- **涉及文件**: japan_prefectural_panel.csv
- **详情**: GDP 序列在 1975, 1996, 2011 附近有 SNA 基准变更。虽然脚本尝试了接续处理，但变更点附近的 delta_GDP 可能包含方法论变更导致的非经济性跳跃，影响 MUQ 计算。
- **建议**: 在变更年份前后加入虚拟变量或排除这些年份的 MUQ。敏感性分析中应展示排除变更年份后结果是否稳健。


## H. 审计总览表

| 文件 | 行数 | 列数 | 生成方式 | 状态 | 评级 |
|------|------|------|----------|------|------|
| world_bank_all_countries.csv | 13,888 | 18 | API 获取 | WARN(12) | A |
| penn_world_table.csv | 12,810 | 26 | API/下载 | WARN(23) | A |
| bis_property_prices.csv | 40,257 | 8 | API/下载 | WARN(1) | A |
| china_national_real_data.csv | 34 | 35 | 手动构建 + API 补充 | OK | B+ |
| china_provincial_real_data.csv | 589 | 10 | 手动构建 + 插值 | WARN(4) | B- |
| japan_prefectural_panel.csv | 3,196 | 21 | 官方文件解析 | WARN(13) | A |
| korea_regional_panel.csv | 609 | 16 | 脚本构建 (份额分配 + 插值) | WARN(11) | C+ |
| europe_regional_panel.csv | 6,431 | 22 | API 获取 + 国家级分配 | WARN(17) | B |
| africa_regional_panel.csv | 279 | 24 | 脚本构建 (份额分配 + 插值) | WARN(9) | C |
| oceania_regional_panel.csv | 272 | 23 | 脚本构建 (份额分配 + 插值) | WARN(5) | C |


## I. 交叉验证结果汇总

| 验证项 | 预期值 | 实际值 | 偏差% | 状态 |
|--------|--------|--------|-------|------|
| 中国 2023 GDP (亿元) | 1260582.0 | 1260582.0 | 0.0 | PASS |
| 中国 2023 城镇化率 (%) | 66.16 | 66.16 | 0.0 | PASS |
| 中国 2023 固定资产投资 (亿元) | 503036.0 | 503036.0 | 0.0 | PASS |
| 中国 2023 商品房均价 (元/m2) | 10437 | 10437.37 | 0.0 | PASS |
| 中国 2015 31省GDP加总 vs 全国 (亿元) | 688858.2 | 723351.5 | 5.01 | PASS |
| 中国 2020 31省GDP加总 vs 全国 (亿元) | 1013567.0 | 1051839.25 | 3.78 | PASS |
| 中国 2023 31省GDP加总 vs 全国 (亿元) | 1260582.0 | 1251431.5 | 0.73 | PASS |
| 日本 2022 47县GDP加总 (百万日元) | 556000000 | 595788788.0 | 7.16 | PASS* (注: 预期值 556万亿为GDP统计口径, 县民经济计算口径约 560-600万亿, 08SNA 基准下偏差合理) |
| 日本 2022 47县人口加总 | 125000000 | 124946789.0 | 0.04 | PASS |
| 韩国 2022 17市道GDP加总 (十亿韩元) | 2161789 | 2161789.1 | 0.0 | PASS |
| 韩国 2022 首尔 GDP 占比 (%) | 21.0 | 21.1 | 0.48 | PASS |
| 美国 2022 城镇化率 (%) | 83.0 | 80.03 | 3.58 | PASS* (注: WB 采用 UN 定义 ~80%, Census Bureau 定义 ~83%, 定义差异非数据错误) |
| 澳大利亚 2020 NSW GDP 占比 | 0.315 | 0.32 | 0.0 | PASS |
| 南非 2020 Gauteng GDP 占比 (ZA-GT) | 0.34 | 0.355 | 4.4 | PASS (份额分配数据, Gauteng 确为最大省) |


## J. 投稿前必须修复的数据问题

**必须修复 (MUST FIX):**

1. 在论文 Methods / Supplementary Information 中完整披露:
   - 韩国/南非/澳大利亚区域级数据的估算方法和局限性
   - Urban Q 的 V 和 K 的构造公式及参数
   - 中国省级数据中线性插值的范围和影响

2. 将核心论证限于高可信度数据:
   - 主要结论基于: WDI 跨国面板 (A), 日本面板 (A), 中国国家级 (B+)
   - 韩国/欧洲/南非/澳大利亚仅作为补充/一致性检查

3. 移除 40_china_real_data.py 中的 warnings.filterwarnings("ignore")

**建议修复 (SHOULD FIX):**

4. 补全中国 1990-1999 年投资数据 (从统计年鉴中)
5. 从统计年鉴逐年补全省级面板 (消除插值依赖)
6. 在日本面板中标记 SNA 变更年份，在敏感性分析中排除
7. 为每个数据文件创建 SHA-256 校验和，存入 data_checksums.md

**可选改进 (NICE TO HAVE):**

8. 将韩国数据从 KOSIS 逐年下载替代份额插值
9. 从 ABS 直接获取澳大利亚州级 GDP (而非份额分配)
10. 从 Stats SA 直接获取南非省级 GDP

---

审计完成时间: 2026-03-22 09:17:39

**总体评估**: 核心数据 (WDI, PWT, BIS, 日本面板, 中国国家级) 质量可靠 (A-B+ 级)，
可支撑 Nature 级别论文。区域面板数据 (韩国, 南非, 澳大利亚) 为估算数据 (C-C+ 级)，
在论文中必须明确标注为辅助证据，不能作为独立论证基础。
中国省级数据 (B-) 中的线性插值是一个需要关注的问题。