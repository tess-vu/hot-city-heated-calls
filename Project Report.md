# 1. INTRODUCTION

## 1.1. Research Background

Extreme heat is one of the deadliest environmental hazards in the United States and, while its effects are felt by everyone, they're also felt disproportionately. In dense, urban metropolitan cities like New York, extreme temperatures interact with not just the built environment and local infrastructure conditions, but also the socioeconomic climate—extreme heat acts as one of the many architects shaping where service disruptions, complaints, and other surrounding stressors occur, degrading quality-of-life (QoL) for urbanites, suburbanites, and ruralites alike.

Within the context of this degradation is New York City's 311 service, a complaint system that accepts reports via calls, emails, and website submissions that can reflect extreme-heat induced behavior; it is a granular, real-time lens that provides understanding of how heat-related aggravation and other aspects can translate into observable, negative resident sentiment. This project in particular seeks to connect extreme heat versus normal heat weeks with environmental factors, socioeconomic conditions, and urban morphology to potentially explain QoL issues and their increases during hotter periods.

In this regard, the project is built upon geospatial data science techniques for modeling weekly QoL outcomes, as proxied by selected 311 report categories, using ordinary least squares (OLS) regression modeling as a baseline followed by modern machine learning (ML) models RandomForest (RF) and SHapley Additive exPlanations (SHAP).

## 1.2. Research Gap

While a substantial body of literature has established the correlation between rising temperatures and increased frequency of 311 service requests—specifically regarding noise, energy, and water consumption—most existing studies treat temperature as a continuous linear variable or focus on the aggregate summer season as a single period. (Hsu et al., 2021) (Harlan et al., 2006) There is a lack of research that explicitly compares the mechanisms driving QoL degradation between normal summer conditions versus extreme heat events.

Current urban research usually identifies where vulnerability exists, connecting heat exposure to socioeconomic disparities and lack of green infrastructure. (Uejio et al., 2010) However, fewer studies investigate how the influence of these environmental and urban morphology factors shifts when the thermal environment crosses into extreme thresholds.

Tranditional approaches like OLS in 311 analysis generally struggle to capture the non-linear behaviors of human-environment interactions. While machine learning offers improved predictive power, (Kontokosta & Tull, 2017) it generally lacks interpretability. So, by integrating SHAP to compare extreme versus normal heat weeks, this study addresses a critical gap, where it takes a step further from simple prediction to interpret and explain socioeconomic, environmental, and urban built drivers under two different heat regimes, of which is explained in detail in section 2. (Lundberg & Lee, 2017)

## 1.3. Research Objective

With the research gap's context, this study asks: how do environmental, socioeconomic, and urban morphology factors influence the QoL in New York City, defined as QoL-related 311 report rate per capita, during extreme heat weeks versus normal heat weeks?

Heat-related academic literature suggests that discomfort rises with temperature, so it is hypothesized that the QoL rate per capita will align with those findings. However, the objective of this research is to produce SHAP model values that can help reveal the drivers of QoL complaints in New York City.

# 2. METHODS

## 2.1. Study Area and Period

The study area is based in New York City with spatial resolution at the census tract level, with these observations during summer 2025, defined as the beginning of June through August 23rd at a weekly temporal resolution. The full month of August was not used due to recent weather data only recorded up to the 24th, therefore not providing a whole week, so it was removed from the study.

## 2.2. Data Preparation

### Heat Data

The subsequent removal of August's last week provided a total of 12 weeks in summer 2025, where extreme heat weeks were defined as at least two extreme heat days within a week with a temperature cutoff threshold at 93°F using the John F. Kennedy (JFK) weather station located at Philadelphia's international airport. This threshold was determined according to a climatological baseline from 1981 through 2010 daily max temperature with a 95th percentile, and this split the observations into two needed regimes: 17 extreme heat days and 71 normal heat days, providing 5 extreme heat weeks and 7 normal heat weeks. Data was directly downloaded from the National Oceanic and Atmospheric Administration (NOAA).

### Socioeconomic Data

Socioeconomic data was derived from the United States Census, specifically the most recent 5-year American Community Survey (ACS) in 2023. Python's `pyCensus` module provided easy access to filter the data down to main investigative, derived variables in the final table:

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

Environmental urban data were all derived from Landsat raster calculations, specifically scenes within the same study timeline, with the computation done through ArcGIS Pro. However, land-cover land-use (LULC) data was a static raster from 2024.

-   LULC Raster
    -   Percent Tree Canopy
    -   Percent Impervious Surface
-   Surface Temperature / Reflectance Raster
    -   Average Height of Buildings (AH)
    -   Building Density (BD)
    -   Normalized Difference Vegetation Index (NDVI)
    -   Water Coverage Ratio (WCR)

Other data included deriving spatial features from Python's `osmnx` module to calculate points-of-interest (POI) density utilizing a 500-meter buffer and mean Euclidean distance to the nearest subway of census tract centroids.

Justification for these variables are that quantifiable metrics of greenery such as tree canopy and NDVI, as well as water coverage, could help explore the relationship between their roles in heat mitigation and alleviating air pollution within cities, and how they could potentially affect QoL requests as a byproduct. In addition, the impervious surface can suggest high heat absorption throughout the city at high percentages, and this is the same case with the building heights and densities. While many of these environmental and urban forms may be multicollinear, the goal is striving for interpretation rather than maximizing prediction, and this helps to explore the different properties of a city.

POIs were determined as everyday main amenities, shops, leisure, and public transport categories in OpenStreet Maps (OSM) yielding 21,309 points, and are as follows:

-   Amenity
    -   library
    -   community_centre
    -   social_facility
    -   bus_station
    -   bar
    -   restaurant
    -   fast_food
    -   toilets
    -   hospital
    -   clinic
    -   pharmacy
-   Shop
    -   convenience
    -   supermarket
    -   alcohol
    -   deli
-   Leisure
    -   park
-   Public Transport
    -   station

## 2.3. OLS Regression Model

OLS regression was used as the foundational statistical model in this study because it provides an interperetable, baseline framework for understanding the linear associations between environmental, socioeconomic, urban morphology, and spatial accessibility characteristics and the dependent variable of heat-related QoL 311 complaints per capita.

Separate cross-sectional OLS models were estimated for extreme heat weeks defined as those with at least two extreme heat days, and normal heat weeks defined as those with less than two extreme heat days, with each of the 2,225 observations representing a census tract by week.

Predictors were structured into three conceptual categories, which were added incrementally to assess the added explanatory value of each predictor block: Environmental Predictors, Socioeconomic Predictors, and Urban Morphology Predictors.

**Environmental:** NDVI, percent tree canopy, percent impervious surface, and WCR.

**Socioeconomic:** Median income, poverty rate, percent renters, percent limited English, percent bachelor’s or more, and percent non-white.

**Urban Morphology:** AH, BD, distance to the nearest subway station, and 500-meter buffer POI density.

OLS provides a transparent estimation of how predictors correlate with QoL complaint rates, and coefficients can be directly interpreted and compared across extreme versus normal heat conditions, serving as an important reference model before introducing nonlinear ML approaches with Random Forest. So, given the behavioral nature of 311 complaint reporting and the noisy, high-frequency variability of QoL calls, relatively low R² values are expected in this domain, consistent with existing literature on 311 data, urban complaints, and human-environment interactions.

## 2.4. ML Model and SHAP

Stepping further to understanding QoL and heat dynamics, to complement the OLS framework, a nonlinear ML model was used to test whether environmental, socioeconomic, and urban predictors collectively produce stronger predictive power for QoL rates per capita during extreme and normal heat weeks.

In the case of this study RF, is stable on moderate-size datasets and can handle high multicollinearity and correlated predictors like this study's without requiring regularization. In addition, it is less sensitive to hyperparameter tuning and is capable of modeling nonlinear relationships and threshold behaviors associated with heat stress, as it is a popular ML model used in the environmental exposure, health, and urban prediction literature.

Like the OLS model, the RF models were trained in the extreme heat weeks and normal heat weeks with the same predictor groups for direct comparison. Then, to prevent overfitting and ensure generalizability, a 3-fold cross-validation was implemented, partitioning the tracts into an 80% train set and 20% test set, with the RF hyperparameters as follows:

-   n_estimators: `[200, 400, 600]`
-   max_depth: `[10, 20, 30]`
-   min_samples_split: `[2, 5, 10]`
-   max_samples_leaf: `[1, 2, 4]`
-   max_features: `["auto", "sqrt", 0.5]`

While OLS is useful for interpretation, extreme heat effects on QoL likely possess nonlinearity, interactions between the built environment and socioeconomic vulnerability, among others, and RF accommodates to these unique idiosyncracies, capturing behavioral and nonlinear dynamics that OLS falls short on.

Finally, SHAP was used to interpret the Random Forest predictions and quantify the contribution of each predictor to the predicted QoL complaint rate per capita. This particular methodology is well-suited for urban and environmental modeling because it, like Random Forest, can handle nonlinear, interactive relationships, but it can especially decomposes predictions into additive contributions from each predictor, providing a measure of global importance and local explanations, so this makes the two regimes of extreme heat weeks versus normal heat weeks comparable.

With this, SHAP allows identification of which environmental, socioeconomic, or urban factors become more influential during extreme heat, and whether predictors behave differently under high heat versus normal heat conditions.

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

# 5. REFERENCES

Harlan, S. L., Brazel, A. J., Prashad, L., Stefanov, W. L., & Larsen, L. (2006). Neighborhood microclimates and vulnerability to heat stress. *Social Science & Medicine*, 63(11), 2847–2863. https://doi.org/10.1016/j.socscimed.2006.07.030

Hsu, A., Sheriff, G., Chakraborty, T., & Manya, D. (2021). Disproportionate exposure to urban heat island intensity across major US cities. *Nature Communications*, 12(1). https://doi.org/10.1038/s41467-021-22799-5

Kontokosta, C. E., & Tull, C. (2017). A data-driven predictive model of city-scale energy use in buildings. *Applied Energy*, 197, 303–317. https://doi.org/10.1016/j.apenergy.2017.04.005

Lundberg, S., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *NIPS’17: Proceedings of the 31st International Conference on Neural Information Processing Systems*, 9781510860964. https://doi.org/10.5555/3295222.3295230

Uejio, C. K., Wilhelmi, O. V., Golden, J. S., Mills, D. M., Gulino, S. P., & Samenow, J. P. (2010). Intra-urban societal vulnerability to extreme heat: The role of heat exposure and the built environment, socioeconomics, and neighborhood stability. *Health & Place*, 17(2), 498–507. https://doi.org/10.1016/j.healthplace.2010.12.005