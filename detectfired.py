import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import random
import geopandas
import plotly.express as px
import numpy as np
import os
from datetime import datetime


# All 77 Thai provinces with their approximate coordinates
THAI_PROVINCES = {
    "Amnat Charoen": (15.8661, 104.6289),
    "Ang Thong": (14.5896, 100.4549),
    "Bangkok": (13.7563, 100.5018),
    "Bueng Kan": (18.3609, 103.6466),
    "Buri Ram": (14.9951, 103.1116),
    "Chachoengsao": (13.6904, 101.0779),
    "Chai Nat": (15.1851, 100.1251),
    "Chaiyaphum": (15.8068, 102.0317),
    "Chanthaburi": (12.6100, 102.1034),
    "Chiang Mai": (18.7883, 98.9853),
    "Chiang Rai": (19.9105, 99.8406),
    "Chon Buri": (13.3611, 100.9847),
    "Chumphon": (10.4930, 99.1800),
    "Kalasin": (16.4315, 103.5059),
    "Kamphaeng Phet": (16.4827, 99.5226),
    "Kanchanaburi": (14.0023, 99.5328),
    "Khon Kaen": (16.4419, 102.8360),
    "Krabi": (8.0863, 98.9063),
    "Lampang": (18.2854, 99.5122),
    "Lamphun": (18.5743, 99.0087),
    "Loei": (17.4860, 101.7223),
    "Lop Buri": (14.7995, 100.6534),
    "Mae Hong Son": (19.2988, 97.9684),
    "Maha Sarakham": (16.0132, 103.1615),
    "Mukdahan": (16.5425, 104.7240),
    "Nakhon Nayok": (14.2069, 101.2130),
    "Nakhon Pathom": (13.8196, 100.0645),
    "Nakhon Phanom": (17.3948, 104.7692),
    "Nakhon Ratchasima": (14.9799, 102.0978),
    "Nakhon Sawan": (15.7030, 100.1371),
    "Nakhon Si Thammarat": (8.4304, 99.9631),
    "Nan": (18.7756, 100.7730),
    "Narathiwat": (6.4318, 101.8259),
    "Nong Bua Lam Phu": (17.2217, 102.4260),
    "Nong Khai": (17.8782, 102.7418),
    "Nonthaburi": (13.8622, 100.5140),
    "Pathum Thani": (14.0208, 100.5253),
    "Pattani": (6.8691, 101.2550),
    "Phang Nga": (8.4509, 98.5194),
    "Phatthalung": (7.6167, 100.0743),
    "Phayao": (19.2147, 100.2020),
    "Phetchabun": (16.4190, 101.1591),
    "Phetchaburi": (13.1119, 99.9438),
    "Phichit": (16.4398, 100.3489),
    "Phitsanulok": (16.8211, 100.2659),
    "Phra Nakhon Si Ayutthaya": (14.3692, 100.5876),
    "Phrae": (18.1445, 100.1405),
    "Phuket": (7.8804, 98.3923),
    "Prachin Buri": (14.0509, 101.3660),
    "Prachuap Khiri Khan": (11.8126, 99.7957),
    "Ranong": (9.9529, 98.6085),
    "Ratchaburi": (13.5282, 99.8134),
    "Rayong": (12.6815, 101.2816),
    "Roi Et": (16.0566, 103.6517),
    "Sa Kaeo": (13.8244, 102.0645),
    "Sakon Nakhon": (17.1664, 104.1486),
    "Samut Prakan": (13.5990, 100.5998),
    "Samut Sakhon": (13.5475, 100.2745),
    "Samut Songkhram": (13.4094, 100.0021),
    "Saraburi": (14.5289, 100.9109),
    "Satun": (6.6238, 100.0675),
    "Sing Buri": (14.8920, 100.3970),
    "Sisaket": (15.1185, 104.3229),
    "Songkhla": (7.1756, 100.6142),
    "Sukhothai": (17.0069, 99.8265),
    "Suphan Buri": (14.4744, 100.0913),
    "Surat Thani": (9.1351, 99.3268),
    "Surin": (14.8820, 103.4936),
    "Tak": (16.8840, 99.1259),
    "Trang": (7.5645, 99.6239),
    "Trat": (12.2428, 102.5179),
    "Ubon Ratchathani": (15.2448, 104.8472),
    "Udon Thani": (17.4156, 102.7872),
    "Uthai Thani": (15.3838, 100.0255),
    "Uttaradit": (17.6200, 100.0990),
    "Yala": (6.5414, 101.2803),
    "Yasothon": (15.7921, 104.1458)
}

def read_shapefile(uploaded_file):
    # Create a temporary directory to extract the zip file
    with Centroid_Area.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Find the .shp file in the extracted directory
        shp_file = next(Path(tmpdirname).glob('*.shp'))
        
        # Read the shapefile using geopandas
        gdf = gpd.read_file(shp_file)
    
    return gdf

def process_shapefile_data(gdf):
    # Extract centroid coordinates
    gdf['Longitude'] = gdf.geometry.centroid.x
    gdf['Latitude'] = gdf.geometry.centroid.y
    
    # Generate random data for demonstration purposes
    gdf['Risk'] = np.random.uniform(0, 100, len(gdf))
    gdf['Day'] = np.random.randint(1, 16, len(gdf))
    gdf['Size'] = np.random.randint(100, 1000, len(gdf))
    gdf['Carbon'] = gdf['Size'] * 8  # 8 tons of carbon per rai
    
    # Assign area names based on the closest Thai province
    gdf['Area'] = gdf.apply(lambda row: min(THAI_PROVINCES.items(), key=lambda x: ((x[1][0] - row['Latitude'])**2 + (x[1][1] - row['Longitude'])**2)**0.5)[0], axis=1)
    
    return gdf

def read_shapefile_data():
    hotspot_df = pd.read_csv(r'C:\Users\User\Documents\hotspotsugarcrane_lat_long.csv')
    return hotspot_df

def main():
    
    st.set_page_config(layout="wide", page_title="Hotspot Prediction Dashboard")
    
    # Custom CSS for improved styling
    st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    
    .dashboard-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    .risk-item {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 0.3rem;
    }
    .risk-high {
        background-color: rgba(255, 0, 0, 0.2);
        border-left: 4px solid red;
    }
    .risk-medium {
        background-color: rgba(255, 165, 0, 0.2);
        border-left: 4px solid orange;
    }
    .risk-low {
        background-color: rgba(0, 128, 0, 0.2);
        border-left: 4px solid green;
    }
    .risk-value {
        font-weight: bold;
    }
    .scrollable-risk-area {
        max-height: 800px;
        overflow-y: auto;
        padding-right: 1rem;
    }
    .stPlotlyChart {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Input")
        '''
        uploaded_file = st.file_uploader("Upload shapefile (as .zip)", type="zip")
        
        if uploaded_file is not None:
            try:
                gdf = read_shapefile(uploaded_file)
                if 'geometry' in gdf.columns:
                    processed_gdf = process_shapefile_data(gdf)
                    st.success("Imported shapefile successfully")
                else:
                    st.error("The shapefile must contain a 'geometry' column.")
            except Exception as e:
                st.error(f"Error reading shapefile: {e}")
            
        run_button = st.button("Run Analysis")
        '''
    
    # Main content
    st.title("Hotspot Prediction")
    filtered_data = read_shapefile_data()
    # Province selection with dropdown
    selected_province = st.selectbox("Choose a province:", ["All Provinces"] + list(THAI_PROVINCES.keys()))

    # Filter data based on selection
    if selected_province and selected_province != "All Provinces":
        center_lat, center_lon = THAI_PROVINCES[selected_province]
        zoom_start = 16  # Closer zoom for a specific province
    else:
        center_lat, center_lon = 13.7563, 100.5018  # Center of Thailand
        zoom_start = 6  # Default zoom for all of Thailand

    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map
        st.subheader("Map of Fire Risk Areas")
        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
        
        for _, row in filtered_data.iterrows():
            #color = 'red' if row['Risk'] > 66 else 'orange' if row['Risk'] > 33 else 'green'
            
            # Add circle with 500m radius (more transparent)
            
            folium.Circle(
                location=[row['LATITUDE'], row['LONGITUDE']],
                radius=500,  # 500 meters
                color='red',
                weight=2,  # Slightly thicker border for visibility
                fill=True,
                fill_color='red',
                fill_opacity=0.1,  # Increased transparency
                #popup=f"Area: {row['Area']}<br>Risk: {row['Risk']:.2f}%<br>Size: {row['Size']} rai"
            ).add_to(m)
           
            # Add center point
            #folium.CircleMarker(
                #location=[row['LATITUDE'], row['LONGITUDE']],
                #radius=500,  # Slightly larger for better visibility
                #color='red',
                #fill=True,
                #fill_color='red',
                #fill_opacity=1,
                #popup=f"Center of {row['Area']}<br>Risk: {row['Risk']:.2f}%"
            #).add_to(m)
        
        folium_static(m, width=800, height=400)
        
        # Amount of net carbon
        """st.subheader("Amount of net carbon (8 ton/rai)")
        fig = px.bar(filtered_data, x='Area', y='Carbon', color='Risk',
                     labels={'Carbon': 'Net Carbon (tons)', 'Area': 'Province'},
                     title='Net Carbon by Province',
                     color_continuous_scale='RdYlGn_r')
        fig.update_layout(
            height=400, 
            xaxis={'categoryorder':'total descending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff'
        )
        st.plotly_chart(fig, use_container_width=True)"""
    
    """with col2:
        st.markdown('<h3 class="dashboard-title">Top 20 Fire Risk Areas (Next 16 Days)</h3>', unsafe_allow_html=True)
        st.markdown('<div class="scrollable-risk-area">', unsafe_allow_html=True)
        
        # Sort the filtered data by Risk (descending), Day, and Size
        sorted_data = filtered_data.sort_values(['Risk', 'Day', 'Size'], ascending=[False, True, False])
        
        # Display top 20 areas (or all if less than 20)
        for _, row in sorted_data.head(20).iterrows():
            if row['Risk'] > 66:
                risk_class = "risk-high"
            elif row['Risk'] > 33:
                risk_class = "risk-medium"
            else:
                risk_class = "risk-low"
            
            st.markdown(f"""
            #<div class="risk-item {risk_class}">
                #<span class="risk-value">Risk: {row['Risk']:.2f}%</span><br>
                #<strong>{row['Area']}</strong><br>
                #Day: {row['Day']} | Size: {row['Size']} rai
            #</div>
            #""", unsafe_allow_html=True)
        
        #st.markdown('</div>', unsafe_allow_html=True)
        
if __name__ == "__main__":
    main()

    