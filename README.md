# Cloud Autoscaling Demonstration System# Sistema de Registro de Visitas con Autoscaling# 🚀 Sistema de Autoscaling Demo



## Project Overview



This project demonstrates horizontal autoscaling implementation on Azure cloud infrastructure using Infrastructure as Code (IaC) principles. The system automatically scales compute resources based on CPU utilization metrics, providing a practical example of cloud elasticity and resource optimization.Sistema web full-stack que demuestra autoscaling horizontal mediante el registro de visitas web. Implementado con Flask (backend), React (frontend), PostgreSQL (base de datos compartida) y despliegue en Azure usando Infraestructura como Código (Pulumi).Aplicación full stack ligera diseñada para demostrar autoscaling en proveedores cloud usando herramientas IaC open source.



## Technology Stack



### Infrastructure## Arquitectura## 📋 Stack Tecnológico

- **IaC Tool**: Pulumi (Open Source, Python SDK)

- **Cloud Provider**: Microsoft Azure

- **Compute**: Virtual Machine Scale Sets (VMSS)

- **Database**: PostgreSQL Flexible Server```- **Backend**: Flask (Python) - API REST ligera

- **Load Balancing**: Azure Load Balancer (Standard SKU)

- **Networking**: Virtual Network with NAT GatewayInternet → Azure Load Balancer (puerto 80 → 5000)- **Frontend**: React + Vite - Interfaz moderna y rápida



### Application                    ↓- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)

- **Backend**: Flask (Python 3.11)

- **Database Driver**: psycopg2        VM Scale Set (1-3 instancias Ubuntu)- **Containerización**: Docker & Docker Compose

- **Monitoring**: Prometheus + Grafana + Node Exporter

        - Flask API en puerto 5000

### Development

- **Containerization**: Docker + Docker Compose        - Autoscaling basado en CPU## 🎯 Características

- **Version Control**: Git

- **CI/CD**: GitHub        - Standard_B1s (1 vCPU, 1 GB RAM)



## Architecture                    ↓- ✅ Contador de visitas en tiempo real



```        Azure PostgreSQL Flexible Server- ✅ Métricas de CPU y memoria

Internet

    |        - Base de datos compartida entre instancias- ✅ Endpoint de stress test para simular carga

    v

[Load Balancer]        - Standard_B1ms (Burstable tier)- ✅ Interfaz web para monitoreo

    |

    +---> [VMSS Instance 1] ---+        - 32 GB storage- ✅ Scripts de prueba de carga externos

    |                          |

    +---> [VMSS Instance 2] ---+---> [PostgreSQL Server]```- ✅ Completamente containerizado

    |                          |

    +---> [VMSS Instance 3] ---+

```

### Flujo de Autoscaling## 🚀 Inicio Rápido

### Key Components



1. **Load Balancer**: Distributes incoming traffic across VMSS instances

2. **VMSS**: Automatically scales between 1-3 instances based on CPU metrics- **Scale UP**: Cuando CPU > 70% por 5 minutos → +1 instancia### ✅ Estado: FUNCIONANDO PERFECTAMENTE

3. **PostgreSQL**: Centralized database shared across all instances

4. **Monitoring**: Real-time metrics via Prometheus and Grafana dashboards- **Scale DOWN**: Cuando CPU < 30% por 5 minutos → -1 instanciaÚltima verificación: 23 octubre 2025 ✓  



## Features- **Rango**: Mínimo 1 instancia, Máximo 3 instanciasTodos los endpoints probados y operativos ✓  



- Automatic horizontal scaling based on CPU utilizationError 500 resuelto ✓

- Load balancing across multiple instances

- Health monitoring and auto-recovery## Características

- Real-time metrics and visualization

- Infrastructure versioning and reproducibility### Prerrequisitos



## Project Structure- **Backend Flask**: API REST con 6 endpoints para gestión de visitas y métricas



```- **Frontend React**: Interfaz de usuario con Tailwind CSS- Docker & Docker Compose instalados

sistema-autoscaling/

├── backend/                  # Flask application- **Base de Datos Compartida**: PostgreSQL accesible desde todas las instancias- Python 3.11+ (para scripts de prueba)

│   ├── app.py               # Main application

│   ├── requirements.txt     # Python dependencies- **Infraestructura como Código**: Pulumi con Python para Azure- AWS CLI configurado (para despliegue)

│   └── Dockerfile           # Container definition

├── infrastructure-azure/     # IaC implementation- **Containerización**: Docker y Docker Compose para desarrollo local- Pulumi CLI (para IaC)

│   ├── __main__.py          # Pulumi infrastructure code

│   ├── Pulumi.yaml          # Project configuration- **Monitoreo**: Métricas de CPU y memoria en tiempo real

│   ├── test_autoscaling.py  # Load testing script

│   ├── check_deployment.sh  # Deployment verification- **Load Testing**: Endpoint de stress test para simular carga### Probar localmente

│   └── README.md            # Infrastructure documentation

└── docker-compose.yml        # Local development environment

```

## Estructura del Proyecto```bash

## Quick Start

# Ir al directorio del proyecto

### Local Development

```cd sistema-autoscaling

```bash

# Start all services.

docker-compose up -d

├── backend/                    # API Flask# Levantar todos los servicios

# Access application

# Frontend: http://localhost:3000│   ├── app.py                 # Aplicación principaldocker-compose up -d --build

# Backend API: http://localhost:5000

# PostgreSQL: localhost:5433│   ├── requirements.txt       # Dependencias Python

```

│   └── Dockerfile            # Imagen Docker# Ver logs

### Cloud Deployment

├── frontend/                  # Aplicación Reactdocker-compose logs -f

Refer to `infrastructure-azure/README.md` for detailed deployment instructions.

│   ├── src/                  # Código fuente

```bash

cd infrastructure-azure│   ├── package.json          # Dependencias Node.js# Abrir en navegador

pulumi up

```│   └── Dockerfile           # Imagen Dockerfirefox http://localhost



## Autoscaling Configuration├── infrastructure-azure/      # IaC con Pulumi```



### Scale-Out Policy│   ├── __main__.py           # Definición de infraestructura

- **Trigger**: CPU > 70% (average)

- **Duration**: 5 minutes sustained│   ├── Pulumi.yaml           # Configuración del proyectoLa aplicación estará disponible en:

- **Action**: Add 1 instance

- **Cooldown**: 5 minutes│   └── requirements.txt      # Dependencias Pulumi- **Frontend**: http://localhost



### Scale-In Policy├── docker-compose.yml        # Orquestación local- **Backend API**: http://localhost:5000

- **Trigger**: CPU < 30% (average)

- **Duration**: 5 minutes sustained└── scripts/                  # Scripts de utilidad- **PostgreSQL**: localhost:5433 (puerto 5433 para evitar conflictos)

- **Action**: Remove 1 instance

- **Cooldown**: 5 minutes    ├── deploy.sh            # Script de despliegue



### Capacity Limits    └── test-load.sh         # Script de pruebas de carga### Pruebas rápidas

- **Minimum**: 1 instance

- **Maximum**: 3 instances```

- **Default**: 1 instance

```bash

## Testing

## Tecnologías Utilizadas# Health check

### Load Test

```bashcurl http://localhost:5000/health

cd infrastructure-azure

LB_IP=$(pulumi stack output load_balancer_ip)### Backend

python3 test_autoscaling.py $LB_IP

```- Python 3.11# Registrar visita



### Monitor Scaling- Flask 3.0.0curl -X POST http://localhost:5000/api/visit

```bash

watch -n 10 'az vmss list-instances \- Flask-CORS

  -g cpe-autoscaling-demo-rg \

  -n cpe-autoscaling-demo-vmss \- psycopg2-binary (PostgreSQL driver)# Ver métricas

  -o table'

```- psutil (métricas del sistema)curl http://localhost:5000/api/metrics



## Monitoring



Access monitoring dashboards:### Frontend# Prueba de carga local

- **Grafana**: http://LOAD_BALANCER_IP:3000 (admin/admin)

- **Prometheus**: http://LOAD_BALANCER_IP:9090- React 18python scripts/load-test.py http://localhost:5000 500 50



## Documentation- Vite```



- `/infrastructure-azure/README.md` - Complete infrastructure documentation- Tailwind CSS 3.4

- `/backend/` - Application source code

- `/docs/` - Additional technical documentation- Axios### Detener los servicios



## Prerequisites



### Local Development### Infraestructura```bash

- Docker 20.10+

- Docker Compose 2.0+- Azure Virtual Networkdocker-compose down



### Cloud Deployment- Azure Load Balancer

- Azure CLI

- Pulumi CLI- Azure VM Scale Set# Incluir volúmenes (borrar datos)

- Python 3.8+

- Active Azure subscription- Azure Database for PostgreSQL Flexible Serverdocker-compose down -v



## Cost Estimation- Azure Monitor (autoscaling)```



Estimated monthly cost (West US):- Pulumi (IaC)

- VMSS (1-3 instances): $9-27/month

- PostgreSQL Server: $12/month## 🧪 Pruebas de Carga

- Load Balancer: $18/month

- NAT Gateway: $32/month### DevOps

- **Total**: ~$75-95/month

- Docker### Opción 1: Desde la Interfaz Web

## License

- Docker Compose

MIT License

- GitHub1. Abre http://localhost en tu navegador

## Author

- Azure CLI2. Usa los botones de "Prueba de CPU" y "50 Peticiones Simultáneas"

Cloud Infrastructure and Autoscaling Demonstration Project

3. Observa las métricas en tiempo real

## Requisitos Previos

### Opción 2: Script Python (Recomendado para autoscaling)

### Desarrollo Local

- Docker y Docker Compose```bash

- Node.js 18+ (opcional, para desarrollo frontend)# Instalar dependencias

- Python 3.11+ (opcional, para desarrollo backend)pip install -r scripts/requirements.txt



### Despliegue en Azure# Ejecutar prueba

- Cuenta de Azure (con créditos disponibles)python scripts/load-test.py http://localhost:5000 1000 50

- Azure CLI instalado y configurado```

- Pulumi CLI instalado

- Python 3.11+### Opción 3: Apache Bench (bash)



## Instalación y Uso```bash

chmod +x scripts/load-test.sh

### Desarrollo Local con Docker./scripts/load-test.sh http://localhost:5000 1000 50

```

```bash

# Clonar el repositorio## 📊 API Endpoints

git clone https://github.com/ChristianPE1/Registro-Visitas-WebApp.git

cd Registro-Visitas-WebApp| Endpoint | Método | Descripción |

|----------|---------|-------------|

# Iniciar todos los servicios| `/health` | GET | Health check |

docker-compose up -d| `/api/visit` | POST | Registrar visita |

| `/api/visits` | GET | Obtener contador de visitas |

# Acceder a la aplicación| `/api/stress` | POST | Simular carga de CPU |

# Frontend: http://localhost:3000| `/api/metrics` | GET | Métricas del servidor |

# Backend: http://localhost:5000

```## 🏗️ Arquitectura



### Desarrollo Local sin Docker```

sistema-autoscaling/

#### Backend├── backend/              # API Flask

```bash│   ├── app.py           # Aplicación principal

cd backend│   ├── requirements.txt

pip install -r requirements.txt│   └── Dockerfile

python app.py├── frontend/            # React App

```│   ├── src/

│   ├── package.json

#### Frontend│   ├── nginx.conf

```bash│   └── Dockerfile

cd frontend├── scripts/             # Scripts de prueba de carga

npm install│   ├── load-test.py     # Script Python

npm run dev│   └── load-test.sh     # Script Bash

```└── docker-compose.yml   # Orquestación

```

## API Endpoints

---

### Health Check

```bash## 📖 Documentación Completa

GET /health

```### 📚 Guías Disponibles

Verifica el estado del servidor y la conexión a la base de datos.

1. **[GUIA_COMPLETA.md](./GUIA_COMPLETA.md)** - Todo lo que necesitas saber:

### Registrar Visita   - ¿Qué hace la aplicación?

```bash   - ¿Qué se guarda en la base de datos?

POST /api/visit   - ¿Cómo funciona el autoscaling?

```   - Análisis de opciones de BD (PostgreSQL vs DynamoDB vs Aurora)

Registra una nueva visita en la base de datos.   - Timeline de pruebas esperado

   - Troubleshooting

### Obtener Visitas

```bash2. **[COMANDOS_RAPIDOS.md](./COMANDOS_RAPIDOS.md)** - Comandos para copiar-pegar:

GET /api/visits   - Setup local (hoy)

```   - Despliegue en AWS (mañana)

Retorna el total de visitas y las 10 más recientes.   - Monitoreo y troubleshooting

   - Atajos útiles

### Test de Estrés

```bash3. **[infrastructure/README.md](./infrastructure/README.md)** - Infraestructura Pulumi:

POST /api/stress   - Recursos creados en AWS

Content-Type: application/json   - Costos estimados

   - Guía de despliegue paso a paso

{   - Configuración de autoscaling

  "duration": 10,

  "intensity": 5000000---

}

```## 🌩️ DECISIONES FINALES PARA AWS + PULUMI

Genera carga de CPU durante el tiempo especificado para probar autoscaling.

### ✅ Stack Elegido

### Métricas del Sistema

```bash```

GET /api/metricsPulumi (Python) + AWS + GitHub Actions

``````

Retorna métricas de CPU y memoria de la instancia actual.

**Por qué:**

### Home- ✅ Pulumi es open source (requisito cumplido)

```bash- ✅ Python (lenguaje que conoces)

GET /- ✅ AWS Free Tier generoso ($100 créditos + 12 meses gratis)

```- ✅ GitHub Actions gratis para pruebas automatizadas

Información general de la API y endpoints disponibles.- ✅ Todo documentado y listo para usar



## Despliegue en Azure### ✅ Base de Datos: RDS PostgreSQL



### 1. Configurar Azure CLI**Decisión final: Mantener PostgreSQL (NO cambiar a DynamoDB)**



```bash**Razones:**

# Instalar Azure CLI1. ✅ Free tier: 750 horas/mes de db.t3.micro (suficiente)

curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash2. ✅ 20 GB gratis (más que suficiente)

3. ✅ Tu código ya funciona con SQL

# Login4. ✅ No requiere reescribir lógica

az login5. ✅ Backups automáticos incluidos



# Verificar suscripción**Comparación rápida:**

az account show| | RDS PostgreSQL | DynamoDB | Aurora DSQL |

```|---|---|---|---|

| **Storage gratis** | 20 GB (12 meses) | 25 GB (forever) | 1 GB |

### 2. Configurar Pulumi| **Costo después** | ~$12-15/mes | Gratis hasta 25GB | Caro |

| **Código actual** | ✅ Funciona | ❌ Reescribir | ❌ Reescribir |

```bash| **SQL estándar** | ✅ Sí | ❌ No | ⚠️ Limitado |

cd infrastructure-azure| **Recomendado** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |



# Crear entorno virtual### ✅ Configuración AWS Free Tier

python3 -m venv venv

source venv/bin/activate**Infraestructura desplegada:**

- **EC2**: 1-3 instancias t2.micro (750 hrs/mes gratis)

# Instalar dependencias- **RDS**: 1 instancia db.t3.micro PostgreSQL (750 hrs/mes gratis)

pip install -r requirements.txt- **ALB**: Application Load Balancer (750 hrs/mes gratis)

- **CloudWatch**: Monitoreo y alarmas (métricas básicas gratis)

# Configurar contraseñas (deben cumplir requisitos de Azure)- **Auto Scaling**: Gratis (solo pagas por las instancias)

pulumi config set --secret admin_password "TuPasswordSegura123!"

pulumi config set --secret db_password "TuPasswordDB123!"**Límites respetados:**

- ✅ Máximo 3 instancias EC2 (no excede 750 hrs mensuales)

# Opcional: cambiar región (por defecto: eastus)- ✅ 1 RDS instance (no excede 750 hrs)

pulumi config set location "eastus"- ✅ 1 Load Balancer (no excede 750 hrs)

```- ✅ Storage total: ~30 GB (dentro del límite de 30 GB)



### 3. Desplegar Infraestructura**Costo estimado con tus $100 de créditos:**

- Primeros 12 meses: **$0/mes** (todo en free tier)

```bash- Después del free tier: **~$25-40/mes**

# Vista previa de cambios- Con tus $100 créditos: **~2.5 meses adicionales gratis**

pulumi preview

---

# Desplegar

pulumi up --yes## 🌩️ RECOMENDACIONES PARA IaC Y CLOUD

```

### 1️⃣ Herramientas IaC Open Source (sin Terraform)

El despliegue toma aproximadamente 10-15 minutos debido a la creación de PostgreSQL.

#### **Opción A: Pulumi** ⭐ RECOMENDADA

### 4. Obtener URL de la Aplicación- **Ventajas**:

  - Código en Python, JavaScript, Go, etc.

```bash  - Excelente para AWS, Azure, DigitalOcean

pulumi stack output load_balancer_url  - State management incluido

```  - Capa gratuita generosa (hasta 1000 recursos)

- **Ideal para**: Infraestructura compleja, múltiples clouds

## Pruebas de Autoscaling

#### **Opción B: Ansible** ⭐ BUENA OPCIÓN

### 1. Verificar Estado Inicial- **Ventajas**:

```bash  - Ya lo conoces

LOAD_BALANCER_URL=$(pulumi stack output load_balancer_url)  - Excelente para configuración y despliegue

curl $LOAD_BALANCER_URL/health  - No requiere agentes

```  - Totalmente gratis

- **Limitación**: Menos declarativo que otras opciones para infraestructura

### 2. Generar Carga de CPU- **Ideal para**: Provisionamiento y configuración de instancias

```bash

# Ejecutar test de estrés de 30 segundos#### **Opción C: OpenTofu** ⭐ ALTERNATIVA A TERRAFORM

curl -X POST $LOAD_BALANCER_URL/api/stress \- **Ventajas**:

  -H "Content-Type: application/json" \  - Fork open source de Terraform

  -d '{"duration": 30, "intensity": 10000000}'  - Sintaxis HCL compatible

```  - Comunidad activa

- **Ideal para**: Si buscas algo similar a Terraform

### 3. Monitorear Autoscaling

```bash#### **Opción D: CloudFormation (solo AWS)**

# Ver instancias del Scale Set- Gratis, nativo de AWS

az vmss list-instances \- Limitado a AWS únicamente

  --resource-group cpe-autoscaling-demo-rg \

  --name cpe-autoscaling-demo-vmss \### 2️⃣ Proveedor Cloud Recomendado

  --output table

```#### **🥇 DigitalOcean** - LA MEJOR OPCIÓN PARA TU CASO



### 4. Verificar Métricas**Por qué DigitalOcean:**

```bash- ✅ $200 USD de crédito gratuito por 60 días

curl $LOAD_BALANCER_URL/api/metrics- ✅ Droplets desde $4/mes (suficiente para tu app)

```- ✅ Kubernetes gestionado (3 nodos gratis)

- ✅ Load Balancer integrado

## Gestión de Recursos- ✅ Autoscaling simple de configurar

- ✅ Interfaz muy intuitiva

### Detener Recursos (sin destruir)- ✅ Excelente documentación



```bash**Arquitectura sugerida:**

# Reducir Scale Set a 0 instancias```

az vmss scale \┌─────────────────────────────────────┐

  --resource-group cpe-autoscaling-demo-rg \│     DigitalOcean Load Balancer      │

  --name cpe-autoscaling-demo-vmss \└──────────────┬──────────────────────┘

  --new-capacity 0               │

    ┌──────────┴──────────┐

# Detener PostgreSQL    │                     │

az postgres flexible-server stop \┌───▼────┐           ┌───▼────┐

  --resource-group cpe-autoscaling-demo-rg \│Droplet1│           │Droplet2│ (Autoscaling)

  --name cpe-autoscaling-demo-postgres└────────┘           └────────┘

```    │                     │

    └──────────┬──────────┘

### Reactivar Recursos          ┌────▼─────┐

          │PostgreSQL│

```bash          │ Managed  │

# Iniciar PostgreSQL          └──────────┘

az postgres flexible-server start \```

  --resource-group cpe-autoscaling-demo-rg \

  --name cpe-autoscaling-demo-postgres#### **🥈 AWS EC2 con Free Tier** - ALTERNATIVA



# Escalar a 1 instancia**Incluye:**

az vmss scale \- 750 horas/mes de t2.micro (12 meses)

  --resource-group cpe-autoscaling-demo-rg \- Application Load Balancer (750 horas)

  --name cpe-autoscaling-demo-vmss \- RDS PostgreSQL gratis

  --new-capacity 1- Auto Scaling Groups

```

**Limitación:** Solo 12 meses gratis

### Destruir Infraestructura

#### **🥉 Azure** - TERCERA OPCIÓN

```bash

cd infrastructure-azure- $200 crédito por 30 días

pulumi destroy --yes- VM B1S gratis por 12 meses

```- Más complejo de configurar



## Costos Estimados en Azure### 3️⃣ Estrategia de Autoscaling



Costos mensuales aproximados (sin créditos gratuitos):#### **Configuración Recomendada:**



| Recurso | Especificación | Costo Mensual |**Métrica de escalado**: CPU utilization

|---------|---------------|---------------|- Scale up: cuando CPU > 70% por 2 minutos

| VM Scale Set | Standard_B1s × 1 VM | $7.59 |- Scale down: cuando CPU < 30% por 5 minutos

| PostgreSQL | Standard_B1ms | $12.41 |

| Load Balancer | Standard SKU | $18.26 |**Configuración:**

| Public IP | Static | $3.65 |- Min instances: 1

| Storage | Standard LRS | $1-2 |- Max instances: 3 (para capa gratuita)

| Bandwidth | Transferencia de datos | $1-5 |- Desired: 1

| **TOTAL** | | **~$43-45/mes** |

### 4️⃣ Pruebas de Autoscaling Automatizadas

**Nota**: Azure ofrece $200 en créditos gratuitos por 30 días para nuevas cuentas.

#### **Opción A: GitHub Actions** ⭐ RECOMENDADA

## Arquitectura de la Solución

Crear workflow que:

### Componentes Azure Creados1. Se ejecute bajo demanda o scheduled

2. Use el script `load-test.py` contra tu URL pública

1. **Resource Group**: Contenedor lógico de todos los recursos3. Monitoree el escalado

2. **Virtual Network**: Red virtual 10.0.0.0/16 con 2 subnets4. Genere reporte

3. **Public IP**: IP estática para el Load Balancer

4. **Load Balancer**: Standard SKU con health probe en puerto 5000```yaml

5. **Network Security Group**: Reglas de firewall (HTTP, Flask, SSH)# .github/workflows/autoscaling-test.yml

6. **PostgreSQL Flexible Server**: Base de datos compartida con VNet integrationname: Autoscaling Test

7. **VM Scale Set**: 1-3 instancias Ubuntu 22.04 LTS

8. **Autoscale Settings**: Reglas basadas en métricas de CPUon:

  workflow_dispatch:

### Flujo de Datos    inputs:

      target_url:

1. Usuario accede via HTTP (puerto 80) al Load Balancer        description: 'URL del servidor'

2. Load Balancer distribuye tráfico a las instancias del Scale Set (puerto 5000)        required: true

3. Cada instancia ejecuta Flask y se conecta a PostgreSQL compartido

4. Las visitas se registran con el `instance_id` para trazabilidadjobs:

5. Azure Monitor evalúa CPU cada minuto  load-test:

6. Autoscaling ajusta el número de instancias según las reglas configuradas    runs-on: ubuntu-latest

    steps:

## Troubleshooting      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4

### Error: No se puede conectar a la base de datos        with:

          python-version: '3.11'

Verifica que PostgreSQL esté en estado "Available":      - name: Install dependencies

```bash        run: pip install -r scripts/requirements.txt

az postgres flexible-server show \      - name: Run load test

  --resource-group cpe-autoscaling-demo-rg \        run: python scripts/load-test.py ${{ github.event.inputs.target_url }} 2000 100

  --name cpe-autoscaling-demo-postgres \```

  --query state

```#### **Opción B: Locust** (Herramienta especializada)



### Error: Load Balancer no responde```python

# locustfile.py

Verifica las instancias del Scale Set:from locust import HttpUser, task, between

```bash

az vmss list-instances \class AutoscalingUser(HttpUser):

  --resource-group cpe-autoscaling-demo-rg \    wait_time = between(1, 3)

  --name cpe-autoscaling-demo-vmss \    

  --output table    @task(3)

```    def visit(self):

        self.client.post("/api/visit", json={})

### Ver logs de una instancia    

    @task(1)

```bash    def stress(self):

# Conectar via SSH        self.client.post("/api/stress", json={"duration": 10, "intensity": 1000000})

az vmss list-instance-connection-info \    

  --resource-group cpe-autoscaling-demo-rg \    @task(2)

  --name cpe-autoscaling-demo-vmss    def metrics(self):

        self.client.get("/api/metrics")

# Ver logs de Flask

ssh azureuser@<IP> "tail -f /var/log/flask-app.log"# Ejecutar:

```# locust -f locustfile.py --host=http://your-server.com --users 100 --spawn-rate 10

```

## Decisiones de Diseño

#### **Opción C: K6** (Más moderno)

### ¿Por qué Azure en lugar de AWS?

```javascript

La cuenta de AWS presentó restricciones para crear Application Load Balancers. Azure fue elegido como alternativa porque:// load-test.js

- No presenta restricciones en Load Balancersimport http from 'k6/http';

- Ofrece $200 en créditos gratuitos (vs $100 en AWS)import { check, sleep } from 'k6';

- VM Scale Sets son más simples de configurar

- PostgreSQL Flexible Server es más modernoexport let options = {

  stages: [

## Licencia    { duration: '2m', target: 50 },   // Ramp up

    { duration: '5m', target: 100 },  // Stay at 100 users

MIT License    { duration: '2m', target: 0 },    // Ramp down

  ],

## Autor};



Christian Pizarro Espinozaexport default function() {

- GitHub: [@ChristianPE1](https://github.com/ChristianPE1)  let response = http.post('http://your-server/api/visit', JSON.stringify({}));

- Email: crash_17_18@outlook.es  check(response, { 'status is 201': (r) => r.status === 201 });

  sleep(1);
}
```

### 5️⃣ Stack IaC Recomendado Final

**MI RECOMENDACIÓN:**

```
┌─────────────────────────────────────────┐
│   Pulumi (Python) + DigitalOcean        │
│   + GitHub Actions (para pruebas)       │
└─────────────────────────────────────────┘
```

**Ventajas:**
- ✅ Pulumi en Python (fácil de aprender)
- ✅ DigitalOcean simple y generoso
- ✅ GitHub Actions gratis e integrado
- ✅ Todo el stack es open source
- ✅ Costo mínimo (puedes usar créditos gratis)

**Estructura del proyecto completo:**

```
sistema-autoscaling/
├── infrastructure/          # Código IaC con Pulumi
│   ├── __main__.py         # Definición infraestructura
│   ├── Pulumi.yaml
│   └── requirements.txt
├── .github/
│   └── workflows/
│       ├── deploy.yml      # CI/CD
│       └── load-test.yml   # Pruebas automáticas
├── backend/
├── frontend/
└── scripts/
```

### 6️⃣ Plan de Implementación

1. **Semana 1**: 
   - ✅ Aplicación lista (ya está hecha)
   - Registrarte en DigitalOcean
   - Instalar Pulumi

2. **Semana 2**:
   - Crear infraestructura con Pulumi
   - Desplegar aplicación en Droplets
   - Configurar Load Balancer

3. **Semana 3**:
   - Configurar autoscaling
   - Crear scripts de prueba
   - Configurar GitHub Actions

4. **Semana 4**:
   - Pruebas de autoscaling
   - Documentación
   - Video demo

## 📚 Recursos Adicionales

- [Pulumi Getting Started](https://www.pulumi.com/docs/get-started/)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/)
- [Ansible Cloud Modules](https://docs.ansible.com/ansible/latest/collections/community/digitalocean/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

## 🎯 Plan de Acción

### ✅ HOY (23 octubre) - Completado
- ✅ Aplicación full stack creada
- ✅ Docker y Docker Compose configurados
- ✅ Scripts de prueba de carga listos
- ✅ Error 500 solucionado
- ✅ PostgreSQL agregado a docker-compose
- ✅ Infraestructura Pulumi para AWS lista
- ✅ GitHub Actions configurados
- ✅ Documentación completa

### 📋 MAÑANA (24 octubre) - Tu turno

#### Fase 1: Setup (30 min)
```bash
# 1. Instalar Pulumi
curl -fsSL https://get.pulumi.com | sh

# 2. Configurar AWS CLI (si no lo has hecho)
aws configure

# 3. Setup del proyecto
cd infrastructure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Login en Pulumi
pulumi login

# 5. Configurar
pulumi stack init production
pulumi config set aws:region us-east-1
pulumi config set --secret autoscaling-demo:db_password 'TuPassword123!'
```

#### Fase 2: Despliegue (15 min)
```bash
# Preview
pulumi preview

# Deploy (confirma con 'yes')
pulumi up
```

#### Fase 3: Pruebas (30 min)
```bash
# Obtener URL
export ALB_URL=$(pulumi stack output alb_url)

# Prueba básica
curl $ALB_URL/health

# Prueba de autoscaling
python ../scripts/load-test.py $ALB_URL 2000 100

# Monitorear
watch -n 30 'aws ec2 describe-instances --filters "Name=tag:ManagedBy,Values=Pulumi" --query "Reservations[*].Instances[*].[InstanceId,State.Name]" --output table'
```

#### Fase 4: Documentación (15 min)
- Tomar screenshots de CloudWatch Alarms
- Capturar historial del Auto Scaling Group
- Documentar timeline del autoscaling
- Anotar métricas observadas

#### Fase 5: Limpieza
```bash
# IMPORTANTE: Al terminar, destruir recursos
pulumi destroy
```

## 🎓 Qué esperar en las pruebas

| Tiempo | Evento | Instancias | CPU |
|--------|--------|------------|-----|
| 0:00 | Sistema estable | 1 | ~20% |
| 1:00 | Carga inicia, CPU sube | 1 | ~80% |
| 2:30 | Alarma activa, scale up | 1→2 | ~80% |
| 4:00 | Nueva instancia healthy | 2 | ~40% |
| 10:00 | Carga termina | 2 | ~20% |
| 15:00 | Scale down activa | 2→1 | ~20% |

## 🚨 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Error 500 local | `docker-compose down && docker-compose up -d --build` |
| Instancias unhealthy | Revisar Security Groups y health check endpoint |
| No hay autoscaling | Esperar 2-5 min, verificar CloudWatch Alarms |
| Costos altos | `pulumi destroy` inmediatamente |

## 📊 Checklist de Documentación

Para tu entrega final, documenta:
- [ ] Arquitectura desplegada (diagrama)
- [ ] Screenshots de AWS Console:
  - [ ] EC2 Instances
  - [ ] Auto Scaling Group Activity
  - [ ] CloudWatch Alarms
  - [ ] Load Balancer
  - [ ] RDS Database
- [ ] Código de infraestructura (Pulumi)
- [ ] Logs de las pruebas de carga
- [ ] Timeline del autoscaling observado
- [ ] Métricas: CPU, peticiones/seg, tiempo de respuesta
- [ ] Conclusiones: ¿Funcionó el autoscaling?

## 📝 Archivos Clave

```
sistema-autoscaling/
├── GUIA_COMPLETA.md          ← Lee esto primero
├── COMANDOS_RAPIDOS.md       ← Comandos para copiar-pegar
├── README.md                  ← Este archivo
├── backend/                   ← API Flask
├── frontend/                  ← React App
├── infrastructure/            ← Pulumi (AWS IaC)
│   ├── __main__.py           ← Definición completa de AWS
│   ├── README.md             ← Guía de Pulumi
│   └── requirements.txt
├── scripts/                   ← Pruebas de carga
│   └── load-test.py          ← Script principal
├── .github/workflows/         ← CI/CD
│   ├── deploy.yml            ← Deploy automático
│   └── load-test.yml         ← Pruebas automáticas
└── docker-compose.yml         ← Desarrollo local
```

## 🎯 Resumen Ejecutivo

**Aplicación**: Full stack ligera (Flask + React + PostgreSQL)  
**IaC**: Pulumi (Python) - Open Source ✅  
**Cloud**: AWS Free Tier  
**Autoscaling**: 1-3 instancias EC2, basado en CPU (>70% scale up, <30% scale down)  
**Pruebas**: Automatizadas con Python (externas, no manuales) ✅  
**Costo**: $0 con free tier + $100 créditos = ~15 meses gratis  

**Estado**: ✅ TODO LISTO PARA DESPLEGAR MAÑANA

---

**¿Dudas antes de empezar mañana?** Revisa:
1. [GUIA_COMPLETA.md](./GUIA_COMPLETA.md) - Explicación detallada
2. [COMANDOS_RAPIDOS.md](./COMANDOS_RAPIDOS.md) - Comandos listos
3. [infrastructure/README.md](./infrastructure/README.md) - Guía de Pulumi

**¡Éxito con el despliegue! 🚀**
