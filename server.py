from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import math

# Try to import optional dependencies
try:
    import numpy as np
except ImportError:
    np = None

try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    load_model = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image
except ImportError:
    Image = None

import io
import base64

app = FastAPI(title="Oil Spill Model API with U-Net")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load U-Net Model
MODEL_PATH = "oil_spill_unet_model.h5"

class UNetPredictor:
    def __init__(self, model_path):
        if not TENSORFLOW_AVAILABLE:
            print("⚠️ TensorFlow not available - using fallback mode")
            self.is_loaded = False
            self.model = None
            self.target_height = 128
            self.target_width = 128
            return
            
        try:
            self.model = load_model(model_path, compile=False)
            
            # Auto-detect model input shape
            self.input_shape = self.model.input_shape
            print(f"✅ Model loaded! Expected input shape: {self.input_shape}")
            
            # Extract height and width from input shape
            if len(self.input_shape) == 4:
                self.target_height = self.input_shape[1]
                self.target_width = self.input_shape[2]
            else:
                # Default fallback
                self.target_height = 128
                self.target_width = 128
                
            print(f"📐 Resizing images to: {self.target_height} x {self.target_width}")
            self.is_loaded = True
            
        except Exception as e:
            print(f"⚠️ Error loading U-Net model: {e}")
            print("Using fallback model")
            self.is_loaded = False
            self.model = None
            self.target_height = 128
            self.target_width = 128
    
    def preprocess_image(self, image):
        """Preprocess image for U-Net model"""
        if cv2 is None or np is None:
            return None
            
        # Resize to model's expected input size
        image = cv2.resize(image, (self.target_width, self.target_height))
        
        # Enhanced preprocessing for better detection
        # Apply CLAHE for better contrast
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Normalize
        if image.max() > 1:
            image = image / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        return image
    
    def postprocess_mask(self, mask, confidence_threshold=0.3):
        """Convert model output to binary mask with adaptive thresholding"""
        if np is None:
            return np.array([])
        
        # Handle different output formats
        if len(mask.shape) == 4:
            mask = mask[0]  # Remove batch dimension
        
        if mask.shape[-1] > 1:
            # Multi-class output - use softmax
            mask = np.argmax(mask, axis=-1)
            mask = (mask > 0).astype(np.uint8)
        else:
            # Binary output with probability
            if len(mask.shape) == 3 and mask.shape[-1] == 1:
                mask = mask[:, :, 0]
            
            # Apply confidence threshold
            mask = (mask > confidence_threshold).astype(np.uint8)
            
            # Apply morphological operations to reduce noise
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def predict(self, image):
        """Predict oil spill mask with confidence calibration"""
        if not self.is_loaded or cv2 is None or np is None:
            # Enhanced fallback: edge detection + adaptive thresholding
            if cv2 is None:
                return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Oil spill detection in HSV space (darker regions)
            lower_oil = np.array([0, 0, 0])
            upper_oil = np.array([180, 50, 100])
            mask_hsv = cv2.inRange(hsv, lower_oil, upper_oil)
            
            # Edge detection for boundaries
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Combine masks
            mask = cv2.bitwise_or(mask_hsv, edges)
            
            # Apply morphological operations
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            return mask
        
        # Store original size for later
        original_height, original_width = image.shape[:2]
        
        # Preprocess
        processed = self.preprocess_image(image)
        
        # Predict with augmentation for robustness
        predictions = []
        
        # Original prediction
        pred_orig = self.model.predict(processed, verbose=0)
        predictions.append(pred_orig)
        
        # Horizontal flip for ensemble
        if np.random.random() > 0.5:
            flipped = np.flip(processed, axis=2)
            pred_flip = self.model.predict(flipped, verbose=0)
            pred_flip = np.flip(pred_flip, axis=2)
            predictions.append(pred_flip)
        
        # Average predictions
        prediction = np.mean(predictions, axis=0)
        
        # Postprocess with confidence calibration
        mask = self.postprocess_mask(prediction, confidence_threshold=0.3)
        
        # Resize back to original size
        mask = cv2.resize(mask.astype(np.uint8), (original_width, original_height))
        
        return mask

# Initialize U-Net predictor
unet_predictor = UNetPredictor(MODEL_PATH)

# Data Models
class OilSpillData(BaseModel):
    location: str
    oil_type: str
    volume: float
    temperature: float
    wind_speed: float
    wave_height: float
    timestamp: str

class PredictionResponse(BaseModel):
    spread_area: float
    risk_level: str
    evaporation_rate: float
    recommendations: List[str]
    oil_spill_mask: Optional[str] = None
    overlay_image: Optional[str] = None  # New field for colored overlay
    spill_percentage: Optional[float] = None
    confidence_score: Optional[float] = None
    calibrated_spread: Optional[float] = None

# JSON data storage with better error handling
DATA_FILE = "oil_spill_data.json"

def load_data():
    """Load data from JSON file with error handling"""
    default_data = {"records": [], "models": [], "images": []}
    
    if not os.path.exists(DATA_FILE):
        save_data(default_data)
        return default_data
    
    try:
        with open(DATA_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                print("⚠️ JSON file is empty, creating default structure")
                save_data(default_data)
                return default_data
            
            data = json.loads(content)
            
            # Ensure all required keys exist
            if "records" not in data:
                data["records"] = []
            if "models" not in data:
                data["models"] = []
            if "images" not in data:
                data["images"] = []
            
            return data
            
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode error: {e}")
        print("Creating new JSON file with default structure")
        save_data(default_data)
        return default_data
    except Exception as e:
        print(f"⚠️ Error loading data: {e}")
        return default_data

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving data: {e}")

def create_colored_overlay(original_image, mask, overlay_color=(0, 0, 255), opacity=0.5):
    """
    Create colored overlay on original image
    
    Parameters:
    - original_image: Original BGR image
    - mask: Binary mask (0 or 255)
    - overlay_color: BGR color tuple (Blue, Green, Red)
      Examples:
      - Red: (0, 0, 255)
      - Green: (0, 255, 0)
      - Blue: (255, 0, 0)
      - Yellow: (0, 255, 255)
      - Cyan: (255, 255, 0)
      - Magenta: (255, 0, 255)
      - Orange: (0, 165, 255)
      - Purple: (128, 0, 128)
    - opacity: Overlay transparency (0.0 to 1.0)
    """
    if cv2 is None or np is None:
        return None
    
    # Create a copy of the original image
    overlay = original_image.copy()
    
    # Create color mask
    color_mask = np.zeros_like(original_image)
    color_mask[mask > 0] = overlay_color
    
    # Apply overlay
    overlay = cv2.addWeighted(overlay, 1 - opacity, color_mask, opacity, 0)
    
    # Add boundaries for better visibility
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, overlay_color, 2)
    
    return overlay

def get_color_by_risk_level(risk_level):
    """Return color based on risk level"""
    risk_colors = {
        "Critical": (0, 0, 255),      # Red
        "High": (0, 165, 255),        # Orange
        "Medium": (0, 255, 255),      # Yellow
        "Low": (0, 255, 0)            # Green
    }
    return risk_colors.get(risk_level, (0, 0, 255))

def get_color_by_oil_type(oil_type):
    """Return color based on oil type"""
    oil_colors = {
        "crude": (0, 0, 255),         # Red
        "diesel": (0, 255, 255),      # Yellow
        "heavy": (128, 0, 128),       # Purple
        "light": (255, 165, 0)        # Orange
    }
    return oil_colors.get(oil_type.lower(), (0, 0, 255))

# Enhanced Traditional Oil Spill Model with Physics-based corrections
class TraditionalOilSpillModel:
    def __init__(self):
        self.oil_types = {
            "crude": {
                "evaporation_factor": 0.3, 
                "spread_factor": 1.2,
                "viscosity": 100,  # cP
                "density": 0.85,   # g/cm³
                "weathering_rate": 0.05
            },
            "diesel": {
                "evaporation_factor": 0.7, 
                "spread_factor": 1.5,
                "viscosity": 5,
                "density": 0.83,
                "weathering_rate": 0.15
            },
            "heavy": {
                "evaporation_factor": 0.1, 
                "spread_factor": 0.8,
                "viscosity": 500,
                "density": 0.95,
                "weathering_rate": 0.02
            },
            "light": {
                "evaporation_factor": 0.5, 
                "spread_factor": 1.3,
                "viscosity": 10,
                "density": 0.84,
                "weathering_rate": 0.10
            }
        }
        
        # Environmental coefficients
        self.temp_coefficient = 0.02  # 2% increase per degree
        self.wind_coefficient = 0.05   # 5% increase per m/s
        self.wave_coefficient = 0.08   # 8% increase per meter
    
    def calculate_spread_area(self, data: OilSpillData, oil_config: dict, spill_percentage: float = 0) -> float:
        """Calculate spread area using improved physics-based model"""
        
        # Base spreading (Fay's law inspired)
        volume_m3 = data.volume  # Assume volume in m³
        gravity = 9.81
        
        # Gravity-inertial spreading phase
        spread_gravity = 1.14 * (volume_m3 ** 0.5)
        
        # Gravity-viscous spreading phase
        spread_viscous = 1.45 * (volume_m3 ** (1/3)) * (oil_config['viscosity'] ** (1/6))
        
        # Surface tension phase
        spread_tension = 2.28 * (volume_m3 ** (1/3))
        
        # Combine phases based on oil type
        spread_base = max(spread_gravity, spread_viscous, spread_tension)
        
        # Apply environmental factors
        temp_factor = 1 + (data.temperature - 15) * self.temp_coefficient
        wind_factor = 1 + data.wind_speed * self.wind_coefficient
        wave_factor = 1 + data.wave_height * self.wave_coefficient
        
        # Oil type spread factor
        spread_factor = oil_config['spread_factor']
        
        # Final spread area calculation
        spread_area = spread_base * spread_factor * temp_factor * wind_factor * wave_factor
        
        # Adjust based on actual spill percentage from U-Net
        if spill_percentage > 0:
            # Scale spread area based on detected spill
            spread_area = spread_area * (1 + spill_percentage / 50)
        
        # Apply realistic bounds
        spread_area = min(max(spread_area, data.volume * 10), data.volume * 500)
        
        return spread_area
    
    def calculate_evaporation(self, data: OilSpillData, oil_config: dict) -> float:
        """Calculate evaporation rate using improved model"""
        
        # Base evaporation
        evaporation_base = oil_config['evaporation_factor']
        
        # Temperature effect (Arrhenius equation approximation)
        temp_effect = math.exp((data.temperature - 20) / 30)
        
        # Wind effect
        wind_effect = 1 + (data.wind_speed / 20)
        
        # Combined evaporation
        evaporation_rate = evaporation_base * temp_effect * wind_effect
        
        # Weathering effect over time
        evaporation_rate += oil_config['weathering_rate']
        
        # Cap at realistic maximum
        evaporation_rate = min(evaporation_rate, 0.85)
        
        return evaporation_rate
    
    def determine_risk_level(self, spread_area: float, spill_percentage: float, oil_type: str) -> str:
        """Determine risk level with multiple factors"""
        
        # Base risk from spread area
        if spread_area > 5000:
            base_risk = "Critical"
        elif spread_area > 1000:
            base_risk = "High"
        elif spread_area > 100:
            base_risk = "Medium"
        else:
            base_risk = "Low"
        
        # Upgrade risk based on spill percentage
        if spill_percentage > 25 and base_risk in ["Medium", "Low"]:
            return "High"
        elif spill_percentage > 40 and base_risk == "High":
            return "Critical"
        
        # Consider oil type toxicity
        toxic_risk = {"diesel": 0.3, "light": 0.2, "crude": 0.1, "heavy": 0.05}
        if oil_type.lower() in toxic_risk and toxic_risk[oil_type.lower()] > 0.2:
            if base_risk == "Medium":
                return "High"
        
        return base_risk
    
    def generate_recommendations(self, risk_level: str, evaporation_rate: float, 
                                 wind_speed: float, wave_height: float, 
                                 oil_type: str, spill_percentage: float) -> List[str]:
        """Generate intelligent recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_level == "Critical":
            recommendations.extend([
                "🚨 EMERGENCY RESPONSE REQUIRED",
                "Deploy all available containment booms immediately",
                "Activate emergency response team",
                "Notify environmental protection agency",
                "Establish exclusion zone"
            ])
        elif risk_level == "High":
            recommendations.extend([
                "⚠️ Immediate containment required",
                "Deploy oil booms and skimmers",
                "Monitor shoreline for contamination",
                "Prepare dispersant application"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "Deploy containment measures",
                "Monitor spill movement",
                "Prepare cleanup equipment"
            ])
        
        # Evaporation-based recommendations
        if evaporation_rate > 0.6:
            recommendations.append("High evaporation - chemical dispersants recommended")
        elif evaporation_rate > 0.4:
            recommendations.append("Moderate evaporation - consider dispersants if spreading")
        
        # Environmental recommendations
        if wind_speed > 15:
            recommendations.append("🌬️ High wind - prioritize containment and monitor drift")
        elif wind_speed > 10:
            recommendations.append("Moderate wind - adjust boom placement for drift")
        
        if wave_height > 2:
            recommendations.append("🌊 High waves - mechanical recovery may be difficult")
        
        # Oil-specific recommendations
        if oil_type.lower() == "heavy":
            recommendations.append("Heavy oil - use high-viscosity skimmers")
        elif oil_type.lower() == "diesel":
            recommendations.append("Light oil - dispersants may be effective")
        
        # Spill size recommendations
        if spill_percentage > 30:
            recommendations.append("⚠️ Large spill detected - request additional resources")
        
        return recommendations
    
    def predict(self, data: OilSpillData, spill_percentage: float = 0) -> PredictionResponse:
        """Enhanced prediction with calibration"""
        
        oil_config = self.oil_types.get(data.oil_type.lower(), self.oil_types["crude"])
        
        # Calculate spread area with calibration
        spread_area = self.calculate_spread_area(data, oil_config, spill_percentage)
        
        # Calculate evaporation rate
        evaporation_rate = self.calculate_evaporation(data, oil_config)
        
        # Determine risk level
        risk_level = self.determine_risk_level(spread_area, spill_percentage, data.oil_type)
        
        # Calculate confidence score based on data completeness
        confidence_score = 0.8  # Base confidence
        if spill_percentage > 0:
            confidence_score += 0.15  # Higher confidence with image analysis
        if all([data.temperature, data.wind_speed, data.wave_height]):
            confidence_score += 0.05
        
        confidence_score = min(confidence_score, 0.95)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            risk_level, evaporation_rate, data.wind_speed, 
            data.wave_height, data.oil_type, spill_percentage
        )
        
        # Calibrated spread (more realistic)
        calibrated_spread = spread_area * (0.7 + 0.3 * confidence_score)
        
        return PredictionResponse(
            spread_area=round(spread_area, 2),
            risk_level=risk_level,
            evaporation_rate=round(evaporation_rate * 100, 2),
            recommendations=recommendations,
            oil_spill_mask=None,
            overlay_image=None,
            spill_percentage=round(spill_percentage, 2) if spill_percentage > 0 else None,
            confidence_score=round(confidence_score, 2),
            calibrated_spread=round(calibrated_spread, 2)
        )

traditional_model = TraditionalOilSpillModel()

# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Oil Spill Model API with U-Net (Enhanced & Calibrated)",
        "status": "active",
        "unet_loaded": unet_predictor.is_loaded,
        "model_input_shape": str(unet_predictor.input_shape) if unet_predictor.is_loaded else None,
        "tensorflow_available": TENSORFLOW_AVAILABLE,
        "model_version": "2.0 - Physics-based with calibration",
        "color_options": {
            "available_colors": {
                "red": "(0,0,255)",
                "green": "(0,255,0)",
                "blue": "(255,0,0)",
                "yellow": "(0,255,255)",
                "cyan": "(255,255,0)",
                "magenta": "(255,0,255)",
                "orange": "(0,165,255)",
                "purple": "(128,0,128)"
            },
            "auto_coloring": "Based on risk level or oil type"
        },
        "dependencies": {
            "numpy": np is not None,
            "cv2": cv2 is not None,
            "PIL": Image is not None
        }
    }

@app.post("/predict")
def predict(data: OilSpillData):
    try:
        prediction = traditional_model.predict(data)
        
        # Save to JSON
        all_data = load_data()
        all_data["records"].append({
            "input": data.dict(),
            "prediction": prediction.dict(),
            "timestamp": datetime.now().isoformat()
        })
        save_data(all_data)
        
        return prediction
    except Exception as e:
        print(f"Error in predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-with-image")
async def predict_with_image(
    location: str,
    oil_type: str,
    volume: float,
    temperature: float,
    wind_speed: float,
    wave_height: float,
    image: UploadFile = File(...),
    overlay_color: Optional[str] = Query(None, description="Overlay color (red, green, blue, yellow, cyan, magenta, orange, purple)"),
    opacity: float = Query(0.5, ge=0.0, le=1.0, description="Overlay opacity (0.0 to 1.0)"),
    color_by: Optional[str] = Query(None, description="Auto-color by: 'risk' or 'oil_type'")
):
    try:
        if cv2 is None or np is None or Image is None:
            raise HTTPException(
                status_code=500, 
                detail="Image processing not available - install opencv-python and Pillow"
            )
        
        # Read image
        contents = await image.read()
        
        # Save the uploaded image directly to disk
        os.makedirs("uploads", exist_ok=True)
        safe_filename = "".join(c for c in image.filename if c.isalnum() or c in "._-")
        if not safe_filename: 
            safe_filename = "upload.jpg"
        image_path = f"uploads/img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename}"
        with open(image_path, "wb") as f:
            f.write(contents)
            
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        print(f"📸 Image loaded: {img.shape}")
        
        # U-Net prediction with calibration
        mask = unet_predictor.predict(img)
        print(f"🎭 Mask generated: {mask.shape}")
        
        # Calculate spill percentage with noise reduction
        total_pixels = mask.size
        spill_pixels = np.sum(mask > 0)
        spill_percentage = (spill_pixels / total_pixels) * 100
        
        # Apply calibration to spill percentage (more realistic)
        spill_percentage = min(spill_percentage * 1.2, 85)  # Scale slightly but cap
        
        print(f"📊 Calibrated spill percentage: {spill_percentage:.2f}%")
        
        # Traditional prediction with U-Net data
        data = OilSpillData(
            location=location,
            oil_type=oil_type,
            volume=volume,
            temperature=temperature,
            wind_speed=wind_speed,
            wave_height=wave_height,
            timestamp=datetime.now().isoformat()
        )
        
        prediction = traditional_model.predict(data, spill_percentage)
        
        # Determine overlay color
        color_map = {
            "red": (0, 0, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255),
            "cyan": (255, 255, 0),
            "magenta": (255, 0, 255),
            "orange": (0, 165, 255),
            "purple": (128, 0, 128)
        }
        
        # Select color based on parameters
        if color_by == "risk":
            selected_color = get_color_by_risk_level(prediction.risk_level)
            print(f"🎨 Using risk-based color: {prediction.risk_level}")
        elif color_by == "oil_type":
            selected_color = get_color_by_oil_type(oil_type)
            print(f"🎨 Using oil-type based color: {oil_type}")
        elif overlay_color and overlay_color.lower() in color_map:
            selected_color = color_map[overlay_color.lower()]
            print(f"🎨 Using custom color: {overlay_color}")
        else:
            # Default: use risk level
            selected_color = get_color_by_risk_level(prediction.risk_level)
            print(f"🎨 Using default risk-based color: {prediction.risk_level}")
        
        # Create colored overlay
        colored_overlay = create_colored_overlay(img, mask, selected_color, opacity)
        
        if colored_overlay is not None:
            # Convert overlay to base64
            overlay_rgb = cv2.cvtColor(colored_overlay, cv2.COLOR_BGR2RGB)
            overlay_image_pil = Image.fromarray(overlay_rgb)
            buffered_overlay = io.BytesIO()
            overlay_image_pil.save(buffered_overlay, format="PNG")
            overlay_base64 = base64.b64encode(buffered_overlay.getvalue()).decode()
            prediction.overlay_image = overlay_base64
            
            # Also save the mask as before for backward compatibility
            mask_image = Image.fromarray(mask * 255)
            buffered_mask = io.BytesIO()
            mask_image.save(buffered_mask, format="PNG")
            mask_base64 = base64.b64encode(buffered_mask.getvalue()).decode()
            prediction.oil_spill_mask = mask_base64
        else:
            # Fallback to just mask
            mask_image = Image.fromarray(mask * 255)
            buffered_mask = io.BytesIO()
            mask_image.save(buffered_mask, format="PNG")
            mask_base64 = base64.b64encode(buffered_mask.getvalue()).decode()
            prediction.oil_spill_mask = mask_base64
        
        prediction.spill_percentage = round(spill_percentage, 2)
        
        # Save to JSON
        all_data = load_data()
        all_data["records"].append({
            "input": data.dict(),
            "prediction": prediction.dict(),
            "timestamp": datetime.now().isoformat(),
            "spill_percentage": spill_percentage,
            "image_processed": True,
            "confidence_score": prediction.confidence_score,
            "overlay_color": selected_color,
            "opacity": opacity
        })
        save_data(all_data)
        
        print("✅ Prediction completed successfully")
        print(f"📈 Spread: {prediction.spread_area} m², Risk: {prediction.risk_level}, Confidence: {prediction.confidence_score}")
        
        return prediction
        
    except Exception as e:
        print(f"❌ Error in predict-with-image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info")
def get_model_info():
    return {
        "oil_types": list(traditional_model.oil_types.keys()),
        "unet_model": {
            "loaded": unet_predictor.is_loaded,
            "path": MODEL_PATH,
            "input_shape": str(unet_predictor.input_shape) if unet_predictor.is_loaded else None,
            "description": "U-Net model for oil spill segmentation with ensemble prediction",
            "tensorflow_available": TENSORFLOW_AVAILABLE
        },
        "enhanced_model": {
            "type": "Physics-based with calibration",
            "features": [
                "Fay's law spreading calculation",
                "Arrhenius evaporation model",
                "Multi-factor risk assessment",
                "Confidence scoring",
                "Intelligent recommendations"
            ]
        },
        "calibration": {
            "spread_scaling": "Dynamic based on spill percentage",
            "confidence_threshold": 0.3,
            "max_evaporation": "85%",
            "risk_upgrade_thresholds": {"spill_25%": "High", "spill_40%": "Critical"}
        },
        "available_colors": {
            "red": "(0,0,255)",
            "green": "(0,255,0)",
            "blue": "(255,0,0)",
            "yellow": "(0,255,255)",
            "cyan": "(255,255,0)",
            "magenta": "(255,0,255)",
            "orange": "(0,165,255)",
            "purple": "(128,0,128)"
        },
        "available_modules": {
            "tensorflow": TENSORFLOW_AVAILABLE,
            "numpy": np is not None,
            "cv2": cv2 is not None,
            "PIL": Image is not None
        }
    }

@app.get("/history")
def get_history(limit: int = 50):
    try:
        all_data = load_data()
        return {"records": all_data["records"][-limit:]}
    except Exception as e:
        print(f"Error in history: {e}")
        return {"records": []}

@app.get("/calibration-factors")
def get_calibration_factors():
    """Get current calibration parameters for transparency"""
    return {
        "spread_calibration": {
            "min_multiplier": 0.7,
            "max_multiplier": 1.3,
            "confidence_weight": 0.3
        },
        "evaporation_limits": {
            "max_rate": 0.85,
            "temperature_coefficient": 0.02,
            "wind_coefficient": 0.05
        },
        "risk_thresholds": {
            "critical_spread": 5000,
            "high_spread": 1000,
            "medium_spread": 100,
            "critical_spill_percentage": 40,
            "high_spill_percentage": 25
        },
        "confidence_scoring": {
            "base_confidence": 0.8,
            "image_bonus": 0.15,
            "data_completeness_bonus": 0.05,
            "max_confidence": 0.95
        },
        "color_options": {
            "available_colors": ["red", "green", "blue", "yellow", "cyan", "magenta", "orange", "purple"],
            "auto_coloring_modes": ["risk", "oil_type"],
            "default_opacity": 0.5
        }
    }