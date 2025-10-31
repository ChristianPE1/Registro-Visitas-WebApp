#!/usr/bin/env python3
"""
Script de carga EXTREMA para saturar CPU y forzar autoscaling.
Mantiene carga constante con miles de peticiones concurrentes.
"""
import asyncio
import aiohttp
import time
import sys
from datetime import datetime
import random
import string

# Configuración AGRESIVA
LB_IP = sys.argv[1] if len(sys.argv) > 1 else None
if not LB_IP:
    print("Error: Debes proporcionar la IP del Load Balancer")
    sys.exit(1)

BASE_URL = f"http://{LB_IP}"
CONCURRENT_REQUESTS = 200  
REQUESTS_PER_BATCH = 5000  # 5k peticiones por lote
CONTINUOUS = True 

# Estadísticas globales
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'get': 0,
    'post': 0,
    'start_time': None,
    'batch': 0,
}

def generate_random_visitor():
    """Genera datos aleatorios para un visitante"""
    names = ['Juan', 'María', 'Pedro', 'Ana', 'Luis', 'Carmen', 'José', 'Laura', 'Carlos', 'Sofia']
    companies = ['TechCorp', 'DataSys', 'CloudInc', 'DevHub', 'CodeLab', 'SoftWorks']
    
    return {
        'name': random.choice(names) + str(random.randint(100, 999)),
        'email': f"user{random.randint(10000, 99999)}@test.com",
        'company': random.choice(companies),
        'purpose': f"Test {random.randint(1, 9999)}"
    }

async def make_request(session, semaphore, method='GET'):
    """Hace una petición GET o POST"""
    async with semaphore:
        try:
            if method == 'GET':
                async with session.get(
                    f"{BASE_URL}/api/visits",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    await response.read()
                    stats['get'] += 1
            else:  # POST
                # POST a /api/visit (singular) - registra visita
                async with session.post(
                    f"{BASE_URL}/api/visit",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    await response.read()
                    stats['post'] += 1
            
            stats['success'] += 1
        except:
            stats['failed'] += 1
        finally:
            stats['total'] += 1

async def print_stats():
    """Imprime estadísticas en tiempo real"""
    while True:
        if stats['start_time']:
            elapsed = time.time() - stats['start_time']
            rps = stats['total'] / elapsed if elapsed > 0 else 0
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            print(f"\rLote #{stats['batch']} | "
                  f"Total: {stats['total']:,} | "
                  f"✓ {stats['success']:,} ({success_rate:.1f}%) | "
                  f"✗ {stats['failed']:,} | "
                  f"GET: {stats['get']:,} | POST: {stats['post']:,} | "
                  f"{rps:.1f} req/s", end='', flush=True)
        
        await asyncio.sleep(1)

async def run_batch(session, semaphore, batch_size):
    """Ejecuta un lote de peticiones"""
    tasks = []
    for _ in range(batch_size):
        # 30% GET, 70% POST (POST es más pesado y genera más CPU)
        method = 'GET' if random.random() < 0.3 else 'POST'
        task = make_request(session, semaphore, method)
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)

async def run_continuous_load():
    """Ejecuta carga continua"""
    print(f"\n{'='*80}")
    print(f"CARGA EXTREMA - Target: {BASE_URL}")
    print(f"Concurrencia: {CONCURRENT_REQUESTS} | Lote: {REQUESTS_PER_BATCH:,} peticiones")
    print(f"{'='*80}\n")
    
    # Verificar conectividad
    print("Verificando conectividad...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print(f"✓ Servidor OK\n")
    except Exception as e:
        print(f"⚠ Advertencia: {e}\n")
    
    stats['start_time'] = time.time()
    
    # Crear semáforo y sesión
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    connector = aiohttp.TCPConnector(
        limit=CONCURRENT_REQUESTS * 2,
        limit_per_host=CONCURRENT_REQUESTS * 2,
        ttl_dns_cache=300
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Iniciar tarea de estadísticas
        stats_task = asyncio.create_task(print_stats())
        
        try:
            while CONTINUOUS:
                stats['batch'] += 1
                await run_batch(session, semaphore, REQUESTS_PER_BATCH)
                
        except KeyboardInterrupt:
            pass
        finally:
            stats_task.cancel()
            try:
                await stats_task
            except asyncio.CancelledError:
                pass
    
    # Resultados finales
    elapsed = time.time() - stats['start_time']
    rps = stats['total'] / elapsed if elapsed > 0 else 0
    
    print(f"\n\n{'='*80}")
    print(f"RESULTADOS FINALES")
    print(f"{'='*80}")
    print(f"Total: {stats['total']:,} | Exitosas: {stats['success']:,} ({stats['success']/stats['total']*100:.1f}%) | Fallidas: {stats['failed']:,}")
    print(f"GET: {stats['get']:,} | POST: {stats['post']:,}")
    print(f"Tiempo: {elapsed:.1f}s | Velocidad: {rps:.1f} req/s | Lotes: {stats['batch']}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        print("\nIniciando en 3 segundos...\n")
        time.sleep(3)
        asyncio.run(run_continuous_load())
    except KeyboardInterrupt:
        print(f"\n\n⚠ Detenido por el usuario\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
