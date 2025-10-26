from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import os
import time
import socket
import hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Inicializar Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

# Detectar si estamos en producción (Azure) o desarrollo (local)
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'
INSTANCE_ID = socket.gethostname()

if IS_PRODUCTION:
    # PostgreSQL en producción
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    def get_db_connection():
        return psycopg2.connect(**DB_CONFIG)
    
    def init_db():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    instance_id VARCHAR(100)
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            print("PostgreSQL database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
else:
    # SQLite en desarrollo
    import sqlite3
    
    DB_PATH = os.getenv('DB_PATH', 'visits.db')
    
    def get_db_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db():
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                instance_id TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("SQLite database initialized successfully")

# Inicializar la base de datos
init_db()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'instance_id': INSTANCE_ID,
            'database': 'connected',
            'db_type': 'mysql' if IS_PRODUCTION else 'sqlite',
            'environment': 'production' if IS_PRODUCTION else 'development'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'instance_id': INSTANCE_ID
        }), 503

@app.route('/api/visit', methods=['POST'])
def register_visit():
    """Registra una visita"""
    try:
        ip_address = request.remote_addr
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_PRODUCTION:
            cursor.execute(
                'INSERT INTO visits (ip_address, instance_id) VALUES (%s, %s)',
                (ip_address, INSTANCE_ID)
            )
            conn.commit()
            cursor.execute('SELECT COUNT(*) as count FROM visits')
            result = cursor.fetchone()
            total = result[0] if result else 0
        else:
            cursor.execute(
                'INSERT INTO visits (ip_address, instance_id) VALUES (?, ?)',
                (ip_address, INSTANCE_ID)
            )
            conn.commit()
            cursor.execute('SELECT COUNT(*) as count FROM visits')
            total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Visit registered',
            'total_visits': total,
            'ip': ip_address,
            'instance_id': INSTANCE_ID
        }), 201
    except Exception as e:
        return jsonify({
            'error': str(e),
            'instance_id': INSTANCE_ID
        }), 500

@app.route('/api/visits', methods=['GET'])
def get_visits():
    """Obtiene el total de visitas"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_PRODUCTION:
            cursor.execute('SELECT COUNT(*) as count FROM visits')
            result = cursor.fetchone()
            total = result[0] if result else 0
            cursor.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')
            columns = [desc[0] for desc in cursor.description]
            recent = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            cursor.execute('SELECT COUNT(*) as count FROM visits')
            total = cursor.fetchone()['count']
            cursor.execute('SELECT * FROM visits ORDER BY timestamp DESC LIMIT 10')
            recent = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_visits': total,
            'recent_visits': recent,
            'instance_id': INSTANCE_ID
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'instance_id': INSTANCE_ID
        }), 500

@app.route('/api/stress', methods=['GET', 'POST'])
def stress_test():
    """
    Endpoint para simular carga intensiva de CPU
    Diseñado para probar autoscaling de VMSS
    """
    if request.method == 'GET':
        duration = int(request.args.get('duration', 60))
        intensity = int(request.args.get('intensity', 5000000))
    else:
        data = request.get_json() or {}
        duration = int(data.get('duration', 60))
        intensity = int(data.get('intensity', 5000000))
    
    # Limitar duración máxima a 120 segundos
    duration = min(duration, 120)
    
    start_time = time.time()
    operations = 0
    
    # Generar carga CPU intensiva con múltiples operaciones
    while time.time() - start_time < duration:
        # Cálculos matemáticos intensivos
        for i in range(intensity):
            # Operaciones hash (muy intensivas en CPU)
            _ = hashlib.sha512(str(i * 12345).encode()).hexdigest()
            # Cálculos matemáticos adicionales
            _ = sum([j**2 for j in range(100)])
            operations += 1
    
    elapsed = time.time() - start_time
    
    return jsonify({
        'status': 'completed',
        'duration_seconds': round(elapsed, 2),
        'operations': operations,
        'instance_id': INSTANCE_ID,
        'timestamp': datetime.now().isoformat()
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
