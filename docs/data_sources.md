# Data sources

## IBGE — POF 2017–2018

- Main page: https://www.ibge.gov.br/estatisticas/sociais/saude/24786-pof-2017-2018.html
- Microdata archive: `Dados_20230713.zip`, stored in browser-safe chunks.
- Documentation, translators, questionnaires and reading programs are retained in `data/raw/ibge_pof/supporting_files/`.

The OMAL extraction uses household members, housing characteristics, conditions of life, estimated rent, collective expenses, household notebooks and individual expenses.

## IBGE — IPCA

- SIDRA table 7060: https://sidra.ibge.gov.br/tabela/7060
- The repository contains both source workbooks supplied for the nine groups and the general index.

## IBGE — PNAD Contínua

- Labour income, SIDRA table 6472: https://sidra.ibge.gov.br/tabela/6472
- Informality, SIDRA table 8529: https://sidra.ibge.gov.br/tabela/8529

## DIEESE

- Basic basket methodology: https://www.dieese.org.br/metodologia/metodologiaCestaBasica2016.pdf
- The monthly nominal minimum wage and necessary minimum wage series used in the article are stored in `data/raw/dieese/`.

## Ipea

- Real minimum wage series: GAC12_SALMINRE12.
- PPP minimum wage series: GAC12_SALMINDOL12.
- Text exports are stored in `data/raw/ipea/`.

## OECD and World Bank

- OECD minimum-to-median wage ratios are retained in `data/raw/other/kaitz_brazil_oecd.xlsx`.
- World Bank 2021-PPP poverty-line values used in the article are stored in `data/processed/article/world_bank_poverty_lines_2021_ppp.csv`.
