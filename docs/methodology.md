# Methodology

## 1. Research problem

The DIEESE necessary minimum wage converts the cost of the most expensive basic food basket into a total household budget. The formula is:

```latex
SMN_t = \frac{3C_t^{max}}{0.3571}
```

`C_t^{max}` is the most expensive city basket in month `t`. The multiplier of three represents two adults and two children as three adult food baskets. The denominator assumes that food represents 35.71 per cent of the household budget.

The article treats this as a transparent bargaining benchmark rather than a representative needs standard. The empirical objections concern the fixed household structure, the old food coefficient, the use of the highest observed city cost and the mismatch between a family budget and an individual legal wage.

## 2. OMAL concept

OMAL is a monthly **local household reference budget**, not an individual wage and not a survival threshold. It estimates the private expenditure associated with a modest, non-deprived urban consumption pattern for a specified household type, city and month.

The term *adequate* is operational rather than biological. The indicator does not estimate the smallest amount required to remain alive, a calorie-based subsistence line or an official poverty threshold. It is anchored in the observed expenditure patterns of POF households that are food secure, do not report severe food deprivation or arrears on basic housing and utility obligations, and fall between the weighted 30th and 60th percentiles of equivalised disposable income. This prevents the benchmark from reproducing either severe deprivation or affluent consumption.

OMAL covers private household expenditure under the public-service arrangements observed in the data. It does not fully value in-kind access to public health, education, transport or housing. It should therefore be interpreted as a transparent reference budget for comparative and diagnostic use, not as a complete welfare measure or an automatic minimum-wage recommendation.

It is estimated by city and household composition. Required income per worker is derived only after specifying the number of workers in the household.

For city `c`, household type `h`, group `g` and month `t`:

```latex
OMAL_{c,h,t}
=
AE_h
\sum_{g=1}^{9}
\widehat{B}_{c,g,2018}
\times
Bridge_{2018\rightarrow2019}
\times
IPCA_{c,g,t}
```

The nine expenditure groups are:

1. Food and beverages
2. Housing
3. Household articles
4. Clothing
5. Transport
6. Health and personal care
7. Personal expenses
8. Education
9. Communication

## 3. Household equivalence scale

The modified OECD scale is used:

```latex
AE_h = 1 + 0.5(A_h-1) + 0.3C_h
```

The first adult receives weight 1, additional adults 0.5 and children under 14 receive 0.3. A household with two adults and two children therefore has `AE = 2.1`.

## 4. POF reference sample

The POF reference group contains consumption units that:

- are classified as food secure;
- report no arrears on rent, mortgage or basic utility bills;
- report no severe food-deprivation episodes;
- lie between the weighted 30th and 60th percentiles of equivalised disposable income.

This choice does not eliminate normative judgment. It prevents the reference budget from mechanically reproducing either severe deprivation or affluent consumption.

## 5. Monthly expenditure construction

POF expense records are converted to monthly values using their annualisation factors and reference periods. The analysis includes estimated rent so that owner-occupied and rented housing are compared on a common service-flow basis.

For consumption unit `i`, expenditure group `g` and variant `v`:

```latex
b_{i,g,v}
=
\frac{MonthlyExpense_{i,g,v}}{AE_i}
```

The core basket includes recurring food, housing, clothing, transport, health, hygiene, education and communication expenditures. The expanded basket additionally includes household articles, recreation, personal services, miscellaneous expenses and occasional travel. Vehicle acquisition remains excluded.

## 6. Partial pooling across cities and regions

Small city samples can produce unstable weighted medians. City estimates are therefore shrunk toward their regional estimate:

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
\frac{n^{eff}_c}{n^{eff}_c + 80}
```

The effective sample size is:

```latex
n^{eff}_c
=
\frac{\left(\sum_i w_i\right)^2}{\sum_i w_i^2}
```

Large, well-balanced city samples receive more weight. Small or highly unequal weighted samples are pulled more strongly toward their regional benchmark.

## 7. Price updating

Each POF component is updated with its corresponding local IPCA group. For monthly percentage change `π_{c,g,s}`:

```latex
IPCA_{c,g,t}
=
\prod_{s=2020m1}^{t}
\left(1+\frac{\pi_{c,g,s}}{100}\right)
```

A bridge based on national IPCA inflation in 2018 and 2019 places the POF base near December 2019 prices before the local monthly series begins:

```latex
Bridge_{2018\rightarrow2019}
=
(1+0.0375)(1+0.0431)
```

## 8. Required income per worker

For `N_h` equivalent full-time workers:

```latex
RequiredIncome_{c,h,t}(N_h)
=
\frac{OMAL_{c,h,t}}{N_h}
```

The article presents one-worker and two-worker scenarios. This conversion is deliberately separate from the household budget itself.

## 9. Comparisons

The repository compares OMAL with:

- the statutory minimum wage;
- the DIEESE family benchmark;
- mean labour income in PNAD Contínua;
- the Kaitz ratio;
- informality rates;
- international poverty lines expressed in 2021 PPP dollars.

These comparisons answer different questions and are not treated as interchangeable policy rules.

## 10. Limitations

- The POF refers to 2017–2018 expenditure patterns.
- Local price updating uses IPCA groups rather than every item or subitem.
- Public provision of health, education and transport is not modelled as a city-specific in-kind transfer.
- Small city samples remain uncertain even after partial pooling.
- OMAL is a reference budget, not a biological survival threshold, an official poverty line or an optimal minimum-wage rule.
