import React, { useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { UploadCloud, Activity, AlertTriangle, Crosshair, Navigation, Loader2, Image as ImageIcon, Layers } from 'lucide-react';
import InteractiveGlobe from '../features/3d/InteractiveGlobe';
import GlassCard from '../components/GlassCard';
import GlowingButton from '../components/GlowingButton';
import { useNavigate } from 'react-router-dom';

const UserDashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showMask, setShowMask] = useState(false);
  const [backendError, setBackendError] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setShowMask(false);
      setBackendError(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setShowMask(false);
      setBackendError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    
    setLoading(true);
    setResult(null);
    setShowMask(false);
    setBackendError(null);

    const formData = new FormData();
    formData.append('image', selectedFile);
    
    const params = {
      location: "Active Scan",
      oil_type: "Unknown",
      volume: 100,
      temperature: 25.0,
      wind_speed: 15.0,
      wave_height: 2.0
    };

    try {
      const response = await axios.post('http://localhost:8000/predict-with-image', formData, {
        params: params,
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResult(response.data);
      setTimeout(() => setShowMask(true), 500); 
    } catch (error) {
      console.error("Error predicting:", error);
      setBackendError("Cannot connect to server.py. Please ensure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', backgroundColor: 'var(--bg-dark)' }}>
      {/* Top Navbar */}
      <GlassCard className="neon-border" style={{ 
        margin: '20px', 
        padding: '15px 30px', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        background: 'rgba(5, 10, 21, 0.8)',
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <Crosshair color="var(--cyan-neon)" size={28} className="pulse-glow" style={{ borderRadius: '50%' }} />
          <h2 className="glow-text" style={{ margin: 0, color: 'var(--text-primary)', letterSpacing: '2px' }}>OSDS CORE</h2>
        </div>
        <div>
          <GlowingButton variant="secondary" onClick={() => navigate('/admin')} style={{ marginRight: '15px' }}>Admin Console</GlowingButton>
          <GlowingButton onClick={() => navigate('/')}>Disconnect</GlowingButton>
        </div>
      </GlassCard>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', padding: '0 20px 20px 20px', gap: '20px' }}>
        
        {/* Left Side: 3D Globe */}
        <div style={{ flex: '1 1 30%', position: 'relative', borderRadius: '16px', overflow: 'hidden' }} className="glass-panel">
          <Canvas camera={{ position: [0, 0, 4.5], fov: 45 }}>
            <ambientLight intensity={0.5} />
            <InteractiveGlobe />
          </Canvas>
          <div style={{ position: 'absolute', bottom: '20px', width: '100%', display: 'flex', justifyContent: 'center' }}>
            <GlassCard style={{ padding: '10px 20px', background: 'rgba(0, 50, 100, 0.3)' }} className="neon-border">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Navigation size={18} color="var(--cyan-neon)" className="pulse-glow" />
                <span style={{ color: 'var(--cyan-neon)', fontWeight: 'bold' }}>Threat Scanner Active</span>
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Right Side: Upload and Prediction Panel */}
        <div style={{ flex: '1 1 70%', display: 'flex', flexDirection: 'column', gap: '20px', overflowY: 'auto' }}>
          
          <GlassCard style={{ padding: '30px' }} className="neon-border">
            <h3 style={{ marginBottom: '20px', color: 'var(--cyan-neon)', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <UploadCloud size={24} /> 
              Imagery Upload & Analysis
            </h3>
            
            <div 
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              style={{
                border: '2px dashed rgba(0, 240, 255, 0.5)',
                borderRadius: '12px',
                padding: previewUrl ? '20px' : '60px',
                textAlign: 'center',
                background: 'rgba(0, 240, 255, 0.02)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onClick={() => !loading && fileInputRef.current.click()}
            >
              <input 
                type="file" 
                accept="image/*" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                onChange={handleFileChange}
                disabled={loading}
              />

              {!previewUrl ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <UploadCloud size={64} color="var(--cyan-neon)" style={{ marginBottom: '20px', filter: 'drop-shadow(0 0 10px rgba(0, 240, 255, 0.5))' }} />
                  <p style={{ fontSize: '1.2rem', color: 'var(--text-primary)' }}>Drag & drop aerial footage</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  
                  {/* Visually Distinguish Images Mode */}
                  <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
                    
                    {/* 1. Original Input Image */}
                    <div style={{ flex: 1, minWidth: '250px' }}>
                       <p style={{ color: 'var(--text-secondary)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                         <ImageIcon size={18} /> Original Image
                       </p>
                       <div style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--glass-border)' }}>
                          <img src={previewUrl} alt="Target" style={{ width: '100%', display: 'block' }} />
                          {loading && (
                            <motion.div 
                              initial={{ top: '-10%' }}
                              animate={{ top: '110%' }}
                              transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
                              style={{ position: 'absolute', left: 0, width: '100%', height: '5px', background: 'var(--cyan-neon)', boxShadow: '0 0 15px var(--cyan-neon)', zIndex: 10 }}
                            />
                          )}
                       </div>
                    </div>

                    {/* 2. Generated Mask Output */}
                    <AnimatePresence>
                      {showMask && result && result.oil_spill_mask && (
                        <motion.div 
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          style={{ flex: 1, minWidth: '250px' }}
                        >
                          <p style={{ color: 'var(--risk-high)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <Layers size={18} /> Generated AI Mask (Output)
                          </p>
                          <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--risk-high)', background: '#000' }}>
                            <img src={`data:image/png;base64,${result.oil_spill_mask}`} alt="Raw Mask Generated by Backend" style={{ width: '100%', display: 'block' }} />
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* 3. Combined Overlay Output */}
                    <AnimatePresence>
                      {showMask && result && result.oil_spill_mask && (
                        <motion.div 
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          style={{ flex: 1, minWidth: '250px' }}
                        >
                          <p style={{ color: 'var(--cyan-neon)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <Layers size={18} /> UI Overlay Visualization
                          </p>
                          <div style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--cyan-neon)' }}>
                            <img src={previewUrl} alt="Target" style={{ width: '100%', display: 'block' }} />
                            <img 
                              src={`data:image/png;base64,${result.oil_spill_mask}`} 
                              alt="Overlay Mask" 
                              style={{ 
                                position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', 
                                mixBlendMode: 'screen', // Makes backend's black bg transparent!
                                filter: 'brightness(1.5) contrast(200%) drop-shadow(0 0 5px rgba(255, 0, 0, 0.8))',
                                pointerEvents: 'none'
                              }} 
                            />
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {backendError && (
                    <div style={{ padding: '15px', background: 'rgba(255,0,0,0.1)', color: 'var(--risk-critical)', border: '1px solid var(--risk-critical)', borderRadius: '8px' }}>
                      <AlertTriangle size={20} style={{ display: 'inline', marginRight: '10px' }} />
                      {backendError}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
                    {!result && !loading && (
                      <GlowingButton onClick={(e) => { e.stopPropagation(); handleAnalyze(); }} style={{ padding: '15px 30px' }}>
                        Run U-Net AI Detection
                      </GlowingButton>
                    )}
                    {loading && (
                      <GlowingButton variant="secondary" style={{ cursor: 'default' }}>
                        <Loader2 size={20} style={{ animation: 'spin 2s linear infinite', display: 'inline-block', marginRight: '8px' }}/>
                        Processing with Python Backend...
                      </GlowingButton>
                    )}
                    <GlowingButton variant="secondary" onClick={(e) => { e.stopPropagation(); setPreviewUrl(null); setResult(null); setShowMask(false); setBackendError(null); }} disabled={loading}>
                      Clear Image
                    </GlowingButton>
                  </div>
                </div>
              )}
            </div>
          </GlassCard>

          {/* Results Analytics Section */}
          <AnimatePresence>
            {result && showMask && (
              <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 30 }}>
                <GlassCard style={{ padding: '30px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '25px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '15px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Activity size={28} color="var(--cyan-neon)" />
                      <h3 style={{ margin: 0, fontSize: '1.5rem', letterSpacing: '1px' }}>Analysis Diagnostics</h3>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '20px', marginBottom: '25px', flexWrap: 'wrap' }}>
                    <div style={{ flex: '1 1 200px', padding: '20px', background: 'rgba(5, 10, 21, 0.6)', borderRadius: '12px', borderLeft: `4px solid ${result.risk_level?.toLowerCase() === 'critical' ? 'var(--risk-critical)' : result.risk_level?.toLowerCase() === 'high' ? 'var(--risk-high)' : 'var(--risk-medium)'}` }}>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase' }}>System Risk Level</p>
                      <h2 style={{ margin: 0, fontSize: '2.2rem', color: result.risk_level?.toLowerCase() === 'critical' ? 'var(--risk-critical)' : result.risk_level?.toLowerCase() === 'high' ? 'var(--risk-high)' : 'var(--text-primary)' }}>
                        {result.risk_level}
                      </h2>
                    </div>

                    <div style={{ flex: '1 1 200px', padding: '20px', background: 'rgba(5, 10, 21, 0.6)', borderRadius: '12px', borderLeft: '4px solid var(--cyan-neon)' }}>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase' }}>Spill Coverage</p>
                      <h2 style={{ margin: 0, fontSize: '2.2rem', color: 'var(--cyan-neon)' }}>{result.spill_percentage}%</h2>
                    </div>
                  </div>

                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                    <h4 style={{ color: 'var(--text-secondary)', marginBottom: '15px', textTransform: 'uppercase' }}>Automated Recommendations:</h4>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                      {result.recommendations?.map((rec, i) => (
                        <motion.li 
                          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                          key={i} style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: i !== result.recommendations.length - 1 ? '15px' : '0', padding: '12px 15px', borderRadius: '8px', background: 'rgba(255, 42, 42, 0.05)' }}
                        >
                          <AlertTriangle size={18} color="var(--risk-high)" />
                          <span style={{ fontSize: '1.05rem', color: 'var(--text-primary)' }}>{rec}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default UserDashboard;
