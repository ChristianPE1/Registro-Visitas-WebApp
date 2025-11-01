import { useState, useEffect } from 'react'
import axios from 'axios'

// Usar ruta relativa para que funcione con el proxy de nginx
const API_URL = ''

function App() {
  const [visits, setVisits] = useState({ total_visits: 0, recent_visits: [] })
  const [metrics, setMetrics] = useState({ cpu_percent: 0, memory_percent: 0 })
  const [loading, setLoading] = useState(false)
  const [stressConfig, setStressConfig] = useState({ duration: 10, intensity: 1000000 })
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchVisits()
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000) // Actualizar métricas cada 5 segundos
    return () => clearInterval(interval)
  }, [])

  const fetchVisits = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/visits`)
      setVisits(response.data)
    } catch (error) {
      console.error('Error fetching visits:', error)
    }
  }

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/metrics`)
      setMetrics(response.data)
    } catch (error) {
      console.error('Error fetching metrics:', error)
    }
  }

  const registerVisit = async () => {
    try {
      await axios.post(`${API_URL}/api/visit`)
      fetchVisits()
      setMessage('Visita registrada correctamente')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Error al registrar visita')
      console.error('Error registering visit:', error)
    }
  }

  const runStressTest = async () => {
    setLoading(true)
    setMessage('Ejecutando prueba de carga...')
    try {
      const response = await axios.post(`${API_URL}/api/stress`, stressConfig)
      setMessage(`Prueba completada en ${response.data.duration.toFixed(2)}s`)
      fetchMetrics()
    } catch (error) {
      setMessage('Error en prueba de carga')
      console.error('Error running stress test:', error)
    } finally {
      setLoading(false)
      setTimeout(() => setMessage(''), 5000)
    }
  }

  const runMultipleRequests = async () => {
    setLoading(true)
    setMessage('Ejecutando múltiples peticiones...')
    try {
      const requests = Array(50).fill().map(() => 
        axios.post(`${API_URL}/api/visit`)
      )
      await Promise.all(requests)
      fetchVisits()
      setMessage('50 peticiones completadas correctamente')
    } catch (error) {
      setMessage('Error en peticiones múltiples')
      console.error('Error running multiple requests:', error)
    } finally {
      setLoading(false)
      setTimeout(() => setMessage(''), 5000)
    }
  }

  return (
    <div className="App">
      <header className="header">
        <h1>Sistema de Autoscaling</h1>
        <p>Demostración de autoscaling en Kubernetes</p>
      </header>

      <div className="container">
        {/* Métricas del sistema */}
        <div className="card">
          <h2>Métricas en Tiempo Real</h2>
          <div className="metrics">
            <div className="metric">
              <span className="metric-label">CPU:</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${metrics.cpu_percent}%`, backgroundColor: metrics.cpu_percent > 70 ? '#f44336' : '#4caf50' }}
                ></div>
              </div>
              <span className="metric-value">{metrics.cpu_percent}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Memoria:</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${metrics.memory_percent}%`, backgroundColor: metrics.memory_percent > 70 ? '#f44336' : '#2196f3' }}
                ></div>
              </div>
              <span className="metric-value">{metrics.memory_percent}%</span>
            </div>
          </div>
        </div>

        {/* Contador de visitas */}
        <div className="card">
          <h2>Contador de Visitas</h2>
          <div className="visit-counter">
            <h3>{visits.total_visits}</h3>
            <p>Visitas totales</p>
          </div>
          <button onClick={registerVisit} className="btn btn-primary">
            Registrar Visita
          </button>
        </div>

        {/* Pruebas de carga */}
        <div className="card">
          <h2>Pruebas de Carga</h2>
          <div className="stress-config">
            <div className="input-group">
              <label>Duración (segundos):</label>
              <input 
                type="number" 
                min="1" 
                max="30" 
                value={stressConfig.duration}
                onChange={(e) => setStressConfig({...stressConfig, duration: parseInt(e.target.value)})}
              />
            </div>
            <div className="input-group">
              <label>Intensidad:</label>
              <input 
                type="number" 
                min="100000" 
                max="10000000" 
                step="100000"
                value={stressConfig.intensity}
                onChange={(e) => setStressConfig({...stressConfig, intensity: parseInt(e.target.value)})}
              />
            </div>
          </div>
          <div className="button-group">
            <button 
              onClick={runStressTest} 
              disabled={loading}
              className="btn btn-warning"
            >
              {loading ? 'Ejecutando...' : 'Prueba de CPU'}
            </button>
            <button 
              onClick={runMultipleRequests} 
              disabled={loading}
              className="btn btn-info"
            >
              {loading ? 'Ejecutando...' : '50 Peticiones Simultáneas'}
            </button>
          </div>
        </div>

        {/* Mensajes */}
        {message && (
          <div className="message">
            {message}
          </div>
        )}

        {/* Visitas recientes */}
        {visits.recent_visits.length > 0 && (
          <div className="card">
            <h2>Últimas Visitas</h2>
            <div className="recent-visits">
              {visits.recent_visits.map((visit) => (
                <div key={visit.id} className="visit-item">
                  <span>{new Date(visit.timestamp).toLocaleString()}</span>
                  <span className="visit-ip">{visit.ip_address}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
