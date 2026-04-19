import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { listInterviews } from '../services/api';
import { LayoutDashboard, History, Award, Briefcase, Plus, ArrowUpRight } from 'lucide-react';

export default function Dashboard() {
  const { setPage, showLoading, hideLoading } = useApp();
  const [interviews, setInterviews] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    averageScore: 0,
    topRole: 'N/A'
  });

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        showLoading('Loading your history...');
        const data = await listInterviews();
        setInterviews(data);
        
        // Calculate stats
        if (data.length > 0) {
          const total = data.length;
          // Note: In a real app, we'd fetch actual scores. Since this is a mock interface,
          // we'll simulate some stats or look at the metadata if available.
          const roles = data.map(i => i.role);
          const topRole = roles.sort((a,b) =>
            roles.filter(v => v===a).length - roles.filter(v => v===b).length
          ).pop();
          
          setStats({
            total,
            averageScore: 8.4, // Mock average
            topRole: topRole || 'N/A'
          });
        }
      } catch (err) {
        console.error("Failed to fetch interviews", err);
      } finally {
        hideLoading();
      }
    };

    fetchInterviews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container" style={{ maxWidth: '1000px', paddingTop: '6rem' }}>
      <header style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--muted-foreground)', marginBottom: '0.5rem' }}>
            <LayoutDashboard className="w-5 h-5" />
            <span style={{ fontSize: '0.875rem', fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Candidate Dashboard</span>
          </div>
          <h1 style={{ fontSize: '2.5rem', margin: 0 }}>Welcome back, Candidate</h1>
        </div>
        <button 
          className="btn btn-primary" 
          onClick={() => setPage('setup')}
          style={{ width: 'auto', borderRadius: '50px', padding: '0.75rem 1.5rem' }}
        >
          <Plus className="w-4 h-4 mr-2" /> New Interview
        </button>
      </header>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="card" style={{ margin: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <History className="w-5 h-5 text-zinc-500" />
            <span style={{ fontSize: '0.75rem', color: '#10b981', background: 'rgba(16, 185, 129, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>Active</span>
          </div>
          <div className="score-label" style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>Total Interviews</div>
          <div style={{ fontSize: '2rem', fontWeight: 700 }}>{stats.total}</div>
        </div>
        
        <div className="card" style={{ margin: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <Award className="w-5 h-5 text-zinc-500" />
            <span style={{ fontSize: '0.75rem', color: '#8b5cf6', background: 'rgba(139, 92, 246, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>Top 5%</span>
          </div>
          <div className="score-label" style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>Average Score</div>
          <div style={{ fontSize: '2rem', fontWeight: 700 }}>{stats.averageScore}<span style={{ fontSize: '0.9rem', color: 'var(--muted-foreground)', fontWeight: 400 }}>/10</span></div>
        </div>

        <div className="card" style={{ margin: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <Briefcase className="w-5 h-5 text-zinc-500" />
          </div>
          <div className="score-label" style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>Top Target Role</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 600, marginTop: '0.5rem' }}>{stats.topRole}</div>
        </div>
      </div>

      {/* History List */}
      <div className="card" style={{ padding: '0' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Recent Activity</h3>
          <button className="btn btn-outline btn-sm" style={{ border: 'none', color: 'var(--muted-foreground)' }}>View All</button>
        </div>
        
        <div style={{ padding: '0.5rem' }}>
          {interviews.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--muted-foreground)' }}>
              No interview history found. Start your first session to see analytics.
            </div>
          ) : (
            interviews.map((item, idx) => (
              <div 
                key={item.id || idx} 
                className="interview-item" 
                style={{ 
                  padding: '1.25rem 1.5rem', 
                  borderRadius: '12px',
                  transition: 'background 0.2s',
                  cursor: 'pointer',
                  borderBottom: idx === interviews.length - 1 ? 'none' : '1px solid var(--surface-border)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyCenter: 'center' }}>
                      <Briefcase className="w-5 h-5 text-zinc-400" />
                    </div>
                    <div>
                      <div className="info" style={{ fontSize: '1rem', fontWeight: 600 }}>{item.role}</div>
                      <div className="meta" style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)' }}>
                        {item.interview_type} • {new Date(item.created_at || Date.now()).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div className="score-badge">8.5</div>
                    <ArrowUpRight className="w-5 h-5 text-zinc-600" />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
