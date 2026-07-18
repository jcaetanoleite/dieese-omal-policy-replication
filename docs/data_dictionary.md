# Data dictionary

## `omal_fullgroups_pof_base.csv`

| Variable | Description |
|---|---|
| `city` | OMAL city or urban area |
| `region` | Brazilian macro-region |
| `variant` | `core` or `expanded` basket |
| `sample_n` | Trimmed city reference-sample count |
| `effective_n` | Effective weighted sample size |
| `shrinkage_city_weight` | City weight in partial pooling |
| `income_band_low` | Weighted 30th percentile of equivalised disposable income |
| `income_band_high` | Weighted 60th percentile |
| `base_total_per_ae_2018` | POF monthly budget per adult equivalent |
| `share_g1_food` … `share_g9_communication` | Group expenditure shares |

## `ipca_all_groups_city_monthly.csv`

| Variable | Description |
|---|---|
| `city` | City/area label |
| `territory` | Original SIDRA territory label |
| `category` | IPCA group label |
| `group_key` | Internal OMAL group identifier |
| `date` | Month |
| `monthly_change_pct` | Monthly IPCA change in percent |
| `cum_index` | Cumulative price index from January 2020 |

## `omal_fullgroups_monthly_2020_2026.csv`

Contains city, region, basket variant, month, standard household type, equivalence scale, nine expenditure components, OMAL total and POF sample diagnostics.

## `omal_fullgroups_latest_household_types.csv`

Adds six household types, one- and two-worker required income, statutory minimum-wage multiples, DIEESE comparison and latest PNAD labour income.

## `informality_dieese_ratio_state_quarter.csv`

State-quarter panel with informality, average real labour income, the per-person DIEESE benchmark and their ratio.
