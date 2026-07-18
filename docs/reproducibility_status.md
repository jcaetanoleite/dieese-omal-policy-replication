# Reproducibility status

## Fully reproducible from raw inputs

- POF reference-sample construction.
- Mapping POF expenses to nine IPCA groups.
- Local IPCA extraction from included parsed extracts; strict raw-workbook parsing is available with `--mode strict-raw`.
- OMAL monthly series, household types and comparisons.
- OMAL figures 15–22.
- Article assembly from figures and text.

## Reproducible from included processed inputs

- Long-run minimum-wage figures.
- Food-expenditure-share figure.
- State income comparison.
- Regional labour-income panels.
- Informality scatterplot.
- Kaitz and OECD comparisons.
- PPP poverty-line comparison.

## Archived exact outputs

The exact PNGs used in the final editorial article are stored as `outputs/figures/figure01.png` through `figure22.png`. Regenerated versions of figures 1–14 receive the suffix `_regenerated.png`, preventing an automated run from overwriting the archived publication versions.
