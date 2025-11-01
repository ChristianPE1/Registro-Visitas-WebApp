# Backend Kubernetes Manifests

## Descripción
Manifiestos de Kubernetes para el backend Flask con autoscaling.

## Principios IaC Aplicados
- **Ganado no Mascotas** (Cap 2): Pods desechables y reemplazables
- **Asumir sistemas no confiables** (Cap 2): Health checks y auto-healing
- **Minimizar variación** (Cap 2): Node affinity para pool específico
- **Piezas pequeñas débilmente acopladas** (Cap 1): Backend independiente

## Recursos Incluidos
- **Namespace**: backend
- **Secret**: db-credentials (conexión a PostgreSQL)
- **ConfigMap**: backend-config (variables de entorno)
- **Deployment**: 2-10 réplicas con node affinity
- **Service**: ClusterIP para comunicación interna
- **HPA**: Autoscaling basado en CPU (70%) y Memoria (80%)

## Características

### Node Affinity
Los pods solo se despliegan en nodos con label `workload=backend`.

### Anti-Affinity
Los pods se distribuyen en diferentes nodos para alta disponibilidad.

### Health Checks
- **Liveness**: Reinicia pod si no responde
- **Readiness**: Quita pod del service si no está listo

### Autoscaling
- **Min**: 2 réplicas
- **Max**: 10 réplicas
- **CPU**: Escala en 70%
- **Memoria**: Escala en 80%
- **Scale Up**: Inmediato (agresivo)
- **Scale Down**: Espera 5 min (conservador)

## Endpoints
- `/health` - Health check
- `/api/visit` - Registrar visita
- `/api/visits` - Obtener visitas
- `/api/stress` - Test de carga
- `/metrics` - Métricas Prometheus
