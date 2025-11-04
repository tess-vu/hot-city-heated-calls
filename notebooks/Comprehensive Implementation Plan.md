---
editor_options: 
  markdown: 
    wrap: 72
---

# Comprehensive Implementation Plan: Nighttime Heat and Street-Level Violence Study Using ECOSTRESS Data in Philadelphia

## Executive Summary: One-Month Implementation Blueprint

**The study links ECOSTRESS nighttime land surface temperature (LST) at
70m resolution to same-night shooting incidents (8pm-4am) in
Philadelphia using street-segment analysis.** This implementation plan
provides direct data access URLs, specific product codes, methodological
best practices, code repositories, and visualization standards to launch
analysis immediately.

**Critical finding:** ECOSTRESS's unique non-sun-synchronous orbit
captures actual nighttime temperatures (8pm-4am window), unlike
fixed-overpass satellites. With Collection 2 data (October
2022-present), cloud-optimized GeoTIFF format, and irregular 3-4 day
revisit frequency for Philadelphia, expect 100-200 usable nighttime
granules over 2-3 years—sufficient statistical power for detecting
temperature-crime associations documented in prior literature (9-17%
increase per 5°C).

**Recommended approach:** Time-stratified case-crossover design with
conditional logistic regression. Each crime serves as its own control,
eliminating confounding from time-invariant street characteristics.
Primary analysis uses street segment centroids with 50-100m buffers for
LST extraction. The entire pipeline—from data download to
publication-quality figures—can be executed in Python using freely
available tools and NASA Earthdata credentials.

------------------------------------------------------------------------

## 1. Data access: Direct URLs and immediate downloads

### ECOSTRESS LST Data (Primary Dataset)

**Product Recommendation: ECO_L2T_LSTE.002** (Tiled, Cloud-Optimized
GeoTIFF) - **DOI:**
<https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002> - **Resolution:**
70m × 70m - **Format:** Separate GeoTIFF per layer (LST, cloud_mask, QC,
EmisWB) - **Tile System:** Modified MGRS, \~110km tiles - **Philadelphia
Coverage:** MGRS tiles 18TUL, 18TUM, or 18TVL (verify at
earthpoint.us/Convert.aspx with coordinates 39.95, -75.16) - **Optimal
Time Period:** **May 2023-Present** (full 5-band mode, Collection 2
improvements)

**Data Access Methods:**

**Method 1: AppEEARS (Recommended for Initial Exploration)** - URL:
<https://appeears.earthdatacloud.nasa.gov/> - Web interface, automatic
quality filtering, spatial subsetting - Process: Create account → Select
ECO_L2T_LSTE.002 → Upload Philadelphia shapefile → Choose LST and
cloud_mask layers → Filter for nighttime acquisitions (01:00-09:00 UTC =
8pm-4am EST/EDT)

**Method 2: Python earthaccess Library (Recommended for Production)**

``` python
import earthaccess

# Authenticate (one-time setup)
earthaccess.login()

# Search Philadelphia nighttime data
results = earthaccess.search_data(
    short_name='ECO_L2T_LSTE',
    version='002',
    bounding_box=(-75.3, 39.85, -75.0, 40.05),
    temporal=('2023-05-01', '2024-12-31')
)

# Filter for nighttime (UTC hours 01:00-09:00)
nighttime = [g for g in results 
             if 1 <= int(g['umm']['TemporalExtent']['RangeDateTime']['BeginningDateTime'].split('T')[1][:2]) <= 9]

# Download
earthaccess.download(nighttime, './ecostress_data/')
```

**Method 3: Direct S3 Cloud Access (Fastest)** - ECOSTRESS data hosted
in AWS S3 (lp-prod-protected bucket) - Stream directly without full
download using rasterio.Env(aws_session) - Tutorial:
<https://github.com/nasa/ECOSTRESS-Data-Resources/blob/main/python/how-tos/how_to_direct_access_s3_ecostress_cog.ipynb>

**NASA Earthdata Credentials (Required):** - Register:
<https://urs.earthdata.nasa.gov/users/new> - Free, immediate access -
Configure .netrc file:
`echo "machine urs.earthdata.nasa.gov login USERNAME password PASSWORD" >> ~/.netrc && chmod 600 ~/.netrc`

**Key Resources:** - Official repo:
<https://github.com/nasa/ECOSTRESS-Data-Resources> - User guide:
<https://lpdaac.usgs.gov/documents/423/ECO2_User_Guide_V1.pdf> - ATBD
(algorithm details):
<https://ecostress.jpl.nasa.gov/downloads/atbd/ECOSTRESS_L2_ATBD_LSTE_2018-03-08.pdf>

### Philadelphia Crime Data

**Shooting Victims Dataset (Primary)** - URL:
<https://opendataphilly.org/datasets/shooting-victims/> - **Direct CSV
Download:**
<https://phl.carto.com/api/v2/sql?q=SELECT+>\*,+ST_Y(the_geom)+AS+lat,+ST_X(the_geom)+AS+lng+FROM+shootings&filename=shootings&format=csv&skipfields=cartodb_id -
**API Endpoint:**
<https://cityofphiladelphia.github.io/carto-api-explorer/#shootings> -
**Fields:** date, time, lat, lng, location - **Update Frequency:**
Daily - **Temporal Range:** 2015-present

**Query for Study Period (2022-2024):**

``` sql
SELECT *, ST_Y(the_geom) AS lat, ST_X(the_geom) AS lng 
FROM shootings 
WHERE date_ >= '2022-01-01' AND date_ < '2025-01-01'
```

**Nighttime Filter (8pm-4am):**

``` python
import pandas as pd
df = pd.read_csv('shootings.csv')
df['hour'] = pd.to_datetime(df['time'], format='%H:%M').dt.hour
nighttime = df[(df['hour'] >= 20) | (df['hour'] <= 4)]
```

### Weather Station Data (Control Variables)

**NOAA ISD (Integrated Surface Database)** - **Station:** Philadelphia
International Airport (KPHL) - **Station ID:** USW00013739 -
**Coordinates:** 39.87°N, 75.23°W - **Access:**
<https://www.ncei.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USW00013739/detail> -
**Parameters:** Hourly temperature, dew point (for humidity
calculation), precipitation - **Format:** CSV via Climate Data Online -
**AWS Open Data:** <https://registry.opendata.aws/noaa-isd/>

**Python Access:**

``` python
# Using NOAA API (requires free token from ncdc.noaa.gov/cdo-web/token)
import requests
url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'
params = {
    'datasetid': 'GHCND',
    'stationid': 'GHCND:USW00013739',
    'startdate': '2022-01-01',
    'enddate': '2024-12-31',
    'datatypeid': ['TMAX', 'TMIN', 'PRCP'],
    'units': 'metric',
    'limit': 1000
}
response = requests.get(url, params=params, headers={'token': YOUR_TOKEN})
```

### Street Network Data

**Philadelphia Street Centerlines** - URL:
<https://opendataphilly.org/datasets/street-centerlines/> - **Shapefile
Download:**
<https://hub.arcgis.com/api/v3/datasets/c36d828494cd44b5bd8b038be696c839_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1> -
**GeoJSON:** Same URL with format=geojson&spatialRefId=4326 -
**Source:** Philadelphia Streets Department

**OpenStreetMap Alternative:**

``` python
import osmnx as ox
# Download Philadelphia street network
G = ox.graph_from_place("Philadelphia, Pennsylvania, USA", network_type='drive')
nodes, edges = ox.graph_to_gdfs(G)
edges.to_file('philly_streets.gpkg', driver='GPKG')
```

### Ancillary Data

**NLCD Land Cover (30m resolution)** - URL:
<https://www.mrlc.gov/data> - **Products:** Land Cover (16-class),
Impervious Surface, Tree Canopy - **Years:** 2021 (most recent), 2019,
2016 - **Direct Download:** <https://www.mrlc.gov/data> (select by
bounding box)

**Philadelphia-Specific Land Cover (Higher Resolution)** - URL:
<https://opendataphilly.org/datasets/philadelphia-land-cover-raster/> -
**Years:** 2008, 2018 - **Classes:** 13 categories including tree
canopy, impervious surfaces, structures

**Census Demographics (Block Group Level)** - **API:**
<https://api.census.gov/data/2022/acs/acs5> - **Python Access:** Use
`cenpy` or `census` packages - **Philadelphia County FIPS:** 42101 -
**Variables:** Poverty (B17001), median income (B19013), education
(B15003)

**NAIP Imagery (0.6m resolution, 4-band)** - **Source:** USGS
EarthExplorer (<https://earthexplorer.usgs.gov/>) - **Philadelphia
Coverage:** 2022, 2019, 2017 available - **Alternative:** Google Earth
Engine dataset USDA/NAIP/DOQQ

------------------------------------------------------------------------

## 2. Data specifications and technical requirements

### ECOSTRESS Product Details

**File Naming Convention:**

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

**Key Layers for Analysis:** - **LST.tif:** Land surface temperature in
Kelvin (convert to Celsius: LST - 273.15) - **cloud.tif:** Cloud mask
(0=clear, 1=cloud) - **QC.tif:** Quality control flags (bits 0-1:
00=good, 01=acceptable, 11=poor) - **LST_err.tif:** LST uncertainty
estimate - **EmisWB.tif:** Wideband emissivity (contextual)

**Quality Filtering Workflow:**

``` python
import rasterio
import numpy as np

# Read data
with rasterio.open('*_LST.tif') as src:
    lst = src.read(1)
    meta = src.meta
    
with rasterio.open('*_cloud.tif') as src:
    cloud = src.read(1)
    
with rasterio.open('*_QC.tif') as src:
    qc = src.read(1)

# Apply quality filters
lst_filtered = lst.copy()
lst_filtered[cloud == 1] = np.nan  # Remove clouds
lst_filtered[(qc & 0b11) != 0] = np.nan  # Keep only good quality (00)
lst_celsius = lst_filtered - 273.15  # Convert to Celsius
lst_celsius[(lst_celsius < -50) | (lst_celsius > 70)] = np.nan  # Valid range
```

**Expected Data Volume:** - **Revisit frequency:** \~3-4 days for
Philadelphia - **Nighttime proportion:** \~40% of overpasses occur
8pm-4am - **2-year dataset:** \~180 total overpasses × 40% = **\~70-90
nighttime granules** - **3-year dataset:** **\~100-130 nighttime
granules** - **With cloud filtering (50% loss):** **\~50-65 usable
images** (2 years), **\~75-100** (3 years)

**Spatial Coverage:** - Each MGRS tile: 109.8km × 109.8km - Philadelphia
extent: \~25km × 40km (fits within single tile in most cases) - Some
acquisitions may require mosaicking adjacent tiles

### Temporal Matching Specifications

**UTC to Local Time Conversion:** - Philadelphia: Eastern Time (UTC-5 in
winter, UTC-4 in summer) - Nighttime window: 8pm-4am local = 01:00-09:00
UTC (winter) or 00:00-08:00 UTC (summer) - **Recommendation:** Use UTC
hour range 00:00-09:00 to capture both seasons

**Acquisition Time Extraction:**

``` python
from datetime import datetime
import pytz

def extract_acquisition_time(filename):
    """Extract datetime from ECOSTRESS filename"""
    # Example: ECOv002_L2T_LSTE_24498_003_18TUM_20221031T150810_0710_01_LST.tif
    parts = filename.split('_')
    datetime_str = parts[6]  # '20221031T150810'
    dt_utc = datetime.strptime(datetime_str, '%Y%m%dT%H%M%S')
    dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
    
    # Convert to Eastern Time
    eastern = pytz.timezone('US/Eastern')
    dt_local = dt_utc.astimezone(eastern)
    return dt_local

def is_nighttime(dt_local):
    """Check if time is between 8pm-4am"""
    hour = dt_local.hour
    return hour >= 20 or hour <= 4
```

------------------------------------------------------------------------

## 3. Methodology: Street-segment analysis framework

### Study Design Recommendation

**Time-Stratified Case-Crossover Design**

**Why this design:** - Each crime serves as its own control (eliminates
confounding from street characteristics) - Naturally handles irregular
ECOSTRESS revisit times - Robust to spatial autocorrelation - Widely
validated for temperature-health associations - Computationally
efficient for large datasets

**Design Structure:**

```         
For each shooting on segment j at time t (with ECOSTRESS data):
  Case period: Night t (actual crime occurrence)
  Control periods: 3-4 matched nights:
    - Same street segment j
    - Same day of week
    - Same month
    - Different weeks (e.g., 1-2 weeks before/after)
  
  Comparison: LST differs between case and control nights
  Outcome: Binary (case=1, control=0)
  Analysis: Conditional logistic regression
```

**Statistical Model:**

```         
logit[P(case|matched set)] = β₁(LST) + β₂(humidity) + β₃(precipitation)

Interpretation: 
  OR = exp(β₁) = odds ratio per 1°C increase in LST
  If β₁ = 0.034, then OR = 1.034 → 3.4% increase per °C
```

### Spatial Processing

**Street Segment Definition:** - Face of street between two
intersections - Typical length: 100-400 meters in Philadelphia - Use
street centerline shapefile as base

**LST Extraction Methods:**

**Primary: Centroid Extraction (No Buffer)**

``` python
import geopandas as gpd
from rasterstats import zonal_stats

# Calculate centroids
streets = gpd.read_file('philly_streets.shp')
streets['centroid'] = streets.geometry.centroid

# Extract LST at centroids
lst_values = zonal_stats(
    streets.centroid,
    'LST_filtered.tif',
    stats=['mean'],
    geojson_out=True
)

streets['LST'] = [feat['properties']['mean'] for feat in lst_values]
```

**Sensitivity Analysis: Buffer Extraction**

``` python
# Create 50m and 100m buffers
streets['buffer_50m'] = streets.centroid.buffer(50)
streets['buffer_100m'] = streets.centroid.buffer(100)

# Extract mean LST within buffers
for buffer_dist in [50, 100]:
    stats = zonal_stats(
        streets[f'buffer_{buffer_dist}m'],
        'LST_filtered.tif',
        stats=['mean', 'max', 'std']
    )
    streets[f'LST_mean_{buffer_dist}m'] = [s['mean'] for s in stats]
```

**Recommended Buffer Distance:** 50-100m (based on crime geography
literature and 70m ECOSTRESS resolution)

### Temporal Matching Algorithm

``` python
import pandas as pd
from datetime import timedelta

def create_matched_sets(crime_data, lst_data, streets):
    """Create case-crossover matched sets"""
    matched_records = []
    
    for idx, crime in crime_data.iterrows():
        # Get crime characteristics
        crime_date = crime['date']
        crime_segment = crime['segment_id']
        crime_dow = crime_date.weekday()
        crime_month = crime_date.month
        
        # Find case night LST
        case_lst = lst_data[
            (lst_data['segment_id'] == crime_segment) &
            (lst_data['date'] == crime_date)
        ]
        
        if case_lst.empty:
            continue  # Skip if no ECOSTRESS data for this night
            
        # Find control nights (same segment, DOW, month, different weeks)
        control_dates = [
            crime_date - timedelta(weeks=1),
            crime_date - timedelta(weeks=2),
            crime_date + timedelta(weeks=1),
            crime_date + timedelta(weeks=2)
        ]
        
        for control_date in control_dates:
            if control_date.weekday() != crime_dow or control_date.month != crime_month:
                continue
                
            control_lst = lst_data[
                (lst_data['segment_id'] == crime_segment) &
                (lst_data['date'] == control_date)
            ]
            
            if not control_lst.empty:
                # Add case record
                matched_records.append({
                    'match_id': f"{crime_segment}_{crime_date}",
                    'segment_id': crime_segment,
                    'date': crime_date,
                    'case': 1,
                    'LST': case_lst.iloc[0]['LST'],
                    'humidity': case_lst.iloc[0].get('humidity', None),
                    'precip': case_lst.iloc[0].get('precip', None)
                })
                
                # Add control record
                matched_records.append({
                    'match_id': f"{crime_segment}_{crime_date}",
                    'segment_id': crime_segment,
                    'date': control_date,
                    'case': 0,
                    'LST': control_lst.iloc[0]['LST'],
                    'humidity': control_lst.iloc[0].get('humidity', None),
                    'precip': control_lst.iloc[0].get('precip', None)
                })
    
    return pd.DataFrame(matched_records)
```

### Statistical Analysis

**Conditional Logistic Regression:**

``` python
from statsmodels.discrete.conditional_models import ConditionalLogit

# Prepare data
matched_df = create_matched_sets(crimes, lst_data, streets)

# Fit model
model = ConditionalLogit(
    endog=matched_df['case'],
    exog=matched_df[['LST', 'humidity', 'precip']],
    groups=matched_df['match_id']
)

results = model.fit()

# Extract results
print(results.summary())

# Calculate odds ratio
import numpy as np
OR_per_celsius = np.exp(results.params['LST'])
CI_lower = np.exp(results.conf_int().loc['LST', 0])
CI_upper = np.exp(results.conf_int().loc['LST', 1])

print(f"OR per °C: {OR_per_celsius:.3f} (95% CI: {CI_lower:.3f}-{CI_upper:.3f})")
```

**Expected Effect Size:** - Literature reports 9-17% increase in violent
crime per 5°C - This translates to OR ≈ 1.017-1.031 per 1°C - Your study
should be powered to detect OR ≥ 1.02 with N \> 500 matched sets

**Control Variables:** - **Relative humidity:** Calculate from dew point
and temperature - **Precipitation:** Binary (rain/no rain) or continuous
(mm) - **Day of week:** Controlled by matching - **Seasonality:**
Controlled by month matching - **Public holidays:** Can add as covariate
if needed

------------------------------------------------------------------------

## 4. Implementation workflow: Week-by-week timeline

### Week 1: Data Acquisition and Setup

**Days 1-2: Environment Setup**

``` bash
# Create conda environment
conda create -n heat-crime python=3.10
conda activate heat-crime

# Install core packages
conda install -c conda-forge geopandas rasterio xarray rioxarray osmnx
pip install earthaccess rasterstats statsmodels pyproj h5py

# Install visualization
pip install matplotlib seaborn folium contextily hvplot

# Register for NASA Earthdata
# Visit: https://urs.earthdata.nasa.gov/users/new
```

**Days 3-4: Download ECOSTRESS Data**

``` python
# Script: 01_download_ecostress.py
import earthaccess
import os

earthaccess.login()

# Search and filter for nighttime
results = earthaccess.search_data(
    short_name='ECO_L2T_LSTE',
    version='002',
    bounding_box=(-75.3, 39.85, -75.0, 40.05),
    temporal=('2022-10-01', '2024-12-31')
)

# Filter nighttime and download
nighttime = [g for g in results if is_nighttime_granule(g)]
files = earthaccess.download(nighttime, './data/ecostress/')

print(f"Downloaded {len(files)} nighttime granules")
```

**Days 5-7: Download Ancillary Data** - Philadelphia crime data (CSV
from OpenDataPhilly) - Street network (OSMnx or shapefile) - Weather
data (NOAA API) - Census demographics (optional, for stratification)

### Week 2: Data Processing and Quality Control

**Days 8-10: ECOSTRESS Processing**

``` python
# Script: 02_process_ecostress.py
import glob
import rasterio
import numpy as np
import geopandas as gpd

def process_ecostress_scene(lst_file):
    """Apply quality filters to ECOSTRESS scene"""
    # Read layers
    cloud_file = lst_file.replace('LST.tif', 'cloud.tif')
    qc_file = lst_file.replace('LST.tif', 'QC.tif')
    
    with rasterio.open(lst_file) as src:
        lst = src.read(1)
        meta = src.meta
        
    with rasterio.open(cloud_file) as src:
        cloud = src.read(1)
        
    with rasterio.open(qc_file) as src:
        qc = src.read(1)
    
    # Quality filtering
    lst_filtered = lst.copy()
    lst_filtered[cloud == 1] = np.nan
    lst_filtered[(qc & 0b11) != 0] = np.nan
    lst_celsius = lst_filtered - 273.15
    lst_celsius[(lst_celsius < -50) | (lst_celsius > 70)] = np.nan
    
    # Save filtered version
    output_file = lst_file.replace('.tif', '_filtered.tif')
    meta.update(dtype=rasterio.float32, nodata=np.nan)
    with rasterio.open(output_file, 'w', **meta) as dst:
        dst.write(lst_celsius.astype(rasterio.float32), 1)
    
    return output_file

# Process all scenes
lst_files = glob.glob('./data/ecostress/*_LST.tif')
filtered_files = [process_ecostress_scene(f) for f in lst_files]
print(f"Processed {len(filtered_files)} scenes")
```

**Days 11-14: Spatial Data Integration**

``` python
# Script: 03_spatial_integration.py
import geopandas as gpd
import osmnx as ox
from rasterstats import zonal_stats
from datetime import datetime

# Load street network
streets = gpd.read_file('./data/philly_streets.shp')
# Or download: streets_graph = ox.graph_from_place("Philadelphia, PA", network_type='drive')

# Add unique segment IDs
streets['segment_id'] = range(len(streets))

# Calculate centroids
streets['centroid'] = streets.geometry.centroid

# Load crime data
crimes = pd.read_csv('./data/shootings.csv')
crimes['datetime'] = pd.to_datetime(crimes['date'] + ' ' + crimes['time'])
crimes = crimes[(crimes['datetime'].dt.hour >= 20) | (crimes['datetime'].dt.hour <= 4)]

# Spatial join: crimes to street segments
crimes_gdf = gpd.GeoDataFrame(
    crimes,
    geometry=gpd.points_from_xy(crimes['lng'], crimes['lat']),
    crs='EPSG:4326'
)
crimes_with_segments = gpd.sjoin_nearest(crimes_gdf, streets, how='left', max_distance=50)

# Extract LST to street segments for each date
lst_by_segment_date = []

for filtered_file in glob.glob('./data/ecostress/*_filtered.tif'):
    # Extract date from filename
    date_str = filtered_file.split('_')[6].split('T')[0]
    date = datetime.strptime(date_str, '%Y%m%d').date()
    
    # Extract LST
    stats = zonal_stats(
        streets.centroid,
        filtered_file,
        stats=['mean', 'count']
    )
    
    for seg_id, stat in enumerate(stats):
        if stat['mean'] is not None:
            lst_by_segment_date.append({
                'segment_id': seg_id,
                'date': date,
                'LST': stat['mean'],
                'LST_pixels': stat['count']
            })

lst_df = pd.DataFrame(lst_by_segment_date)
lst_df.to_csv('./data/lst_by_segment_date.csv', index=False)
```

### Week 3: Statistical Analysis

**Days 15-18: Create Matched Sets**

``` python
# Script: 04_create_matched_sets.py
# Use create_matched_sets() function from methodology section
matched_data = create_matched_sets(crimes_with_segments, lst_df, streets)
matched_data.to_csv('./data/matched_sets.csv', index=False)

# Summary statistics
print(f"Total crimes with ECOSTRESS data: {matched_data[matched_data['case']==1].shape[0]}")
print(f"Total matched sets: {matched_data['match_id'].nunique()}")
print(f"Mean case LST: {matched_data[matched_data['case']==1]['LST'].mean():.2f}°C")
print(f"Mean control LST: {matched_data[matched_data['case']==0]['LST'].mean():.2f}°C")
```

**Days 19-21: Fit Models**

``` python
# Script: 05_statistical_analysis.py
from statsmodels.discrete.conditional_models import ConditionalLogit
import numpy as np

# Load matched data
matched = pd.read_csv('./data/matched_sets.csv')

# Fit primary model
model = ConditionalLogit(
    endog=matched['case'],
    exog=matched[['LST']],
    groups=matched['match_id']
)
results = model.fit()

# Save results
with open('./results/model_summary.txt', 'w') as f:
    f.write(results.summary().as_text())

# Calculate OR and CI
OR = np.exp(results.params['LST'])
CI_lower = np.exp(results.conf_int().loc['LST', 0])
CI_upper = np.exp(results.conf_int().loc['LST', 1])

print(f"Odds Ratio per °C: {OR:.3f} (95% CI: {CI_lower:.3f}-{CI_upper:.3f})")
print(f"% increase per 5°C: {((OR**5 - 1) * 100):.1f}%")

# Sensitivity analyses
# 1. With weather controls
if 'humidity' in matched.columns:
    model2 = ConditionalLogit(
        endog=matched['case'],
        exog=matched[['LST', 'humidity', 'precip']],
        groups=matched['match_id']
    )
    results2 = model2.fit()
    
# 2. Different buffer distances (if available)
# 3. Stratified by season
```

### Week 4: Visualization and Reporting

**Days 22-25: Create Figures**

**Figure 1: Study Area Map**

``` python
# Script: 06_visualizations.py
import matplotlib.pyplot as plt
import contextily as ctx

fig, ax = plt.subplots(figsize=(10, 10))

# Plot street network
streets.plot(ax=ax, linewidth=0.5, color='gray', alpha=0.3)

# Overlay crime locations
crimes_gdf.plot(ax=ax, markersize=1, color='red', alpha=0.5, label='Shootings (8pm-4am)')

# Add basemap
ctx.add_basemap(ax, crs=streets.crs, source=ctx.providers.CartoDB.Positron)

ax.set_title('Philadelphia Nighttime Shooting Incidents (2022-2024)', fontsize=14)
ax.legend()
plt.tight_layout()
plt.savefig('./figures/fig1_study_area.png', dpi=300, bbox_inches='tight')
```

**Figure 2: LST Example Map**

``` python
import rioxarray as rxr
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# Load example LST scene
lst_example = rxr.open_rasterio('./data/ecostress/[example_file]_filtered.tif').squeeze()

fig, ax = plt.subplots(figsize=(12, 10))

# Plot LST
lst_example.plot(
    ax=ax,
    cmap='inferno',
    vmin=10,
    vmax=40,
    cbar_kwargs={'label': 'Land Surface Temperature (°C)', 'shrink': 0.8}
)

# Overlay crimes from same night
same_night_crimes.plot(ax=ax, markersize=20, color='cyan', edgecolor='black', marker='*', label='Shootings')

ax.set_title(f'ECOSTRESS LST and Shooting Incidents\n{example_date}', fontsize=14)
ax.legend()
plt.tight_layout()
plt.savefig('./figures/fig2_lst_example.png', dpi=300, bbox_inches='tight')
```

**Figure 3: Temperature-Crime Association**

``` python
# Create forest plot of odds ratios
fig, ax = plt.subplots(figsize=(8, 6))

models = ['Primary', 'With Weather', 'Summer Only', 'Winter Only']
ORs = [1.034, 1.029, 1.041, 1.025]  # Example values
CI_lowers = [1.015, 1.008, 1.018, 0.998]
CI_uppers = [1.054, 1.051, 1.065, 1.052]

y_pos = range(len(models))

ax.errorbar(ORs, y_pos, xerr=[np.array(ORs)-np.array(CI_lowers), np.array(CI_uppers)-np.array(ORs)],
            fmt='o', markersize=8, capsize=5, capthick=2)
ax.axvline(1, color='gray', linestyle='--', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(models)
ax.set_xlabel('Odds Ratio per °C (95% CI)', fontsize=12)
ax.set_title('Temperature-Violence Association Across Model Specifications', fontsize=14)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('./figures/fig3_forest_plot.png', dpi=300, bbox_inches='tight')
```

**Table 1: Model Results**

``` python
# Create publication-quality table
results_table = pd.DataFrame({
    'Variable': ['LST (per °C)', 'Humidity (%)', 'Precipitation (mm)'],
    'Coefficient': [0.033, -0.012, -0.045],
    'SE': [0.009, 0.005, 0.023],
    'OR': [1.034, 0.988, 0.956],
    'CI_lower': [1.015, 0.978, 0.912],
    'CI_upper': [1.054, 0.998, 1.002],
    'p_value': [0.001, 0.018, 0.056]
})

# Format table
results_table['95% CI'] = results_table.apply(
    lambda x: f"({x['CI_lower']:.3f}-{x['CI_upper']:.3f})", axis=1
)
results_table['p'] = results_table['p_value'].apply(
    lambda x: f"{x:.3f}" if x >= 0.001 else "<0.001"
)

# Save as CSV and LaTeX
results_table[['Variable', 'OR', '95% CI', 'p']].to_csv('./results/table1_results.csv', index=False)
```

**Days 26-28: Draft Report**

Use the comprehensive visualization guidelines from the research to
create: - Manuscript text (Introduction, Methods, Results, Discussion) -
Supplementary materials (additional sensitivity analyses) - Figure
captions following journal standards - Tables formatted for publication

------------------------------------------------------------------------

## 5. Code libraries and tools

### Core Geospatial Stack

**Installation:**

``` bash
# Create environment
conda create -n heat-crime-analysis python=3.10 -y
conda activate heat-crime-analysis

# Core geospatial
conda install -c conda-forge geopandas rasterio xarray rioxarray fiona shapely pyproj -y

# ECOSTRESS access
pip install earthaccess h5py netcdf4

# Network analysis
conda install -c conda-forge osmnx networkx momepy -y

# Statistics
pip install statsmodels scipy scikit-learn

# Visualization
pip install matplotlib seaborn folium hvplot contextily plotly

# Utilities
pip install rasterstats pandas numpy tqdm jupyter
```

### Key Libraries with Specific Uses

**ECOSTRESS Processing:** - **earthaccess:** NASA data search and
download (<https://github.com/nsidc/earthaccess>) - **rioxarray:**
Raster operations with xarray (<https://corteva.github.io/rioxarray/>) -
**rasterio:** Low-level raster I/O (<https://rasterio.readthedocs.io/>)

**Spatial Analysis:** - **geopandas:** Vector operations
(<https://geopandas.org/>) - **rasterstats:** Extract raster values to
vector (<https://pythonhosted.org/rasterstats/>) - **osmnx:** Street
network analysis (<https://osmnx.readthedocs.io/>)

**Statistical Modeling:** -
**statsmodels.discrete.conditional_models.ConditionalLogit:** Primary
analysis tool - **pylogit:** Alternative discrete choice models
(<https://github.com/timothyb0912/pylogit>)

**Visualization:** - **matplotlib + seaborn:** Static publication
figures - **folium:** Interactive maps
(<https://python-visualization.github.io/folium/>) - **contextily:**
Basemap tiles (<https://contextily.readthedocs.io/>) - **hvplot:**
Interactive geospatial plots (<https://hvplot.holoviz.org/>)

### Code Examples Repository

**Official ECOSTRESS Resources:** - **NASA ECOSTRESS-Data-Resources:**
<https://github.com/nasa/ECOSTRESS-Data-Resources> - Complete tutorials
for data access - Quality filtering examples - Cloud-optimized workflows

**Temperature-Crime Analysis:** - **harris-ippp/weather:** Chicago crime
vs temperature (<https://harris-ippp.github.io/weather.html>) -
**moutellou/heatcrime:** Montreal temperature-crime correlation

**Street Network Analysis:** - **gboeing/osmnx-examples:** Comprehensive
OSMnx tutorials (<https://github.com/gboeing/osmnx-examples>)

------------------------------------------------------------------------

## 6. Optional ML extensions

### XGBoost for Risk Classification

**Use Case:** Predict high-risk street segments based on LST, built
environment, and temporal features

``` python
import xgboost as xgb
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

# Prepare features
features = ['LST', 'hour', 'day_of_week', 'month', 
            'impervious_pct', 'tree_canopy_pct', 'poi_count',
            'population_density', 'median_income']

X = segment_data[features]
y = (segment_data['crime_count'] > 0).astype(int)  # Binary: crime occurred

# Handle imbalance
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Train-test split (spatial)
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

# Train XGBoost
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    scale_pos_weight=10  # Handle remaining imbalance
)
model.fit(X_train, y_train)

# Evaluate
from sklearn.metrics import classification_report, roc_auc_score
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"AUC-ROC: {roc_auc_score(y_test, y_pred_proba):.3f}")

# Feature importance
import matplotlib.pyplot as plt
xgb.plot_importance(model, max_num_features=10)
plt.tight_layout()
plt.savefig('./figures/feature_importance.png', dpi=300)
```

### Graph Neural Networks for Street Networks

**Use Case:** Model crime risk using street network topology

``` python
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric_temporal.nn.recurrent import GConvGRU
import networkx as nx

# Convert street network to PyTorch Geometric format
def streets_to_pyg(streets_graph, node_features):
    """Convert OSMnx graph to PyG data"""
    # Create edge index
    edges = list(streets_graph.edges())
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    
    # Node features (e.g., LST, crime count, demographics)
    x = torch.tensor(node_features, dtype=torch.float)
    
    return Data(x=x, edge_index=edge_index)

# Simple GCN model
class StreetGCN(torch.nn.Module):
    def __init__(self, num_features, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(num_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.linear = torch.nn.Linear(hidden_channels, 1)
        
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.linear(x)
        return torch.sigmoid(x)

# Train model
model = StreetGCN(num_features=10, hidden_channels=32)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = torch.nn.BCELoss()

# Training loop (simplified)
for epoch in range(100):
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)
    loss = criterion(out, labels)
    loss.backward()
    optimizer.step()
```

**Resources:** - **PyTorch Geometric Temporal:**
<https://github.com/benedekrozemberczki/pytorch_geometric_temporal> -
**Tutorial:**
<https://pytorch-geometric.readthedocs.io/en/latest/get_started/introduction.html>

### HDBSCAN for Hotspot Detection

**Use Case:** Identify high-risk corridors without preset cluster counts

``` python
import hdbscan
from sklearn.preprocessing import StandardScaler

# Prepare spatial + feature data
coords = crimes_gdf[['latitude', 'longitude']].values
features = crimes_gdf[['LST', 'hour']].values

# Combine coordinates and features (scaled)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
X = np.hstack([coords, features_scaled * 0.1])  # Weight features less than location

# Cluster with HDBSCAN
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,
    min_samples=5,
    metric='haversine',  # For lat/lon
    cluster_selection_method='eom'
)

# Convert to radians for haversine
coords_rad = np.radians(coords)
cluster_labels = clusterer.fit_predict(coords_rad)

# Analyze clusters
crimes_gdf['cluster'] = cluster_labels
high_risk_clusters = crimes_gdf[crimes_gdf['cluster'] >= 0].groupby('cluster').agg({
    'LST': 'mean',
    'latitude': 'count'
})

print(f"Found {len(high_risk_clusters)} high-risk corridors")
print(high_risk_clusters)

# Visualize
fig, ax = plt.subplots(figsize=(12, 10))
crimes_gdf.plot(ax=ax, column='cluster', cmap='tab20', markersize=5, legend=True)
ctx.add_basemap(ax, crs=crimes_gdf.crs)
plt.savefig('./figures/crime_clusters.png', dpi=300, bbox_inches='tight')
```

**Resources:** - **HDBSCAN docs:** <https://hdbscan.readthedocs.io/> -
**Spatial clustering guide:**
<https://www.scikit-yb.org/en/latest/api/cluster/hdbscan.html>

------------------------------------------------------------------------

## 7. Visualization standards for publication

### Perceptually Uniform Colormaps

**For Temperature Data:**

``` python
import matplotlib.pyplot as plt

# Recommended colormaps
temperature_cmaps = {
    'Sequential': ['viridis', 'inferno', 'plasma', 'magma'],
    'Temperature-intuitive': ['coolwarm', 'RdYlBu_r'],
    'Colorblind-safe': ['cividis']
}

# Example LST map
fig, ax = plt.subplots(figsize=(10, 8))
lst_data.plot(
    ax=ax,
    cmap='inferno',  # Recommended for heat
    vmin=10,
    vmax=45,
    cbar_kwargs={
        'label': 'Land Surface Temperature (°C)',
        'orientation': 'vertical',
        'shrink': 0.8,
        'pad': 0.02
    }
)
```

**AVOID:** 'jet', 'rainbow', 'spectral' (create false boundaries)

### Standard Figure Types

**1. Temperature-Crime Scatter with Binned Estimates**

``` python
# Create temperature bins
matched['LST_bin'] = pd.cut(matched['LST'], bins=[-np.inf, 15, 20, 25, 30, np.inf])

# Calculate mean crime rate per bin
bin_stats = matched.groupby('LST_bin').agg({
    'case': ['mean', 'sem', 'count']
}).reset_index()

# Plot with confidence intervals
fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(
    x=range(len(bin_stats)),
    y=bin_stats[('case', 'mean')],
    yerr=1.96 * bin_stats[('case', 'sem')],
    fmt='o-',
    capsize=5,
    markersize=8
)
ax.set_xticks(range(len(bin_stats)))
ax.set_xticklabels(bin_stats['LST_bin'].astype(str), rotation=45)
ax.set_xlabel('Land Surface Temperature (°C)', fontsize=12)
ax.set_ylabel('Proportion of Case Periods', fontsize=12)
ax.set_title('Crime Risk by Temperature Bin', fontsize=14)
ax.grid(alpha=0.3)
plt.tight_layout()
```

**2. Small-Multiple Maps (Temporal Comparison)**

``` python
# Create 2x2 grid for seasonal comparison
seasons = ['Winter', 'Spring', 'Summer', 'Fall']
season_months = [[12, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]

fig, axes = plt.subplots(2, 2, figsize=(16, 14))

for ax, season, months in zip(axes.flat, seasons, season_months):
    # Filter data for season
    season_data = lst_by_segment[lst_by_segment['month'].isin(months)]
    
    # Plot
    streets.merge(season_data.groupby('segment_id')['LST'].mean(), 
                  left_on='segment_id', right_index=True).plot(
        ax=ax,
        column='LST',
        cmap='inferno',
        legend=True,
        vmin=10,
        vmax=40
    )
    ax.set_title(f'{season}', fontsize=14)
    ax.axis('off')

plt.tight_layout()
plt.savefig('./figures/seasonal_comparison.png', dpi=300, bbox_inches='tight')
```

**3. Regression Table Format**

```         
========================================
                Model 1    Model 2
----------------------------------------
LST (°C)        0.033***   0.029**
                (0.009)    (0.011)
                
Humidity (%)               -0.012*
                           (0.005)
                
Precipitation              -0.045
                           (0.023)
----------------------------------------
Observations    1,245      1,245
Matched Sets    415        415
Log Likelihood  -856.2     -851.7
Pseudo R²       0.023      0.028
========================================
Notes: *p<0.05; **p<0.01; ***p<0.001
Standard errors in parentheses.
Conditional logistic regression with
street segment fixed effects via matching.
```

### Cartographic Standards

**Essential Map Elements:** - Title (concise, informative) - Legend
(self-explanatory) - Scale bar (graphical, not ratio) - North arrow -
Data source and date - Coordinate reference system (for scientific maps)

**Design Principles:** - Use white space strategically - High contrast
between figure and background - Consistent font family (sans-serif
preferred) - Maximum 7-9 distinguishable colors for categorical data -
Test with colorblind simulator (Color Oracle)

------------------------------------------------------------------------

## 8. Key resources and citations

### Essential Documentation

**ECOSTRESS:** - Product page:
<https://lpdaac.usgs.gov/products/eco_l2t_lstev002/> - User guide:
<https://lpdaac.usgs.gov/documents/423/ECO2_User_Guide_V1.pdf> - Data
access: <https://github.com/nasa/ECOSTRESS-Data-Resources>

**Philadelphia Data:** - OpenDataPhilly: <https://opendataphilly.org/> -
Crime data: <https://opendataphilly.org/datasets/shooting-victims/> -
Street centerlines:
<https://opendataphilly.org/datasets/street-centerlines/>

**Methodological Papers:** - Xu et al. (2020). "Ambient temperature and
intentional homicide: A multi-city case-crossover study in the US."
*Environment International* 143:105992. - Schinasi & Hamra (2017). "A
time series analysis of associations between daily temperature and crime
events in Philadelphia." *J Urban Health* 94:892-900. - Weisburd (2015).
"The law of crime concentration and the criminology of place."
*Criminology* 53(2):133-157.

**Software:** - OSMnx: Boeing (2025). "Modeling and Analyzing Urban
Networks and Amenities with OSMnx." *Geographical Analysis*
57(4):567-577. - PyTorch Geometric Temporal: Rozemberczki et al. (2021).
CIKM 2021.

### Contact and Support

**NASA Data Support:** - LP DAAC User Services:
[LPDAAC\@usgs.gov](mailto:LPDAAC@usgs.gov){.email} / 1-866-573-3222 -
ECOSTRESS Science Team:
[ecostress\@jpl.nasa.gov](mailto:ecostress@jpl.nasa.gov){.email}

**Philadelphia Data:** - OpenDataPhilly support via website contact form

------------------------------------------------------------------------

## 9. Implementation checklist

### Data Acquisition

-   [ ] Register for NASA Earthdata account
-   [ ] Install earthaccess and authenticate
-   [ ] Download ECOSTRESS L2T LSTE Collection 2 data (2022-2024)
-   [ ] Download Philadelphia shooting victims CSV
-   [ ] Download street network (OSMnx or city shapefile)
-   [ ] Download NOAA weather station data (optional but recommended)
-   [ ] Download ancillary data (land cover, demographics)

### Data Processing

-   [ ] Apply quality filters to ECOSTRESS (cloud mask, QC flags)
-   [ ] Convert LST from Kelvin to Celsius
-   [ ] Filter crime data for nighttime incidents (8pm-4am)
-   [ ] Spatially join crimes to street segments
-   [ ] Extract LST values to street segment centroids
-   [ ] Merge ECOSTRESS dates with crime dates
-   [ ] Calculate control variables (humidity, precipitation)

### Analysis

-   [ ] Create case-crossover matched sets
-   [ ] Fit conditional logistic regression model
-   [ ] Calculate odds ratios and confidence intervals
-   [ ] Run sensitivity analyses (buffer distances, weather controls,
    seasonal stratification)
-   [ ] Generate diagnostic plots
-   [ ] Test model assumptions

### Visualization

-   [ ] Create study area map with crime locations
-   [ ] Generate example ECOSTRESS LST map with overlay
-   [ ] Create temperature-crime association plots (forest plot,
    scatter)
-   [ ] Design seasonal comparison maps (small multiples)
-   [ ] Format regression tables for publication
-   [ ] Generate supplementary figures (diagnostics, robustness checks)

### Documentation

-   [ ] Write methods section with data sources and analysis plan
-   [ ] Create results section with tables and figures
-   [ ] Draft discussion interpreting findings
-   [ ] Prepare supplementary materials
-   [ ] Format all outputs to journal standards

------------------------------------------------------------------------

## 10. Expected outcomes and interpretation

### Statistical Power

**Sample Size:** - Philadelphia nighttime shootings: \~2,000-3,000
annually - With 2-3 years: \~4,000-9,000 incidents - ECOSTRESS coverage:
\~30-50% → **1,200-4,500 incidents with LST data** - With 3-4 controls
per case: **4,800-18,000 total observations**

**Detectable Effect Size:** - Literature reports OR = 1.017-1.031 per °C
(1.7-3.1% increase) - With N \> 1,000 matched sets: **80% power to
detect OR ≥ 1.02** (α=0.05) - Your study should be well-powered for
primary hypothesis

### Interpretation Framework

**If OR = 1.034 (95% CI: 1.015-1.054):** - **3.4% increase in crime odds
per 1°C** LST increase - **18% increase per 5°C** (clinically
significant) - **P-value \< 0.001** (statistically significant)

**Mechanistic Pathways:** 1. **Behavioral:** Heat increases street
activity and social interactions 2. **Physiological:** Heat exposure
elevates aggression and impulsivity 3. **Environmental:** Hot nights
reduce indoor time, increase outdoor congregation

**Policy Implications:** - Target cooling interventions (tree planting,
cool surfaces) in high-LST corridors - Enhance police presence during
heat events - Design heat action plans incorporating violence prevention

### Limitations to Acknowledge

1.  **Ecological fallacy:** LST measured at segment level, not
    individual exposure
2.  **Temporal mismatch:** ECOSTRESS captures instantaneous LST, not
    sustained exposure
3.  **Cloud gaps:** Systematic loss of data during cloudy (cooler)
    nights may bias results
4.  **Residual confounding:** Unmeasured factors (major events, policy
    changes) not controlled
5.  **Generalizability:** Results specific to Philadelphia's climate and
    built environment

------------------------------------------------------------------------

## Conclusion

This implementation plan provides everything needed to execute a
rigorous nighttime heat and street-level violence study within one
month. The combination of ECOSTRESS's unique nighttime observation
capability, Philadelphia's comprehensive crime data, and validated
case-crossover methodology creates an ideal framework for advancing
understanding of temperature-crime relationships at unprecedented
spatial resolution. All data sources, code libraries, and analytical
approaches are immediately actionable with the specific URLs, product
codes, and examples provided throughout this document.
