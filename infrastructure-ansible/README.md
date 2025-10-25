# Azure Infrastructure with Ansible

Este proyecto utiliza Ansible para gestionar la infraestructura en Azure de forma automatizada. Está configurado para usar recursos de **capa gratuita** o recursos mínimos para mantener los costos bajos.

## 📋 Requisitos Previos

### 1. Instalar Dependencias

```bash
# Python 3.8 o superior
python3 --version

# Instalar pip si no lo tienes
sudo apt install python3-pip

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar colección de Azure para Ansible
ansible-galaxy collection install -r requirements.yml
```

### 2. Azure CLI y Autenticación

```bash
# Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Iniciar sesión en Azure
az login

# Verificar suscripción activa
az account show

# (Opcional) Establecer suscripción específica
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 3. Crear Service Principal (Recomendado para CI/CD)

```bash
# Crear service principal
az ad sp create-for-rbac --name "ansible-deployment" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Esto generará credenciales que debes guardar
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` o exporta las variables:

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_SECRET="your-client-secret"
export AZURE_TENANT="your-tenant-id"
export MYSQL_PASSWORD="YourSecurePassword123!"
```

## 🗂️ Estructura del Proyecto

```
infrastructure-ansible/
├── ansible.cfg              # Configuración de Ansible
├── requirements.txt         # Dependencias Python
├── requirements.yml         # Colecciones Ansible
├── inventories/
│   └── hosts.yml           # Inventario (localhost)
├── group_vars/
│   └── all.yml             # Variables globales
├── deploy-all.yml          # Playbook principal (ejecuta todo)
├── deploy-infrastructure.yml  # Despliega red y recursos base
├── deploy-mysql.yml        # Despliega MySQL Flexible Server
├── deploy-apps.yml         # Despliega aplicaciones web
└── destroy.yml             # Destruye toda la infraestructura
```

## 🚀 Uso

### Despliegue Completo

Para desplegar toda la infraestructura de una vez:

```bash
cd infrastructure-ansible

# Desplegar todo
ansible-playbook deploy-all.yml

# O con más verbosidad para debugging
ansible-playbook deploy-all.yml -vvv
```

### Despliegue por Componentes

Puedes ejecutar playbooks individuales:

```bash
# 1. Desplegar infraestructura base (VNet, Subnet, NSG)
ansible-playbook deploy-infrastructure.yml

# 2. Desplegar MySQL Flexible Server
ansible-playbook deploy-mysql.yml

# 3. Desplegar aplicaciones (Backend + Frontend)
ansible-playbook deploy-apps.yml
```

### Destruir Infraestructura

```bash
# Con confirmación interactiva
ansible-playbook destroy.yml

# Sin confirmación (automático)
ansible-playbook destroy.yml -e "auto_approve=true"
```

## ⚙️ Configuración

### Personalizar Variables

Edita `group_vars/all.yml` para personalizar:

- **project_name**: Nombre de tu proyecto
- **location**: Región de Azure (por defecto: eastus)
- **mysql_admin_password**: Contraseña del admin de MySQL
- **backend_docker_image**: Tu imagen Docker del backend
- **frontend_docker_image**: Tu imagen Docker del frontend

Ejemplo:

```yaml
project_name: "mi-proyecto"
location: "eastus"
mysql_admin_password: "MiPassword123!"
backend_docker_image: "tuusuario/backend:latest"
frontend_docker_image: "tuusuario/frontend:latest"
```

### Variables de Entorno

Puedes sobrescribir variables desde la línea de comandos:

```bash
ansible-playbook deploy-all.yml \
  -e "project_name=test" \
  -e "environment=development" \
  -e "mysql_admin_password=MySecretPass123!"
```

## 📦 Recursos Desplegados

### Capa Gratuita / Recursos Mínimos

1. **Resource Group**: Contenedor de todos los recursos
2. **Virtual Network**: Red virtual 10.0.0.0/16
3. **Subnet**: Subred 10.0.1.0/24 con delegación para MySQL
4. **Network Security Group**: Reglas de firewall
5. **MySQL Flexible Server**:
   - SKU: Standard_B1ms (1 vCore, 2GB RAM)
   - Storage: 20GB
   - Backup: 7 días
6. **App Service Plan**: F1 Free Tier
7. **Web Apps**: 
   - Backend (Flask/Python)
   - Frontend (React/Nginx)

### Costos Estimados

- **MySQL Flexible Server B1ms**: ~$12-15/mes (sin capa gratuita)
- **App Service F1**: Gratuito (con limitaciones)
- **Networking**: Gratuito en su mayoría
- **Total estimado**: ~$15-20/mes

> ⚠️ **Nota**: Azure no tiene una capa totalmente gratuita para MySQL Flexible Server. El SKU más pequeño (B1ms) tiene costo. Para desarrollo, considera usar Azure Database for MySQL Single Server (tiene 12 meses gratis con cuenta nueva) o usar MySQL en un Container.

## 🔧 Troubleshooting

### Error de Autenticación

```bash
# Verificar credenciales
az account show

# Re-autenticar
az login
```

### Error: Región no disponible

Algunas regiones no tienen todos los servicios. Usa `eastus`, `westus2`, o `westeurope`:

```yaml
location: "eastus"
```

### Error: Cuota excedida

Si tienes cuenta gratuita, verifica tus límites:

```bash
az vm list-usage --location eastus -o table
```

### Ver logs de despliegue

```bash
# Ejecutar con verbosidad máxima
ansible-playbook deploy-all.yml -vvv

# Ver logs en Azure Portal
az webapp log tail --name app-autoscaling-system-backend-production \
  --resource-group rg-autoscaling-system-production
```

## 🐳 Preparar Imágenes Docker

Antes de desplegar, asegúrate de tener tus imágenes Docker publicadas:

```bash
# Backend
cd backend
docker build -t tuusuario/autoscaling-backend:latest .
docker push tuusuario/autoscaling-backend:latest

# Frontend
cd frontend
docker build -t tuusuario/autoscaling-frontend:latest .
docker push tuusuario/autoscaling-frontend:latest
```

Actualiza las variables en `group_vars/all.yml`:

```yaml
backend_docker_image: "tuusuario/autoscaling-backend:latest"
frontend_docker_image: "tuusuario/autoscaling-frontend:latest"
```

## 🔄 CI/CD con GitHub Actions

Ejemplo de workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Ansible
        run: |
          pip install -r infrastructure-ansible/requirements.txt
          ansible-galaxy collection install -r infrastructure-ansible/requirements.yml
      
      - name: Deploy Infrastructure
        working-directory: infrastructure-ansible
        env:
          AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_SECRET: ${{ secrets.AZURE_SECRET }}
          AZURE_TENANT: ${{ secrets.AZURE_TENANT }}
          MYSQL_PASSWORD: ${{ secrets.MYSQL_PASSWORD }}
        run: ansible-playbook deploy-all.yml
```

## 📚 Recursos Adicionales

- [Ansible Azure Guide](https://docs.ansible.com/ansible/latest/scenario_guides/guide_azure.html)
- [Azure Free Services](https://azure.microsoft.com/free/)
- [MySQL Flexible Server Pricing](https://azure.microsoft.com/pricing/details/mysql/)
- [App Service Pricing](https://azure.microsoft.com/pricing/details/app-service/)

## 🆘 Soporte

Si encuentras problemas:

1. Verifica que todas las dependencias están instaladas
2. Asegúrate de estar autenticado en Azure (`az login`)
3. Verifica que la contraseña de MySQL cumple los requisitos de complejidad
4. Revisa los logs con `-vvv` para más detalles
5. Consulta el Azure Portal para ver el estado de los recursos

## 📝 Licencia

Este proyecto es parte del sistema de autoscaling y sigue la misma licencia del proyecto principal.
