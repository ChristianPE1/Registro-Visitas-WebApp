#!/usr/bin/env python3
"""
Script ULTRA AGRESIVO - Usa múltiples procesos para saturar completamente el CPU.
Este script ejecuta múltiples instancias del script asyncio en paralelo.
"""
import multiprocessing as mp
import asyncio
import aiohttp
import time
import sys
import random

LB_IP = sys.argv[1] if len(sys.argv) > 1 else None
if not LB_IP:
    print("Error: Proporciona la IP del Load Balancer")
    print("Uso: python3 ultra-load.py <IP>")
    sys.exit(1)

BASE_URL = f"http://{LB_IP}"
WORKERS = 4  # Número de procesos paralelos
CONCURRENT_PER_WORKER = 100  # Peticiones concurrentes por worker
DURATION_SECONDS = 300  # 5 minutos de carga continua

# Stats globales por worker
worker_stats = []

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
                    return True, method
            else:
                async with session.post(
                    f"{BASE_URL}/api/visit",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    await response.read()
                    return True, method
        except:
            return False, method

async def worker_load(worker_id, duration):
    """Worker que genera carga continua"""
    print(f"[Worker {worker_id}] Iniciando...")
    
    stats = {'success': 0, 'failed': 0, 'get': 0, 'post': 0}
    start_time = time.time()
    
    semaphore = asyncio.Semaphore(CONCURRENT_PER_WORKER)
    connector = aiohttp.TCPConnector(limit=CONCURRENT_PER_WORKER * 2)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        while time.time() - start_time < duration:
            # Crear lote de peticiones
            tasks = []
            for _ in range(CONCURRENT_PER_WORKER):
                method = 'GET' if random.random() < 0.3 else 'POST'
                task = make_request(session, semaphore, method)
                tasks.append(task)
            
            # Ejecutar lote
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Contar resultados
            for result in results:
                if isinstance(result, tuple):
                    success, method = result
                    if success:
                        stats['success'] += 1
                        if method == 'GET':
                            stats['get'] += 1
                        else:
                            stats['post'] += 1
                    else:
                        stats['failed'] += 1
    
    elapsed = time.time() - start_time
    rps = (stats['success'] + stats['failed']) / elapsed
    
    print(f"[Worker {worker_id}] Completado: {stats['success']:,} exitosas, "
          f"{stats['failed']:,} fallidas | {rps:.1f} req/s")
    
    return stats

def run_worker(worker_id, duration, return_dict):
    """Función para ejecutar en proceso separado"""
    stats = asyncio.run(worker_load(worker_id, duration))
    return_dict[worker_id] = stats

def main():
    print("\n" + "="*80)
    print(f"CARGA ULTRA AGRESIVA")
    print("="*80)
    print(f"Target: {BASE_URL}")
    print(f"Workers: {WORKERS} procesos paralelos")
    print(f"Concurrencia por worker: {CONCURRENT_PER_WORKER}")
    print(f"Duración: {DURATION_SECONDS}s")
    print(f"Carga total simultánea: {WORKERS * CONCURRENT_PER_WORKER} peticiones")
    print("="*80)
    
    # Verificar conectividad
    print("\nVerificando servidor...")
    import requests
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("✓ Servidor OK\n")
    except:
        print("⚠ No se pudo verificar, continuando de todas formas...\n")
    
    print(f"Iniciando {WORKERS} workers en 3 segundos...\n")
    time.sleep(3)
    
    # Crear manager para compartir datos entre procesos
    manager = mp.Manager()
    return_dict = manager.dict()
    
    # Iniciar workers
    start_time = time.time()
    processes = []
    
    for i in range(WORKERS):
        p = mp.Process(target=run_worker, args=(i, DURATION_SECONDS, return_dict))
        p.start()
        processes.append(p)
    
    # Esperar a que terminen
    for p in processes:
        p.join()
    
    # Calcular totales
    elapsed = time.time() - start_time
    total_success = sum(s['success'] for s in return_dict.values())
    total_failed = sum(s['failed'] for s in return_dict.values())
    total_get = sum(s['get'] for s in return_dict.values())
    total_post = sum(s['post'] for s in return_dict.values())
    total = total_success + total_failed
    
    print("\n" + "="*80)
    print("RESULTADOS FINALES")
    print("="*80)
    print(f"Total peticiones: {total:,}")
    print(f"Exitosas: {total_success:,} ({total_success/total*100:.1f}%)")
    print(f"Fallidas: {total_failed:,}")
    print(f"GET: {total_get:,} | POST: {total_post:,}")
    print(f"Tiempo: {elapsed:.1f}s")
    print(f"Velocidad promedio: {total/elapsed:.1f} req/s")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrumpido por el usuario\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
