# 1. INTRODUCTION

## 1.1. Research Background

Extreme heat is one of the deadliest environmental hazards in the United States and, while its effects are felt by everyone, they're also felt disproportionately. In dense, urban metropolitan cities like New York, extreme temperatures interact with not just the built environment and local infrastructure conditions, but also the socioeconomic climate—extreme heat acts as one of the many architects shaping where service disruptions, complaints, and other surrounding stressors occur, degrading quality-of-life (QoL) for urbanites, suburbanites, and ruralites alike.

Within the context of this degradation is New York City's 311 service, a complaint system that accepts reports via calls, emails, and website submissions that can reflect extreme-heat induced behavior; it is a granular, real-time lens that provides understanding of how heat-related aggravation and other aspects can translate into observable, negative resident sentiment. This project in particular seeks to connect extreme heat versus normal heat weeks with environmental factors, socioeconomic conditions, and urban morphology to potentially explain QoL issues and their increases during hotter periods.

In this regard, the project is built upon geospatial data science techniques for modeling weekly QoL outcomes, as proxied by selected 311 report categories, using ordinary least squares (OLS) regression modeling as a baseline followed by modern machine learning (ML) models RandomForest (RF) and SHapley Additive exPlanations (SHAP).

## 1.2. Research Gap

few studies compare the mechanism difference between extreme heat day and regular heat day

## 1.3. Research Objective

With the research gap's context, this paper asks: how do environmental, socioeconomic, and urban morphology factors influence the QoL in New York City, defined as QoL-related 311 report rate per capita, during extreme heat weeks versus normal heat weeks?

Heat-related academic literature suggests that discomfort rises with temperature, so it is hypothesized that the QoL rate per capita will align with those findings. However, the objective of this research is to produce SHAP model values that can help reveal the drivers of QoL complaints in New York City.

# 2. METHODS

## 2.1. Study Area and Period

The study area is based in New York City with spatial resolution at the census tract level, with these observations during summer 2025, defined as the beginning of June through August 23rd at a weekly temporal resolution. The full month of August was not used due to recent weather data only recorded up to the 24th, therefore not providing a whole week, so it was removed from the study.

## 2.2. Data Preparation

### Heat Data

The subsequent removal of August's last week provided a total of 12 weeks in summer 2025, where extreme heat weeks were defined as at least two extreme heat days within a week with a temperature cutoff threshold at 93°F using the John F. Kennedy (JFK) weather station located at Philadelphia's international airport. This threshold was determined according to a climatological baseline from 1981 through 2010 daily max temperature with a 95th percentile, and this split the observations between 17 extreme heat days and 71 normal heat days, providing 5 extreme heat weeks and 7 normal heat weeks. Data was directly downloaded from the National Oceanic and Atmospheric Administration (NOAA).

### Socioeconomic Data

Socioeconomic data was derived from the United States Census, specifically the most recent 5-year American Community Survey (ACS) in 2023. The pyCensus module provided easy access to filter the data down to main investigative, derived variables in the final table:

-   Percent Bachelor's or More (B15003_022E / B15003_001E)

    -   Bachelor's or More / Education Total

-   Percent Renters (B25003_003E / B25003_001E)

    -   Renter Count / Household Total

-   Percent Limited English Speakers (B16005_007E / B16005_001E)

    -   Limited English Speaker Count / Household Total

-   Median Household Income (B19013_001E)

-   Poverty Rate (B17001_002E / B17001_001E)

    -   Poverty Count / Total Whom Poverty Status is Recorded

-   Percent Non-White (1 - B02001_002E / B01003_001E)

    -   (1 - White Count / Total Population)

Justifications for these variables highlight socioeconomic issues and how heat-related issues disproportionately affect different communities as well as how different communities interact with public services like New York City's 311. Educated and higher-income individuals may know how to navigate what their cities offer, limited English speakers may have more barriers accessing 311 services, renters may face more infrastructural issues compared to owners,

### Environmental and Urban Data

Environmental uruban data were all derived from Landsat raster calculations, specifically scenes within the same study timeline, with the computation done through ArcGIS Pro. However, land-cover land-use (LULC) data was a static raster from 2024.

-   LULC Raster

    -   Percent Tree Canopy

    -   Percent Impervious Surface

-   Surface Temperature / Reflectance Raster

    -   Average Height of Buildings (AH)

    -   Building Density (BD)

    -   Normalized Difference Vegetation Index (NDVI)

    -   Water Coverage Ratio (WCR)

Other data included deriving spatial features from Python's osmnx module to calculate points-of-interest (POI) density utilizing a 500-meter buffer and mean Euclidean distance to the nearest subway of census tract centroids.

## 2.3. OLS Regression Model

## 2.4. ML Model and SHAP

# 3. RESULTS

## 3.1. Exploratory Data Analysis

## 3.2. OLS Model Results

### Extreme Heat Model

### Normal Heat Model

## 3.3. ML and SHAP Results

### Extreme Heat Model

### Normal Heat Model

# 4. DISCUSSION

Results, and discuss about why the mechanism might be different and study limitations.
