---
editor_options: 
  markdown: 
    wrap: 72
---

# Heat and Block Group-Level Urban Livability in Philadelphia

## Goal, Research, and Hypotheses

**GOAL:** Estimate how heat exposure changes urban livability—proxied by
the percentage of quality-of-life (QoL)-related 311
complaints—controlling for socioeconomic, built-infrastructure, and
environmental conditions across Philadelphia neighborhoods.

**QUESTION:** How does heat exposure influence urban livability—as
reflected in the proportion of QoL-related 311 service requests—across
neighborhoods in Philadelphia, Pennsylvania, after accounting for
socioeconomic, built-infrastructure, and environmental conditions?

-   Are some neighborhoods (e.g., hotter, lower-income, less green, more
    impervious) more sensitive to extreme heat in terms of 311 complaint
    activity?

-   Which neighborhood characteristics amplify or buffer the effects of
    heat on perceived livability?

-   **Hypothesis 1:** Days with abnormally high heat will exhibit a
    higher percentage of quality-of-life-related 311 complaints compared
    with normal-heat weeks, controlling for other factors.

-   **Hypothesis 2:** Neighborhoods with greater tree canopy or higher
    NDVI will show a smaller increase in QoL-related complaints during
    hot periods, whereas areas with higher impervious surface will show
    a larger increase.

-   **Hypothesis 3:** The relationship between heat and QoL-related 311
    complaints will vary by neighborhood socioeconomic status.

    -   Affluent areas may have increased reports due to bandwidth for
        higher civic engagement, lower tolerance for discomfort, and
        more knowledge on how to navigate the city services.

    -   Vulnerable areas may be more muted due to under-reporting, even
        if QoL and heat exposure disproportionately affect them.

## Data

### Primary

**311 Service Requests**

Filter by categories related to:

-   Sanitation/Solid Waste (missed collections, illegal dumping,
    overflowing baskets)

-   Water/Infrastructure Stress (broken hydrants, water leaks)

-   Utilities (streetlight outages, lighting failure, power-adjacent
    issues)

-   Noise

-   Cooling Assistance/Heat Safety

Then filter within the hours of how "abnormally hot" and "normally hot"
days are defined:

1.  Years 2018 through 2025

2.  Restrict from June through August

3.  Calculate 90th percentile of daily max

4.  Abnormally hot for a daily max equal to or above the percentile,
    normally hot for daily maxes below the percentile. Should create
    weekly summaries noting how many abnormally hot days were in that
    week

5.  Note hourly temperatures above the percentile threshold. Should
    create daily summaries noting how many abnormally hot hours were in
    the day

Oikolab provides historical temperature.

Then calculate the percentage by dividing the QoL requests by the total
requests in the block groups.

**NOTE:** Philadelphia 311 might only be dense enough to support weekly
calculations per block group in summer.

### Secondary

**Hourly Oikolab Historical Weather**

-   Temperature

-   Wind

-   Pressure

-   Precipitation

-   Humidity

**ACS 5-Year**

-   2018 through 2023 5-year ACS at block-group level

Potential Variables:

-   Median Income

-   Poverty Rate

-   Unemployment

-   Renter %

-   Bachelor's or More %

-   Ages 65+ %

-   Ages Below 5 %

-   Disability %

-   Limited English Speaker %

-   No Vehicle %

-   Housing Age (pre-1950, 1950–1980, \>1980)

-   White % / Non-White %

**Urban Infrastructure / Environment**

-   Tree Canopy %

-   Impervious Surface %

-   Block Group boundaries

### Feature Engineering

**311 to QoL Proxies**

-   Map raw categories to QoL taxonomy (sanitation, noise,
    streetlight/utility, water/hydrant, vacant lot/graffiti, cooling
    assistance)

-   Aggregate to block group \* week:

```{r}
qol_pct = 100 * (qol_calls_sum / all_calls_sum)
```

-   Optional: separate daytime vs nighttime windows?

**Weather to Exposure Metrics**

-   Hourly to daily/weekly since Philly's 311 is likely not dense enough
    to do hourly at the block group level

-   Compute Heat Index from temperature and humidity

-   Build per-day features, then average to week per city (since
    station-level is citywide), OR maybe could interpolate spatially and
    average per block group

**Static Socioeconomic, Built, and Environmental**

-   %poverty, med_income, %renter, %unemployed, %65plus, %no_vehicle,
    %bach_plus, %limited_english, %non_white, %children

-   %impervious, %tree_canopy

-   Optional: %buildings, %roads, housing age buckets as proxy for
    cooling infrastructure

**Temporal Controls**

-   Season fixed effects?

**Exposure Labeling**

-   Hot vs. Normal

    -   Calculate abnormally hot days then add up to abnormally hot days
        in a week using 90th percentile

### Modeling

Unit: Block groups and weeks in 2018 through 2025 summers

-   Response: 311 QoL Percents

-   Predictors: Heat features (abnormally hot days, hourly temperature,
    etc.) \* interactions with %poverty, %65plus, %impervious,
    %tree_canopy

-   Fixed Effects: Seasons, neighborhoods

-   Spatial CV

-   SHAP?

- Split temporally (train 2018–2023 / validate 2024–2025) to avoid leakage.

  - 2020's height of COVID could be a potential problem affecting overall
  behavior in cities, wondering about omission.

### Potential Final Dataset

Unit: Census Block Group \* Week \* Year during summer months (June 1 –
August 31), 2018–2025

Each record represents the QoL conditions in one block group during one
week of one summer.

| Category | Variable | Type | Description |
|------------------|------------------|------------------|------------------|
| Identifiers | GEOID | str |  |
|  | year | int |  |
|  | week_id | int | Week index in summer (e.g. June 5 would be week ID 1) |
| Dependent Variables | qol_calls | int | Count of 311 QoL calls in week |
|  | total_calls | int | Count of 311 total calls in week |
|  | qol_pct | float | qol_calls / total_calls |
|  | qol_rate | float | qol_calls per 1,000 residents |
| Heat Index (HI) | mean_HI_day | float | Mean daytime heat index |
|  | mean_HI_night | float | Mean nighttime heat index |
|  | hot_hours | float | Sum of hourly HI where it is higher than 85F |
|  | hot_days | int | Number of days in week with daily HI greater than year's 90th percentile |
| Optional Weather Controls | mean_humidity | float |  |
|  | mean_wind_spead | float |  |
|  | precipitation | float |  |
|  | wet_bulb | float |  |
|  | apparent_temp (called "real feel" in weather apps) | float |  |
| Socioeconomic Controls | pop_total | int |  |
|  | med_income | float |  |
|  | poverty_rate | float |  |
|  | unemployment_rate | float |  |
|  | renter_pct | float |  |
|  | bach_plus_pct | float |  |
|  | elderly_pct | float |  |
|  | children_pct | float |  |
|  | no_vehicle_pct | float |  |
|  | internet_access_pct | float |  |
|  | white_pct | float |  |
|  | nonwhite_pct | float |  |
| Built Infrastructure | impervious_pct | float |  |
| Optional Infrastructure | road_area_pct | float |  |
|  | housing_density | float |  |
|  | housing_pre1950_pct | float | Percent housing built before 1950 |
| Environmental | tree_canopy_pct | float |  |
|  | ndvi_mean | float | Average summer NDVI |
| Temporal Control | is_hot_week | binary | 1 if mean HI is equal to are greater than year's 90th percentile |
|  | week_in_summer | int | 1-13 index, for fixed effect on weekly differences in summer heatwaves |
|  | holiday_week | binary | 1 if there is a major holiday (4th of July) |
| Derived Modeling Features | heat_x_poverty | float | Interaction: mean_HI_day \* poverty_rate |
|  | heat_x_canopy | float | Interaction: mean_HI_day \* tree_canopy_pct |
|  | heat_x_impervious | float | Interaction: mean_HI_day \* impervious_pct |

## Cleaning and Normalization Rough Workflow

1. Temporal filtering: keep only June – August.

2. Join logic:

- Aggregate 311 to BG * week;

- Aggregate weather to week (citywide);

- Join static ACS + land-cover by GEOID.

3. Normalize continuous variables (z-score or 0–1 scaling) for ML.

4. Log-transform skewed ones (income, degree-hours, call counts).

5. Convert % fields to decimals (0–1) for modeling.

6. Handle missingness: Drop block groups with < 2 years of data.