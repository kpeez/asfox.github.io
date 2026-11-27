---
title: "What is a genetic correlation?"
date: 2013-04-24
kind: "tutorial"
summary: "An explanation of the genetic correlation: how the correlation between two traits can be split into genetic and environmental parts, and how heritability and bivariate heritability are estimated."
legacy:
  - "/what-is-a-genetic-correlation.html"
---

Much of what we do as affective and social scientists is correlational. It's funny that we rarely think about the *source* of our correlations. We often think about the genetic or environmental effects on traits that we study, but rarely consider these influences on our favorite correlations. The genetic correlation is an estimate of the additive genetic effect that is shared between our pair of traits. For example, self-reported mood and physiological reactivity could both be heritable, but their genetic correlation can tell you if they are likely to share the same genes.

It is interesting to think about source of the correlation between two phenotypic traits. In particular, you could consider the correlation between two variables as the sum of the genetic and environmental contributions to these effects.

> $$
> \rho = \rho_g + \rho_e
> $$

Using the framework for estimating heritability, we can estimate the genetic heritability for two variables.

## What is shared heritability?

Even when you can show that variables $X$ (e.g. height) and $Y$ (e.g. eye-color) are heritable in the same population, this obviously does not imply that they rely on the same genes. It could be that these two traits are passed on by different sets of genes, such that while you inherit your mother's height, your sibling might inherit her eye-color. To determine if two traits are likely to share the same genes you can compute the genetic heritability ($\rho_g$). The genetic heritability examines if these two variables (e.g. height and eye-color) fall through the family tree in the same way, for example if you inherit your mother's height you are also likely to inherit her eye-color. Some traits, e.g. height and eye-color, are likely to depend on different genes, while others, e.g. height and weight, are likely to depend on many overlapping genes. Importantly, for many moderately correlated individual differences that we study as affective and social scientists, the genetic correlation could go either way – we don't often consider whether our correlations arise from similar genetic dependence.

## Computing heritability (h<sup>2</sup>)

First some background. In order to compute the genetic correlation you need to examine the heritability of two traits.

To estimate the heritability of a single trait, you must first compute the trait's covariance matrix, which we will call $\Omega$, where location $i,j$ in the matrix is filled with the covariance in X between subject $i$ and subject $j$

> $$
> \Omega_X = Cov[X,X] = \begin{bmatrix} cov(X_1,X_1) & cov(X_1,X_2) & \cdots & cov(X_1,X_n) \\ cov(X_2,X_1) & cov(X_2,X_2) & ... & cov(X_2,X_n) \\ \vdots & \vdots & \ddots & \vdots \\ cov(X_1,X_n) & cov(X_2,X_n) & \cdots & cov(X_n,X_n) \end{bmatrix}
> $$
>
> Where covariance is defined as:
>
> $$
> cov[X_i, X_j] = E[(X_i - E[X_i]) (X_j - E[X_j])]
> $$
>
> Where, at least in this case, the expectation can be defined as:
>
> $$
> E[X] = \mu(X) = \frac{1}{N} \sum_{i=1:N} X_i
> $$

Similarly, you can compute a similar *kinship matrix* ($\Phi$) where location $i,j$ represents i-j's relationship ($r_{ij}$) as the probability that any given gene is identical by descent (IBD).

> $\Phi$ can be computed based on the pedigree, as:
>
> $$
> \Phi = \frac{1}{2}R
> $$
>
> where R is the matrix of each pair of animals' relationship to each other, with the $r$ for a parent and a child $.5 = (2^{-1})$, $r$ for siblings $.5 = (2^{-2}+2^{-2})$, and so on according to the table below, and beyond.

| r | relationship | degree of relationship |
| :---: | --- | --- |
| 100% | identical twins; clones | 0 |
| 50% | parent-offspring | 1 |
| 50% | full siblings | 2 |
| 37.5% | 3/4 siblings or sibling cousins | 2 |
| 25% | grandparent-grandchild | 2 |
| 25% | half siblings | 2 |
| 25% | aunt/uncle-nephew/niece | 3 |
| 25% | double first cousins | 4 |
| 12.5% | great grandparent-great grandchild | 3 |
| 12.5% | first cousins | 4 |
| 12.5% | quadruple second cousins | 6 |
| 9.38% | triple second cousins | 6 |
| 6.25% | half-first cousins | 4 |
| 6.25% | first cousins once removed | 5 |
| 6.25% | double second cousins | 6 |
| 3.13% | second cousins | 6 |
| 0.78% | third cousins | 8 |
| 0.20% | fourth cousins | 10 |

Once you have these two matrices, you can estimate the putatively genetic and environmental variance of a quantitative phenotypic trait in the form:

> $$
> \Omega \;\approxeq\; 2\Phi \sigma^2_g + I_n \sigma^2_e
> $$

Where

> $\Omega$ is the covariance matrix of the phenotype
>
> $\Phi$ is the n x n kinship matrix for the pedigree
>
> $\sigma^2_g$ is the variance in the trait due to additive genetic ($g$) effects
>
> $I_n$ is the n x n identity matrix
>
> $\sigma^2_e$ is the variance due to unmeasured random effects, presumably environmental ($e$)

It is worth noting that the variance attributed to the environment in this mode, is considered to be random for each subject, and not shared between subjects.

The variance parameters ($\sigma$) can be estimated by maximizing the likelihood function:

> $$
> {\cal L}( \sigma^2_g, \sigma^2_e \;\vert\; y ) = -\frac{n}{2}\ln(2\eta) - \frac{1}{2}\ln(\Omega) - \frac{1}{2}(x-\mu_X)\Omega^{-1}(X-\mu_X)
> $$
>
> $\eta$ is ??? The three parts of this function are: a constant (under the assumption of normality), the genetic and environmental components, and the mean.

After estimating this model, the heritability ($h^2$) can be estimated based on the variance in genetic and environmental effects, by calculating:

> $$
> h^2 = \frac{\sigma^2_g}{(\sigma^2_g + \sigma ^2_e)}
> $$

Computing the probability of this heritability and is computed by comparing the log likelihood of the model above and the difference between this model and another where $\sigma^2_g$ is constrained to equal 0.

$$
\chi^2_1[\sigma^2_g] = -2{\cal L}_{\sigma^2_g=0} + 2{\cal L}
$$

## Computing bivariate heritability & genetic correlations

Now that we know how to estimate heritability, we can move on to estimate bivariate heritability.

We can do this by essentially concatenating traits X and Y, along with their interactions. More specifically,

> $$
> \Omega_B = \begin{bmatrix} \Omega_X & \Omega_{YX} \\ \Omega_{XY} & \Omega_Y \end{bmatrix}
> $$
>
> Where $\Omega_X$ and $\Omega_Y$ are as $\Omega$ above, and the bivariate portions are:
>
> $$
> \Omega_{XY} \;\approxeq\; 2\Phi\sigma^2_{g_{XY}} + I_n\sigma^2_{e_{XY}}
> $$
>
> with $\phi$ defined as before, and the variance of $X,Y$ can be decomposed to its component parts:
>
> $$
> \sigma^2_{XY} = \sigma_X\sigma_Y\rho_{XY}
> $$
>
> where $\rho_{g_{XY}}$ is the genetic correlation, that we have set out to estimate.

This can now be estimated using the same maximum likelihood estimation we discussed above:

> $$
> \begin{align} {\cal L}( \sigma^2_{g_{X}}, \sigma^2_{e_{X}}, \sigma^2_{g_{Y}}, \sigma^2_{e_{Y}}, \rho_{e_{XY}} \;\vert\; X, Y ) = &- n \ln(2\eta) -\frac{1}{2}\ln\lvert\Omega_B\rvert \\ & -\frac{1}{2}\biggl({X \brack Y}-\mu_{X \brack Y}\biggr)\Omega^{-1}\biggl({X \brack Y}-\mu_{X \brack Y}\biggr) \end{align}
> $$
>
> As before, the three parts of this function are: a distribution parameter (now for bivariate normal), the genetic and environmental components (now including a mean), and the mean.

Similar to the test above, the p-values for $\rho$s can be computed by estimating the same model with $\rho = 0$.

$$
\chi^2_1[\rho_g] = -2{\cal L}_{\rho_g=0} + 2{\cal L}
$$

## Asides

- This technique is extensible to inclusion of covariates, which may contribute to $E[X]$. Ideally, these should be non-heritable factors such as Age. For example, we could define $E[X]$ using a linear model.

  > $$
  > E[X] = c\beta_0 + W_X\beta_X
  > $$
  >
  > where $W_X$ is an arbitrary design matrix similar to what we would use in standard regression analyses.

- It is important to consider that you can find high $\rho$ values in traits with extremely low $h^2$ values. Therefore, it can be informative to estimate the total phenotypic $\rho$ by modulating $\rho_g$ and $\rho_e$ by the $h^2$ estimates. This can give you an idea of how much variance in your traits is *really* explained by the genetic correlation.

  > $$
  > \rho = \sqrt{h^2_X}*\sqrt{h^2_Y}*\rho_g + \sqrt{1-h^2_X} * \sqrt{1-h^2_Y} * \rho_e
  > $$

## References:

Almasy L, Dyer TD, and Blangero J (1997). [Bivariate Quantitative Trait Linkage Analysis: Pleiotropy Versus Co-incident Linkages.](http://www.ncbi.nlm.nih.gov/pubmed/9433606) *Genetic Epidemiology 14:953-958*

Almasy L, Blangero J (1998). [Multipoint quantitative-trait linkage analysis in general pedigrees.](http://www.ncbi.nlm.nih.gov/pubmed/9545414) *Am J Hum Genet. 62(5):1198-211*

Williams JT, Van Eerdewegh P, Almasy L, Blangero J (1999). [Joint multipoint linkage analysis of multivariate qualitative and quantitative traits. I. Likelihood formulation and simulation results.](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1288247/) *American journal of human genetics 65(4):1134*

To learn more, check out work by [John Blangero](http://scholar.google.com/citations?user=b4zuw-IAAAAJ&h) and his team.
