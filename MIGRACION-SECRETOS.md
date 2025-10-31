# 🔐 Migración de Secretos de Pulumi

## Situación Actual

Tienes secretos en el proyecto viejo (`infrastructure-azure`):
- `db_password`: Contraseña de PostgreSQL
- `admin_password`: Contraseña de administrador

## ✅ Reutilización de Secretos (Recomendado)

### Opción 1: Copiar los valores encriptados (Más Seguro)

Los secretos de Pulumi están encriptados. Puedes copiarlos directamente:

```bash
# 1. Ver el password actual (desencriptado)
cd infrastructure-azure
pulumi config get db_password --show-secrets

# 2. Usar ese mismo valor en las nuevas pilas
cd ../infrastructure-k8s-db
pulumi config set --secret db_admin_password "EL_MISMO_PASSWORD_QUE_VISTE_ARRIBA"

# 3. Repetir para infrastructure-k8s-deploy
cd ../infrastructure-k8s-deploy
pulumi config set --secret db_admin_password "EL_MISMO_PASSWORD_QUE_VISTE_ARRIBA"
```

### Opción 2: Script Automático (Recomendado)

Crea un script para migrar los secretos automáticamente:

```bash
#!/bin/bash
# migrate-secrets.sh

# Obtener password de la pila vieja
OLD_DB_PASS=$(cd infrastructure-azure && pulumi config get db_password --show-secrets)

# Configurar en las nuevas pilas
echo "Configurando secrets en infrastructure-k8s-db..."
cd infrastructure-k8s-db
pulumi config set --secret db_admin_password "$OLD_DB_PASS"

echo "Configurando secrets en infrastructure-k8s-deploy..."
cd ../infrastructure-k8s-deploy
pulumi config set --secret db_admin_password "$OLD_DB_PASS"

echo "✅ Secretos migrados exitosamente"
```

## 📋 Verificación de Configuración

### Para infrastructure-k8s-base
```bash
cd infrastructure-k8s-base
pulumi config

# Deberías ver:
# KEY                  VALUE
# k8s-base:location    eastus
# k8s-base:ssh_public_key  ssh-rsa AAAA...
```

### Para infrastructure-k8s-db
```bash
cd infrastructure-k8s-db
pulumi config

# Deberías ver:
# KEY                          VALUE
# k8s-db:location              eastus
# k8s-db:db_admin_password     [secret]
```

### Para infrastructure-k8s-deploy
```bash
cd infrastructure-k8s-deploy
pulumi config

# Deberías ver:
# KEY                                VALUE
# k8s-deploy:backend_image           cpeautoscalingacr.azurecr.io/...
# k8s-deploy:frontend_image          cpeautoscalingacr.azurecr.io/...
# k8s-deploy:db_admin_password       [secret]
```

## ⚠️ Importante: Subscription ID

Tu subscription ID es la misma para todos los proyectos:
```
1eb83675-114b-4f93-8921-f055b5bd6ea8
```

Ya está hardcodeado en `infrastructure-k8s-base/__main__.py` y `infrastructure-k8s-deploy/__main__.py`.

## 🔒 Seguridad

- ✅ Los secretos nunca se guardan en texto plano en Git
- ✅ Pulumi los encripta automáticamente
- ✅ Solo tú (con tu sesión de Pulumi) puedes desencriptarlos
- ✅ Reutilizar passwords es seguro (no se exponen)

## 🚀 Resumen: Pasos Corregidos

1. **Ver password actual**:
   ```bash
   cd infrastructure-azure
   pulumi config get db_password --show-secrets
   # Anota el valor
   ```

2. **Configurar en nuevas pilas**:
   ```bash
   # Pila DB
   cd ../infrastructure-k8s-db
   pulumi stack select production  # O init si no existe
   pulumi config set --secret db_admin_password "PASSWORD_ANOTADO"
   
   # Pila Deploy
   cd ../infrastructure-k8s-deploy
   pulumi stack select production
   pulumi config set --secret db_admin_password "PASSWORD_ANOTADO"
   ```

3. **Verificar**:
   ```bash
   pulumi config  # Debe mostrar [secret]
   ```

**¡Listo! Ahora puedes proceder con el despliegue.**
