import React from 'react';
import { Canvas } from '@react-three/fiber';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import OceanScene from '../features/3d/OceanScene';
import GlassCard from '../components/GlassCard';
import GlowingButton from '../components/GlowingButton';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* 3D Background */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
        <Canvas camera={{ position: [0, 2, 5], fov: 45 }}>
          <ambientLight intensity={0.5} />
          <OceanScene />
        </Canvas>
      </div>

      {/* Foreground Content */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <GlassCard style={{ padding: '40px', textAlign: 'center', maxWidth: '800px' }}>
            <h1 className="glow-text" style={{ fontSize: '3rem', marginBottom: '20px' }}>AI-Powered Oil Spill Detection</h1>
            <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '40px' }}>
              Futuristic, high-accuracy model using U-Net for real-time risk assessment and ocean protection.
            </p>
            
            <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
              <GlowingButton onClick={() => navigate('/auth')}>Login / Register</GlowingButton>
              <GlowingButton variant="secondary" onClick={() => navigate('/dashboard')}>Try Demo Dashboard</GlowingButton>
            </div>
            
            <div style={{ 
              display: 'flex', 
              gap: '40px', 
              justifyContent: 'center', 
              marginTop: '40px',
              borderTop: '1px solid var(--glass-border)',
              paddingTop: '20px'
            }}>
              <div>
                <h3 className="glow-text" style={{ fontSize: '2rem' }}>96.5%</h3>
                <p style={{ color: 'var(--text-secondary)' }}>Accuracy Rate</p>
              </div>
              <div>
                <h3 className="glow-text" style={{ fontSize: '2rem' }}>&lt; 2s</h3>
                <p style={{ color: 'var(--text-secondary)' }}>Processing Time</p>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
};

export default Landing;
