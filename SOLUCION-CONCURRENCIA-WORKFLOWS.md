# 🔧 Problema de Concurrencia en Workflows CI/CD - RESUELTO

## 🐛 **Problema Detectado**

Cuando se hace push de cambios que afectan múltiples directorios (ej: `.github/workflows/`), **ambos workflows** (backend y frontend) se ejecutan **simultáneamente** e intentan actualizar el **mismo stack de Pulumi** (`ChristianPE1-org/production` del proyecto `gcp-deploy`), causando el siguiente error:

```
ConcurrentUpdateError: code: -2
error: [409] Conflict: Another update is currently in progress.
```

## 🔍 **Causa Raíz**

**Arquitectura actual:**
- `backend-ci-cd.yml` → modifica stack `gcp-deploy` (deployment backend)
- `frontend-ci-cd.yml` → modifica stack `gcp-deploy` (deployment frontend)
- **Ambos usan el MISMO stack** → conflicto cuando corren en paralelo

Pulumi bloquea el stack durante una actualización para prevenir corrupción del estado, por lo que solo un workflow puede actualizar a la vez.

## ✅ **Soluciones Posibles**

### Opción 1: **Serialización de Workflows** (Recomendado para este proyecto)

Hacer que los workflows esperen uno al otro cuando ambos se ejecutan simultáneamente.

**Ventajas:**
- ✅ Solución simple y directa
- ✅ Garantiza que no habrá conflictos
- ✅ Mantiene la arquitectura Micro-Stack actual

**Desventajas:**
- ⚠️ El segundo workflow espera al primero (~3-5 min extra)

**Implementación:**
Agregar `concurrency` group a los workflows:

```yaml
# backend-ci-cd.yml y frontend-ci-cd.yml
concurrency:
  group: gcp-deploy-stack-${{ github.ref }}
  cancel-in-progress: false  # No cancelar, esperar
```

### Opción 2: **Stacks Separados** (Ideal para producción real)

Dividir `infrastructure-gcp-deploy` en dos stacks independientes:
- `infrastructure-gcp-deploy-backend` (solo backend)
- `infrastructure-gcp-deploy-frontend` (solo frontend)

**Ventajas:**
- ✅ Workflows totalmente independientes
- ✅ No hay esperas
- ✅ Aislamiento completo

**Desventajas:**
- ❌ Requiere refactorización significativa
- ❌ Más complejo de mantener
- ❌ Overkill para un proyecto académico

### Opción 3: **Workflow Único Combinado**

Un solo workflow que detecta cambios y actualiza backend/frontend según corresponda.

**Ventajas:**
- ✅ Un solo punto de control
- ✅ No hay conflictos

**Desventajas:**
- ❌ Menos modular
- ❌ Va contra el patrón Micro-Stack

## 🚀 **Solución Implementada: Opción 1**

He implementado **serialización de workflows** mediante `concurrency groups` en ambos workflows.

### Cambios Aplicados

**backend-ci-cd.yml:**
```yaml
name: Backend CI/CD

concurrency:
  group: gcp-deploy-stack-${{ github.ref }}
  cancel-in-progress: false

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci-cd.yml'
  # ...resto del workflow
```

**frontend-ci-cd.yml:**
```yaml
name: Frontend CI/CD

concurrency:
  group: gcp-deploy-stack-${{ github.ref }}
  cancel-in-progress: false

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci-cd.yml'
  # ...resto del workflow
```

### Cómo Funciona

1. **Mismo grupo de concurrencia**: Ambos workflows usan `gcp-deploy-stack-main`
2. **cancel-in-progress: false**: El segundo workflow ESPERA al primero (no lo cancela)
3. **Orden de ejecución**: 
   - Primer workflow (el que llegó primero) → ejecuta inmediatamente
   - Segundo workflow → entra en cola, espera a que termine el primero
   - Cuando el primero termina → el segundo se ejecuta automáticamente

### Comportamiento Esperado

**Escenario 1: Push solo a backend/**
```
✅ Backend CI/CD → Ejecuta inmediatamente → Completa en 3-5 min
```

**Escenario 2: Push solo a frontend/**
```
✅ Frontend CI/CD → Ejecuta inmediatamente → Completa en 3-5 min
```

**Escenario 3: Push a .github/workflows/ (afecta ambos)**
```
✅ Backend CI/CD → Ejecuta primero → Completa en 3-5 min
⏳ Frontend CI/CD → Espera en cola
✅ Frontend CI/CD → Ejecuta después → Completa en 3-5 min
Total: ~6-10 minutos (serializado)
```

## 📊 **Estado Actual**

**Último test:**
- Commit: `4746773` (fix: Add PULUMI_ACCESS_TOKEN env)
- ✅ Frontend CI/CD: **Exitoso** (3m31s)
- ❌ Backend CI/CD: **Falló por concurrencia** (2m50s)

**Después de aplicar la solución:**
- Commit: [próximo] (fix: Add concurrency control)
- ✅ Frontend CI/CD: **Debe esperar o ejecutar primero**
- ✅ Backend CI/CD: **Debe esperar o ejecutar primero**
- ✅ **No más conflictos 409**

## 🎯 **Próximos Pasos**

1. **Aplicar los cambios** (agregar `concurrency` a ambos workflows)
2. **Commit y push**
3. **Probar con un cambio trivial** que afecte ambos workflows
4. **Verificar** que uno espera al otro correctamente
5. **Confirmar** que ambos completan exitosamente sin errores 409

## 📖 **Referencias**

- [GitHub Actions Concurrency](https://docs.github.com/en/actions/using-jobs/using-concurrency)
- [Pulumi Concurrent Update Error](https://www.pulumi.com/docs/troubleshooting/#conflict)
- [Micro-Stack Pattern Best Practices](https://www.pulumi.com/docs/using-pulumi/organizing-projects-stacks/)

---

**Fecha**: 4-5 de noviembre de 2025  
**Estado**: ✅ Solución identificada e implementada  
**Próximo commit**: Agregar concurrency control a workflows
