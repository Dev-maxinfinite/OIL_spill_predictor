import React from 'react';
import { motion } from 'framer-motion';

const GlowingButton = ({ children, onClick, variant = 'primary', className = '', style = {}, disabled = false }) => {
  const isPrimary = variant === 'primary';
  
  const baseStyle = {
    padding: '12px 24px',
    borderRadius: '8px',
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: 'bold',
    fontSize: '1rem',
    color: isPrimary ? '#050a15' : 'var(--cyan-neon)',
    backgroundColor: isPrimary ? 'var(--cyan-neon)' : 'transparent',
    border: isPrimary ? 'none' : '1px solid var(--cyan-neon)',
    boxShadow: isPrimary ? '0 0 15px rgba(0, 240, 255, 0.4)' : 'none',
    opacity: disabled ? 0.5 : 1,
    outline: 'none',
    ...style
  };

  return (
    <motion.button
      onClick={onClick}
      style={baseStyle}
      disabled={disabled}
      className={`${isPrimary ? 'pulse-glow' : ''} ${className}`}
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
    >
      {children}
    </motion.button>
  );
};

export default GlowingButton;
