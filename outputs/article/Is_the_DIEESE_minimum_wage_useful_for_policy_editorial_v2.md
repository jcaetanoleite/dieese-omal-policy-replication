# Is the DIEESE minimum wage useful for policy?

*DIEESE gave Brazilian workers an independent economic vocabulary. Its “necessary minimum wage” remains useful in bargaining, but the formula is too rigid to measure household need and too detached from labour-market evidence to guide the statutory wage floor.*

The complete editorial revision, formulas, citations and figures are contained in the DOCX. The markdown companion reproduces the OMAL construction formulas and links the final figures.

## OMAL formulas

$$AE_h = 1 + 0.5(A_h-1) + 0.3C_h$$

$$y_h^{eq} = \frac{Y_h^{disp}}{AE_h}$$

$$\mathcal{R}=\{h:FS_h=1,\;ARR_h=0,\;q_{0.30}\le y_h^{eq}\le q_{0.60}\}$$

$$X_{hg}^{m}=\sum_{j\in g}\frac{x_{hj}}{m_j}$$

$$\widehat b_{cgv}=\arg\min_b\sum_{h\in\mathcal{R}_c}w_h\left|\frac{X_{hgv}^{m}}{AE_h}-b\right|$$

$$n_{eff,c}=\frac{\left(\sum_h w_h\right)^2}{\sum_h w_h^2}$$

$$\widetilde b_{cgv}=\lambda_c\widehat b_{cgv}+(1-\lambda_c)\widehat b_{rgv},\qquad \lambda_c=\frac{n_{eff,c}}{n_{eff,c}+80}$$

$$P_{cgt}=\prod_{\tau=2020m1}^{t}\left(1+\frac{\pi_{cg\tau}}{100}\right)$$

$$OMAL_{cht}^{v}=AE_h\sum_{g=1}^{9}\widetilde b_{cgv}\times 1.08221625\times P_{cgt}$$

$$W_{cht}^{net}(n)=\frac{OMAL_{cht}^{v}}{n}$$

$$R_{cht}^{MW}(n)=\frac{W_{cht}^{net}(n)}{MW_t},\qquad R_{cht}^{DIEESE}=\frac{OMAL_{cht}^{v}}{SMN_t}$$

## OMAL figures

![Figure 15](figures/figure15.png)

![Figure 16](figures/figure16.png)

![Figure 17](figures/figure17.png)

![Figure 18](figures/figure18.png)

![Figure 19](figures/figure19.png)

![Figure 20](figures/figure20.png)

![Figure 21](figures/figure21.png)

![Figure 22](figures/figure22.png)
