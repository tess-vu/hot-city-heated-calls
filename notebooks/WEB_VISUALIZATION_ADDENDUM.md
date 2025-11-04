---
editor_options: 
  markdown: 
    wrap: 72
---

# Web Visualization Addendum: Interactive Heat-Crime Maps for Public Engagement

## Overview: Python Analysis → JavaScript Visualization Pipeline

This addendum extends the core implementation plan to support
**interactive web visualizations** alongside static academic figures.
The workflow separates analysis (Python) from presentation (JavaScript),
allowing you to publish findings on websites, create interactive
dashboards, and engage broader audiences beyond academic journals.

**Core Philosophy:** - **Python for heavy lifting:** Data processing,
statistical analysis, ML models - **JavaScript for interaction:**
Dynamic maps, filtering, animations, storytelling - **JSON/GeoJSON
bridge:** Lightweight data formats both ecosystems understand

------------------------------------------------------------------------

## 1. Modified Folder Structure for Web Outputs

```         
project/
  data_raw/
  data_intermediate/
  data_final/
  src/
  models/
  figures/                    # Static publication figures
  web_assets/                 # NEW: Web-ready data exports
    data/
      geojson/                # Vector data for web maps
      tiles/                  # Optional: raster tiles for large datasets
      json/                   # Time series, statistics for charts
    static/                   # CSS, images, fonts
    js/                       # JavaScript visualization code
    index.html                # Main web page
  notebooks/
```

------------------------------------------------------------------------

## 2. Python Libraries for Web-Ready Exports

### Essential Additions to Environment

``` bash
# Add to your existing conda environment
pip install folium mapbox mapboxgl geopandas plotly keplergl pydeck

# For advanced web mapping
pip install geojsonio mercantile mbtiles

# For data serialization
pip install geojson topojson ujson
```

### Key Libraries for Python → Web Workflow

**Folium** (Leaflet.js wrapper) - **Use case:** Quick interactive maps
without writing JavaScript - **Export:** Self-contained HTML files

``` python
import folium
from folium.plugins import HeatMap, MarkerCluster

# Create base map
m = folium.Map(
    location=[39.95, -75.16],
    zoom_start=12,
    tiles='CartoDB dark_matter'
)

# Add heatmap layer
heat_data = [[row['lat'], row['lng']] for idx, row in crimes_gdf.iterrows()]
HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(m)

# Save
m.save('./web_assets/crime_heatmap.html')
```

**Plotly** (Cross-platform) - **Use case:** Interactive charts that work
in Python notebooks AND web - **Export:** HTML or JSON for Plotly.js

``` python
import plotly.graph_objects as go
import plotly.express as px

# Create interactive scatter
fig = px.scatter(
    matched_df,
    x='LST',
    y='case',
    color='season',
    hover_data=['date', 'segment_id'],
    title='Temperature-Crime Association'
)

# Export as HTML
fig.write_html('./web_assets/scatter_interactive.html')

# Export as JSON for custom JS visualization
fig.write_json('./web_assets/data/json/scatter_data.json')
```

**Kepler.gl** (Uber's geospatial tool) - **Use case:** Large-scale
spatiotemporal data exploration - **Export:** Standalone HTML with
advanced filters

``` python
from keplergl import KeplerGl

# Create map with multiple layers
map_1 = KeplerGl(height=600)
map_1.add_data(data=crimes_gdf, name='crimes')
map_1.add_data(data=streets_with_lst, name='street_temps')

# Save with custom config
map_1.save_to_html(file_name='./web_assets/kepler_map.html')
```

**PyDeck** (deck.gl wrapper) - **Use case:** WebGL-powered 3D
visualizations - **Export:** HTML or JSON for deck.gl

``` python
import pydeck as pdk

# 3D hexagon layer for crime density
layer = pdk.Layer(
    'HexagonLayer',
    data=crimes_gdf,
    get_position='[lng, lat]',
    radius=100,
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
)

# Create view
view_state = pdk.ViewState(
    longitude=-75.16,
    latitude=39.95,
    zoom=11,
    pitch=45
)

# Render and save
r = pdk.Deck(layers=[layer], initial_view_state=view_state)
r.to_html('./web_assets/3d_crime_density.html')
```

------------------------------------------------------------------------

## 3. Export Data Formats for JavaScript Consumption

### GeoJSON: The Web Mapping Standard

**Export Street Segments with LST:**

``` python
import geopandas as gpd
import json

# Prepare data
streets_web = streets[['segment_id', 'geometry', 'LST_mean', 'crime_count']].copy()

# Simplify geometries to reduce file size
streets_web['geometry'] = streets_web.geometry.simplify(0.0001)

# Export as GeoJSON
streets_web.to_file(
    './web_assets/data/geojson/streets_with_temp.geojson',
    driver='GeoJSON'
)

# Alternative: Export as TopoJSON (50-80% smaller)
# Requires: pip install topojson
import topojson as tp
topo = tp.Topology(streets_web, prequantize=1e5)
with open('./web_assets/data/geojson/streets_with_temp.topojson', 'w') as f:
    f.write(topo.to_json())
```

**Export Crime Points with Temporal Data:**

``` python
# Add temporal attributes
crimes_web = crimes_gdf[['date', 'time', 'lat', 'lng', 'LST', 'hour', 'month']].copy()
crimes_web['datetime'] = pd.to_datetime(crimes_web['date'] + ' ' + crimes_web['time'])
crimes_web['timestamp'] = crimes_web['datetime'].astype(int) // 10**9  # Unix timestamp

# Convert to GeoJSON
crimes_geojson = crimes_web.__geo_interface__

# Save
with open('./web_assets/data/geojson/crimes_temporal.geojson', 'w') as f:
    json.dump(crimes_geojson, f)
```

### JSON for Time Series and Statistics

**Export Aggregated Data for Charts:**

``` python
# Monthly crime counts with average temperature
monthly_stats = matched_df.groupby(['year', 'month']).agg({
    'case': 'sum',
    'LST': 'mean'
}).reset_index()

monthly_stats['date'] = pd.to_datetime(monthly_stats[['year', 'month']].assign(day=1))
monthly_stats['date_str'] = monthly_stats['date'].dt.strftime('%Y-%m-%d')

# Export as JSON
monthly_json = monthly_stats[['date_str', 'case', 'LST']].to_dict(orient='records')

with open('./web_assets/data/json/monthly_trends.json', 'w') as f:
    json.dump(monthly_json, f, indent=2)
```

**Export Model Results:**

``` python
# Create results object
results_json = {
    'primary_model': {
        'OR': float(OR),
        'CI_lower': float(CI_lower),
        'CI_upper': float(CI_upper),
        'p_value': float(p_value),
        'interpretation': f"{((OR-1)*100):.1f}% increase per °C"
    },
    'sensitivity_analyses': [
        {
            'name': 'With weather controls',
            'OR': 1.029,
            'CI': [1.008, 1.051]
        },
        # ... more models
    ],
    'sample_stats': {
        'total_crimes': int(n_crimes),
        'matched_sets': int(n_matched),
        'date_range': [start_date, end_date]
    }
}

with open('./web_assets/data/json/model_results.json', 'w') as f:
    json.dump(results_json, f, indent=2)
```

### CSV for Simple Tables

**Export Segment-Level Risk Scores:**

``` python
# Calculate risk score for each segment
segment_risk = streets.groupby('segment_id').agg({
    'crime_count': 'sum',
    'LST_mean': 'mean',
    'population': 'first'
}).reset_index()

segment_risk['risk_score'] = (
    segment_risk['crime_count'] / segment_risk['population'] * 1000
)

# Export as CSV (smaller and faster to parse than JSON for tabular data)
segment_risk.to_csv('./web_assets/data/json/segment_risk.csv', index=False)
```

------------------------------------------------------------------------

## 4. JavaScript Mapping Libraries: Detailed Guide

### Mapbox GL JS (Recommended for Main Map)

**Why Mapbox:** - **Vector tiles:** Smooth zooming, dynamic styling -
**Performance:** Handles 100k+ features without lag - **3D support:**
Terrain, buildings, custom extrusions - **Styling:** Full cartographic
control via Mapbox Studio

**Setup:**

``` html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8' />
    <title>Nighttime Heat and Violence in Philadelphia</title>
    <meta name='viewport' content='width=device-width, initial-scale=1' />
    <script src='https://api.mapbox.com/mapbox-gl-js/v3.0.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v3.0.0/mapbox-gl.css' rel='stylesheet' />
    <style>
        body { margin: 0; padding: 0; }
        #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        .legend {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 3px;
            bottom: 30px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            padding: 10px;
            position: absolute;
            right: 10px;
            z-index: 1;
        }
    </style>
</head>
<body>
    <div id='map'></div>
    <div class='legend' id='legend'></div>
    <script src='js/main.js'></script>
</body>
</html>
```

**Main JavaScript (js/main.js):**

``` javascript
mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN'; // Get free token at mapbox.com

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [-75.16, 39.95],
    zoom: 11,
    pitch: 45, // 3D view
    bearing: -17.6
});

map.on('load', async () => {
    // Load street temperature data
    const streetsResponse = await fetch('data/geojson/streets_with_temp.geojson');
    const streetsData = await streetsResponse.json();
    
    // Add source
    map.addSource('streets-temp', {
        type: 'geojson',
        data: streetsData
    });
    
    // Add layer with data-driven styling
    map.addLayer({
        id: 'streets-heat',
        type: 'line',
        source: 'streets-temp',
        paint: {
            'line-color': [
                'interpolate',
                ['linear'],
                ['get', 'LST_mean'],
                10, '#3288bd',  // Cool (blue)
                20, '#66c2a5',
                25, '#fee08b',
                30, '#fc8d59',
                40, '#d53e4f'   // Hot (red)
            ],
            'line-width': [
                'interpolate',
                ['linear'],
                ['get', 'crime_count'],
                0, 2,
                5, 6
            ],
            'line-opacity': 0.8
        }
    });
    
    // Add crime points
    const crimesResponse = await fetch('data/geojson/crimes_temporal.geojson');
    const crimesData = await crimesResponse.json();
    
    map.addSource('crimes', {
        type: 'geojson',
        data: crimesData
    });
    
    map.addLayer({
        id: 'crime-points',
        type: 'circle',
        source: 'crimes',
        paint: {
            'circle-radius': [
                'interpolate',
                ['linear'],
                ['zoom'],
                10, 3,
                15, 8
            ],
            'circle-color': '#ff4444',
            'circle-opacity': 0.7,
            'circle-stroke-width': 1,
            'circle-stroke-color': '#ffffff'
        }
    });
    
    // Add interactivity
    map.on('click', 'streets-heat', (e) => {
        const props = e.features[0].properties;
        new mapboxgl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`
                <h3>Street Segment ${props.segment_id}</h3>
                <p><strong>Avg Temperature:</strong> ${props.LST_mean.toFixed(1)}°C</p>
                <p><strong>Crime Count:</strong> ${props.crime_count}</p>
            `)
            .addTo(map);
    });
    
    // Change cursor on hover
    map.on('mouseenter', 'streets-heat', () => {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'streets-heat', () => {
        map.getCanvas().style.cursor = '';
    });
    
    // Create legend
    createLegend();
});

function createLegend() {
    const legend = document.getElementById('legend');
    const colors = ['#3288bd', '#66c2a5', '#fee08b', '#fc8d59', '#d53e4f'];
    const labels = ['10°C', '20°C', '25°C', '30°C', '40°C'];
    
    legend.innerHTML = '<h4 style="margin-top:0;">Land Surface Temperature</h4>';
    colors.forEach((color, i) => {
        legend.innerHTML += `
            <div>
                <span style="background-color:${color};display:inline-block;width:20px;height:10px;"></span>
                <span>${labels[i]}</span>
            </div>
        `;
    });
}
```

### Leaflet.js (Open-Source Alternative)

**When to use:** Simpler projects, no Mapbox account needed, full
control

**Setup:**

``` html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

**Implementation:**

``` javascript
// Initialize map
const map = L.map('map').setView([39.95, -75.16], 12);

// Add basemap
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Load and display GeoJSON
fetch('data/geojson/streets_with_temp.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            style: function(feature) {
                return {
                    color: getColor(feature.properties.LST_mean),
                    weight: feature.properties.crime_count > 3 ? 4 : 2,
                    opacity: 0.8
                };
            },
            onEachFeature: function(feature, layer) {
                layer.bindPopup(`
                    <b>Segment ${feature.properties.segment_id}</b><br>
                    Temperature: ${feature.properties.LST_mean.toFixed(1)}°C<br>
                    Crimes: ${feature.properties.crime_count}
                `);
            }
        }).addTo(map);
    });

function getColor(temp) {
    return temp > 35 ? '#d53e4f' :
           temp > 30 ? '#fc8d59' :
           temp > 25 ? '#fee08b' :
           temp > 20 ? '#66c2a5' :
                       '#3288bd';
}
```

### D3.js for Custom Visualizations

**Use case:** Highly customized, publication-quality interactive charts

**Time Series with Brushing:**

``` html
<script src="https://d3js.org/d3.v7.min.js"></script>
<div id="chart"></div>
<script>
// Load data
d3.json('data/json/monthly_trends.json').then(data => {
    // Parse dates
    data.forEach(d => {
        d.date = new Date(d.date_str);
        d.crime_count = +d.case;
        d.temperature = +d.LST;
    });
    
    // Set dimensions
    const margin = {top: 20, right: 60, bottom: 30, left: 60};
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select('#chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Scales
    const x = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width]);
    
    const y1 = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.crime_count)])
        .range([height, 0]);
    
    const y2 = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.temperature)])
        .range([height, 0]);
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .call(d3.axisLeft(y1))
        .append('text')
        .attr('fill', '#000')
        .attr('transform', 'rotate(-90)')
        .attr('y', -50)
        .attr('x', -height/2)
        .attr('text-anchor', 'middle')
        .text('Crime Count');
    
    svg.append('g')
        .attr('transform', `translate(${width},0)`)
        .call(d3.axisRight(y2))
        .append('text')
        .attr('fill', '#000')
        .attr('transform', 'rotate(-90)')
        .attr('y', 50)
        .attr('x', -height/2)
        .attr('text-anchor', 'middle')
        .text('Temperature (°C)');
    
    // Line generators
    const line1 = d3.line()
        .x(d => x(d.date))
        .y(d => y1(d.crime_count));
    
    const line2 = d3.line()
        .x(d => x(d.date))
        .y(d => y2(d.temperature));
    
    // Draw lines
    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#e74c3c')
        .attr('stroke-width', 2)
        .attr('d', line1);
    
    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#f39c12')
        .attr('stroke-width', 2)
        .attr('d', line2);
    
    // Add tooltip
    const tooltip = d3.select('body')
        .append('div')
        .style('position', 'absolute')
        .style('background', 'rgba(0,0,0,0.8)')
        .style('color', 'white')
        .style('padding', '8px')
        .style('border-radius', '4px')
        .style('display', 'none');
    
    svg.selectAll('.dot')
        .data(data)
        .enter().append('circle')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y1(d.crime_count))
        .attr('r', 4)
        .attr('fill', '#e74c3c')
        .on('mouseover', (event, d) => {
            tooltip.style('display', 'block')
                .html(`
                    Date: ${d.date.toLocaleDateString()}<br>
                    Crimes: ${d.crime_count}<br>
                    Temp: ${d.temperature.toFixed(1)}°C
                `);
        })
        .on('mousemove', (event) => {
            tooltip.style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', () => {
            tooltip.style('display', 'none');
        });
});
</script>
```

------------------------------------------------------------------------

## 5. Advanced Features for Web Engagement

### Temporal Animation

**Animate Crime Events Over Time:**

``` javascript
// In Mapbox GL JS
let currentFrame = 0;
const frames = crimesData.features.sort((a, b) => 
    a.properties.timestamp - b.properties.timestamp
);

function animateFrame() {
    const visibleFeatures = frames.slice(0, currentFrame);
    
    map.getSource('crimes').setData({
        type: 'FeatureCollection',
        features: visibleFeatures
    });
    
    currentFrame = (currentFrame + 10) % frames.length;
    
    // Update date display
    document.getElementById('current-date').textContent = 
        new Date(frames[currentFrame].properties.timestamp * 1000)
            .toLocaleDateString();
}

// Start animation
setInterval(animateFrame, 50); // 20 fps

// Add play/pause controls
document.getElementById('play-btn').addEventListener('click', () => {
    // Toggle animation
});
```

### Interactive Filtering

**Filter by Temperature Range:**

``` javascript
// Add slider control
const slider = document.getElementById('temp-slider');
const output = document.getElementById('temp-value');

slider.addEventListener('input', function() {
    const minTemp = parseFloat(this.value);
    output.textContent = `${minTemp}°C`;
    
    // Update map filter
    map.setFilter('streets-heat', ['>=', ['get', 'LST_mean'], minTemp]);
    map.setFilter('crime-points', ['>=', ['get', 'LST'], minTemp]);
});

// HTML for slider
// <input type="range" min="10" max="40" value="10" id="temp-slider">
// <span id="temp-value">10°C</span>
```

### Storytelling with Scrollytelling

**Use Scrollama.js for narrative:**

``` html
<script src="https://unpkg.com/intersection-observer@0.12.0/intersection-observer.js"></script>
<script src="https://unpkg.com/scrollama"></script>

<div id='scrolly'>
    <div class='sticky-thing'>
        <div id='map'></div>
    </div>
    <div class='steps'>
        <div class='step' data-step='1'>
            <h2>Philadelphia's Hottest Nights</h2>
            <p>On July 20, 2023, surface temperatures exceeded 40°C...</p>
        </div>
        <div class='step' data-step='2'>
            <h2>Crime Concentration</h2>
            <p>During that same night, 15 shooting incidents occurred...</p>
        </div>
        <div class='step' data-step='3'>
            <h2>The Temperature Connection</h2>
            <p>Our analysis reveals a 3.4% increase in crime odds per °C...</p>
        </div>
    </div>
</div>

<script>
const scroller = scrollama();

scroller
    .setup({
        step: '.step',
        offset: 0.5,
    })
    .onStepEnter(response => {
        const step = response.element.dataset.step;
        
        if (step === '1') {
            map.flyTo({center: [-75.16, 39.95], zoom: 11});
            map.setLayoutProperty('streets-heat', 'visibility', 'visible');
        } else if (step === '2') {
            map.flyTo({center: [-75.15, 39.97], zoom: 13});
            map.setLayoutProperty('crime-points', 'visibility', 'visible');
        } else if (step === '3') {
            // Show comparison view
        }
    });
</script>
```

### Dashboard with Charts

**Use Chart.js for simple dashboards:**

``` html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div class="dashboard">
    <div class="chart-container">
        <canvas id="tempChart"></canvas>
    </div>
    <div class="chart-container">
        <canvas id="crimeChart"></canvas>
    </div>
</div>

<script>
fetch('data/json/monthly_trends.json')
    .then(r => r.json())
    .then(data => {
        // Temperature trend
        new Chart(document.getElementById('tempChart'), {
            type: 'line',
            data: {
                labels: data.map(d => d.date_str),
                datasets: [{
                    label: 'Avg Temperature (°C)',
                    data: data.map(d => d.LST),
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Temperature Trends'
                    }
                }
            }
        });
        
        // Crime trend
        new Chart(document.getElementById('crimeChart'), {
            type: 'bar',
            data: {
                labels: data.map(d => d.date_str),
                datasets: [{
                    label: 'Crime Count',
                    data: data.map(d => d.case),
                    backgroundColor: '#e74c3c'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Crime Incidents'
                    }
                }
            }
        });
    });
</script>
```

------------------------------------------------------------------------

## 6. Modern Web Frameworks

### Observable Framework (Recommended for Data Journalism)

**Why Observable:** - Live coding environment (like Jupyter for
JavaScript) - Built-in reactivity (data changes automatically update
visualizations) - Easy deployment to Observable.com or GitHub Pages -
Excellent for exploratory analysis → publication pipeline

**Getting Started:**

``` bash
npm install @observablehq/framework -g
observable create heat-crime-viz
cd heat-crime-viz
observable preview
```

**Example Observable Notebook:**

``` javascript
// Load data
data = FileAttachment("data/json/monthly_trends.json").json()

// Create chart
Plot.plot({
  marks: [
    Plot.line(data, {x: "date_str", y: "LST", stroke: "orange"}),
    Plot.line(data, {x: "date_str", y: "case", stroke: "red"}),
    Plot.ruleY([0])
  ],
  y: {
    grid: true,
    label: "Temperature (°C) / Crime Count"
  },
  color: {
    legend: true
  }
})
```

### Svelte for Interactive Apps

**Why Svelte:** - Minimal JavaScript framework (no virtual DOM
overhead) - Reactive by default (variables automatically update UI) -
Great for complex dashboards

**Quick Setup:**

``` bash
npm create vite@latest heat-crime-app -- --template svelte
cd heat-crime-app
npm install
npm install mapbox-gl d3
```

**Example Component (App.svelte):**

``` svelte
<script>
  import { onMount } from 'svelte';
  import mapboxgl from 'mapbox-gl';
  
  let map;
  let selectedTemp = 25;
  let crimeCount = 0;
  
  onMount(() => {
    mapboxgl.accessToken = 'YOUR_TOKEN';
    map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [-75.16, 39.95],
      zoom: 11
    });
    
    map.on('load', loadData);
  });
  
  function loadData() {
    // Load and filter by temperature
    fetch('/data/geojson/crimes_temporal.geojson')
      .then(r => r.json())
      .then(data => {
        const filtered = data.features.filter(f => 
          f.properties.LST >= selectedTemp
        );
        crimeCount = filtered.length;
        
        map.addSource('crimes', {
          type: 'geojson',
          data: { ...data, features: filtered }
        });
        
        map.addLayer({
          id: 'crime-points',
          type: 'circle',
          source: 'crimes',
          paint: {
            'circle-radius': 6,
            'circle-color': '#ff4444'
          }
        });
      });
  }
  
  function updateFilter() {
    loadData(); // Reload with new filter
  }
</script>

<main>
  <div id="map"></div>
  <div class="controls">
    <label>
      Minimum Temperature: {selectedTemp}°C
      <input 
        type="range" 
        min="10" 
        max="40" 
        bind:value={selectedTemp}
        on:input={updateFilter}
      />
    </label>
    <p>Crimes shown: {crimeCount}</p>
  </div>
</main>

<style>
  #map { width: 100%; height: 80vh; }
  .controls {
    position: absolute;
    top: 10px;
    left: 10px;
    background: white;
    padding: 15px;
    border-radius: 5px;
  }
</style>
```

------------------------------------------------------------------------

## 7. Deployment and Hosting

### GitHub Pages (Free, Simple)

**Setup:**

``` bash
# Build static site
cd project
mkdir docs
cp -r web_assets/* docs/

# Push to GitHub
git add docs/
git commit -m "Add web visualization"
git push

# Enable GitHub Pages in repo settings → Pages → Source: docs/
# Your site: https://username.github.io/repo-name/
```

### Netlify (Free, Auto-Deploy)

**Setup:**

``` bash
# Create netlify.toml
cat > netlify.toml << EOF
[build]
  publish = "web_assets"
  
[[headers]]
  for = "/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
EOF

# Deploy via Netlify CLI
npm install -g netlify-cli
netlify deploy --prod --dir=web_assets
```

### Observable (Best for Data Journalism)

**Publish directly:** 1. Create notebook at observablehq.com 2. Upload
data files 3. Build visualizations 4. Click "Publish" → Public link

**Self-host Observable Framework:**

``` bash
observable build
# Outputs to dist/ directory
# Deploy dist/ to any static host
```

### Custom Server (For Dynamic Features)

**Express.js backend (if needed):**

``` javascript
// server.js
const express = require('express');
const app = express();

app.use(express.static('web_assets'));

// API endpoint for dynamic queries
app.get('/api/crimes', (req, res) => {
  const { minTemp, maxTemp } = req.query;
  // Query database and return filtered JSON
  res.json(filteredCrimes);
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

------------------------------------------------------------------------

## 8. Performance Optimization

### Vector Tiles for Large Datasets

**When to use:** \> 10,000 features, complex geometries

**Create tiles with Tippecanoe:**

``` bash
# Install Tippecanoe
brew install tippecanoe  # macOS
# Or: https://github.com/felt/tippecanoe

# Convert GeoJSON to MBTiles
tippecanoe -o streets_tiles.mbtiles \
  --maximum-zoom=14 \
  --minimum-zoom=10 \
  --drop-densest-as-needed \
  streets_with_temp.geojson

# Upload to Mapbox Studio or serve locally
```

**Serve tiles with tileserver-gl:**

``` bash
npm install -g tileserver-gl-light
tileserver-gl-light streets_tiles.mbtiles
# Access at http://localhost:8080
```

### Data Simplification

**Reduce GeoJSON file size:**

``` python
import geopandas as gpd
from shapely.geometry import shape, mapping
import json

# Load data
gdf = gpd.read_file('streets_with_temp.geojson')

# Simplify geometries (tolerance in degrees)
gdf['geometry'] = gdf.geometry.simplify(0.0001, preserve_topology=True)

# Remove unnecessary columns
gdf_minimal = gdf[['segment_id', 'LST_mean', 'crime_count', 'geometry']]

# Round numeric values
gdf_minimal['LST_mean'] = gdf_minimal['LST_mean'].round(1)

# Export
gdf_minimal.to_file('streets_simplified.geojson', driver='GeoJSON')

# Further compression with gzip
import gzip
with open('streets_simplified.geojson', 'rb') as f_in:
    with gzip.open('streets_simplified.geojson.gz', 'wb') as f_out:
        f_out.writelines(f_in)
```

### Lazy Loading

**Load data only when needed:**

``` javascript
// Load base map immediately
const map = new mapboxgl.Map({...});

// Load heavy datasets on user interaction
document.getElementById('show-crimes-btn').addEventListener('click', async () => {
  if (!map.getSource('crimes')) {
    const data = await fetch('data/geojson/crimes_temporal.geojson').then(r => r.json());
    map.addSource('crimes', { type: 'geojson', data });
    map.addLayer({
      id: 'crime-points',
      type: 'circle',
      source: 'crimes',
      paint: { 'circle-radius': 6, 'circle-color': '#ff4444' }
    });
  } else {
    // Toggle visibility
    const visibility = map.getLayoutProperty('crime-points', 'visibility');
    map.setLayoutProperty('crime-points', 'visibility', 
      visibility === 'visible' ? 'none' : 'visible');
  }
});
```

------------------------------------------------------------------------

## 9. Accessibility and Usability

### Colorblind-Safe Palettes

**Use ColorBrewer schemes:**

``` javascript
// In Mapbox style expression
const colorblindSafePalette = [
  '#2166ac', // Blue
  '#4393c3',
  '#92c5de',
  '#fddbc7',
  '#f4a582',
  '#d6604d',
  '#b2182b'  // Red
];

map.setPaintProperty('streets-heat', 'line-color', [
  'interpolate',
  ['linear'],
  ['get', 'LST_mean'],
  10, colorblindSafePalette[0],
  15, colorblindSafePalette[1],
  20, colorblindSafePalette[2],
  25, colorblindSafePalette[3],
  30, colorblindSafePalette[4],
  35, colorblindSafePalette[5],
  40, colorblindSafePalette[6]
]);
```

### Keyboard Navigation

``` javascript
// Make map keyboard-accessible
map.getCanvas().setAttribute('tabindex', '0');

map.getCanvas().addEventListener('keydown', (e) => {
  const step = 0.01;
  const center = map.getCenter();
  
  switch(e.key) {
    case 'ArrowUp':
      map.panTo([center.lng, center.lat + step]);
      break;
    case 'ArrowDown':
      map.panTo([center.lng, center.lat - step]);
      break;
    case 'ArrowLeft':
      map.panTo([center.lng - step, center.lat]);
      break;
    case 'ArrowRight':
      map.panTo([center.lng + step, center.lat]);
      break;
    case '+':
      map.zoomIn();
      break;
    case '-':
      map.zoomOut();
      break;
  }
});
```

### Screen Reader Support

``` html
<!-- Add ARIA labels -->
<div id="map" role="application" aria-label="Interactive map of Philadelphia showing nighttime temperature and crime locations">
  <div class="mapboxgl-canvas" aria-hidden="true"></div>
</div>

<!-- Provide text alternative -->
<div class="sr-only">
  <h2>Map Description</h2>
  <p>This map shows the relationship between land surface temperature and nighttime crime incidents in Philadelphia. Streets are colored by average temperature, with cooler areas in blue and hotter areas in red. Crime locations are marked with red points.</p>
</div>
```

------------------------------------------------------------------------

## 10. Updated Project Timeline with Web Development

### Week 4 (Revised): Static Figures + Initial Web Prototypes

**Days 22-23:** - Generate all static publication figures (as originally
planned) - Export web-ready data formats (GeoJSON, JSON, CSV)

**Days 24-25:** - Build basic Mapbox/Leaflet map with street temperature
layer - Add crime point overlay with popups - Implement simple filters
(temperature threshold, date range)

**Days 26-28:** - Create interactive charts (D3.js or Chart.js) - Add
temporal animation (optional) - Deploy to GitHub Pages for preview

### Week 5 (Optional Extension): Advanced Web Features

**Days 29-31:** - Implement scrollytelling narrative - Build dashboard
with multiple linked views - Add comparison tools (side-by-side maps)

**Days 32-33:** - Optimize performance (vector tiles, lazy loading) -
Test accessibility (keyboard nav, screen readers, colorblind) -
Cross-browser testing

**Days 34-35:** - Final deployment to production host - Create
documentation for web visualization - Share on social media, research
networks

------------------------------------------------------------------------

## 11. Complete Web Visualization Checklist

### Data Export

-   [ ] Export streets with LST as GeoJSON/TopoJSON
-   [ ] Export crime points with timestamps as GeoJSON
-   [ ] Create aggregated JSON for time series charts
-   [ ] Generate CSV for tabular data displays
-   [ ] Compress large files (gzip or vector tiles)

### Base Map

-   [ ] Choose mapping library (Mapbox GL JS vs Leaflet)
-   [ ] Set up project structure (index.html, CSS, JS)
-   [ ] Configure map style (dark/light, basemap tiles)
-   [ ] Test on mobile devices

### Data Layers

-   [ ] Add street temperature layer with color ramp
-   [ ] Add crime point layer with symbology
-   [ ] Implement layer toggles (show/hide)
-   [ ] Add legend with clear labels

### Interactivity

-   [ ] Popup/tooltip on click with segment info
-   [ ] Hover effects (cursor change, highlight)
-   [ ] Filter by temperature range (slider)
-   [ ] Filter by date/time (date picker or timeline)
-   [ ] Search/zoom to specific locations

### Visualization

-   [ ] Time series chart (temperature vs crime trends)
-   [ ] Scatter plot with regression line
-   [ ] Histogram of temperature distribution
-   [ ] Bar chart of monthly/seasonal patterns
-   [ ] Optional: 3D extrusion or heatmap layer

### Advanced Features (Optional)

-   [ ] Temporal animation with play/pause controls
-   [ ] Side-by-side comparison (hot vs cool nights)
-   [ ] Scrollytelling narrative
-   [ ] Dashboard with multiple coordinated views
-   [ ] Export/share functionality (permalink, image download)

### Performance

-   [ ] Optimize file sizes (\< 5MB for GeoJSON, \< 1MB for JSON)
-   [ ] Implement lazy loading for heavy datasets
-   [ ] Test load time (\< 3 seconds on 3G)
-   [ ] Add loading indicators

### Accessibility

-   [ ] Colorblind-safe palette
-   [ ] Keyboard navigation support
-   [ ] Screen reader compatible (ARIA labels)
-   [ ] High contrast mode option
-   [ ] Text alternatives for visual content

### Deployment

-   [ ] Test locally (all browsers: Chrome, Firefox, Safari)
-   [ ] Deploy to staging environment
-   [ ] Test on mobile (iOS Safari, Android Chrome)
-   [ ] Deploy to production (GitHub Pages, Netlify, etc.)
-   [ ] Set up custom domain (optional)
-   [ ] Add analytics (Google Analytics, Plausible)

### Documentation

-   [ ] Write README with usage instructions
-   [ ] Document data sources and methodology
-   [ ] Create "About" page explaining the project
-   [ ] Add contact information
-   [ ] License data and code (CC-BY, MIT, etc.)

------------------------------------------------------------------------

## 12. Resources for Learning JavaScript Mapping

### Free Courses

-   **Mapbox Tutorials:** <https://docs.mapbox.com/help/tutorials/>
-   **Observable Learn:** <https://observablehq.com/learn>
-   **D3 Gallery:**
    [https://observablehq.com/\@d3/gallery](https://observablehq.com/@d3/gallery){.uri}
-   **Leaflet Tutorials:** <https://leafletjs.com/examples.html>

### Books

-   *Interactive Data Visualization for the Web* by Scott Murray
    (O'Reilly)
-   *D3.js in Action* by Elijah Meeks (Manning)
-   *Web Cartography* by Ian Muehlenhaus (CRC Press)

### Example Projects

-   **Mapbox Crime Mapping:**
    <https://docs.mapbox.com/mapbox-gl-js/example/visualize-population-density/>
-   **Urban Heat Islands:**
    <https://www.bloomberg.com/graphics/2021-heat-islands/>
-   **NYT Climate Visualizations:**
    <https://www.nytimes.com/interactive/2020/04/19/climate/climate-crash-course-1.html>

### Communities

-   **Mapbox Community:**
    <https://github.com/mapbox/mapbox-gl-js/discussions>
-   **Observable Forum:** <https://talk.observablehq.com/>
-   **Stack Overflow:** Tag `mapbox-gl-js`, `leaflet`, `d3.js`

------------------------------------------------------------------------

## Conclusion

This web visualization addendum transforms your research from static
publication to dynamic storytelling. By exporting Python analysis
results to web-friendly formats and leveraging modern JavaScript
libraries, you can:

1.  **Engage broader audiences** beyond academic journals
2.  **Enable exploration** through interactive filters and animations
3.  **Communicate findings** more effectively with visual narratives
4.  **Demonstrate impact** to policymakers and community stakeholders
5.  **Showcase technical skills** in data science and web development

The key is maintaining the **separation of concerns:** Python for
rigorous analysis, JavaScript for compelling presentation. Start with
simple Mapbox/Leaflet maps, then progressively enhance with D3 charts,
temporal animations, and scrollytelling as time permits.

Your ECOSTRESS heat-crime study is perfectly suited for web
visualization—the spatial detail, temporal dynamics, and policy
relevance all benefit from interactive exploration. The tools and code
examples above provide everything needed to go from Jupyter notebooks to
published web maps within your one-month timeline.
