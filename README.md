# 🌊 3D Oil Spill Detection System
A state-of-the-art, AI-powered system for detecting, analyzing, and forecasting ocean oil spills using exceptionally resilient Deep Learning and Computer Vision techniques. 

Equipped with a futuristic 3D backend dashboard and a high-performance backend, this project is designed for critical environmental monitoring.

## 🌟 Key Features

### 🧠 Robust AI & CV Backend (FastAPI)
- **U-Net Architecture**: Accurately segments satellite/aerial imagery to identify oil spills.
- **Smart CV Fallback**: Ensures reliable predictions—even if the Neural Network fails—by utilizing K-Means Clustering, Otsu's Thresholding, and advanced morphological cleanup.
- **Physics-Based Simulation**: Calculates oil spread area, evaporation rate, and precise risk levels based on temperature, wind speed, wave height, and oil type.
- **Real-Time Forecasting**: Recommends immediate response strategies depending on situational severity.

### 🌐 Futuristic 3D Frontend
- **Interactive Environment**: Built with an animated ocean background and a robust UI interface.
- **Rich Dashboard UI**: Immersive glassmorphism and modern UI elements to present predictive insights beautifully.
- **Real-time Analytics Overlay**: Seamlessly blends prediction masking (customizable coloring) directly onto uploaded imagery.

## 📂 Project Structure
- `/server.py` : High-performance FastAPI server and model pipelines.
- `/frontend-3d` : Next-generation responsive UI and 3D environment graphics.
- `/oil_spill_unet_model.h5` : Pre-trained U-Net weights for instance segmentation.
- `/oil_spill_data.json` : Historical context and log saving ecosystem.

## 🚀 Getting Started

### 1. Requirements & Backend Setup
Ensure you have Python 3.9+ installed.
```bash
# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt
# (or manually: pip install fastapi uvicorn tensorflow opencv-python pillow pydantic numpy python-multipart)
```

### 2. Run the Backend Server
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) to view the API Swagger Documentation.

### 3. Frontend Setup
```bash
# Navigate to the frontend workspace
cd frontend-3d

# Install packages
npm install

# Start the dev server
npm run dev
```

## 🧠 Technologies Used
- **Backend:** Python, FastAPI, TensorFlow/Keras, OpenCV, Numpy
- **Frontend:** React, Three.js / React Three Fiber, Framer Motion
- **Models:** Convolutional Neural Networks (U-Net), Feature Extraction (K-Means/Otsu), Physics-based Spread Prediction.

## 🛡️ Fallback Logic Architecture
To solve edge-case failure modes where models may predict a blank mask, the backend employs a smart decision logic tree:
1. It tries standard execution through the U-Net.
2. Parallelly computes K-Means and CLAHE-enhanced Otsu anomaly mapping.
3. Evaluates U-Net prediction area coverage. If Coverage < 1% or > 80% (which signifies a model anomaly crash), it discards the ML output and merges predictions from robust CV tracking. 
4. Ensures that the output remains structurally stable in almost all scenarios.

---
*Built to preserve and protect our oceans. 🌊🚢*
