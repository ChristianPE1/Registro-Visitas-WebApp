#!/usr/bin/env python3
"""
Script de prueba de carga para autoscaling
Genera carga CPU intensiva sostenida para forzar el escalado del VMSS
"""

import requests
import time
import sys
import threading
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def stress_worker(base_url, duration, intensity, thread_id):
    """Worker que hace peticiones continuas al endpoint de estrés"""
    try:
        url = f"{base_url}/api/stress?duration={duration}&intensity={intensity}"
        log(f"Thread-{thread_id}: Iniciando petición de estrés ({duration}s)")
        response = requests.get(url, timeout=duration+30)
        if response.status_code == 200:
            data = response.json()
            log(f"Thread-{thread_id}: Completado - {data.get('operations', 0)} operaciones")
            return True
        else:
            log(f"Thread-{thread_id}: HTTP {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        log(f"Thread-{thread_id}: Timeout (esperado en cargas largas)")
        return True
    except Exception as e:
        log(f"Thread-{thread_id}: Error - {str(e)}")
        return False

def continuous_stress(base_url, total_duration, thread_id):
    """Genera peticiones continuas durante un periodo prolongado"""
    start = time.time()
    iteration = 0
    
    while time.time() - start < total_duration:
        iteration += 1
        log(f"Thread-{thread_id}: Iteración {iteration}")
        
        try:
            # Hacer petición corta pero intensa
            url = f"{base_url}/api/stress?duration=15&intensity=8000000"
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200:
                log(f"Thread-{thread_id}: Iteración {iteration} completada")
            else:
                log(f"Thread-{thread_id}: HTTP {response.status_code}")
        except Exception as e:
            log(f"Thread-{thread_id}: Error en iteración {iteration} - {str(e)}")
        
        # Pequeña pausa entre iteraciones
        time.sleep(2)
    
    log(f"Thread-{thread_id}: Finalizado después de {iteration} iteraciones")

def check_health(base_url):
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 test_autoscaling.py <IP_LOAD_BALANCER>")
        print("Ejemplo: python3 test_autoscaling.py 20.184.147.57")
        sys.exit(1)
    
    lb_ip = sys.argv[1]
    base_url = f"http://{lb_ip}"
    
    print("\n" + "="*60)
    print("PRUEBA DE AUTOSCALING - CARGA INTENSIVA SOSTENIDA")
    print("="*60)
    log(f"Target: {base_url}")
    
    # Health check
    log("Verificando disponibilidad del endpoint...")
    if not check_health(base_url):
        log("ERROR: Health check falló. ¿Está la aplicación corriendo?")
        sys.exit(1)
    log("Health check OK")
    
    # Configuración agresiva
    num_threads = 12
    total_duration = 360  # 6 minutos de carga sostenida
    
    print("\nConfiguración:")
    print(f"  Threads concurrentes: {num_threads}")
    print(f"  Duración total: {total_duration}s ({total_duration//60} minutos)")
    print(f"  Estrategia: Peticiones continuas de 15s con intensidad alta")
    print(f"  Objetivo: CPU >70% sostenida por 5+ minutos")
    print(f"  Comportamiento esperado: VMSS debe escalar de 1 a 2-3 instancias")
    print("\n" + "="*60)
    
    log(f"Iniciando generación de carga con {num_threads} threads...")
    log("IMPORTANTE: Este test durará 6 minutos. Monitorea en otra terminal:")
    log("  watch -n 10 'az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table'")
    print()
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=continuous_stress,
            args=(base_url, total_duration, i+1)
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Pequeño delay entre threads
    
    # Esperar a que todos terminen
    for thread in threads:
        thread.join()
    
    print("\n" + "="*60)
    log("Test de carga completado")
    print("="*60)
    print("\nComandos de verificación:")
    print("1. Ver instancias del VMSS:")
    print("   az vmss list-instances -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss -o table")
    print("\n2. Ver historial de autoscaling:")
    print("   az monitor autoscale-settings show -g cpe-autoscaling-demo-rg -n cpe-autoscaling-demo-vmss-autoscale")
    print("\n3. Ver métricas en Azure Portal:")
    print("   Portal > Virtual Machine Scale Sets > cpe-autoscaling-demo-vmss > Metrics")

if __name__ == "__main__":
    main()
