from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import time
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)

# Configuración de base de datos
DB_PATH = os.getenv('DB_PATH', 'visits.db')

def init_db():
    """Inicializa la base de datos"""
    # Crear directorio si no existe
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar la base de datos al importar el módulo
init_db()

def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/visit', methods=['POST'])
def register_visit():
    """Registra una visita"""
    ip_address = request.remote_addr
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO visits (ip_address) VALUES (?)', (ip_address,))
    conn.commit()
    
    # Obtener total de visitas
    cursor.execute('SELECT COUNT(*) as count FROM visits')
    total = cursor.fetchone()['count']
    conn.close()
    
    return jsonify({
        'message': 'Visit registered',
        'total_visits': total,
        'ip': ip_address
    }), 201

@app.route('/api/visits', methods=['GET'])
def get_visits():
    """Obtiene el total de visitas"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM visits')
    total = cursor.fetchone()['count']
    
    # Últimas 10 visitas
    cursor.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')
    recent = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'total_visits': total,
        'recent_visits': recent
    }), 200

@app.route('/api/stress', methods=['POST'])
def stress_test():
    """
    Endpoint para simular carga de CPU
    Útil para probar el autoscaling
    """
    data = request.get_json() or {}
    duration = min(int(data.get('duration', 5)), 30)  # Máximo 30 segundos
    intensity = min(int(data.get('intensity', 1000000)), 10000000)  # Límite de intensidad
    
    start_time = time.time()
    iterations = 0
    
    # Simular carga de CPU con operaciones hash
    while time.time() - start_time < duration:
        for i in range(intensity):
            hashlib.sha256(str(i).encode()).hexdigest()
        iterations += 1
    
    elapsed = time.time() - start_time
    
    return jsonify({
        'message': 'Stress test completed',
        'duration': elapsed,
        'iterations': iterations,
        'intensity': intensity
    }), 200

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Retorna métricas básicas del servidor"""
    import psutil
    
    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Ruta principal"""
    return jsonify({
        'message': 'Autoscaling Demo API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'register_visit': 'POST /api/visit',
            'get_visits': 'GET /api/visits',
            'stress_test': 'POST /api/stress',
            'metrics': 'GET /api/metrics'
        }
    }), 200

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
