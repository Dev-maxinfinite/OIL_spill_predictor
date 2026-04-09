import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CheckCircle, XCircle, ShieldAlert } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import GlowingButton from '../components/GlowingButton';

const mockData = [
  { name: 'Mon', incidents: 3 },
  { name: 'Tue', incidents: 5 },
  { name: 'Wed', incidents: 2 },
  { name: 'Thu', incidents: 8 },
  { name: 'Fri', incidents: 4 },
  { name: 'Sat', incidents: 10 },
  { name: 'Sun', incidents: 6 },
];

const mockActivities = [
  { id: 1, user: 'John Doe', location: 'Gulf of Mexico', risk: 'Critical', status: 'Pending', time: '10 mins ago' },
  { id: 2, user: 'Jane Smith', location: 'North Sea', risk: 'Medium', status: 'Approved', time: '1 hour ago' },
  { id: 3, user: 'Auto-Sentinel', location: 'Arabian Sea', risk: 'High', status: 'Pending', time: '2 hours ago' },
  { id: 4, user: 'System Bot', location: 'Baltic Sea', risk: 'Low', status: 'Rejected', time: '5 hours ago' },
];

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [activities, setActivities] = useState(mockActivities);

  const handleStatusChange = (id, newStatus) => {
    setActivities(activities.map(a => a.id === id ? { ...a, status: newStatus } : a));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', backgroundColor: 'var(--bg-dark)', padding: '20px', overflowY: 'auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2 className="glow-text">System Analytics & Administration</h2>
        <GlowingButton variant="secondary" onClick={() => navigate('/dashboard')}>User Dashboard</GlowingButton>
      </div>

      {/* Analytics Row */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <GlassCard style={{ flex: 1, padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <div style={{ padding: '15px', background: 'rgba(255, 42, 42, 0.1)', borderRadius: '12px' }}>
              <ShieldAlert size={32} color="var(--risk-critical)" />
            </div>
            <div>
              <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Critical Alerts (24h)</p>
              <h1 style={{ margin: 0, color: 'var(--risk-critical)' }}>12</h1>
            </div>
          </div>
        </GlassCard>
        
        <GlassCard style={{ flex: 2, padding: '20px', height: '300px' }}>
          <h3 style={{ marginBottom: '20px', color: 'var(--cyan-neon)' }}>Detection Trends (Past 7 Days)</h3>
          <ResponsiveContainer width="100%" height="80%">
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="var(--text-secondary)" />
              <YAxis stroke="var(--text-secondary)" />
              <Tooltip contentStyle={{ backgroundColor: 'var(--bg-dark)', border: '1px solid var(--glass-border)' }} />
              <Line type="monotone" dataKey="incidents" stroke="var(--cyan-neon)" strokeWidth={3} dot={{ r: 6, fill: 'var(--bg-dark)' }} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>

      {/* Activity Table */}
      <GlassCard style={{ flex: 1, padding: '20px' }}>
        <h3 style={{ marginBottom: '20px', color: 'var(--cyan-neon)' }}>Recent Detection Reports</h3>
        
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '15px' }}>Location</th>
              <th style={{ padding: '15px' }}>Reported By</th>
              <th style={{ padding: '15px' }}>Risk Level</th>
              <th style={{ padding: '15px' }}>Time</th>
              <th style={{ padding: '15px' }}>Status</th>
              <th style={{ padding: '15px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {activities.map((item, index) => (
              <motion.tr 
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
              >
                <td style={{ padding: '15px' }}>{item.location}</td>
                <td style={{ padding: '15px' }}>{item.user}</td>
                <td style={{ padding: '15px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    background: item.risk === 'Critical' ? 'rgba(255,0,0,0.2)' : 'rgba(255,255,0,0.1)',
                    color: item.risk === 'Critical' ? 'var(--risk-critical)' : 'var(--risk-medium)'
                  }}>
                    {item.risk}
                  </span>
                </td>
                <td style={{ padding: '15px', color: 'var(--text-secondary)' }}>{item.time}</td>
                <td style={{ padding: '15px' }}>
                  <span style={{ 
                    color: item.status === 'Pending' ? 'var(--text-secondary)' : item.status === 'Approved' ? 'var(--risk-safe)' : 'var(--risk-high)'
                  }}>
                    {item.status}
                  </span>
                </td>
                <td style={{ padding: '15px', display: 'flex', gap: '10px' }}>
                  {item.status === 'Pending' && (
                    <>
                      <button 
                        onClick={() => handleStatusChange(item.id, 'Approved')}
                        style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                        title="Approve API Dispersants"
                      >
                        <CheckCircle color="var(--risk-safe)" size={20} />
                      </button>
                      <button 
                        onClick={() => handleStatusChange(item.id, 'Rejected')}
                        style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                        title="Reject / False Alarm"
                      >
                        <XCircle color="var(--risk-critical)" size={20} />
                      </button>
                    </>
                  )}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
};

export default AdminDashboard;
