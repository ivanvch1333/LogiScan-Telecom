# ARQUITECTURA DE SEGURIDAD Y EVIDENCIA TÉCNICA
## LOGISCAN TELECOM — SISTEMA WEB MOBILE DE CONTROL DE INVENTARIOS Y CONCILIACIÓN DE ACTIVOS

---

# TABLA DE CONTENIDOS
1. [Resumen Ejecutivo de Seguridad](#1-resumen-ejecutivo-de-seguridad)
2. [Control de Acceso Basado en Roles (RBAC)](#2-control-de-acceso-basado-en-roles-rbac)
   - 2.1 Evidencia en Backend (Laravel & FastAPI)
   - 2.2 Evidencia en Frontend (JavaScript SPA)
   - 2.3 Evidencia Visual en Funcionamiento (Capturas)
3. [Gestión Segura de Contraseñas y Hashing Bcrypt](#3-gestión-segura-de-contraseñas-y-hashing-bcrypt)
   - 3.1 Política Estricta de Complejidad de Contraseñas
   - 3.2 Almacenamiento Irreversible con Algoritmo Bcrypt
   - 3.3 Evidencia Visual en Funcionamiento (Capturas)
4. [Autenticación Basada en Tokens Bearer (JWT / Sanctum)](#4-autenticación-basada-en-tokens-bearer-jwt--sanctum)
   - 4.1 Generación de Tokens de Acceso
   - 4.2 Intercepción y Validación en Cliente y Servidor
   - 4.3 Evidencia Visual en Funcionamiento (Capturas)
5. [Mitigación de Vulnerabilidades OWASP Top 10](#5-mitigación-de-vulnerabilidades-owasp-top-10)
   - 5.1 Prevención de Inyección SQL (ORM)
   - 5.2 Protección Cross-Origin (CORS Middleware)
   - 5.3 Sanitización y Seguridad en Carga de Archivos
   - 5.4 Evidencia Visual en Funcionamiento (Capturas)
6. [Matriz Resumen de Evidencias de Código Fuente](#6-matriz-resumen-de-evidencias-de-código-fuente)

---

# 1. RESUMEN EJECUTIVO DE SEGURIDAD

El sistema **LogiScan Telecom** implementa un modelo de seguridad en capas (*Defense in Depth*) diseñado para proteger la integridad de los datos de inventario auditado, restringir el acceso a usuarios autenticados y prevenir vulnerabilidades comunes identificadas en el estándar **OWASP Top 10**.

---

# 2. CONTROL DE ACCESO BASADO EN ROLES (RBAC)

## 2.1 Evidencia en Backend (Laravel & FastAPI)

### Evidencia en Laravel (PHP): Middleware `AdminMiddleware.php`
Ubicación: [`laravel/app/Http/Middleware/AdminMiddleware.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Middleware/AdminMiddleware.php#L12-L21)

```php
public function handle(Request $request, Closure $next)
{
    if ($request->user() && $request->user()->rol === 'admin') {
        return $next($request);
    }

    return response()->json([
        'detail' => 'No tiene permisos de administrador para esta acción.'
    ], 403);
}
```

### Aplicación del Middleware en Rutas API de Laravel
Ubicación: [`laravel/routes/api.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/routes/api.php#L26-L32)

```php
Route::middleware('admin')->group(function () {
    Route::get('/usuarios', [UsuarioController::class, 'index']);
    Route::post('/usuarios/registro', [UsuarioController::class, 'store']);
    Route::put('/usuarios/{id}/rol', [UsuarioController::class, 'updateRol']);
    Route::delete('/usuarios/{id}', [UsuarioController::class, 'destroy']);
    Route::post('/config', [ConfigController::class, 'update']);
});
```

### Evidencia en FastAPI (Python): Dependencia `get_current_admin`
Ubicación: [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L83-L90)

```python
def get_current_admin(current_user: models.Usuario = Depends(get_current_user)) -> models.Usuario:
    if current_user.rol != models.RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador para esta acción."
        )
    return current_user
```

## 2.2 Evidencia en Frontend (JavaScript SPA)

Ubicación: [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L201-L226)

```javascript
function buildSidebar() {
    const nav = document.getElementById('sidebar-nav');
    const isAdmin = APP.user?.rol === 'admin';

    let html = `
        <div class="nav-item active" data-section="dashboard" onclick="navigateTo('dashboard')">Dashboard</div>
        <div class="nav-item" data-section="equipos" onclick="navigateTo('equipos')">Equipos</div>
        <div class="nav-item" data-section="movimientos" onclick="navigateTo('movimientos')">Movimientos</div>
        <div class="nav-item" data-section="busqueda-qr" onclick="navigateTo('busqueda-qr')">Lector QR</div>
    `;

    if (isAdmin) {
        html += `
            <div class="nav-item" data-section="usuarios" onclick="navigateTo('usuarios')">Usuarios</div>
            <div class="nav-item" data-section="ajustes" onclick="navigateTo('ajustes')">Ajustes</div>
        `;
    }

    nav.innerHTML = html;
}
```

## 2.3 Evidencia Visual en Funcionamiento (Capturas)

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 1: Vista de Menú Completo para Rol Administrador**  
> *(Insertar captura de pantalla de la aplicación iniciada con el usuario `ectronix_log_amb`, mostrando en el menú lateral las opciones exclusivas de **Usuarios** y **Ajustes**)*  
> `![Evidencia RBAC Admin](evidencias/01_rbac_admin.png)`

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 2: Vista de Menú Restringido para Rol Técnico**  
> *(Insertar captura de pantalla al iniciar sesión con un usuario de rol `Técnico`, verificando el ocultamiento automático de las pestañas de Usuarios y Ajustes)*  
> `![Evidencia RBAC Tecnico](evidencias/02_rbac_tecnico.png)`

---

# 3. GESTIÓN SEGURA DE CONTRASEÑAS Y HASHING BCRYPT

## 3.1 Política Estricta de Complejidad de Contraseñas

### Evidencia 1: Validación en Pydantic / Python Backend
Ubicación: [`app/schemas.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/schemas.py#L25-L36)

```python
@field_validator('password')
@classmethod
def validar_password(cls, v: str) -> str:
    if len(v) < 8:
        raise ValueError('La contraseña debe tener al menos 8 caracteres.')
    if not re.search(r'[A-Z]', v):
        raise ValueError('La contraseña debe incluir al menos una letra mayúscula.')
    if not re.search(r'[0-9]', v):
        raise ValueError('La contraseña debe incluir al menos un número.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\[\]\\]', v):
        raise ValueError('La contraseña debe incluir al menos un carácter especial.')
    return v
```

### Evidencia 2: Validación Regex en Frontend (JS)
Ubicación: [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L869-L873)

```javascript
const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>_\-\[\]\\]).{8,}$/;
if (!regex.test(body.password)) {
    showToast('La contraseña debe tener al menos 8 caracteres, incluir una mayúscula, un número y un carácter especial.', 'error');
    return;
}
```

## 3.2 Almacenamiento Irreversible con Algoritmo Bcrypt

* **FastAPI (Python):** [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L22) inicializa `CryptContext(schemes=["bcrypt"], deprecated="auto")`.
* **Laravel (PHP):** `Hash::make($password)` genera el hash seguro.

## 3.3 Evidencia Visual en Funcionamiento (Capturas)

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 3: Rechazo por Política de Contraseña Insegura**  
> *(Insertar captura intentando registrar un usuario con clave débil (ej: `123456`), donde se observe el mensaje flotante de rechazo)*  
> `![Evidencia Validacion Password](evidencias/03_validacion_password.png)`

---

# 4. AUTENTICACIÓN BASADA EN TOKENS BEARER (JWT / SANCTUM)

## 4.1 Generación de Tokens de Acceso
Ubicación: [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L44-L55)

```python
def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

## 4.2 Intercepción y Validación en Cliente
Ubicación: [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L54-L77)

```javascript
async function api(method, path, body = null, isFormData = false) {
    const headers = {};
    if (APP.token) headers['Authorization'] = `Bearer ${APP.token}`;
    if (!isFormData && body) headers['Content-Type'] = 'application/json';

    const opts = { method, headers };
    if (body) opts.body = isFormData ? body : JSON.stringify(body);

    const res = await fetch(path, opts);
    if (res.status === 401) {
        logout();
        return null;
    }
    return await res.json();
}
```

## 4.3 Evidencia Visual en Funcionamiento (Capturas)

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 4: Almacenamiento del Token Bearer en LocalStorage**  
> *(Insertar captura de las Herramientas de Desarrollador del Navegador (F12 -> Aplicación / Storage -> Local Storage) donde se observe la clave `teletrack_token` cargada)*  
> `![Evidencia Token Bearer](evidencias/04_token_storage.png)`

---

# 5. MITIGACIÓN DE VULNERABILIDADES OWASP TOP 10

## 5.1 Evidencia Visual en Funcionamiento (Capturas)

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 5: Conciliación de Activos e Inventario (Qty SAP - Qty EAIM)**  
> *(Insertar captura de la tabla de Equipos mostrando el cálculo dinámico de la columna Desviación)*  
> `![Evidencia Conciliacion](evidencias/05_conciliacion_desviacion.png)`

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 6: Trazabilidad de Instalaciones en Cliente**  
> *(Insertar captura del formulario de Movimiento seleccionando "Instalación Nodo" con los campos obligatorios de Cliente y Dirección)*  
> `![Evidencia Instalacion Cliente](evidencias/06_instalacion_cliente.png)`

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 7: Lector QR de Cámara Móvil Activo**  
> *(Insertar captura del módulo de Búsqueda QR mostrando el visor de cámara escaneando un código)*  
> `![Evidencia Escaner QR](evidencias/07_escaner_qr_camara.png)`

---

# 6. MATRIZ RESUMEN DE EVIDENCIAS DE CÓDIGO FUENTE

| Característica de Seguridad | Mecanismo Implementado | Archivo de Código Evidencia |
|-----------------------------|-----------------------|-----------------------------|
| **Control de Acceso (RBAC)** | Middleware exclusivo Admin | [`laravel/app/Http/Middleware/AdminMiddleware.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Middleware/AdminMiddleware.php) |
| **Protección de Rutas REST** | Middleware Admin en grupos API | [`laravel/routes/api.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/routes/api.php#L26-L32) |
| **Validación de Contraseñas** | Regex de 8+ caracteres, mayúscula, número y especial | [`app/schemas.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/schemas.py#L25-L36) |
| **Hashing de Contraseñas** | Encriptación Bcrypt | [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L22) |
| **Autenticación Token Bearer** | Tokens JWT con expiración y firma secreta | [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L44-L55) |
| **Protección Inyección SQL** | Prepared Statements con Eloquent / SQLAlchemy | [`laravel/app/Http/Controllers/EquipoController.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Controllers/EquipoController.php#L18-L34) |
| **Gestión de Sesión Cliente** | Interceptor Fetch HTTP con Bearer Token y Auto-logout en 401 | [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L54-L77) |
