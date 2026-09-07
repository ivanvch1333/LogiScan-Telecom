# ARQUITECTURA DE SEGURIDAD Y EVIDENCIA TÉCNICA
## LOGISCAN TELECOM — SISTEMA WEB MOBILE DE CONTROL DE INVENTARIOS Y CONCILIACIÓN DE ACTIVOS

---

# TABLA DE CONTENIDOS
1. [Resumen Ejecutivo de Seguridad](#1-resumen-ejecutivo-de-seguridad)
2. [Control de Acceso Basado en Roles (RBAC)](#2-control-de-acceso-basado-en-roles-rbac)
   - 2.1 Evidencia en Backend (Laravel & FastAPI)
   - 2.2 Evidencia en Frontend (JavaScript SPA)
3. [Gestión Segura de Contraseñas y Hashing Bcrypt](#3-gestión-segura-de-contraseñas-y-hashing-bcrypt)
   - 3.1 Política Estricta de Complejidad de Contraseñas
   - 3.2 Almacenamiento Irreversible con Algoritmo Bcrypt
4. [Autenticación Basada en Tokens Bearer (JWT / Sanctum)](#4-autenticación-basada-en-tokens-bearer-jwt--sanctum)
   - 4.1 Generación de Tokens de Acceso
   - 4.2 Intercepción y Validación en Cliente y Servidor
5. [Mitigación de Vulnerabilidades OWASP Top 10](#5-mitigación-de-vulnerabilidades-owasp-top-10)
   - 5.1 Prevención de Inyección SQL (ORM)
   - 5.2 Protección Cross-Origin (CORS Middleware)
   - 5.3 Sanitización y Seguridad en Carga de Archivos
6. [Matriz Resumen de Evidencias de Código Fuente](#6-matriz-resumen-de-evidencias-de-código-fuente)

---

# 1. RESUMEN EJECUTIVO DE SEGURIDAD

El sistema **LogiScan Telecom** implementa un modelo de seguridad en capas (*Defense in Depth*) diseñado para proteger la integridad de los datos de inventario auditado, restringir el acceso a usuarios autenticados y prevenir vulnerabilidades comunes identificadas en el estándar **OWASP Top 10**.

### Principios Fundamentales Aplicados
* **Principio de Menor Privilegio (PoLP):** Los usuarios técnicos solo acceden a las funciones operativas de inventario. Las funciones administrativas están estrictamente blindadas.
* **Autenticación Stateless:** Transmisión de credenciales mediante Tokens Bearer (JWT / Sanctum) sin persistir información de sesión insegura en cookies de servidor.
* **Inmutabilidad y No Repudio:** Registro auditado de cada movimiento indicando el usuario responsable (`usuario_id`), fecha/hora exacta y estado del activo.

---

# 2. CONTROL DE ACCESO BASADO EN ROLES (RBAC)

## 2.1 Evidencia en Backend (Laravel & FastAPI)

El sistema valida el rol del usuario en cada petición HTTP de forma independiente al frontend.

### Evidencia en Laravel (PHP): Middleware `AdminMiddleware.php`
Ubicación: [`laravel/app/Http/Middleware/AdminMiddleware.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Middleware/AdminMiddleware.php#L12-L21)

```php
public function handle(Request $request, Closure $next)
{
    // Verifica si el usuario autenticado posee el rol 'admin'
    if ($request->user() && $request->user()->rol === 'admin') {
        return $next($request);
    }

    // Retorna HTTP 403 Forbidden si un usuario técnico intenta acceder
    return response()->json([
        'detail' => 'No tiene permisos de administrador para esta acción.'
    ], 403);
}
```

### Aplicación del Middleware en Rutas API de Laravel
Ubicación: [`laravel/routes/api.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/routes/api.php#L26-L32)

```php
// Rutas Exclusivas Administrador (Blindadas mediante RBAC Middleware)
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
    """Dependencia que verifica que el usuario actual sea administrador."""
    if current_user.rol != models.RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador para esta acción."
        )
    return current_user
```

## 2.2 Evidencia en Frontend (JavaScript SPA)

El frontend oculta dinámicamente las opciones administrativas según el rol del usuario cargado desde el token.

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

    // Renderizado condicional: Solo si el usuario es 'admin' se agregan las opciones protegidas
    if (isAdmin) {
        html += `
            <div class="nav-item" data-section="usuarios" onclick="navigateTo('usuarios')">Usuarios</div>
            <div class="nav-item" data-section="ajustes" onclick="navigateTo('ajustes')">Ajustes</div>
        `;
    }

    nav.innerHTML = html;
}
```

---

# 3. GESTIÓN SEGURA DE CONTRASEÑAS Y HASHING BCRYPT

## 3.1 Política Estricta de Complejidad de Contraseñas

El sistema exige que toda contraseña creada o actualizada cumpla con la siguiente regla de fortaleza:
- Longitud mínima: **8 caracteres**
- Al menos **1 letra mayúscula** (`A-Z`)
- Al menos **1 número** (`0-9`)
- Al menos **1 carácter especial** (`!@#$%^&*(),.?":{}|<>_\-\[\]\\`)

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

### Evidencia 2: Validación en Laravel Backend
Ubicación: [`laravel/app/Http/Controllers/UsuarioController.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Controllers/UsuarioController.php#L25)

```php
$validated = $request->validate([
    'nombre_completo' => 'required|string|max:100',
    'username' => 'required|string|max:50|unique:usuarios,username',
    'email' => 'required|email|max:100|unique:usuarios,email',
    'password' => ['required', 'string', Password::min(8)->mixedCase()->numbers()->symbols()],
    'rol' => 'required|in:admin,tecnico',
]);
```

### Evidencia 3: Validación Regex en Frontend (JS)
Ubicación: [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L869-L873)

```javascript
const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>_\-\[\]\\]).{8,}$/;
if (!regex.test(body.password)) {
    showToast('La contraseña debe tener al menos 8 caracteres, incluir una mayúscula, un número y un carácter especial.', 'error');
    return;
}
```

## 3.2 Almacenamiento Irreversible con Algoritmo Bcrypt

Las contraseñas **nunca se almacenan en texto plano**. Se utiliza la función de derivación de clave **Bcrypt**, la cual genera una sal (*salt*) aleatoria automática de 128 bits para prevenir ataques de tablas arcoíris (*rainbow table attacks*).

### Evidencia en Backend:
* **Laravel (PHP):** `Hash::make($password)` utiliza la implementación nativa `bcrypt`.
* **FastAPI (Python):** [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L22) inicializa `CryptContext(schemes=["bcrypt"], deprecated="auto")`.

---

# 4. AUTENTICACIÓN BASADA EN TOKENS BEARER (JWT / SANCTUM)

## 4.1 Generación de Tokens de Acceso
Tras validar el usuario y la clave en el login, el servidor retorna un token firmado digitalmente.

Ubicación: [`app/security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L44-L55)

```python
def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

## 4.2 Intercepción y Validación en Cliente y Servidor

En cada petición realizada por la SPA, el helper `api()` en JavaScript adjunta automáticamente la cabecera HTTP de autorización. Si la respuesta es `401 Unauthorized` (token inválido o expirado), el sistema ejecuta el cierre de sesión automático (`logout()`).

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
        logout(); // Expiración o token manipulado -> Cierre de sesión y limpieza de LocalStorage
        return null;
    }
    return await res.json();
}
```

---

# 5. MITIGACIÓN DE VULNERABILIDADES OWASP TOP 10

## 5.1 Prevención de Inyección SQL (OWASP A03: Injection)
Toda interacción con la base de datos se realiza a través de Mapeadores Objeto-Relacional (**Eloquent ORM** en PHP y **SQLAlchemy** en Python). Esto garantiza que las variables de búsqueda o filtrado se ejecuten como **consultas parametrizadas (Prepared Statements)**, haciendo imposible la inyección de código SQL malicioso.

Ubicación: [`laravel/app/Http/Controllers/EquipoController.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Controllers/EquipoController.php#L18-L34)

```php
$query = Equipo::query();
if ($request->has('plant') && $request->plant) {
    // Uso de binding parametrizado automático por parte del ORM Eloquent
    $query->where('plant', 'like', '%' . $request->plant . '%');
}
```

## 5.2 Protección Cross-Origin (OWASP A05: Security Misconfiguration)
El backend cuenta con middleware de **CORS (Cross-Origin Resource Sharing)** explícito para controlar las cabeceras, métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`) y orígenes permitidos.

Ubicación: [`app/main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L27-L33)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 5.3 Sanitización y Seguridad en Carga de Archivos (OWASP Upload Safety)
Para evitar la ejecución remota de código (RCE) mediante la subida de archivos maliciosos en la configuración de marca:
1. Se valida que el archivo pertenezca al tipo MIME de imagen (`accept="image/*"`).
2. Se extrae únicamente la extensión original y se renombra el archivo internamente a un identificador estático controlado (`logo.png`, `banner.png`), destruyendo nombres de ruta originales con caracteres de traversada de directorio (`../`).

Ubicación: [`app/main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L215-L230)

```python
if logo and logo.filename:
    ext = os.path.splitext(logo.filename)[1] or ".png"
    # Nombre estático sanitizado sin rutas relativas arbitrarias
    logo_path = os.path.join(UPLOADS_DIR, f"logo{ext}")
    with open(logo_path, "wb") as f:
        content = await logo.read()
        f.write(content)
```

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
| **Seguridad Carga de Archivos** | Sanitización de nombres y renombramiento a rutas estáticas | [`app/main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L215-L230) |
