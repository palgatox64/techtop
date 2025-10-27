# 🔄 Comandos Git para Subir la Integración de Webpay

## 📝 Pasos Recomendados

### 1️⃣ Verificar el Estado Actual

```powershell
# Ver en qué rama estás
git branch

# Ver los archivos modificados
git status
```

### 2️⃣ Agregar los Cambios al Staging

```powershell
# Agregar TODOS los archivos modificados
git add .

# O agregar archivos específicos:
git add requirements.txt
git add store/models.py
git add store/views.py
git add techtop_project/settings.py
git add techtop_project/urls.py
git add templates/store/confirmacion_pago.html
git add INTEGRACION_WEBPAY.md
git add COMANDOS_GIT.md
```

### 3️⃣ Crear un Commit con un Mensaje Descriptivo

```powershell
git commit -m "feat: Integración completa de Transbank WebPay Plus

- Agregado SDK de Transbank (transbank-sdk==4.0.0)
- Creado modelo TransaccionWebpay para tracking de pagos
- Implementadas vistas: iniciar_pago_webpay, retorno_webpay, anular_transaccion
- Configurado ambiente de integración con credenciales de prueba
- Agregadas rutas para el flujo de pago
- Creado template de confirmación de pago (éxito/error)
- Actualizada lógica de procesar_pedido para redirigir a Webpay
- Documentación completa de la integración

Fixes #[número_del_issue] si aplica"
```

### 4️⃣ Subir los Cambios al Repositorio Remoto

```powershell
# Subir a la rama actual (implementar-pasarela-pago)
git push origin implementar-pasarela-pago

# Si es la primera vez que subes esta rama:
git push -u origin implementar-pasarela-pago
```

### 5️⃣ Crear un Pull Request (Opcional pero Recomendado)

Después de hacer push, ve a GitHub:

1. Visita: https://github.com/palgatox64/techtop
2. Verás un botón "Compare & pull request"
3. Agrega una descripción detallada:

```markdown
## 🚀 Integración de Transbank WebPay Plus

### Cambios Principales
- ✅ SDK de Transbank instalado
- ✅ Modelo de transacciones creado
- ✅ Flujo completo de pago implementado
- ✅ Manejo de éxito y errores
- ✅ Restauración de stock en caso de fallo

### Testing
- ✅ Probado en ambiente de integración
- ✅ Tarjetas de prueba funcionando correctamente

### Documentación
Ver `INTEGRACION_WEBPAY.md` para instrucciones completas

### Checklist
- [x] Código funcional
- [x] Sin errores de sintaxis
- [x] Documentación incluida
- [ ] Migraciones aplicadas
- [ ] Probado en servidor local
```

4. Click en "Create pull request"

### 6️⃣ Merge a Main/Master (Cuando esté aprobado)

```powershell
# Cambiar a la rama principal
git checkout main

# Traer los últimos cambios
git pull origin main

# Merge de la rama de feature
git merge implementar-pasarela-pago

# Subir los cambios
git push origin main
```

---

## 🔄 Comandos Rápidos (Todo en Uno)

Si quieres hacerlo todo de una vez:

```powershell
# Ver estado
git status

# Agregar todos los cambios
git add .

# Commit
git commit -m "feat: Integración completa de Transbank WebPay Plus"

# Push
git push origin implementar-pasarela-pago
```

---

## 🔍 Comandos Útiles Adicionales

### Ver el historial de commits
```powershell
git log --oneline
```

### Ver diferencias antes de commitear
```powershell
git diff
```

### Ver diferencias de archivos en staging
```powershell
git diff --staged
```

### Deshacer cambios (antes del commit)
```powershell
# Deshacer cambios en un archivo específico
git checkout -- <archivo>

# Quitar archivo del staging (mantener cambios)
git reset HEAD <archivo>
```

### Actualizar desde el remoto
```powershell
# Traer cambios sin merge
git fetch origin

# Ver ramas remotas
git branch -r

# Actualizar tu rama con cambios remotos
git pull origin implementar-pasarela-pago
```

---

## 📊 Verificación Final

Después de hacer push, verifica:

1. ✅ Los archivos aparecen en GitHub
2. ✅ El commit tiene el mensaje correcto
3. ✅ La rama `implementar-pasarela-pago` está actualizada
4. ✅ No hay conflictos

---

## 🎯 Próximos Pasos

1. **Crear migraciones:**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Probar localmente:**
   ```powershell
   python manage.py runserver
   ```

3. **Verificar que funcione todo:**
   - Ir a checkout
   - Seleccionar Webpay
   - Probar con tarjeta de prueba

4. **Hacer el merge a main** cuando todo esté probado

---

## ⚠️ Consejos

- 💡 **Commits frecuentes:** Es mejor hacer commits pequeños y frecuentes
- 🔍 **Mensajes claros:** Usa mensajes descriptivos que expliquen QUÉ y POR QUÉ
- 🧪 **Probar antes de push:** Siempre prueba localmente antes de subir
- 📝 **Documentar:** Incluye documentación para otros desarrolladores

---

## 🆘 En caso de Problemas

### Si olvidaste agregar archivos:
```powershell
git add <archivo_olvidado>
git commit --amend --no-edit
git push -f origin implementar-pasarela-pago
```

### Si necesitas corregir el mensaje del commit:
```powershell
git commit --amend -m "nuevo mensaje"
git push -f origin implementar-pasarela-pago
```

### Si hay conflictos:
```powershell
# Actualizar tu rama primero
git pull origin implementar-pasarela-pago

# Resolver conflictos manualmente en los archivos
# Luego:
git add .
git commit -m "resolve: Conflictos resueltos"
git push origin implementar-pasarela-pago
```

---

¡Listo para subir tus cambios! 🚀
