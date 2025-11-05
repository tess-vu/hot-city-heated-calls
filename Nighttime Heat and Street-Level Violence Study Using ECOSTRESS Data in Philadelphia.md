---
editor_options: 
  markdown: 
    wrap: 72
---

# Nighttime Heat and Street-Level Violence Study Using ECOSTRESS Data in Philadelphia

These are my findings to get things outlined and in order, anything is
subject to change if we need to pivot!

**QUESTION:** How do satellite-derived heat (LST) and urban greening
(tree canopy or LSTE) interact to influence violent crime counts at the
block group level in Philadelphia, after controlling for
socio-demographic vulnerability and built-environment density?

-   **Hypothesis 1:** Higher LST associated with higher rates of violent
    crime.

-   **Hypothesis 2:** Higher tree canopy or LSTE percentage associated
    with lower rates of violent crime.

-   **Hypothesis 3:** Crime-mitigating effect of tree canopy will be
    most pronounced in the hottest areas.

**NOTES:** ECOSTRESS has a non-sun-synchronous orbit that captures
nighttime temperatures (8pm-4am window), unlike fixed-overpass
satellites like LANDSAT for daytime. Currently 2 sets of collection
timeline deployments, with the 3rd just launched in September 2025.
[Collection 1 has less geolocation accuracy than Collection
2](https://www.earthdata.nasa.gov/data/alerts-outages/ecostress-version-1-forward-processing-ended).
Could use just 2 or both. [Collection 2 data (October
2022-present](https://ecostress.jpl.nasa.gov/data)) has irregular 3-4
day revisit frequency for Philadelphia with a lot of usable data to
detect [temperature-crime associations documented in prior literature
(9-17% increase per 5°C)]().

**POTENTIAL PLAN:** Time-matching design with Poisson or Negative
Binomial Regression? Crime is count data, wouldn't make sense to use a
regression that doesn't work for continuous or negative data. Negative
Binomial is the ideal for crime data. Primary analysis using street
segment centroids with 150-300ft (TBD) buffers for LST. Aggregated by
census block groups, gives more observations, but census tracts would
introduce the Modifiable Areal Unit Problem we talked about in PPA and
Stats. We're trying to link high resolution environmental data to social
data, tracts would cancel that out.

## DATA

### ECOSTRESS LST Data (Primary Dataset)

**NOTE:** I think it could be a good idea to do the LST and the cloud
mask data and perform a raster calculation because this could help
filter out "bad/dirty data" pixels.

-   **Satellite:** ECO_L2T_LSTE.002 (GeoTIFF Tiles, .002 means
    collection 2)

-   **DOI:**
    [https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002](#0){.uri}

-   **Resolution:** 70m by 70m (230ft by 230ft)

-   **Format:** Separate GeoTIFF per layer (LST, cloud_mask, QC, EmisWB)

-   **Tile System:** \~110km tiles (\~360,892ft)

-   **Time Period:** June 2023-Present during summer months likely from
    summer solstice thru day before fall equinox

**DATA ACCESS**

**Method 1: AppEEARS (Web Interface w/ Filters)**

-   **URL:** <https://appeears.earthdatacloud.nasa.gov/>

-   **Process:** Create account → Select ECO_L2T_LSTE.002 → Upload
    Philadelphia shapefile → Choose LST and cloud_mask layers → Filter
    for nighttime target (ex. 01:00-09:00 UTC = 8pm-4am EST/EDT)

-   This requires manual-ish download with the filtering, they're
    downloaded as zip files locally, but obviously the rasters have
    large sizes.

**Method 2: Python earthaccess Library**

``` python
import earthaccess

# Authenticate (one-time setup)
earthaccess.login()

# Search Philadelphia nighttime data
results = earthaccess.search_data(
    short_name = "ECO_L2T_LSTE",
    version = "002",
    bounding_box = (-75.3, 39.85, -75.0, 40.05),
    temporal = ("2023-05-01", "2024-12-31")
)

# Filter for nighttime (UTC hours 01:00-09:00)
nighttime = [g for g in results 
             if 1 <= int(g["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"].split("T")[1][:2]) <= 9]

# Download
earthaccess.download(nighttime, "./ecostress_data/")
```

**Method 3: Direct S3 Cloud Access (Fastest)**

-   ECOSTRESS data hosted in AWS S3 (lp-prod-protected bucket)

-   Stream directly without full download using
    rasterio.Env(aws_session)

-   Tutorial:
    <https://github.com/nasa/ECOSTRESS-Data-Resources/blob/main/python/how-tos/how_to_direct_access_s3_ecostress_cog.ipynb>

**NASA Earthdata Credentials (Required):**

-   Register: <https://urs.earthdata.nasa.gov/users/new> - Free,
    immediate access - Configure .netrc file:
    `echo "machine urs.earthdata.nasa.gov login USERNAME password PASSWORD" >> ~/.netrc && chmod 600 ~/.netrc`

**Other Resources:**

-   Official Repo: <https://github.com/nasa/ECOSTRESS-Data-Resources>

-   User Guide:
    <https://lpdaac.usgs.gov/documents/423/ECO2_User_Guide_V1.pdf>

-   ATBD (algorithm details):
    <https://ecostress.jpl.nasa.gov/downloads/atbd/ECOSTRESS_L2_ATBD_LSTE_2018-03-08.pdf>

### Philadelphia Crime Data

**Shooting Victims Dataset (Primary)**

**NOTE:** We could use Shooting Victims dataset because it would be less
computationally heavy, or we could get crime data and filter by general
violent crime.

-   **URL:** <https://opendataphilly.org/datasets/shooting-victims/>

-   **API Endpoint:**
    <https://cityofphiladelphia.github.io/carto-api-explorer/#shootings>

-   **Fields:** date, time, lat, lng, location

-   **Update Frequency:** Daily

-   **Temporal Range:** 2015-present

**Query for Study Period (2022-2024):**

``` sql
SELECT *, ST_Y(the_geom) AS lat, ST_X(the_geom) AS lng 
FROM shootings 
WHERE date_ >= "2022-01-01" AND date_ < "2025-01-01"
```

**Nighttime Filter (can adjust time):**

``` python
import pandas as pd
df = pd.read_csv("shootings.csv")
df["hour"] = pd.to_datetime(df["time"], format="%H:%M").dt.hour
nighttime = df[(df["hour"] >= 20) | (df["hour"] <= 4)]
```

### Social Mechanisms Data

**Census Demographics (Block Group Level)**

-   **API:** <https://api.census.gov/data/2022/acs/acs5>

-   **Python Access:** Use `cenpy` or `census` packages

-   **Philadelphia County FIPS:** 42101

-   **My Suggested Variables:**

    -   total population (B01003)

    -   poverty (B17001)

    -   race, but use White only to avoid ethical concerns, groups
        people of color together in general (B03002)

    -   age (B01001), could do ages 65+ and separate by male and female

    -   households living alone (B11012) and separate by male and
        female, good proxy for measuring social isolation vulnerability

### Other Potential Data?

**Philadelphia-Specific Building Footprints**

-   **URL:** <https://opendataphilly.org/datasets/building-footprints/>

-   **Products:** Raster updated weekly

-   **Years:** 2021 (most recent), 2019, 2016

**Philadelphia-Specific Land Cover (Higher Resolution)**

-   **URL:**
    <https://opendataphilly.org/datasets/philadelphia-land-cover-raster/>

-   **Years:** 2008, 2018

-   **Classes:** 13 categories including tree canopy, impervious
    surfaces, structures

## DATA PROCESSING

### ECOSTRESS Product Details

**File Naming Convention:**

ECOv002_L2T_LSTE_24498_003_18TUM_20221031T150810_0710_01_LST.tif

ECO \<- ECOSTRESS Sensor

v002 \<- Collection/Version 2

L2T \<- Level 2 Tiled

LSTE \<- Orbit Number

24498 \<- Scene ID

003 \<- MGRS Tile ID

18TUM \<- Datetime (UTC)

20221031T150810 \<- Build ID

0710 \<- Product Iteration

01 \<- Layer Name

LST \<- Raster Type (cloud raster could be CLOUD or CLD)

```         
ECOv002_L2T_LSTE_24498_003_18TUM_20221031T150810_0710_01_LST.tif
│      │   │    │     │   │     │               │    │  │
│      │   │    │     │   │     │               │    │  └─ Layer name
│      │   │    │     │   │     │               │    └─ Product iteration
│      │   │    │     │   │     │               └─ Build ID
│      │   │    │     │   │     └─ Acquisition datetime (UTC)
│      │   │    │     │   └─ MGRS tile ID
│      │   │    │     └─ Scene ID
│      │   │    └─ Orbit number
│      │   └─ Level 2 Tiled
│      └─ Collection/Version 2
└─ ECOSTRESS sensor
```

**Layers:**

-   **LST.tif (Primary):** Land surface temperature in Kelvin (convert
    to Celsius: LST - 273.15, convert to Fahrenheit: LST - 459.67)

-   **cloud.tif (Optional):** Cloud mask (0 = clear, 1 = cloud)

**Spatial Coverage:**

-   **MGRS Tile:** 109.8km \* 109.8km

-   **Philadelphia Extent:** \~25km \* 40km (fits within single tile in
    most cases)

-   Might need to mosaic tiles

**Temporal Matching:**

-   Need to specify time and extract from there

**Statistical Analysis:**

-   Need to determine statistical regression

### First Part: Collection

1)  Get boundaries and demographic data

2)  Get crime data

3)  Get built form / urban density (building footprint) and green data
    (tree canopy or LSTE)

4)  Get ECOSTRESS data

### Second Part: Aggregate to block group

5)  Process ECOSTRESS LST

6)  Zonal statistics

7)  Process dependent crime variable, spatial join to count crime points
    within each block group polygon

8)  Consolidate all necessary variables to final columns and create any
    standardized variables if needed

Potential final geodataframe variables before statistical modeling:

|  |  |  |
|------------------------|------------------------|------------------------|
| Column Name | Data Type | Description / Source |
| GEOID | string | Identifier: The unique ID for the Census Block Group. Used to join all data. |
| geometry | geometry | Spatial Data: The polygon shape of the block group. Inherited from pygris. |
| violent_crime_count | integer | Dependent Variable: The outcome to be modeled. The total count of violent crimes (e.g., Aggravated Assault, Robbery) from OpenDataPhilly that fall within the block group polygon. |
| pop_total | integer | Offset/Normalization: The total population of the block group. Used to create the log_pop offset. |
| log_pop | float | Offset Variable: The natural log of pop_total. This is used in the model to analyze the rate of crime, not just the raw count. |
| lst_mean | float | Key Predictor: The mean Land Surface Temperature (LST) value (in Kelvin) for the block group, derived from the ECOSTRESS raster composite. |
| tree_canopy_pct | float | Key Predictor: The percentage of the block group's area covered by tree canopy, derived from the PASDA Land Cover raster. |
| building_pct_cover | float | Control Variable (Built Form): The percentage of the block group's area covered by building footprints, derived from the OpenDataPhilly vector data. |
| pct_poverty | float | Control Variable (Social): Percentage of the population below the poverty line. Derived from ACS data. |
| pct_non_white | float | Control Variable (Social): Percentage of the population not identifying as "White, not Hispanic." Derived from ACS data. |
| pct_age_65_plus | float | Control Variable (Social): Percentage of the population aged 65 or older. Derived from ACS data. |
| pct_living_alone | float | Control Variable (Social): Percentage of households with an individual living alone (proxy for social isolation). Derived from ACS data. |

### Third Part: Statistical Modeling

9)  Test spatial autocorrelation in dependent variable using pysal
    library

10) Model using statsmodels for Poisson or Negative Binomial

11) Could also do a spatial regression to see about the residuals and do
    lag or error or GWR for visualization? Optional

12) Could try a small section or two of block groups with high and low
    crime for street-level segmentation? Optional

## POTENTIAL LIBRARIES / TOOLS

### Key Libraries with Specific Uses

**ECOSTRESS Processing:**

-   **earthaccess:** NASA data search and download
    (<https://github.com/nsidc/earthaccess>)

-   **rioxarray:** Raster operations with xarray
    (<https://corteva.github.io/rioxarray/>)

-   **rasterio:** Low-level raster I/O
    (<https://rasterio.readthedocs.io/>)

**Spatial Analysis:**

-   **geopandas:** Vector operations (<https://geopandas.org/>)

-   **rasterstats:** Extract raster values to vector
    (<https://pythonhosted.org/rasterstats/>)

-   **osmnx:** Street network analysis (<https://osmnx.readthedocs.io/>)

**Statistical Modeling:**

-   **pysal:** Spatial stats (<https://pysal.org/docs/users/>)

-   **pystats:** Statistical modeling (<https://docs.pypi.org/>)

**Visualization:**

-   **matplotlib + seaborn:** Static publication figures

-   **folium:** Interactive maps
    (<https://python-visualization.github.io/folium/>)

-   **contextily:** Basemap tiles (<https://contextily.readthedocs.io/>)

-   **hvplot:** Interactive geospatial plots
    (<https://hvplot.holoviz.org/>)

### Repositories

**Official ECOSTRESS Resources:**

-   **NASA ECOSTRESS-Data-Resources:**
    <https://github.com/nasa/ECOSTRESS-Data-Resources>

**Temperature-Crime Analysis:**

-   **harris-ippp/weather:** Chicago crime vs temperature
    (<https://harris-ippp.github.io/weather.html>)

-   **moutellou/heatcrime:** Montreal temperature-crime correlation

**Street Network Analysis:**

-   **gboeing/osmnx-examples:** Comprehensive OSMnx tutorials
    (<https://github.com/gboeing/osmnx-examples>)

**Resources:**

-   **PyTorch Geometric Temporal:**
    <https://github.com/benedekrozemberczki/pytorch_geometric_temporal>

-   **Tutorial:**
    <https://pytorch-geometric.readthedocs.io/en/latest/get_started/introduction.html>

## RESOURCES

**ECOSTRESS:**

-   Product Page: <https://lpdaac.usgs.gov/products/eco_l2t_lstev002/>

-   User Guide:
    <https://lpdaac.usgs.gov/documents/423/ECO2_User_Guide_V1.pdf>

-   Data Access: <https://github.com/nasa/ECOSTRESS-Data-Resources>

**Philadelphia Data:**

-   OpenDataPhilly: <https://opendataphilly.org/>

-   Crime Data: <https://opendataphilly.org/datasets/shooting-victims/>

-   Street Centerlines:
    <https://opendataphilly.org/datasets/street-centerlines/>

**Methodological Papers:**

-   Xu et al. (2020). "Ambient temperature and intentional homicide: A
    multi-city case-crossover study in the US." *Environment
    International* 143:105992.

-   Schinasi & Hamra (2017). "A time series analysis of associations
    between daily temperature and crime events in Philadelphia." *J
    Urban Health* 94:892-900.

-   Weisburd (2015). "The law of crime concentration and the criminology
    of place." *Criminology* 53(2):133-157.

**Software:**

-   OSMnx: Boeing (2025). "Modeling and Analyzing Urban Networks and
    Amenities with OSMnx." *Geographical Analysis* 57(4):567-577.

-   PyTorch Geometric Temporal: Rozemberczki et al. (2021). CIKM 2021.

**Mechanistic Pathways:**

1\. **Behavioral:** Heat increases street activity and social
interactions

2\. **Physiological:** Heat exposure elevates aggression and impulsivity

3\. **Environmental:** Hot nights reduce indoor time, increase outdoor
congregation

**Policy Implications:**

-   Target cooling interventions (tree planting, cool surfaces) in
    high-LST corridors

-   Enhance police presence during heat events

-   Design heat action plans incorporating violence prevention

**Limitations**

1.  **Ecological fallacy:** LST measured at segment level, not
    individual exposure
2.  **Temporal mismatch:** ECOSTRESS captures instantaneous LST, not
    sustained exposure
3.  **Cloud gaps:** Systematic loss of data during cloudy (cooler)
    nights may bias results
4.  **Residual confounding:** Unmeasured factors (major events,
    holidays, policy changes) not controlled
5.  **Generalizability:** Results specific to Philadelphia's climate and
    built environment
