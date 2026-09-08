import os
import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, File, UploadFile, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import extract
import io
import qrcode

from app import models, schemas, security
from app.database import engine, get_db

# Crear las tablas en la base de datos automáticamente al iniciar la aplicación
models.Base.metadata.create_all(bind=engine)

# Instancia principal de FastAPI
app = FastAPI(
    title="LogiScan Telecom API",
    description="Sistema Web Mobile para el Control de Inventarios, Conciliación de Activos y Trazabilidad de Telecomunicaciones",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio de uploads
UPLOADS_DIR = os.path.join("static", "uploads")
CONFIG_FILE = os.path.join(UPLOADS_DIR, "config.json")


# ==========================================
# HELPER DE AUDITORÍA Y LOGS DEL SISTEMA
# ==========================================

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


# ==========================================
# SEMBRADO AUTOMÁTICO DEL SUPERUSUARIO
# ==========================================

def seed_superuser():
    """Crea el superusuario por defecto si la tabla de usuarios está vacía."""
    db = next(get_db())
    try:
        count = db.query(models.Usuario).count()
        if count == 0:
            hashed = security.get_password_hash("Macara@13")
            admin = models.Usuario(
                nombre_completo="Administrador Principal",
                username="ectronix_log_amb",
                email="admin@teletrack.com",
                hashed_password=hashed,
                rol=models.RolUsuario.ADMIN
            )
            db.add(admin)
            db.commit()
            registrar_log(db, "SISTEMA", models.NivelLog.INFO, "SUPERUSUARIO_SEMBRADO", "Superusuario ectronix_log_amb creado por defecto.")
            print("[OK] Superusuario creado: ectronix_log_amb / Macara@13")
    except Exception as e:
        print(f"[ERROR] Error al crear superusuario: {e}")
        db.rollback()
    finally:
        db.close()


def ensure_uploads_dir():
    """Crea el directorio de uploads y el config inicial si no existen."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        config = {"nombre_empresa": "LogiScan Telecom", "logo_url": None, "banner_url": None}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)


@app.on_event("startup")
def startup_event():
    ensure_uploads_dir()
    seed_superuser()


# ==========================================
# RUTAS DE AUTENTICACIÓN Y USUARIOS
# ==========================================

@app.post("/api/usuarios/registro", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    usuario: schemas.UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Registra un nuevo usuario. Solo administradores pueden crear usuarios."""
    ip = request.client.host if request.client else "127.0.0.1"
    
    # Verificar username único
    if db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first():
        registrar_log(db, current_user.username, models.NivelLog.WARNING, "REGISTRO_FALLIDO", f"Intento de registro duplicado con usuario '{usuario.username}'", ip)
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")
    # Verificar email único
    if db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first():
        registrar_log(db, current_user.username, models.NivelLog.WARNING, "REGISTRO_FALLIDO", f"Intento de registro duplicado con correo '{usuario.email}'", ip)
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    
    hashed_password = security.get_password_hash(usuario.password)
    nuevo_usuario = models.Usuario(
        nombre_completo=usuario.nombre_completo,
        username=usuario.username,
        email=usuario.email,
        hashed_password=hashed_password,
        rol=usuario.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    registrar_log(db, current_user.username, models.NivelLog.INFO, "USUARIO_CREADO", f"Usuario '{nuevo_usuario.username}' ({nuevo_usuario.rol.value}) creado por {current_user.username}", ip)
    return nuevo_usuario


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
            registrar_log(db, user.username, models.NivelLog.CRITICAL, "ACCESO_BLOQUEADO", f"Intento de ingreso a cuenta bloqueada ({user.username}). Tiempo restante: {msg_tiempo}", ip)
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detalle_err,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Si el usuario no está bloqueado pero la contraseña es incorrecta
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
                registrar_log(db, user.username, models.NivelLog.CRITICAL, "BLOQUEO_CUENTA", f"Cuenta de '{user.username}' bloqueada por {minutos_bloqueo} minutos ({user.intentos_fallidos} intentos fallidos)", ip)
            else:
                db.commit()
                intentos_restantes = 3 - user.intentos_fallidos
                detalle_err = f"Usuario o contraseña incorrectos. Intento {user.intentos_fallidos} de 3 antes de bloqueo temporal."
                registrar_log(db, user.username, models.NivelLog.WARNING, "LOGIN_FALLIDO", f"Intento fallido #{user.intentos_fallidos} para usuario '{user.username}'", ip)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detalle_err,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Contraseña correcta: Resetear contador de fallos y desbloquear
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        db.commit()

        access_token = security.create_access_token(data={"sub": user.username, "rol": user.rol.value})
        registrar_log(db, user.username, models.NivelLog.INFO, "LOGIN_EXITOSO", f"Inicio de sesión exitoso de '{user.username}' ({user.rol.value})", ip)
        return {"access_token": access_token, "token_type": "bearer"}

    else:
        # El usuario no existe en la BD
        registrar_log(db, credentials.username, models.NivelLog.WARNING, "LOGIN_USUARIO_INEXISTENTE", f"Intento de login con usuario inexistente '{credentials.username}'", ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/api/usuarios/me", response_model=schemas.UsuarioResponse)
def obtener_perfil_actual(current_user: models.Usuario = Depends(security.get_current_user)):
    """Devuelve la información del usuario autenticado."""
    return current_user


@app.get("/api/usuarios", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Lista todos los usuarios registrados. Solo administradores."""
    return db.query(models.Usuario).all()


@app.put("/api/usuarios/{usuario_id}/rol", response_model=schemas.UsuarioResponse)
def actualizar_rol_usuario(
    usuario_id: int,
    datos: schemas.UsuarioUpdateRol,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Actualiza el rol de un usuario. Solo administradores."""
    ip = request.client.host if request.client else "127.0.0.1"
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puede cambiar su propio rol.")
    
    rol_anterior = usuario.rol.value
    usuario.rol = datos.rol
    db.commit()
    db.refresh(usuario)

    registrar_log(db, current_user.username, models.NivelLog.INFO, "ROL_ACTUALIZADO", f"Rol de '{usuario.username}' cambiado de {rol_anterior} a {usuario.rol.value} por {current_user.username}", ip)
    return usuario


@app.delete("/api/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Elimina un usuario del sistema. Solo administradores."""
    ip = request.client.host if request.client else "127.0.0.1"
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puede eliminarse a sí mismo.")
    
    username_eliminado = usuario.username
    db.delete(usuario)
    db.commit()

    registrar_log(db, current_user.username, models.NivelLog.WARNING, "USUARIO_ELIMINADO", f"Usuario '{username_eliminado}' eliminado por {current_user.username}", ip)


# ==========================================
# RUTAS DE CONFIGURACIÓN DE MARCA
# ==========================================

@app.get("/api/config", response_model=schemas.ConfigResponse)
def obtener_config():
    """Devuelve la configuración de marca (nombre, logo, banner). Público."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    return {"nombre_empresa": "LogiScan Telecom", "logo_url": None, "banner_url": None}


@app.post("/api/config", response_model=schemas.ConfigResponse)
async def actualizar_config(
    request: Request,
    nombre_empresa: str = Form(None),
    logo: UploadFile = File(None),
    banner: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Actualiza la configuración de marca. Solo administradores."""
    ip = request.client.host if request.client else "127.0.0.1"
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    config = {"nombre_empresa": "LogiScan Telecom", "logo_url": None, "banner_url": None}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    
    if nombre_empresa is not None:
        config["nombre_empresa"] = nombre_empresa
    
    if logo and logo.filename:
        ext = os.path.splitext(logo.filename)[1] or ".png"
        logo_path = os.path.join(UPLOADS_DIR, f"logo{ext}")
        with open(logo_path, "wb") as f:
            content = await logo.read()
            f.write(content)
        config["logo_url"] = f"/static/uploads/logo{ext}"
    
    if banner and banner.filename:
        ext = os.path.splitext(banner.filename)[1] or ".png"
        banner_path = os.path.join(UPLOADS_DIR, f"banner{ext}")
        with open(banner_path, "wb") as f:
            content = await banner.read()
            f.write(content)
        config["banner_url"] = f"/static/uploads/banner{ext}"
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)
    
    registrar_log(db, current_user.username, models.NivelLog.INFO, "CONFIGURACION_ACTUALIZADA", f"Marca actualizada por {current_user.username} (Nombre: {config['nombre_empresa']})", ip)
    return config


# ==========================================
# RUTAS DE EQUIPOS E INVENTARIO
# ==========================================

@app.get("/api/equipos", response_model=List[schemas.EquipoResponse])
def listar_equipos(
    categoria: Optional[schemas.CategoriaEquipo] = None,
    estado: Optional[schemas.EstadoEquipo] = None,
    ubicacion: Optional[schemas.UbicacionNodo] = None,
    plant: Optional[str] = None,
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    numero_serie: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Obtiene el listado de equipos con filtros avanzados."""
    query = db.query(models.Equipo)
    if categoria:
        query = query.filter(models.Equipo.categoria == categoria)
    if estado:
        query = query.filter(models.Equipo.estado == estado)
    if ubicacion:
        query = query.filter(models.Equipo.ubicacion_actual == ubicacion)
    if plant:
        query = query.filter(models.Equipo.plant.ilike(f"%{plant}%"))
    if numero_serie:
        query = query.filter(models.Equipo.numero_serie.ilike(f"%{numero_serie}%"))
    if mes:
        query = query.filter(extract('month', models.Equipo.fecha_registro) == mes)
    if anio:
        query = query.filter(extract('year', models.Equipo.fecha_registro) == anio)
    
    return query.all()


@app.post("/api/equipos", response_model=schemas.EquipoResponse, status_code=status.HTTP_201_CREATED)
def registrar_equipo(
    equipo: schemas.EquipoCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Registra un nuevo equipo de telecomunicaciones en el inventario."""
    ip = request.client.host if request.client else "127.0.0.1"
    
    existente_serie = db.query(models.Equipo).filter(models.Equipo.numero_serie == equipo.numero_serie).first()
    if existente_serie:
        raise HTTPException(status_code=400, detail="Ya existe un equipo con ese número de serie (Serial Number).")
    
    existente_tag = db.query(models.Equipo).filter(models.Equipo.asset_tag == equipo.asset_tag).first()
    if existente_tag:
        raise HTTPException(status_code=400, detail="Ya existe un equipo con esa placa de activo (Asset Tag).")
    
    nuevo_equipo = models.Equipo(**equipo.model_dump())
    db.add(nuevo_equipo)
    db.commit()
    db.refresh(nuevo_equipo)
    
    movimiento_inicial = models.HistorialMovimiento(
        equipo_id=nuevo_equipo.id,
        usuario_id=current_user.id,
        tipo_movimiento=schemas.TipoMovimiento.INGRESO_ALMACEN,
        ubicacion_origen=None,
        ubicacion_destino=nuevo_equipo.ubicacion_actual,
        observaciones=f"Registro inicial de equipo en {nuevo_equipo.ubicacion_actual.value}. Conteo Real: {nuevo_equipo.qty_eaim}",
        cliente_nombre=nuevo_equipo.cliente_nombre,
        cliente_direccion=nuevo_equipo.cliente_direccion
    )
    db.add(movimiento_inicial)
    db.commit()
    
    registrar_log(db, current_user.username, models.NivelLog.INFO, "EQUIPO_REGISTRADO", f"Equipo '{nuevo_equipo.nombre}' (SN: {nuevo_equipo.numero_serie}, Tag: {nuevo_equipo.asset_tag}) registrado por {current_user.username}", ip)
    return nuevo_equipo


@app.get("/api/equipos/serie/{numero_serie}", response_model=schemas.EquipoResponse)
def obtener_equipo_por_serie(
    numero_serie: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Busca un equipo por su código o número de serie (para el escáner QR)."""
    equipo = db.query(models.Equipo).filter(
        (models.Equipo.numero_serie == numero_serie) | (models.Equipo.asset_tag == numero_serie)
    ).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")
    return equipo


@app.get("/api/equipos/{equipo_id}/qr")
def generar_codigo_qr(equipo_id: int, db: Session = Depends(get_db)):
    """Genera dinámicamente la imagen PNG del código QR para un equipo."""
    equipo = db.query(models.Equipo).filter(models.Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")
    
    qr_data = equipo.numero_serie
    img = qrcode.make(qr_data)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")


# ==========================================
# RUTAS DE HISTORIAL Y MOVIMIENTOS
# ==========================================

@app.post("/api/movimientos", response_model=schemas.HistorialResponse, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(
    movimiento: schemas.HistorialCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Registra una transferencia o cambio de estado de un equipo."""
    ip = request.client.host if request.client else "127.0.0.1"
    equipo = db.query(models.Equipo).filter(models.Equipo.id == movimiento.equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")
    
    ubicacion_origen = equipo.ubicacion_actual
    equipo.ubicacion_actual = movimiento.ubicacion_destino
    if movimiento.nuevo_estado:
        equipo.estado = movimiento.nuevo_estado
        
    if movimiento.tipo_movimiento == schemas.TipoMovimiento.INSTALACION_NODO:
        equipo.cliente_nombre = movimiento.cliente_nombre
        equipo.cliente_direccion = movimiento.cliente_direccion
    else:
        if movimiento.ubicacion_destino in [schemas.UbicacionNodo.SLOC_1000, schemas.UbicacionNodo.SLOC_2000, schemas.UbicacionNodo.SLOC_1010, schemas.UbicacionNodo.ALMACEN_CENTRAL]:
            equipo.cliente_nombre = None
            equipo.cliente_direccion = None
    
    nuevo_registro = models.HistorialMovimiento(
        equipo_id=equipo.id,
        usuario_id=current_user.id,
        tipo_movimiento=movimiento.tipo_movimiento,
        ubicacion_origen=ubicacion_origen,
        ubicacion_destino=movimiento.ubicacion_destino,
        observaciones=movimiento.observaciones,
        cliente_nombre=movimiento.cliente_nombre,
        cliente_direccion=movimiento.cliente_direccion
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)

    det = f"Movimiento {movimiento.tipo_movimiento.value} en equipo '{equipo.nombre}' hacia {movimiento.ubicacion_destino.value}"
    if movimiento.cliente_nombre:
        det += f" (Cliente: {movimiento.cliente_nombre})"
    registrar_log(db, current_user.username, models.NivelLog.INFO, "MOVIMIENTO_REGISTRADO", det, ip)

    return nuevo_registro


@app.get("/api/movimientos/equipo/{equipo_id}", response_model=List[schemas.HistorialResponse])
def obtener_historial_equipo(
    equipo_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Consulta la trazabilidad e historial completo de un equipo específico."""
    historial = db.query(models.HistorialMovimiento)\
                  .filter(models.HistorialMovimiento.equipo_id == equipo_id)\
                  .order_by(models.HistorialMovimiento.fecha_movimiento.desc())\
                  .all()
    return historial


# ==========================================
# RUTAS DE AUDITORÍA Y LOGS DEL SISTEMA
# ==========================================

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


# ==========================================
# SERVICIO DE ARCHIVOS ESTÁTICOS Y FRONTEND
# ==========================================

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    """Servir la página principal (Frontend Web)."""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"mensaje": "API LogiScan Telecom funcionando correctamente. Acceda a /docs para ver la documentación interactiva."}