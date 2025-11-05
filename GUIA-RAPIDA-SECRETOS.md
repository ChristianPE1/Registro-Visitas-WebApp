# 🚀 Guía Rápida: Configurar Secretos en GitHub (5 minutos)

## ✅ Service Account Creado

Ya se creó el service account `github-actions-sa@cpe-autoscaling-k8s.iam.gserviceaccount.com` con todos los permisos necesarios:

- ✅ Artifact Registry Writer
- ✅ Container Admin  
- ✅ Cloud SQL Client
- ✅ Compute Viewer
- ✅ Service Account User

La clave JSON está en: `~/gcp-sa-key.json`

---

## 📋 Tres Secretos a Configurar

### 1️⃣ GCP_SA_KEY

**Valor**: Todo el contenido del archivo `~/gcp-sa-key.json`

```bash
# Ver el contenido completo
cat ~/gcp-sa-key.json
```

**Cómo configurarlo en GitHub**:
1. Ve a tu repositorio: https://github.com/ChristianPE1/Registro-Visitas-WebApp
2. Click en **Settings** (pestaña superior)
3. En el menú izquierdo: **Secrets and variables** → **Actions**
4. Click en **New repository secret**
5. Nombre: `GCP_SA_KEY`
6. Valor: Copia y pega **TODO** el contenido del JSON (desde `{` hasta `}`)
7. Click en **Add secret**

---

### 2️⃣ DB_ADMIN_PASSWORD

**Valor**: `4v6bZ5FYrGCQuWo+HiOZDEBUNSzBMI9O65NiS8XNNog=`

⚠️ **Importante**: Copia EXACTAMENTE este valor, incluyendo el `=` al final.

**Cómo configurarlo en GitHub**:
1. En la misma página de secretos
2. Click en **New repository secret**
3. Nombre: `DB_ADMIN_PASSWORD`
4. Valor: `4v6bZ5FYrGCQuWo+HiOZDEBUNSzBMI9O65NiS8XNNog=`
5. Click en **Add secret**

---

### 3️⃣ PULUMI_ACCESS_TOKEN

**Cómo obtenerlo**:

1. **Abre tu navegador** y ve a: https://app.pulumi.com/
2. **Inicia sesión** con tu cuenta (la misma que usas para `pulumi login`)
3. Click en tu **avatar** (esquina superior derecha)
4. Selecciona **Settings**
5. En el menú izquierdo, click en **Access Tokens**
6. Click en **Create token**
7. Nombre: `GitHub Actions CI/CD`
8. Descripción: `Token for automated deployments`
9. Click en **Create token**
10. **Copia el token** (solo se muestra una vez)

**Cómo configurarlo en GitHub**:
1. En la misma página de secretos
2. Click en **New repository secret**
3. Nombre: `PULUMI_ACCESS_TOKEN`
4. Valor: Pega el token que copiaste de Pulumi
5. Click en **Add secret**

---

## ✅ Verificar Configuración

Después de configurar los 3 secretos, deberías ver esto en:

**Settings** → **Secrets and variables** → **Actions** → **Repository secrets**

```
✅ GCP_SA_KEY
✅ DB_ADMIN_PASSWORD
✅ PULUMI_ACCESS_TOKEN
```

---

## 🧪 Probar que Funciona

### Opción 1: Trigger Manual (Recomendado)

1. Ve a la pestaña **Actions** en tu repositorio
2. Selecciona el workflow **"Backend CI/CD"**
3. Click en **Run workflow** (botón azul a la derecha)
4. Selecciona la rama `main`
5. Click en **Run workflow**
6. Espera 3-5 minutos y verifica que el workflow termina exitosamente ✅

### Opción 2: Push de Código

```bash
# Haz un pequeño cambio en el backend
cd /home/christianpe/Documentos/proyectos/sistema-autoscaling
echo "# Test CI/CD" >> backend/README.md
git add backend/README.md
git commit -m "test: Verify CI/CD workflow"
git push

# El workflow se ejecutará automáticamente
```

---

## 🔒 Seguridad

**Después de configurar los secretos en GitHub**:

```bash
# IMPORTANTE: Borra la clave JSON de tu máquina local
rm ~/gcp-sa-key.json

# Verificar que se borró
ls ~/gcp-sa-key.json
# Debería decir: No such file or directory
```

La clave ahora está guardada de forma segura en GitHub (cifrada) y no necesitas el archivo local.

---

## 🎯 Resumen de Valores

Para tu referencia rápida:

| Secreto | Valor |
|---------|-------|
| `GCP_SA_KEY` | Contenido completo de `~/gcp-sa-key.json` |
| `DB_ADMIN_PASSWORD` | `4v6bZ5FYrGCQuWo+HiOZDEBUNSzBMI9O65NiS8XNNog=` |
| `PULUMI_ACCESS_TOKEN` | Obtener de https://app.pulumi.com/ |

---

## ❓ Problemas Comunes

### Error: "Error fetching credentials"
- Verifica que copiaste **TODO** el JSON (debe empezar con `{` y terminar con `}`)
- No debe tener espacios en blanco al inicio o final

### Error: "password authentication failed"  
- Verifica que copiaste el password completo, incluyendo el `=` al final
- Asegúrate de no agregar espacios accidentalmente

### Error: "failed to login: invalid access token"
- Verifica que el token de Pulumi fue copiado correctamente
- Genera un nuevo token si es necesario

---

## 🎉 ¡Listo!

Una vez configurados los 3 secretos, tus workflows de CI/CD funcionarán automáticamente:

- ✅ Cambios en `backend/` → Deploy automático del backend
- ✅ Cambios en `frontend/` → Deploy automático del frontend  
- ✅ Cambios en `infrastructure-gcp-*` → Deploy automático de infraestructura

**Tiempo total**: ~5 minutos
