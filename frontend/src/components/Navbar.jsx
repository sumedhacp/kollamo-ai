// src/components/Navbar.jsx
import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'overview', label: 'Platform Overview' },
    { id: 'sandbox', label: 'Inference Sandbox' },
    { id: 'studio', label: 'Social Ingestion' },
    { id: 'analytics', label: 'Audience Intelligence' }
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--border-color)'
    }}>
      <div style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '0 1.5rem',
        height: '66px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Product Brand & Tagline */}
        <div 
          onClick={() => setActiveTab('overview')}
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.85rem' }}
        >
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '800',
            fontSize: '1.2rem',
            boxShadow: '0 4px 10px rgba(37, 99, 235, 0.25)'
          }}>
            K
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontWeight: '800', fontSize: '1.05rem', color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
                Kollamo<span style={{ color: 'var(--primary)' }}>.ai</span>
              </span>
              <span style={{
                fontSize: '0.65rem',
                fontFamily: 'var(--font-mono)',
                backgroundColor: 'var(--primary-light)',
                color: 'var(--primary)',
                padding: '0.15rem 0.45rem',
                borderRadius: '5px',
                border: '1px solid #bfdbfe',
                fontWeight: '700'
              }}>
                v1.0
              </span>
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-subtle)', fontWeight: '600' }}>
              Indic Code-Mixed Sentiment & Social Intelligence Engine
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{
          display: 'flex',
          gap: '0.25rem',
          backgroundColor: 'var(--bg-subtle)',
          padding: '0.3rem',
          borderRadius: '10px',
          border: '1px solid var(--border-color)'
        }}>
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  border: 'none',
                  background: isActive ? '#ffffff' : 'transparent',
                  color: isActive ? 'var(--text-main)' : 'var(--text-muted)',
                  fontWeight: isActive ? '700' : '500',
                  fontSize: '0.8125rem',
                  padding: '0.4rem 0.85rem',
                  borderRadius: '7px',
                  cursor: 'pointer',
                  boxShadow: isActive ? '0 1px 3px rgba(0,0,0,0.06)' : 'none',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* Live Status Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          backgroundColor: 'var(--pos-bg)',
          padding: '0.35rem 0.8rem',
          borderRadius: '9999px',
          border: '1px solid var(--pos-border)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: 'var(--pos-color)',
            boxShadow: '0 0 0 2px rgba(16, 185, 129, 0.2)'
          }} />
          <span style={{
            fontSize: '0.75rem',
            fontWeight: '700',
            color: '#065f46',
            fontFamily: 'var(--font-mono)'
          }}>
            Inference Online
          </span>
        </div>
      </div>
    </header>
  );
}