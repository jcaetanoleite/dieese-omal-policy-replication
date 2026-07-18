# Is the DIEESE minimum wage useful for policy?

Replication package for an empirical and methodological assessment of the Brazilian DIEESE **necessary minimum wage**, together with the construction of the **OMAL — Local Adequate Minimum Budget**.

The repository contains the public inputs, processed data, Python code, figures, tables and final English article required to reproduce the results. The central argument is that the DIEESE series remains useful as a bargaining benchmark, but is not a representative estimate of household need and should not be used as an automatic target for the statutory minimum wage. OMAL provides a more explicit alternative: a local family reference budget estimated from the POF, updated with all nine local IPCA groups and reported separately by household type.

## Main outputs

- `outputs/article/Is_the_DIEESE_minimum_wage_useful_for_policy_editorial_v2.docx`
- `outputs/article/Is_the_DIEESE_minimum_wage_useful_for_policy_editorial_v2.md`
- `outputs/tables/OMAL_indicador_9_grupos_IPCA_2020_2026.xlsx`
- `outputs/figures/figure01.png` through `outputs/figures/figure22.png`

## What OMAL is

OMAL is a **local household reference budget**. It estimates the monthly private expenditure associated with a modest but materially adequate urban consumption pattern for a specified household type, in a specified city and month.

The word *adequate* has a precise operational meaning in this project. The POF reference group is restricted to households that:

- are classified as food secure;
- report no arrears on rent, mortgage or basic utility bills;
- report no severe food-deprivation episodes; and
- lie between the weighted 30th and 60th percentiles of equivalised disposable income.

OMAL therefore does not reproduce the consumption of the poorest households, since observed expenditure at the bottom can reflect deprivation rather than need. It also excludes affluent households whose spending would turn the indicator into a middle- or upper-income consumption standard. The estimate is anchored in the weighted expenditure patterns of households that are neither plainly deprived nor affluent.

OMAL is calculated separately for six household structures:

- one adult;
- one adult and one child;
- one adult and two children;
- two adults;
- two adults and one child; and
- two adults and two children.

Two versions are reported:

- **Core OMAL:** recurring food, housing, clothing, transport, health, hygiene, education and communication expenditure.
- **Expanded OMAL:** the core basket plus household articles, recreation, personal services, miscellaneous expenses and occasional travel. Vehicle acquisition remains excluded.

The result is a **household budget**, not an individual wage. Required income per worker is derived only after specifying the number of earners in the household.

## What OMAL is not

OMAL should not be described as the minimum amount required to survive. It is not:

- a biological subsistence threshold;
- a calorie-based food line;
- an official poverty line;
- a measure of the absolute minimum compatible with physical survival;
- a guarantee that every household above the threshold enjoys an adequate standard of living;
- a complete valuation of publicly provided health, education, transport or housing services;
- a legal recommendation for the statutory minimum wage; or
- an estimate of the wage that a single worker must necessarily earn.

A survival threshold would ask how little a person can consume while remaining alive. OMAL asks a different question: **what monthly private budget is associated with a modest, non-deprived pattern of urban household consumption, after accounting for city, household composition and local price changes?**

This distinction matters. The indicator contains normative choices about the reference group, equivalence scale and included expenditure categories. Those choices are documented and can be changed in sensitivity analyses. OMAL is best used as a diagnostic and comparative reference, not as an immutable welfare standard.

## How OMAL is constructed

For city `c`, household type `h`, expenditure group `g`, basket variant `v` and month `t`:

```latex
OMAL_{c,h,t,v}
=
AE_h
\sum_{g=1}^{9}
\widehat{B}_{c,g,v,2018}
\times
Bridge_{2018\rightarrow2019}
\times
IPCA_{c,g,t}
```

where:

- `AE_h` is the adult-equivalent size of household type `h`;
- `B-hat_{c,g,v,2018}` is the partially pooled monthly expenditure per adult equivalent estimated from the POF reference sample;
- `Bridge_{2018→2019}` moves the POF price base to the start of the local monthly IPCA series; and
- `IPCA_{c,g,t}` is the cumulative local price update for the relevant expenditure group.

### Household equivalence scale

The modified OECD scale is used:

```latex
AE_h = 1 + 0.5(A_h-1) + 0.3C_h
```

The first adult receives weight 1, each additional adult 0.5 and each child under 14 receives 0.3. A household with two adults and two children therefore has `AE = 2.1`.

### Expenditure per adult equivalent

For consumption unit `i`, group `g` and variant `v`:

```latex
b_{i,g,v}
=
\frac{MonthlyExpense_{i,g,v}}{AE_i}
```

POF expenditure records are converted to monthly values using their reference periods and annualisation factors. Estimated rent is included so that owner-occupied and rented housing are compared through a common housing-service measure.

### Partial pooling

Small city samples can generate unstable weighted medians. City estimates are therefore shrunk toward the corresponding regional estimate:

```latex
\widehat{B}_{c,g,v}
=
\lambda_c B_{c,g,v}
+
(1-\lambda_c)B_{r(c),g,v}
```

with:

```latex
\lambda_c
=
\frac{n^{eff}_c}{n^{eff}_c+80}
```

and effective sample size:

```latex
n^{eff}_c
=
\frac{\left(\sum_i w_i\right)^2}{\sum_i w_i^2}
```

Large and well-balanced city samples receive more weight. Small or highly unequal weighted samples are pulled more strongly toward their regional benchmark.

### Price updating

Each POF component is updated with the corresponding local IPCA group:

1. Food and beverages
2. Housing
3. Household articles
4. Clothing
5. Transport
6. Health and personal care
7. Personal expenses
8. Education
9. Communication

For monthly percentage change `pi_{c,g,s}`:

```latex
IPCA_{c,g,t}
=
\prod_{s=2020m1}^{t}
\left(1+\frac{\pi_{c,g,s}}{100}\right)
```

The bridge between the POF period and December 2019 is:

```latex
Bridge_{2018\rightarrow2019}
=
(1+0.0375)(1+0.0431)
```

### Income required per worker

For `N_h` equivalent full-time workers:

```latex
RequiredIncome_{c,h,t,v}(N_h)
=
\frac{OMAL_{c,h,t,v}}{N_h}
```

This conversion is intentionally separate from the household budget. A two-worker household and a one-worker household with the same composition do not imply the same required wage per worker.

## Appropriate uses

OMAL can be used to:

- compare the structure and evolution of private household budgets across cities;
- examine how food, housing, transport and other components contribute to local budget pressure;
- compare household reference budgets with local earnings distributions;
- test alternative equivalence scales, reference groups and basket definitions;
- provide context for wage bargaining and social-policy analysis; and
- study how far a legal wage floor sits from different household-budget scenarios.

It should not be used mechanically to set the statutory minimum wage. Wage policy must also consider the Kaitz ratio, employment, hours, compliance, informality, productivity, prices, fiscal indexation and the distribution of earners across households.

More detail is available in [`docs/methodology.md`](docs/methodology.md).

## Repository structure

```text
.
├── data/
│   ├── raw/             Original third-party inputs and browser-safe file chunks
│   ├── interim/         Parsed PNAD, IPCA and informality files
│   └── processed/       Canonical article and OMAL datasets
├── docs/                Methodology, codebook, sources and upload instructions
├── outputs/
│   ├── article/         Final DOCX and Markdown article
│   ├── figures/         Figures 1–22 in article order
│   └── tables/          Final spreadsheets
├── src/                 Python replication scripts
├── tests/               Output and file-integrity tests
├── run_all.py           Python-only pipeline runner
└── requirements.txt
```

## Quick reproduction

The quick mode uses the included processed datasets and rebuilds the figures and article:

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run_all.py --mode quick
```

On macOS or Linux, replace `.venv\Scripts\python` with `.venv/bin/python`.

## Full reproduction from raw data

The full mode reassembles the large source files, extracts the POF reference sample, uses the included parsed IPCA extracts, prepares PNAD income data, rebuilds OMAL and recreates the article:

```text
python run_all.py --mode full
```

For a strict parse of the original large IPCA workbooks, use:

```text
python run_all.py --mode strict-raw
```

The strict IPCA step streams more than three million spreadsheet rows and can take several minutes.

The first step reconstructs two files stored as 8 MiB chunks:

- `Dados_20230713.zip`, the POF 2017–2018 microdata archive;
- `tabela7060_20.xlsx`, the second IPCA workbook.

No Git, Git LFS, shell script or command-line file upload is required. The chunking exists solely so the repository can be uploaded through the GitHub website, where each browser-uploaded file must remain below 25 MiB.

## Data sources

- IBGE, POF 2017–2018 microdata and documentation.
- IBGE, IPCA SIDRA table 7060, including all nine groups by area.
- IBGE, PNAD Contínua SIDRA table 6472 for labour income.
- IBGE, PNAD Contínua SIDRA table 8529 for informality.
- DIEESE, national basic food basket and necessary minimum wage series.
- Ipea, real and PPP minimum-wage series.
- OECD, minimum-to-median wage ratios.
- World Bank, 2021-PPP international poverty lines.

See [`docs/data_sources.md`](docs/data_sources.md) for source notes and URLs.

## Reproducibility scope

Figures 15–22 and the OMAL tables are rebuilt directly from the included processed data. Figures 1–14 can also be regenerated with `src/make_article_figures_01_14.py`. The exact publication PNGs are retained in `outputs/figures/` so users can distinguish a computationally equivalent regeneration from the final editorial rendering.

## Citation

Please cite:

> Leite, João Gabriel Caetano. 2026. *DIEESE Necessary Minimum Wage and OMAL: Replication Package*, version 1.0.1.

A machine-readable citation is available in `CITATION.cff`.

## License

This repository uses separate licenses for software, original project content and third-party data.

### Software

Source code in `src/`, `tests/`, `run_all.py` and `.github/workflows/` is licensed under the MIT License. See [`LICENSE`](LICENSE).

### Documentation and original derived outputs

Original documentation, article text, figures, tables and derived datasets are licensed under the Creative Commons Attribution 4.0 International License, to the extent that the repository author is legally entitled to license them. See [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md).

### Third-party data

Raw data and documentation obtained from IBGE, Ipea, DIEESE, the World Bank, the OECD and other providers are not relicensed by this repository. They remain subject to the terms, licenses and citation requirements of their original providers. See [`THIRD_PARTY_DATA.md`](THIRD_PARTY_DATA.md) and [`data/raw/README.md`](data/raw/README.md).


## Browser upload

For step-by-step browser upload instructions in Portuguese, see [`docs/UPLOAD_VIA_GITHUB_PTBR.md`](docs/UPLOAD_VIA_GITHUB_PTBR.md). The repository is distributed in eight browser-safe batches.
