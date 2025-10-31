# Pila 2: Base de Datos PostgreSQL - Micro-Stack

## 📋 Descripción
Crea una base de datos PostgreSQL Flexible Server independiente del cluster AKS.

**Micro-Stack Pattern** (Cap 5): Esta pila tiene un ciclo de vida separado.
Puedes destruir y reconstruir el cluster AKS sin afectar los datos persistentes.

## 🎯 Principios IaC Aplicados
- **Micro-Stack Pattern** (Cap 5): Pila independiente con ciclo de vida propio
- **Radio de explosión limitado**: Cambios en el cluster no afectan la DB
- **Datos persistentes**: Separados de infraestructura efímera
- **Hacer reproducible** (Cap 2): Pila idempotente

## 🚀 Despliegue

### Pre-requisitos
- Haber desplegado la Pila 1 (infrastructure-k8s-base)
- Azure CLI configurado
- Pulumi instalado

### Configuración
```bash
cd infrastructure-k8s-db

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Seleccionar/crear stack
pulumi stack init production
# o
pulumi stack select production

# Configurar contraseña de DB (secreto)
pulumi config set --secret db_admin_password "TuContraseñaSegura123!"
```

### Desplegar
```bash
# Preview de cambios
pulumi preview

# Desplegar base de datos
pulumi up

# Ver outputs (connection string estará oculto por seguridad)
pulumi stack output
pulumi stack output connection_string --show-secrets
```

## 📊 Recursos Creados
- **PostgreSQL Flexible Server**: cpe-k8s-autoscaling-postgres
- **Database**: autoscaling_db
- **Subnet**: 10.0.2.0/24 (delegada a PostgreSQL)
- **Firewall Rule**: Permite conexiones desde Azure services

## 🔐 Conexión desde AKS
La base de datos está configurada para aceptar conexiones desde servicios de Azure (incluyendo AKS).

El connection string se pasará como secreto de Kubernetes en la Pila 3.

```bash
# Ver connection string (con secretos)
pulumi stack output connection_string --show-secrets

# Formato: postgresql://postgres_admin:PASSWORD@HOST:5432/autoscaling_db
```

## 💰 Costo Estimado
- PostgreSQL B1ms: ~$12/mes
- Storage 32 GiB: ~$5/mes
- **Total**: ~$17/mes

## 🗑️ Destruir
⚠️ **ADVERTENCIA**: Esto eliminará todos los datos de la base de datos.

```bash
# Backup manual antes de destruir (opcional)
pg_dump -h HOST -U postgres_admin -d autoscaling_db > backup.sql

# Eliminar infraestructura
pulumi destroy
```

## 🔗 Siguiente Paso
Una vez desplegado, continuar con:
- **Manifiestos K8s**: k8s/backend/ y k8s/frontend/
- **Pila 3**: infrastructure-k8s-deploy (Despliegue de aplicaciones)
