import React from 'react';

const GlassCard = ({ children, style, className = '' }) => {
  return (
    <div className={`glass-panel ${className}`} style={{ ...style }}>
      {children}
    </div>
  );
};

export default GlassCard;
