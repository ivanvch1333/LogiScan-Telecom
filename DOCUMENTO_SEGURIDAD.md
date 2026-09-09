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
5. [Mecanismo de Bloqueo Progresivo de Cuentas](#5-mecanismo-de-bloqueo-progresivo-de-cuentas)
   - 5.1 Política de Umbrales y Tiempos de Bloqueo
   - 5.2 Evidencia en Backend (FastAPI): Endpoint de Login con Bloqueo
   - 5.3 Evidencia en Modelo de Datos: Campos de Control
   - 5.4 Evidencia en Frontend: Mensajes de Advertencia Profesional
   - 5.5 Evidencia Visual en Funcionamiento (Capturas)
6. [Bitácora de Auditoría y Logs del Sistema](#6-bitácora-de-auditoría-y-logs-del-sistema)
   - 6.1 Modelo de Datos: Tabla `logs_sistema`
   - 6.2 Función de Registro de Eventos (`registrar_log`)
   - 6.3 Endpoint REST de Consulta (`GET /api/logs`)
   - 6.4 Eventos Registrados por el Sistema
   - 6.5 Evidencia en Frontend: Módulo de Auditoría (Admin)
   - 6.6 Evidencia Visual en Funcionamiento (Capturas)
7. [Mitigación de Vulnerabilidades OWASP Top 10](#7-mitigación-de-vulnerabilidades-owasp-top-10)
   - 7.1 Prevención de Inyección SQL (ORM)
   - 7.2 Protección Cross-Origin (CORS Middleware)
   - 7.3 Sanitización y Seguridad en Carga de Archivos
   - 7.4 Evidencia Visual en Funcionamiento (Capturas)
8. [Matriz Resumen de Evidencias de Código Fuente](#8-matriz-resumen-de-evidencias-de-código-fuente)

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

# 5. MECANISMO DE BLOQUEO PROGRESIVO DE CUENTAS

El sistema implementa un mecanismo de **bloqueo temporal escalonado** que protege contra ataques de fuerza bruta y accesos no autorizados. El esquema de bloqueo incrementa progresivamente el tiempo de suspensión de la cuenta conforme aumentan los intentos fallidos.

## 5.1 Política de Umbrales y Tiempos de Bloqueo

| Intentos Fallidos | Acción del Sistema | Duración del Bloqueo |
|:-----------------:|:-------------------|:--------------------:|
| 1–2 | Mensaje de advertencia con conteo regresivo (`"Intento X de 3 antes de bloqueo temporal"`) | Sin bloqueo |
| 3 | Bloqueo temporal de la cuenta | **3 minutos** |
| 5 | Bloqueo temporal de la cuenta (incremento) | **10 minutos** |
| 10+ | Bloqueo temporal de la cuenta (máximo) | **60 minutos** |

> [!IMPORTANT]
> Al iniciar sesión correctamente, el contador de intentos fallidos se resetea a **0** y el bloqueo se desactiva inmediatamente. Esto permite al usuario legítimo operar sin penalización residual.

## 5.2 Evidencia en Backend (FastAPI): Endpoint de Login con Bloqueo

Ubicación: [`app/main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L230-L302)

```python
@app.post("/api/usuarios/login", response_model=schemas.Token)
def login(credentials: schemas.UsuarioLogin, request: Request, db: Session = Depends(get_db)):
    """Inicia sesión con control de bloqueo progresivo por intentos fallidos."""
    ip = request.client.host if request.client else "127.0.0.1"
    now = datetime.now(timezone.utc)

    user = db.query(models.Usuario).filter(models.Usuario.username == credentials.username).first()

    if user:
        # Verificar si la cuenta se encuentra bloqueada temporalmente
        if user.bloqueado_hasta and user.bloqueado_hasta > now:
            tiempo_restante = user.bloqueado_hasta - now
            minutos = int(tiempo_restante.total_seconds() // 60)
            segundos = int(tiempo_restante.total_seconds() % 60)
            msg_tiempo = f"{minutos} min {segundos} seg" if minutos > 0 else f"{segundos} segundos"
            
            detalle_err = f"Cuenta congelada por intentos fallidos. Intente nuevamente en {msg_tiempo}."
            registrar_log(db, user.username, models.NivelLog.CRITICAL, "ACCESO_BLOQUEADO",
                f"Intento de ingreso a cuenta bloqueada ({user.username}). Tiempo restante: {msg_tiempo}", ip)
            raise HTTPException(status_code=401, detail=detalle_err)

        # Si la contraseña es incorrecta
        if not security.verify_password(credentials.password, user.hashed_password):
            user.intentos_fallidos += 1
            
            # Umbrales de bloqueo: 3 intentos -> 3 min, 5 intentos -> 10 min, 10 intentos -> 60 min
            minutos_bloqueo = 0
            if user.intentos_fallidos >= 10:
                minutos_bloqueo = 60
            elif user.intentos_fallidos >= 5:
                minutos_bloqueo = 10
            elif user.intentos_fallidos >= 3:
                minutos_bloqueo = 3

            if minutos_bloqueo > 0:
                user.bloqueado_hasta = now + timedelta(minutes=minutos_bloqueo)
                db.commit()
                detalle_err = f"Acceso denegado. Se han registrado {user.intentos_fallidos} intentos fallidos. Cuenta bloqueada por {minutos_bloqueo} minutos."
                registrar_log(db, user.username, models.NivelLog.CRITICAL, "BLOQUEO_CUENTA",
                    f"Cuenta de '{user.username}' bloqueada por {minutos_bloqueo} minutos ({user.intentos_fallidos} intentos fallidos)", ip)
            else:
                db.commit()
                detalle_err = f"Usuario o contraseña incorrectos. Intento {user.intentos_fallidos} de 3 antes de bloqueo temporal."
                registrar_log(db, user.username, models.NivelLog.WARNING, "LOGIN_FALLIDO",
                    f"Intento fallido #{user.intentos_fallidos} para usuario '{user.username}'", ip)

            raise HTTPException(status_code=401, detail=detalle_err)

        # Contraseña correcta: Resetear contador de fallos y desbloquear
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        db.commit()

        access_token = security.create_access_token(data={"sub": user.username, "rol": user.rol.value})
        registrar_log(db, user.username, models.NivelLog.INFO, "LOGIN_EXITOSO",
            f"Inicio de sesión exitoso de '{user.username}' ({user.rol.value})", ip)
        return {"access_token": access_token, "token_type": "bearer"}
```

## 5.3 Evidencia en Modelo de Datos: Campos de Control

Ubicación: [`app/models.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/models.py#L59-L72)

La tabla `usuarios` incluye dos columnas dedicadas al control de bloqueo:

```python
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.TECNICO)
    intentos_fallidos = Column(Integer, default=0, nullable=False)        # ← Contador de fallos
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)      # ← Timestamp de desbloqueo
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
```

## 5.4 Evidencia en Frontend: Mensajes de Advertencia Profesional

Ubicación: [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L175-L215)

Los mensajes de error del servidor se muestran directamente dentro del formulario de login, en un panel profesional con icono de alerta (`🚨`), estilo visual coherente y sin recurrir a alertas nativas del navegador:

```javascript
} catch (err) {
    const msg = err.message || 'Error al iniciar sesión';
    errorEl.innerHTML = `<div class="flex items-start gap-2 text-left">
        <span class="text-base leading-none mt-0.5">🚨</span>
        <div class="flex-1">${msg}</div>
    </div>`;
    errorEl.classList.remove('hidden');
    errorEl.classList.add('block');
}
```

Ubicación HTML: [`static/index.html`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/index.html#L60)

```html
<div id="login-error" class="login-error text-red-400 bg-red-500/10 border border-red-500/20
     text-xs p-3 rounded-lg mb-4 text-center hidden"></div>
```

Los mensajes visibles al usuario incluyen:

| Escenario | Mensaje Profesional en UI |
|-----------|---------------------------|
| Campos vacíos | `⚠️ Ingrese su usuario y contraseña` |
| Intento fallido (antes del bloqueo) | `Usuario o contraseña incorrectos. Intento X de 3 antes de bloqueo temporal.` |
| Bloqueo activado | `Acceso denegado. Se han registrado X intentos fallidos. Cuenta bloqueada por Y minutos.` |
| Cuenta ya bloqueada | `Cuenta congelada por intentos fallidos. Intente nuevamente en X min Y seg.` |

## 5.5 Evidencia Visual en Funcionamiento (Capturas)

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 5: Advertencia de Intento Fallido (Pre-Bloqueo)**  
> *(Insertar captura de la pantalla de login mostrando el mensaje de advertencia tras el primer o segundo intento fallido, dentro del panel rojo integrado al formulario)*  
> `![Evidencia Intento Fallido](evidencias/05_intento_fallido.png)`

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 6: Cuenta Bloqueada por 3 Minutos (3 Intentos)**  
> *(Insertar captura tras el tercer intento fallido, mostrando el mensaje de bloqueo temporal de 3 minutos)*  
> `![Evidencia Bloqueo 3min](evidencias/06_bloqueo_3min.png)`

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 7: Cuenta Congelada con Tiempo Restante**  
> *(Insertar captura al intentar iniciar sesión durante el periodo de bloqueo, mostrando el tiempo restante exacto)*  
> `![Evidencia Cuenta Congelada](evidencias/07_cuenta_congelada.png)`

---

# 6. BITÁCORA DE AUDITORÍA Y LOGS DEL SISTEMA

El sistema mantiene una **bitácora persistente de auditoría** que registra automáticamente todos los eventos relevantes de seguridad, operación y administración. Los registros son inmutables y consultables exclusivamente por usuarios con rol **Administrador**.

## 6.1 Modelo de Datos: Tabla `logs_sistema`

Ubicación: [`app/models.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/models.py#L123-L132)

```python
class NivelLog(str, enum.Enum):
    INFO = "INFO"           # Operaciones normales exitosas
    WARNING = "WARNING"     # Advertencias y fallos recuperables
    CRITICAL = "CRITICAL"   # Bloqueos de cuenta, alertas de seguridad

class LogSistema(Base):
    __tablename__ = "logs_sistema"

    id = Column(Integer, primary_key=True, index=True)
    usuario_username = Column(String(50), nullable=True, index=True)
    nivel = Column(Enum(NivelLog), default=NivelLog.INFO, nullable=False)
    accion = Column(String(100), nullable=False, index=True)
    detalle = Column(Text, nullable=False)
    ip_origen = Column(String(50), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
```

## 6.2 Función de Registro de Eventos (`registrar_log`)

Ubicación: [`app/main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L45-L66)

```python
def registrar_log(
    db: Session,
    usuario_username: Optional[str],
    nivel: models.NivelLog,
    accion: str,
    detalle: str,
    ip_origen: Optional[str] = None
):
    """Registra una entrada en la bitácora de auditoría de seguridad del sistema."""
    try:
        nuevo_log = models.LogSistema(
            usuario_username=usuario_username,
            nivel=nivel,
            accion=accion,
            detalle=detalle,
            ip_origen=ip_origen
        )
        db.add(nuevo_log)
        db.commit()
    except Exception as e:
        print(f"[ERROR LOG] No se pudo guardar el log: {e}")
        db.rollback()
```

## 6.3 Endpoint REST de Consulta (`GET /api/logs`)

Ubicación: [`app/main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L604-L621)

```python
@app.get("/api/logs", response_model=List[schemas.LogResponse])
def listar_logs_sistema(
    nivel: Optional[models.NivelLog] = None,
    buscar: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Consulta la bitácora de auditoría y eventos de seguridad. Solo administradores."""
    query = db.query(models.LogSistema)
    if nivel:
        query = query.filter(models.LogSistema.nivel == nivel)
    if buscar:
        query = query.filter(
            (models.LogSistema.usuario_username.ilike(f"%{buscar}%")) |
            (models.LogSistema.accion.ilike(f"%{buscar}%")) |
            (models.LogSistema.detalle.ilike(f"%{buscar}%"))
        )
    return query.order_by(models.LogSistema.fecha.desc()).limit(200).all()
```

> [!IMPORTANT]
> Este endpoint está protegido por la dependencia `get_current_admin`, por lo que **solo los usuarios con rol Administrador** pueden consultar la bitácora. Los usuarios con rol Técnico recibirán un error `403 Forbidden`.

## 6.4 Eventos Registrados por el Sistema

La siguiente tabla resume todos los tipos de eventos que el sistema registra automáticamente en la bitácora:

| Código de Acción | Nivel | Descripción del Evento |
|:-----------------:|:-----:|:-----------------------|
| `LOGIN_EXITOSO` | INFO | Inicio de sesión exitoso de un usuario autenticado |
| `LOGIN_FALLIDO` | WARNING | Intento de login con contraseña incorrecta (pre-bloqueo) |
| `LOGIN_USUARIO_INEXISTENTE` | WARNING | Intento de login con un nombre de usuario que no existe en la BD |
| `BLOQUEO_CUENTA` | CRITICAL | Cuenta bloqueada temporalmente por alcanzar el umbral de intentos fallidos |
| `ACCESO_BLOQUEADO` | CRITICAL | Intento de acceso a una cuenta que ya se encuentra en estado de bloqueo |
| `USUARIO_CREADO` | INFO | Un administrador registró un nuevo usuario en el sistema |
| `USUARIO_ELIMINADO` | WARNING | Un administrador eliminó un usuario existente |
| `ROL_ACTUALIZADO` | INFO | Un administrador cambió el rol de un usuario (Admin ↔ Técnico) |
| `REGISTRO_FALLIDO` | WARNING | Intento de registrar un usuario con username o email duplicado |
| `EQUIPO_REGISTRADO` | INFO | Se registró un nuevo equipo/activo en el inventario |
| `MOVIMIENTO_REGISTRADO` | INFO | Se registró un traslado, instalación o retiro de un equipo |
| `CONFIGURACION_ACTUALIZADA` | INFO | Se actualizó la configuración de marca (logo, banner, nombre) |
| `SUPERUSUARIO_SEMBRADO` | INFO | El sistema creó automáticamente el superusuario por defecto |

## 6.5 Evidencia en Frontend: Módulo de Auditoría (Admin)

Ubicación: [`static/index.html`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/index.html#L454-L491) y [`static/app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L961-L999)

El módulo **📜 Logs del Sistema** es accesible exclusivamente desde el menú lateral del Administrador y presenta:

* **Tabla de Auditoría:** Columnas de Fecha/Hora, Usuario, Nivel (badge con color), Acción (código técnico), Detalle del Evento e IP de Origen.
* **Filtros en Tiempo Real:** Búsqueda por texto libre (usuario, acción o detalle) y filtro por nivel (INFO, WARNING, CRITICAL).
* **Límite de Consulta:** Se muestran las últimas 200 entradas ordenadas por fecha descendente.

```javascript
async function loadLogs() {
    try {
        APP.logs = await api('GET', '/api/logs') || [];
    } catch { APP.logs = []; }
    renderLogsTable(APP.logs);
}
```

Navegación en sidebar (exclusiva Admin):
```javascript
if (isAdmin) {
    html += `
        <div class="nav-section-label">Administración</div>
        <div class="nav-item" data-section="usuarios" onclick="navigateTo('usuarios')">
            <span class="nav-icon">👥</span> Usuarios
        </div>
        <div class="nav-item" data-section="logs" onclick="navigateTo('logs')">
            <span class="nav-icon">📜</span> Logs del Sistema
        </div>
        <div class="nav-item" data-section="ajustes" onclick="navigateTo('ajustes')">
            <span class="nav-icon">⚙️</span> Ajustes
        </div>
    `;
}
```

## 6.6 Evidencia Visual en Funcionamiento (Capturas)

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 8: Módulo de Logs del Sistema con Eventos de Seguridad**  
> *(Insertar captura del módulo de Logs mostrando eventos INFO, WARNING y CRITICAL registrados, con la tabla de auditoría y los filtros activos)*  
> `![Evidencia Logs Sistema](evidencias/08_logs_sistema.png)`

> [!NOTE]
> **EVIDENCIA FOTOGRÁFICA 9: Filtro de Logs por Nivel CRITICAL (Bloqueos de Cuenta)**  
> *(Insertar captura filtrando por nivel CRITICAL donde se observen los eventos BLOQUEO_CUENTA y ACCESO_BLOQUEADO con la IP de origen)*  
> `![Evidencia Logs Critical](evidencias/09_logs_critical.png)`

---

# 7. MITIGACIÓN DE VULNERABILIDADES OWASP TOP 10

## 7.1 Evidencia Visual en Funcionamiento (Capturas)

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

# 8. MATRIZ RESUMEN DE EVIDENCIAS DE CÓDIGO FUENTE

| Característica de Seguridad | Mecanismo Implementado | Archivo de Código Evidencia |
|-----------------------------|-----------------------|-----------------------------|
| **Control de Acceso (RBAC)** | Middleware exclusivo Admin | [`AdminMiddleware.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Middleware/AdminMiddleware.php) |
| **Protección de Rutas REST** | Middleware Admin en grupos API | [`api.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/routes/api.php#L26-L32) |
| **Validación de Contraseñas** | Regex de 8+ caracteres, mayúscula, número y especial | [`schemas.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/schemas.py#L25-L36) |
| **Hashing de Contraseñas** | Encriptación Bcrypt | [`security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L22) |
| **Autenticación Token Bearer** | Tokens JWT con expiración y firma secreta | [`security.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/security.py#L44-L55) |
| **Bloqueo Progresivo de Cuentas** | 3→3min, 5→10min, 10→60min con campos `intentos_fallidos` y `bloqueado_hasta` | [`main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L230-L302) |
| **Bitácora de Auditoría** | Tabla `logs_sistema` con niveles INFO/WARNING/CRITICAL y 13 tipos de eventos | [`models.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/models.py#L123-L132) |
| **Endpoint de Auditoría (Admin)** | `GET /api/logs` con filtros por nivel y búsqueda textual | [`main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L604-L621) |
| **Función de Registro de Logs** | `registrar_log()` con 15+ puntos de invocación en el backend | [`main.py`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/app/main.py#L45-L66) |
| **Protección Inyección SQL** | Prepared Statements con Eloquent / SQLAlchemy | [`EquipoController.php`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/laravel/app/Http/Controllers/EquipoController.php#L18-L34) |
| **Gestión de Sesión Cliente** | Interceptor Fetch HTTP con Bearer Token y Auto-logout en 401 | [`app.js`](file:///c:/Users/ASUS/Documents/ISTE/Proyectos%20web/teletrack_qr/static/app.js#L54-L77) |
