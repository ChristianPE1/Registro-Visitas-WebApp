# Sistema de Autoscaling en Azure

Solución full stack que demuestra autoscaling horizontal sobre infraestructura de Microsoft Azure declarada con Pulumi (IaC open source). El backend está construido con Flask, la base de datos es PostgreSQL Flexible Server y la capa de cómputo usa Virtual Machine Scale Sets (VMSS) detrás de un Load Balancer estándar.

## Arquitectura general

1. **Usuarios** → realizan solicitudes HTTP.
2. **Azure Load Balancer** distribuye el tráfico a las instancias activas del VMSS.
3. **VM Scale Set (1-5 instancias Ubuntu 22.04)** ejecuta el backend Flask y reporta métricas.
4. **PostgreSQL Flexible Server** centraliza los datos compartidos por todas las instancias.
5. **Azure Monitor** analiza la métrica *Percentage CPU* y ajusta la capacidad del VMSS según las reglas configuradas.

> 📄 La arquitectura Azure con todos los recursos, diagramas lógicos, comandos operativos y costos estimados está descrita en detalle en `infrastructure-azure/README.md`.

## Requisitos

### Desarrollo local
- Docker y Docker Compose
- Python 3.11+

### Despliegue en Azure
- Azure CLI configurado (`az login`)
- Pulumi CLI instalado
- Suscripción de Azure activa con permisos para crear recursos

## Uso rápido

```bash
# Clonar repositorio
git clone https://github.com/ChristianPE1/Registro-Visitas-WebApp.git
cd Registro-Visitas-WebApp

# Inicializar Pulumi
cd infrastructure-azure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Desplegar infraestructura
pulumi up --yes

# Obtener IP pública del Load Balancer
echo "LB_IP=$(pulumi stack output load_balancer_ip)"
```

## Pruebas de autoscaling

En `infrastructure-azure/` encontrarás diferentes opciones:

```bash
# Generar carga con wrk (5 minutos, 8 hilos, 150 conexiones)
python3 extreme-load.py $LB_IP$

# Monitorear instancias del VMSS
watch -n 30 './monitor_clean.sh'
```

## Documentación complementaria

- `infrastructure-azure/README.md`: guía completa de infraestructura, autoscaling y comandos operativos.
- `backend/app.py`: aplicación Flask con instrumentación Prometheus.
- `infrastructure-azure/test_autoscaling.py`: script Python para pruebas programáticas.

## Licencia

MIT License

## Autor

Christian Pardavé Espinoza  
GitHub: [@ChristianPE1](https://github.com/ChristianPE1)