# Configuración de GitHub Actions para CI/CD

Este documento explica cómo configurar los secretos necesarios para que los workflows de GitHub Actions funcionen correctamente.

## 📋 Secretos Requeridos

Los workflows de CI/CD requieren tres secretos configurados en tu repositorio de GitHub:

1. **`GCP_SA_KEY`** - Credenciales de Service Account de Google Cloud
2. **`PULUMI_ACCESS_TOKEN`** - Token de acceso a Pulumi Cloud
3. **`DB_ADMIN_PASSWORD`** - Contraseña del administrador de PostgreSQL

---

## 🔐 1. GCP_SA_KEY (Service Account de Google Cloud)

Este secreto contiene las credenciales JSON de una cuenta de servicio de GCP con permisos para gestionar recursos del proyecto.

### Permisos Necesarios

La cuenta de servicio debe tener los siguientes roles:

- `roles/artifactregistry.writer` - Para subir imágenes Docker
- `roles/container.admin` - Para gestionar GKE clusters
- `roles/cloudsql.client` - Para conectarse a Cloud SQL
- `roles/compute.viewer` - Para ver recursos de Compute Engine
- `roles/iam.serviceAccountUser` - Para usar service accounts

### Pasos para Crear la Service Account

```bash
# 1. Definir variables
export PROJECT_ID="cpe-autoscaling-k8s"
export SA_NAME="github-actions-sa"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 2. Crear la service account
gcloud iam service-accounts create ${SA_NAME} \
  --display-name="GitHub Actions CI/CD Service Account" \
  --description="Service account for GitHub Actions workflows" \
  --project=${PROJECT_ID}

# 3. Asignar roles necesarios
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/compute.viewer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# 4. Crear y descargar la clave JSON
gcloud iam service-accounts keys create ~/gcp-sa-key.json \
  --iam-account=${SA_EMAIL} \
  --project=${PROJECT_ID}

# 5. Mostrar el contenido (para copiar al clipboard)
cat ~/gcp-sa-key.json
```

### Configurar en GitHub

1. Ve a tu repositorio en GitHub
2. Navega a **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**
4. Nombre: `GCP_SA_KEY`
5. Valor: Pega el contenido completo del archivo JSON (todo el contenido de `~/gcp-sa-key.json`)
6. Click en **Add secret**

⚠️ **IMPORTANTE**: Guarda el archivo JSON en un lugar seguro y borra `~/gcp-sa-key.json` después de configurar el secreto:
```bash
rm ~/gcp-sa-key.json
```

---

## 🔑 2. PULUMI_ACCESS_TOKEN

Este token permite a GitHub Actions interactuar con Pulumi Cloud para gestionar el estado de la infraestructura.

### Pasos para Obtener el Token

1. **Inicia sesión en Pulumi Cloud**:
   ```bash
   pulumi login
   ```

2. **Ve al dashboard web**:
   - Abre https://app.pulumi.com/
   - Inicia sesión con tu cuenta

3. **Crea un nuevo token de acceso**:
   - Click en tu avatar (esquina superior derecha)
   - Selecciona **Settings**
   - En el menú izquierdo, click en **Access Tokens**
   - Click en **Create token**
   - Nombre sugerido: `GitHub Actions CI/CD`
   - Descripción: `Token for automated deployments via GitHub Actions`
   - Click en **Create token**

4. **Copia el token generado** (solo se mostrará una vez)

### Configurar en GitHub

1. Ve a tu repositorio en GitHub
2. Navega a **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**
4. Nombre: `PULUMI_ACCESS_TOKEN`
5. Valor: Pega el token de acceso de Pulumi
6. Click en **Add secret**

---

## 🔒 3. DB_ADMIN_PASSWORD

Este secreto contiene la contraseña del usuario administrador de la base de datos PostgreSQL en Cloud SQL.

### Valor del Password

Debes usar **la misma contraseña** que configuraste durante el despliegue manual de la base de datos (Paso 2: Database).

Si no recuerdas la contraseña, puedes:

1. **Obtenerla del stack de Pulumi**:
   ```bash
   cd infrastructure-gcp-db
   pulumi stack output db_password --show-secrets
   ```

2. **O cambiarla en Cloud SQL**:
   ```bash
   gcloud sql users set-password postgres \
     --instance=cpe-autoscaling-db \
     --password=TU_NUEVA_PASSWORD_SEGURA
   ```

### Configurar en GitHub

1. Ve a tu repositorio en GitHub
2. Navega a **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**
4. Nombre: `DB_ADMIN_PASSWORD`
5. Valor: La contraseña de la base de datos
6. Click en **Add secret**

⚠️ **Recomendación de Seguridad**: Usa una contraseña fuerte con al menos:
- 16 caracteres de longitud
- Letras mayúsculas y minúsculas
- Números
- Caracteres especiales

---

## ✅ Verificar la Configuración

Después de configurar los tres secretos, deberías verlos listados en:

**Settings** → **Secrets and variables** → **Actions** → **Repository secrets**

Deberías ver:
- ✅ `GCP_SA_KEY`
- ✅ `PULUMI_ACCESS_TOKEN`
- ✅ `DB_ADMIN_PASSWORD`

---

## 🧪 Probar los Workflows

### Opción 1: Trigger Manual

Puedes ejecutar workflows manualmente para probar la configuración:

1. Ve a **Actions** en tu repositorio
2. Selecciona el workflow que quieres probar (ej: "Backend CI/CD")
3. Click en **Run workflow**
4. Selecciona la rama y click en **Run workflow**

### Opción 2: Push de Código

Los workflows se activarán automáticamente cuando hagas push a las rutas configuradas:

```bash
# Trigger backend-ci-cd.yml
git add backend/
git commit -m "Update backend"
git push

# Trigger frontend-ci-cd.yml
git add frontend/
git commit -m "Update frontend"
git push

# Trigger infrastructure-ci-cd.yml
git add infrastructure-gcp-base/
git commit -m "Update GKE cluster config"
git push
```

---

## 🔧 Troubleshooting

### Error: "Error fetching credentials"

**Causa**: El JSON de `GCP_SA_KEY` está malformado o incompleto.

**Solución**:
1. Verifica que copiaste TODO el contenido del archivo JSON (debe empezar con `{` y terminar con `}`)
2. No debe tener espacios en blanco adicionales al inicio o final
3. Regenera la clave si es necesario

### Error: "failed to login: invalid access token"

**Causa**: El `PULUMI_ACCESS_TOKEN` es inválido o ha expirado.

**Solución**:
1. Genera un nuevo token en https://app.pulumi.com/
2. Actualiza el secreto en GitHub

### Error: "password authentication failed"

**Causa**: El `DB_ADMIN_PASSWORD` no coincide con el configurado en Cloud SQL.

**Solución**:
1. Verifica la contraseña con `pulumi stack output db_password --show-secrets`
2. Actualiza el secreto en GitHub con la contraseña correcta

### Error: "Permission denied" en GCP

**Causa**: La service account no tiene los permisos necesarios.

**Solución**:
```bash
# Re-verificar roles asignados
gcloud projects get-iam-policy cpe-autoscaling-k8s \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-sa@*"

# Re-asignar roles si es necesario (ver comandos arriba)
```

---

## 🔗 Referencias

- [GitHub Actions - Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google Cloud - Service accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Pulumi - Access tokens](https://www.pulumi.com/docs/intro/pulumi-cloud/accounts/#access-tokens)
- [Cloud SQL - User management](https://cloud.google.com/sql/docs/postgres/users)

---

## 📞 Soporte

Si encuentras problemas durante la configuración:

1. Revisa los logs del workflow en la pestaña **Actions** de GitHub
2. Consulta la sección de Troubleshooting arriba
3. Verifica que todos los secretos estén configurados correctamente
4. Asegúrate de que los recursos de GCP estén desplegados correctamente

