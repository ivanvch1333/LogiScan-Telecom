import os
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, File, UploadFile, Form
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
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Registra un nuevo usuario. Solo administradores pueden crear usuarios."""
    # Verificar username único
    if db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")
    # Verificar email único
    if db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first():
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
    return nuevo_usuario


@app.post("/api/usuarios/login", response_model=schemas.Token)
def login(credentials: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    """Inicia sesión con nombre de usuario y contraseña, genera un token JWT."""
    user = db.query(models.Usuario).filter(models.Usuario.username == credentials.username).first()
    if not user or not security.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.username, "rol": user.rol.value})
    return {"access_token": access_token, "token_type": "bearer"}


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
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Actualiza el rol de un usuario. Solo administradores."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puede cambiar su propio rol.")
    usuario.rol = datos.rol
    db.commit()
    db.refresh(usuario)
    return usuario


@app.delete("/api/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Elimina un usuario del sistema. Solo administradores."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puede eliminarse a sí mismo.")
    db.delete(usuario)
    db.commit()


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
    nombre_empresa: str = Form(None),
    logo: UploadFile = File(None),
    banner: UploadFile = File(None),
    current_user: models.Usuario = Depends(security.get_current_admin)
):
    """Actualiza la configuración de marca. Solo administradores."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    # Leer config actual
    config = {"nombre_empresa": "LogiScan Telecom", "logo_url": None, "banner_url": None}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    
    # Actualizar nombre
    if nombre_empresa is not None:
        config["nombre_empresa"] = nombre_empresa
    
    # Guardar logo
    if logo and logo.filename:
        ext = os.path.splitext(logo.filename)[1] or ".png"
        logo_path = os.path.join(UPLOADS_DIR, f"logo{ext}")
        with open(logo_path, "wb") as f:
            content = await logo.read()
            f.write(content)
        config["logo_url"] = f"/static/uploads/logo{ext}"
    
    # Guardar banner
    if banner and banner.filename:
        ext = os.path.splitext(banner.filename)[1] or ".png"
        banner_path = os.path.join(UPLOADS_DIR, f"banner{ext}")
        with open(banner_path, "wb") as f:
            content = await banner.read()
            f.write(content)
        config["banner_url"] = f"/static/uploads/banner{ext}"
    
    # Guardar config
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)
    
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
    """Obtiene el listado de equipos con filtros avanzados (Planta, SLOC, Estado, Mes, Año, Serie)."""
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
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Registra un nuevo equipo de telecomunicaciones en el inventario."""
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
    
    # Registrar el movimiento inicial
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
    
    # El contenido del QR incluye la serie para consulta directa
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
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(security.get_current_user)
):
    """Registra una transferencia o cambio de estado de un equipo."""
    equipo = db.query(models.Equipo).filter(models.Equipo.id == movimiento.equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")
    
    ubicacion_origen = equipo.ubicacion_actual
    
    # Actualizar estado, ubicación del equipo y datos del cliente si es instalación
    equipo.ubicacion_actual = movimiento.ubicacion_destino
    if movimiento.nuevo_estado:
        equipo.estado = movimiento.nuevo_estado
        
    if movimiento.tipo_movimiento == schemas.TipoMovimiento.INSTALACION_NODO:
        equipo.cliente_nombre = movimiento.cliente_nombre
        equipo.cliente_direccion = movimiento.cliente_direccion
    else:
        # Si se mueve a una ubicación técnica/almacén se desvincula el cliente activo del equipo
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
# SERVICIO DE ARCHIVOS ESTÁTICOS Y FRONTEND
# ==========================================

# Montar carpeta estática si existe
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    """Servir la página principal (Frontend Web)."""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"mensaje": "API LogiScan Telecom funcionando correctamente. Acceda a /docs para ver la documentación interactiva."}