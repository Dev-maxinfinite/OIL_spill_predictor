import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from PIL import Image
import io
import base64
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Oil Spill Model with U-Net",
    page_icon="🛢️",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .risk-critical {
        background-color: #ff4444;
        padding: 10px;
        border-radius: 5px;
        color: white;
        animation: pulse 1s infinite;
    }
    .risk-high {
        background-color: #ff8800;
        padding: 10px;
        border-radius: 5px;
        color: white;
    }
    .risk-medium {
        background-color: #ffcc00;
        padding: 10px;
        border-radius: 5px;
        color: black;
    }
    .risk-low {
        background-color: #44ff44;
        padding: 10px;
        border-radius: 5px;
        color: black;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🛢️ Oil Spill Prediction Model with U-Net</h1><p>Deep Learning based oil spill detection and spread prediction</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Model Information")
    
    try:
        model_info = requests.get(f"{API_URL}/model-info").json()
        st.info(f"**Oil Types Supported:** {', '.join(model_info['oil_types'])}")
        
        if model_info['unet_model']['loaded']:
            st.success("✅ U-Net Model: Loaded")
            st.write(f"Path: {model_info['unet_model']['path']}")
        else:
            st.warning("⚠️ U-Net Model: Not Loaded (using fallback)")
    except:
        st.error("Backend server not running! Start server.py first")

# Tab selection
tab1, tab2 = st.tabs(["📝 Traditional Prediction", "🖼️ Image-Based Prediction (U-Net)"])

# Tab 1: Traditional Prediction
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Parameters")
        
        with st.form("prediction_form"):
            location = st.text_input("Location", value="Arabian Sea")
            
            oil_type = st.selectbox(
                "Oil Type",
                ["crude", "diesel", "heavy", "light"],
                help="Different oil types have different spread and evaporation rates"
            )
            
            volume = st.number_input(
                "Volume (barrels)",
                min_value=0.0,
                value=100.0,
                help="Total volume of oil spilled"
            )
            
            temperature = st.slider(
                "Water Temperature (°C)",
                min_value=0.0,
                max_value=40.0,
                value=25.0
            )
            
            wind_speed = st.slider(
                "Wind Speed (km/h)",
                min_value=0.0,
                max_value=50.0,
                value=15.0
            )
            
            wave_height = st.slider(
                "Wave Height (m)",
                min_value=0.0,
                max_value=10.0,
                value=2.0
            )
            
            submitted = st.form_submit_button("🚀 Predict", use_container_width=True)
    
    with col2:
        if submitted:
            data = {
                "location": location,
                "oil_type": oil_type,
                "volume": volume,
                "temperature": temperature,
                "wind_speed": wind_speed,
                "wave_height": wave_height,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                response = requests.post(f"{API_URL}/predict", json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.subheader("📈 Prediction Results")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric("🌊 Spread Area", f"{result['spread_area']:,.0f} m²")
                        st.metric("💨 Evaporation Rate", f"{result['evaporation_rate']}%")
                    
                    with col_b:
                        risk_class = f"risk-{result['risk_level'].lower()}"
                        st.markdown(f"""
                            <div class="{risk_class}">
                                <h3>⚠️ Risk Level</h3>
                                <h2>{result['risk_level']}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.subheader("📋 Recommendations")
                    for rec in result['recommendations']:
                        st.info(f"• {rec}")
                    
                    # Risk gauge
                    risk_scores = {"Low": 25, "Medium": 50, "High": 75, "Critical": 100}
                    risk_value = risk_scores.get(result['risk_level'], 0)
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=risk_value,
                        title={'text': "Risk Level"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "darkred"},
                            'steps': [
                                {'range': [0, 33], 'color': "lightgreen"},
                                {'range': [33, 66], 'color': "yellow"},
                                {'range': [66, 100], 'color': "red"}
                            ]
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error: {e}")

# Tab 2: Image-Based Prediction with U-Net
with tab2:
    st.subheader("🖼️ Upload Satellite/Aerial Image")
    st.write("Upload an image to detect oil spills using U-Net model")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload satellite or aerial imagery of water surface"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Input parameters
            st.subheader("Environmental Parameters")
            location_img = st.text_input("Location", value="Satellite Detection")
            oil_type_img = st.selectbox("Oil Type", ["crude", "diesel", "heavy", "light"], key="oil_img")
            volume_img = st.number_input("Estimated Volume (barrels)", min_value=0.0, value=50.0, key="vol_img")
            temperature_img = st.slider("Water Temperature (°C)", 0.0, 40.0, 25.0, key="temp_img")
            wind_speed_img = st.slider("Wind Speed (km/h)", 0.0, 50.0, 15.0, key="wind_img")
            wave_height_img = st.slider("Wave Height (m)", 0.0, 10.0, 2.0, key="wave_img")
            
            predict_btn = st.button("🔍 Detect Oil Spill", type="primary", use_container_width=True)
    
    with col2:
        if uploaded_file is not None and predict_btn:
            try:
                # Prepare files for upload
                files = {"image": uploaded_file.getvalue()}
                
                # Prepare form data
                data = {
                    "location": location_img,
                    "oil_type": oil_type_img,
                    "volume": volume_img,
                    "temperature": temperature_img,
                    "wind_speed": wind_speed_img,
                    "wave_height": wave_height_img
                }
                
                # Make API request
                response = requests.post(
                    f"{API_URL}/predict-with-image",
                    params=data,
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.subheader("🎯 Detection Results")
                    
                    # Spill percentage
                    if result.get('spill_percentage'):
                        st.metric("🛢️ Oil Spill Coverage", f"{result['spill_percentage']}% of image")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric("🌊 Spread Area", f"{result['spread_area']:,.0f} m²")
                        st.metric("💨 Evaporation Rate", f"{result['evaporation_rate']}%")
                    
                    with col_b:
                        risk_class = f"risk-{result['risk_level'].lower()}"
                        st.markdown(f"""
                            <div class="{risk_class}">
                                <h3>⚠️ Risk Level</h3>
                                <h2>{result['risk_level']}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Display U-Net mask
                    if result.get('oil_spill_mask'):
                        st.subheader("🗺️ U-Net Segmentation Result")
                        mask_data = base64.b64decode(result['oil_spill_mask'])
                        mask_image = Image.open(io.BytesIO(mask_data))
                        st.image(mask_image, caption="Detected Oil Spill Area (White = Spill)", use_container_width=True)
                    
                    # Recommendations
                    st.subheader("📋 Recommendations")
                    for rec in result['recommendations']:
                        st.warning(f"• {rec}")
                    
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error processing image: {e}")

# History section
st.markdown("---")
st.subheader("📜 Prediction History")

try:
    history = requests.get(f"{API_URL}/history?limit=10").json()
    
    if history['records']:
        df_data = []
        for record in history['records']:
            df_data.append({
                "Timestamp": record['timestamp'][:19],
                "Location": record['input']['location'],
                "Oil Type": record['input']['oil_type'],
                "Volume": record['input']['volume'],
                "Risk Level": record['prediction']['risk_level'],
                "Spread Area": record['prediction']['spread_area'],
                "Image Based": "Yes" if record.get('image_processed') else "No"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No predictions yet. Make a prediction to see history!")
        
except:
    st.warning("Unable to fetch history. Make sure backend is running.")

# Footer
st.markdown("---")
st.caption("Oil Spill Model v2.0 | U-Net Deep Learning Model | Real-time Oil Spill Detection")