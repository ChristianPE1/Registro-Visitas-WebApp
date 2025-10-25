#!/usr/bin/env python3
"""
Script de prueba de carga usando Python
Alternativa más portable que Apache Bench
"""

import asyncio
import aiohttp
import time
import sys
from typing import List

async def make_request(session: aiohttp.ClientSession, url: str, method: str = 'POST', json_data: dict = None):
    """Realiza una petición HTTP"""
    try:
        if method == 'POST':
            async with session.post(url, json=json_data) as response:
                return response.status
        else:
            async with session.get(url) as response:
                return response.status
    except Exception as e:
        return f"Error: {e}"

async def load_test(url: str, num_requests: int, concurrent: int, endpoint: str, json_data: dict = None):
    """Ejecuta prueba de carga"""
    full_url = f"{url}{endpoint}"
    
    print(f"🎯 Atacando: {full_url}")
    print(f"📊 Peticiones: {num_requests} | Concurrencia: {concurrent}")
    
    connector = aiohttp.TCPConnector(limit=concurrent)
    timeout = aiohttp.ClientTimeout(total=300)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        start_time = time.time()
        
        tasks = []
        for _ in range(num_requests):
            task = make_request(session, full_url, json_data=json_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        success = sum(1 for r in results if r == 200 or r == 201)
        failed = num_requests - success
        rps = num_requests / elapsed if elapsed > 0 else 0
        
        print(f"✅ Exitosas: {success}")
        print(f"❌ Fallidas: {failed}")
        print(f"⏱️  Tiempo total: {elapsed:.2f}s")
        print(f"📈 Peticiones/segundo: {rps:.2f}")
        print("")

async def main():
    if len(sys.argv) < 2:
        print("Uso: python load-test.py <URL_BASE> [num_requests] [concurrent]")
        print("Ejemplo: python load-test.py http://localhost:5000 1000 50")
        sys.exit(1)
    
    base_url = sys.argv[1]
    num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    concurrent = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    print("🚀 Iniciando pruebas de carga...\n")
    
    # Prueba 1: Endpoint de visitas
    print("=" * 50)
    print("TEST 1: Registro de visitas")
    print("=" * 50)
    await load_test(base_url, num_requests, concurrent, "/api/visit", {})
    
    await asyncio.sleep(2)
    
    # Prueba 2: Endpoint de stress
    print("=" * 50)
    print("TEST 2: Stress test")
    print("=" * 50)
    await load_test(base_url, 50, 10, "/api/stress", {"duration": 10, "intensity": 1000000})
    
    await asyncio.sleep(2)
    
    # Prueba 3: Endpoint de métricas
    print("=" * 50)
    print("TEST 3: Consulta de métricas")
    print("=" * 50)
    await load_test(base_url, num_requests // 2, concurrent, "/api/metrics")
    
    print("\n✅ Todas las pruebas completadas!")

if __name__ == "__main__":
    asyncio.run(main())
