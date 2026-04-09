import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Canvas } from '@react-three/fiber';
import { motion } from 'framer-motion';
import OceanScene from '../features/3d/OceanScene';
import GlassCard from '../components/GlassCard';
import GlowingButton from '../components/GlowingButton';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();

  const handleAuth = (e) => {
    e.preventDefault();
    // Dummy authentication
    navigate('/dashboard');
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '20px',
    borderRadius: '8px',
    border: '1px solid var(--glass-border)',
    backgroundColor: 'rgba(5, 10, 21, 0.6)',
    color: 'var(--text-primary)',
    outline: 'none',
    transition: 'all 0.3s ease'
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      
      {/* 3D Ocean Side Panel */}
      <div style={{ flex: 1, position: 'relative', borderRight: '1px solid var(--glass-border)' }}>
        <Canvas camera={{ position: [0, 2, 5], fov: 45 }}>
          <ambientLight intensity={0.5} />
          <OceanScene />
        </Canvas>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
           <h2 className="glow-text" style={{ fontSize: '2.5rem' }}>Secure Access</h2>
           <p style={{ color: 'var(--text-secondary)' }}>Enterprise-grade AI analysis</p>
        </div>
      </div>

      {/* Auth Form Side Panel */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-dark)' }}>
        <motion.div
           initial={{ opacity: 0, x: 50 }}
           animate={{ opacity: 1, x: 0 }}
           transition={{ duration: 0.5 }}
           style={{ width: '100%', maxWidth: '400px' }}
        >
          <GlassCard style={{ padding: '40px' }}>
            <h2 style={{ marginBottom: '30px', textAlign: 'center', color: 'var(--cyan-neon)' }}>
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            
            <form onSubmit={handleAuth}>
              {!isLogin && (
                <input 
                  type="text" 
                  placeholder="Full Name" 
                  style={inputStyle}
                  onFocus={(e) => e.target.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.3)'}
                  onBlur={(e) => e.target.style.boxShadow = 'none'}
                  required
                />
              )}
              
              <input 
                type="email" 
                placeholder="Email Address" 
                style={inputStyle}
                onFocus={(e) => e.target.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.3)'}
                onBlur={(e) => e.target.style.boxShadow = 'none'}
                required
              />
              
              <input 
                type="password" 
                placeholder="Password" 
                style={inputStyle}
                onFocus={(e) => e.target.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.3)'}
                onBlur={(e) => e.target.style.boxShadow = 'none'}
                required
              />

              {!isLogin && (
                <select style={{...inputStyle, appearance: 'none'}} required>
                  <option value="user">Standard User</option>
                  <option value="admin">Administrator</option>
                </select>
              )}

              <GlowingButton style={{ width: '100%', marginTop: '10px' }} onClick={handleAuth}>
                {isLogin ? 'Login to Dashboard' : 'Complete Registration'}
              </GlowingButton>
            </form>

            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <p style={{ color: 'var(--text-secondary)', cursor: 'pointer' }} onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
              </p>
            </div>
          </GlassCard>
        </motion.div>
      </div>

    </div>
  );
};

export default Auth;
