import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import random
import geopandas as gpd
import plotly.express as px
import numpy as np
import os
from datetime import datetime
import requests
from shapely.geometry import Polygon
from pyproj import Transformer
from pathlib import Path
import zipfile
import tempfile as Centroid_Area

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Custom CSS
custom_css = """
/* Main page styling */
body {
    color: #ffffff;
    background-color: #0e1117;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #1e2130;
}

/* Header styling */
h1, h2, h3 {
    color: #4da6ff;
    font-weight: bold;
}

/* Improve button styling */
.stButton > button {
    color: #ffffff;
    background-color: #4da6ff;
    border: none;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #3385ff;
    box-shadow: 0 0 10px rgba(77, 166, 255, 0.5);
}

/* Style selectbox */
.stSelectbox > div > div {
    background-color: #1e2130;
    color: #ffffff;
}

/* Map container styling */
.folium-map {
    border: 2px solid #4da6ff;
    border-radius: 10px;
    overflow: hidden;
}

/* Risk area styling */
.risk-item {
    background-color: #1e2130;
    border-radius: 5px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.risk-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(77, 166, 255, 0.2);
}

.risk-high {
    border-left: 4px solid #ff4d4d;
}

.risk-medium {
    border-left: 4px solid #ffa64d;
}

.risk-low {
    border-left: 4px solid #4dff4d;
}

/* Scrollable risk area */
.scrollable-risk-area {
    max-height: 600px;
    overflow-y: auto;
    padding-right: 1rem;
}

/* Custom metric display */
.metric-container {
    background-color: #1e2130;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(77, 166, 255, 0.1);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #4da6ff;
}

.metric-label {
    font-size: 1rem;
    color: #a6a6a6;
}
"""

# All 77 Thai provinces with their approximate coordinates
THAI_PROVINCES = {
    "Amnat Charoen": (15.8661, 104.6289),
    "Ang Thong": (14.5896, 100.4549),
    "Bangkok": (13.7563, 100.5018),
    "Nakhon Ratchasima": (14.9799, 102.0978),
    "Yasothon": (15.7921, 104.1458)
}

def get_person():
    APP_ID = "fe7224ba-6468-4b6c-82f6-c93ee8ead301"
    TABLE_NAME = "Employee"
    API_KEY = "V2-QebDx-Exm43-4gTHp-KYLK2-cibOk-yeDLy-Vfr5A-CMKQs"
    API_URL = f"https://api.appsheet.com/api/v2/apps/{APP_ID}/tables/{TABLE_NAME}/find"
    headers = {
        "ApplicationAccessKey": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "Action": "Find",
        "Properties": {
            "Locale": "en-US",
            "Timezone": "Pacific Standard Time"
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    persons = [row.get('Name') for row in response.json()]
    return persons

def read_shapefile(uploaded_file):
    with Centroid_Area.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        shp_file = next(Path(tmpdirname).glob('*.shp'))
        gdf = gpd.read_file(shp_file)
    
    return gdf

def process_shapefile_data(gdf):
    gdf['Longitude'] = gdf.geometry.centroid.x
    gdf['Latitude'] = gdf.geometry.centroid.y
    
    gdf['Risk'] = np.random.uniform(0, 100, len(gdf))
    gdf['Day'] = np.random.randint(1, 16, len(gdf))
    gdf['Size'] = np.random.randint(100, 1000, len(gdf))
    gdf['Carbon'] = gdf['Size'] * 8  # 8 tons of carbon per rai
    
    gdf['Area'] = gdf.apply(lambda row: min(THAI_PROVINCES.items(), key=lambda x: ((x[1][0] - row['Latitude'])**2 + (x[1][1] - row['Longitude'])**2)**0.5)[0], axis=1)
    
    return gdf

def read_shapefile_data(file_path):
    return pd.read_csv(file_path)

def get_central_point(farm, src_crs='EPSG:3857'):
    transformer = Transformer.from_crs(src_crs, 'EPSG:4326', always_xy=True)
    
    polygon_points = farm['geometry']
    points_str = [polygon_point.replace("POLYGON ((", "") for polygon_point in polygon_points]
    point_locations = [point_str.replace("))", "") for point_str in points_str]
    point_lists = [point_location.split(',') for point_location in point_locations]
    
    point_tuples = [[(float(location.replace(')', '').replace('(', '').split()[0]), 
                      float(location.replace(')', '').replace('(', '').split()[1])) 
                     for location in point_list] 
                    for point_list in point_lists]
    
    polygon = Polygon(point_tuples[0])
    centroid = polygon.centroid
    
    lon, lat = transformer.transform(centroid.x, centroid.y)
    centroid_coordinates = (lat, lon)
    
    return centroid_coordinates

def emission_calculation(rai):
    emission = 35.9 * rai * 10
    return emission

def display_farm_info(row, assumed_day_prediction, farm, i):
    tab1, tab2 = st.tabs(["Overview", "More Info"])
    
    with tab1:
        risk_level = "high" if row['Risk'] > 66 else "medium" if row['Risk'] > 33 else "low"
        st.markdown(f"""
        <div class="risk-item risk-{risk_level}">
            <h4>Farm {row['Id']}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.session_state.selected_farm_id = row['Id']
        st.session_state.selected_latitude, st.session_state.selected_longitude = get_central_point(farm.iloc[[i]])
        st.session_state.selected_rai = row['Shape_Area']
        st.session_state.selected_yield = row['Shape_Area'] * 10
        st.session_state.selected_emission = emission_calculation(row['Shape_Area'])
        
        st.write(f"Farm ID: {st.session_state.selected_farm_id}")
        st.write(f"Assumed Day Prediction: {assumed_day_prediction[i]} days")
        st.write(f"Latitude: {st.session_state.selected_latitude:.4f}")
        st.write(f"Longitude: {st.session_state.selected_longitude:.4f}")
        st.write(f"Emission: {st.session_state.selected_emission:.2f} kg CO2e")
        st.write(f"Area: {st.session_state.selected_rai:.2f} rai")
        st.write(f"Average Yield: {st.session_state.selected_yield:.2f} tons")
                        
        responsible_person = st.multiselect(
            "Choose a responsible person:", 
            get_person(), 
            key=f"responsible_person_selectbox_{i}"
        )

        if st.button("Confirm", key=f"confirm_button_{i}"):
            st.success("Confirmed!")

def main():
    st.set_page_config(layout="wide", page_title="Hotspot Prediction Dashboard")
    
    st.markdown(f"""
    <style>
    {custom_css}
    </style>
    """, unsafe_allow_html=True)

    st.title("🔥 Hotspot Prediction Dashboard")

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_province = st.selectbox("🏙️ Choose a province:", ["All Provinces"] + list(THAI_PROVINCES.keys()))
        selected_file = st.selectbox(
            "📅 Choose a data file (Year):",
            ["2564", "2565", "2566"]
        )
        selected_file = f"C:\\cu\\Hotspot_latlong\\{selected_file}.csv"
        
        filtered_data = read_shapefile_data(selected_file)
        
        if selected_province and selected_province != "All Provinces":
            center_lat, center_lon = THAI_PROVINCES[selected_province]
            zoom_start = 10
        else:
            center_lat, center_lon = 13.7563, 100.5018
            zoom_start = 6

        st.subheader("🗺️ Map of Fire Risk Areas")
        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
        
        for _, row in filtered_data.iterrows():
            folium.Circle(
                location=[row['LATITUDE'], row['LONGITUDE']],
                radius=500,
                color='red',
                weight=2,
                fill=True,
                fill_color='red',
                fill_opacity=0.1,
            ).add_to(m)
        
        folium_static(m, width=1200, height=600)

        # Carbon emission metric moved here
        farm = pd.read_csv('sample.csv')
        st.session_state.total_emission = emission_calculation(sum(farm['Shape_Area']))
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{st.session_state.total_emission:,.0f}</div>
            <div class="metric-label">Total Carbon Emission (kg CO2e)</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<h3 class="dashboard-title">Top 20 Fire Risk Areas (Next 16 Days)</h3>', unsafe_allow_html=True)
        st.markdown('<div class="scrollable-risk-area">', unsafe_allow_html=True)
        
        assumed_day_prediction = [random.randint(10,30) for _ in range(len(farm))]
        
        for i, row in farm.iloc[:20].iterrows():
            display_farm_info(row, assumed_day_prediction, farm, i)
        
        st.markdown('</div>', unsafe_allow_html=True)
if __name__ == "__main__":
    main()