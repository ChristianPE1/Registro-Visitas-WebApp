# Monitoring con Prometheus y Grafana

## 📋 Descripción
Stack de observabilidad con Prometheus (métricas) y Grafana (visualización).

## 🎯 Principios IaC Aplicados
- **Observabilidad** (Capítulo 1): Métricas para las 4 métricas DORA
- **Define todo como código** (Cap 4): Configuración declarativa
- **Hacer reproducible** (Cap 2): Stack completo versionado

## 📦 Recursos Incluidos
- **Namespace**: monitoring
- **Prometheus**: Recolección de métricas
  - ServiceAccount + RBAC para descubrimiento de servicios
  - Scrape de pods con anotaciones
  - Scrape del backend específicamente
  - Métricas de Kubernetes (nodes, pods, API server)
- **Grafana**: Visualización de métricas
  - Datasource de Prometheus preconfigurado
  - Usuario: admin / Contraseña: admin

## 🚀 Despliegue
```bash
kubectl apply -f k8s/monitoring/prometheus-grafana.yaml
```

## 🔍 Verificación
```bash
# Ver pods de monitoring
kubectl get pods -n monitoring

# Ver servicios (obtener IPs públicas)
kubectl get svc -n monitoring

# Logs de Prometheus
kubectl logs -n monitoring -l app=prometheus

# Logs de Grafana
kubectl logs -n monitoring -l app=grafana
```

## 🌐 Acceso

### Prometheus
```bash
# Obtener IP pública
kubectl get svc -n monitoring prometheus-service

# Acceder a:
http://<PROMETHEUS-EXTERNAL-IP>:9090
```

**Queries útiles**:
- `up` - Estado de targets
- `rate(flask_http_requests_total[5m])` - Requests por segundo del backend
- `flask_http_request_duration_seconds_bucket` - Latencia de requests

### Grafana
```bash
# Obtener IP pública
kubectl get svc -n monitoring grafana-service

# Acceder a:
http://<GRAFANA-EXTERNAL-IP>:3000

# Credenciales por defecto:
Usuario: admin
Contraseña: admin
```

## 📊 Configuración de Scraping

### Backend Pods
Los pods del backend tienen anotaciones:
```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "5000"
prometheus.io/path: "/metrics"
```

Prometheus automáticamente descubrirá y scrapeará estos pods.

## 📈 Dashboards Recomendados

### Importar dashboards en Grafana:
1. Ir a Dashboards → Import
2. Importar por ID:
   - **13770**: Kubernetes Pod Metrics
   - **6417**: Kubernetes Cluster Monitoring
   - **3662**: Prometheus Stats

### Crear dashboard personalizado:
- Métricas del backend Flask
- HPA status (réplicas actuales)
- Node CPU/Memory
- Request rate por endpoint

## 💾 Persistencia

⚠️ **Nota**: Esta configuración usa `emptyDir` para storage (no persistente) para reducir costos.

Los datos se pierden si el pod se reinicia. Para producción real, usar PersistentVolumeClaims.

## 🔒 Seguridad

⚠️ **Cambiar contraseña de Grafana**:
```yaml
- name: GF_SECURITY_ADMIN_PASSWORD
  value: "TU_CONTRASEÑA_SEGURA"
```

## 🗑️ Eliminar
```bash
kubectl delete -f k8s/monitoring/prometheus-grafana.yaml
```

## 🔗 Referencias
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
- [Grafana Kubernetes Monitoring](https://grafana.com/docs/grafana/latest/setup-grafana/configure-kubernetes/)
