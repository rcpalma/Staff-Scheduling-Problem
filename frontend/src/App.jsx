import React, { useState } from 'react';
import axios from 'axios';
import { Play, Activity, Users, Calendar, AlertCircle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';

function App() {
  const [instance, setInstance] = useState(6);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:8000/solve', {
        instance_number: instance
      });

      if (response.data.status !== 'ERROR' && response.data.status !== 'INFEASIBLE') {
        setData(response.data);
      } else {
        setError(response.data.message || 'Optimization failed or returned infeasible state.');
        setData(null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const dayNames = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
  const formatDayLabel = (d) => `${dayNames[d % 7]}${Math.floor(d / 7) + 1}`;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      let barColor = '#22c55e'; // verde
      if (d.actual < d.required) barColor = '#ef4444'; // vermelho
      else if (d.actual > d.required) barColor = '#3b82f6'; // azul
      return (
        <div className="custom-tooltip">
          <div className="tooltip-label">Dia {label}</div>
          <div className="tooltip-item" style={{ color: barColor }}>
            <span>Qtd Alocada:</span>
            <strong>{d.actual}</strong>
          </div>
          <div className="tooltip-item" style={{ color: '#ffffff' }}>
            <span>Qtd Recomendada:</span>
            <strong>{d.required}</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard-container">
      <div style={{ textAlign: 'center', marginBottom: '2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <a
          href="https://www.schedulingbenchmarks.org/nrp/"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#60a5fa', textDecoration: 'none', borderBottom: '1px solid transparent', transition: 'border-color 0.2s', fontSize: '1.2rem', fontWeight: '500' }}
          onMouseOver={(e) => e.target.style.borderColor = '#60a5fa'}
          onMouseOut={(e) => e.target.style.borderColor = 'transparent'}
        >
          Fonte: Nurse Rostering Benchmarks
        </a>
        <a
          href="https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#60a5fa', textDecoration: 'none', fontSize: '0.9rem', opacity: 0.8 }}
          onMouseOver={(e) => e.target.style.opacity = '1'}
          onMouseOut={(e) => e.target.style.opacity = '0.8'}
        >
          Clique para ver o Paper
        </a>
      </div>
      <header className="header">
        <h1>
          <Activity size={32} color="#60a5fa" />
          NSP Optimization Dashboard
        </h1>

        <div className="controls">
          <div className="select-wrapper">
            <span>Instance:</span>
            <select
              value={instance}
              onChange={(e) => setInstance(Number(e.target.value))}
              disabled={loading}
            >
              <option value={1}>Instance 1</option>
              <option value={2}>Instance 2</option>
              <option value={3}>Instance 3</option>
              <option value={4}>Instance 4</option>
              <option value={5}>Instance 5</option>
              <option value={6}>Instance 6</option>
              <option value={7}>Instance 7</option>
              <option value={8}>Instance 8</option>
              <option value={9}>Instance 9</option>
              <option value={10}>Instance 10</option>
            </select>
          </div>

          <button onClick={runOptimization} disabled={loading}>
            {loading ? <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></div> : <Play size={18} />}
            {loading ? 'Optimizing...' : 'Run Optimization'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-message">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {loading && !data && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <div className="loading-text">Solving Gurobi Model... This process will not take longer than 120 seconds.</div>
        </div>
      )}

      {data && !loading && (
        <>
          <section className="metrics-grid">
            <div className="card metric-card">
              <span className="metric-label">Total Cost (Objective)</span>
              <span className="metric-value">{Math.round(data.objective).toLocaleString()}</span>
            </div>
            <div className="card metric-card">
              <span className="metric-label">Optimization Status</span>
              <span className="metric-value" style={{ color: data.status === 'OPTIMAL' ? '#22c55e' : '#f59e0b', fontSize: '1.8rem' }}>
                {data.status}
              </span>
            </div>
            {data.status !== 'OPTIMAL' && (
              <div className="card metric-card">
                <span className="metric-label">MIP Gap</span>
                <span className="metric-value" style={{ color: '#f59e0b' }}>
                  {data.gap.toFixed(2)}%
                </span>
              </div>
            )}
            <div className="card metric-card">
              <span className="metric-label">Total Employees</span>
              <span className="metric-value">{data.metadata.employees.length}</span>
            </div>
          </section>

          <section className="card scale-card">
            <h2 className="card-title">
              <Users size={24} />
              Escala de Trabalho (Schedule Matrix)
            </h2>
            <div className="schedule-container">
              <table className="schedule-table">
                <thead>
                  <tr>
                    <th className="employee-name">Funcionario</th>
                    {data.metadata.days.map(d => (
                      <th key={d}>{formatDayLabel(d)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.results.schedule_grid.map(emp => (
                    <tr key={emp.employee}>
                      <td className="employee-name">{emp.employee}</td>
                      {emp.days.map(shiftObj => (
                        <td
                          key={shiftObj.day}
                          className={shiftObj.shift !== 'Folga' ? 'cell-working' : 'cell-off'}
                          title={`Dia ${formatDayLabel(shiftObj.day)}: ${shiftObj.shift}`}
                        >
                          {shiftObj.shift !== 'Folga' ? shiftObj.shift : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card coverage-card">
            <h2 className="card-title">
              <Calendar size={24} />
              Análise por Turnos (Shift Coverage Analysis)
            </h2>
            <div className="charts-grid">
              {data.metadata.shifts.map(shift => {
                const shiftData = data.results.coverage
                  .filter(c => c.shift === shift)
                  .map(d => ({
                    ...d,
                    dayLabel: formatDayLabel(d.day),
                    // Adding delta for easy calculation of color
                    delta: d.actual - d.required
                  }));

                return (
                  <div key={shift} className="chart-wrapper">
                    <h3 className="chart-title">Turno: {shift}</h3>
                    <div style={{ width: '100%', height: 260 }}>
                      <ResponsiveContainer>
                        <BarChart data={shiftData} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                          <XAxis
                            dataKey="dayLabel"
                            tick={{ fill: '#94a3b8', fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                            angle={-45}
                            textAnchor="end"
                          />
                          <YAxis
                            tick={{ fill: '#94a3b8', fontSize: 12 }}
                            axisLine={false}
                            tickLine={false}
                            allowDecimals={false}
                          />
                          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                          <Bar
                            dataKey="actual"
                            name="Qtd Alocada:"
                            radius={[4, 4, 0, 0]}
                            barSize={30}
                          >
                            {shiftData.map((entry, index) => {
                              let fill = '#22c55e'; // Green (Perfect)
                              if (entry.actual < entry.required) fill = '#ef4444'; // Red (Deficit)
                              else if (entry.actual > entry.required) fill = '#3b82f6'; // Blue (Excess)
                              return <Cell key={`cell-${index}`} fill={fill} />;
                            })}
                          </Bar>
                          {/* We use a line to represent the Required amount, simulating plot.py */}
                          <Bar
                            dataKey="required"
                            name="Qtd Recomendada:"
                            fill="transparent"
                            stroke="#ffffff"
                            strokeWidth={2}
                            barSize={30}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default App;
