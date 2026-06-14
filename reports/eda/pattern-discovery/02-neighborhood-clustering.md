# Neighborhood Clustering by Crime Profile

**Topic:** relational | **Tag:** clustering | **Difficulty:** ●●●○○

## Question
Can districts be grouped into clusters based on their crime profiles?

## Data
Tables: `fact_crime`, `dim_location`, `dim_offense`
Filters: 25 districts, 10 crime type features

## Finding
Districts cluster into 4 distinct crime archetypes based on type mix and arrest rates. Cluster 1 (high-volume, low-arrest) represents south-side districts; Cluster 2 (balanced) represents north-side districts.

## Evidence
K-means clustering (k=4) on standardized crime type distributions. Scatter plot of first two principal components shows clear separation of clusters.

## Methodology Note
K-means (k=4, random_state=42, n_init=10) was chosen for interpretability. Limitations include sensitivity to scaling (StandardScaler applied) and assumption of spherical clusters. Alternatives: HDBSCAN for density-based clusters without requiring k, or Gaussian Mixture Models for probabilistic cluster membership. An elbow plot (not shown) confirmed k=4 as a reasonable choice based on inertia.

## Caveat
K=4 is chosen for interpretability. Different k values may reveal different structures. Synthetic data limits generalizability.

## Notebook
Section 7.2 — `scripts/notebooks/M7_EDA.ipynb`
