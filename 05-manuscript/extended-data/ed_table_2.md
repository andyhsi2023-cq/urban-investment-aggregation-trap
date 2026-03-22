# Extended Data Table 2 | Unified panel regression results: MUQ on income, urbanisation, and scaling law

**Panel A. MUQ ~ ln(GDP per capita) + Country FE + Year FE**

| Variable | beta | SE | t | p-value | 95% CI | R-squared | Adj R-squared | N |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| ln(GDP_pc) | -0.0432 | 0.0126 | -3.429 | 0.000625 | [-0.0679, -0.0184] | 0.4567 | 0.4552 | 28,492 |

Panel: 1,567 regions across 35 countries, years 1955--2024. Dependent variable: GDP-based MUQ (winsorised at 1%/99%). Country and year fixed effects included.

**Panel B. MUQ ~ urbanisation + Country FE + Year FE**

| Variable | beta | SE | t | p-value | 95% CI | R-squared | N |
|---|---:|---:|---:|---:|---|---:|---:|
| urbanization | 0.001051 | 0.000404 | 2.601 | 0.009292 | [0.000259, 0.001843] | 0.9870 | 559 |

Subsample restricted to observations with available urbanisation data.

**Panel C. Global scaling law: ln(GDP) ~ ln(Pop)**

| Sample | beta | SE | 95% CI | R-squared | N |
|---|---:|---:|---|---:|---:|
| **Global** | **0.9725** | **0.0054** | **[0.9620, 0.9830]** | **0.5149** | **30,225** |
| Africa | 1.0856 | 0.0330 | [1.0210, 1.1503] | 0.7545 | 279 |
| Asia | 0.4565 | 0.0302 | [0.3974, 0.5157] | 0.0203 | 12,346 |
| Europe | 0.7825 | 0.0431 | [0.6980, 0.8669] | 0.5356 | 5,647 |
| North America | 1.0655 | 0.0028 | [1.0600, 1.0709] | 0.9303 | 11,681 |
| Oceania | 0.9751 | 0.0256 | [0.9249, 1.0252] | 0.8233 | 272 |

**Panel D. Scaling law by country (selected)**

| Country | beta | 95% CI | R-squared | N |
|---|---:|---|---:|---:|
| China | 1.1613 | [1.1291, 1.1935] | 0.3687 | 9,481 |
| Japan | 1.1188 | [1.0972, 1.1404] | 0.8382 | 2,256 |
| Korea | 0.9424 | [0.8534, 1.0315] | 0.4103 | 609 |
| United States | 1.0655 | [1.0600, 1.0709] | 0.9303 | 11,681 |
| Germany | 1.0870 | [1.0527, 1.1213] | 0.7887 | 928 |
| France | 1.1373 | [1.1071, 1.1676] | 0.9567 | 550 |
| Australia | 0.9751 | [0.9249, 1.0252] | 0.8233 | 272 |
| South Africa | 1.0856 | [1.0210, 1.1503] | 0.7545 | 279 |

---

**Notes.**
Unified regional panel constructed from national statistical agencies and Eurostat NUTS-2 data. GDP-based MUQ = (GDP_t - GDP_{t-1}) / GFCF_t, winsorised at 1%/99% tails. For US MSAs, GFCF estimated as 21% of GDP (national average); cross-MSA MUQ variation therefore reflects GDP growth differences rather than investment allocation differences. Panel A confirms a negative association between income level and MUQ after controlling for country and year fixed effects: a 1% increase in GDP per capita is associated with a 0.043 percentage-point decrease in MUQ. Panel C reports the global scaling law beta < 1 (0.9725), indicating mild sub-linear scaling; however, substantial heterogeneity exists across continents (Asia beta = 0.46, reflecting China's city-size/GDP disconnect).
