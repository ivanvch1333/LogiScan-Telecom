import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Importar la Base desde la configuración de la base de datos
from app.database import Base


# ==========================================
# ENUMERACIONES
# ==========================================

class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    TECNICO = "tecnico"


class CategoriaEquipo(str, enum.Enum):
    ROUTER = "router"
    SWITCH = "switch"
    OLT = "olt"
    EDFA = "edfa"
    ENLACE_RADIO = "enlace_radio"
    OTRO = "otro"


class EstadoEquipo(str, enum.Enum):
    DISPONIBLE = "disponible"
    ASIGNADO = "asignado"
    EN_MANTENIMIENTO = "en_mantenimiento"
    BAJA = "baja"


class UbicacionNodo(str, enum.Enum):
    SLOC_1000 = "1000"
    SLOC_2000 = "2000"
    SLOC_1010 = "1010"
    ALMACEN_CENTRAL = "Almacén Central"


class TipoMovimiento(str, enum.Enum):
    INGRESO_ALMACEN = "ingreso_almacen"
    INSTALACION_NODO = "instalacion_nodo"
    RETIRO_MANTENIMIENTO = "retiro_mantenimiento"
    REEMPLAZO_EMERGENCIA = "reemplazo_emergencia"


class NivelLog(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ==========================================
# MODELOS DE BASE DE DATOS
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.TECNICO)
    intentos_fallidos = Column(Integer, default=0, nullable=False)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    movimientos = relationship("HistorialMovimiento", back_populates="usuario")


class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    numero_serie = Column(String(100), unique=True, index=True, nullable=False)
    
    # Campos SAP
    plant = Column(String(50), nullable=False, default="Planta Latacunga")
    material = Column(String(50), nullable=False)
    asset_tag = Column(String(50), unique=True, index=True, nullable=False)
    qty_sap = Column(Integer, default=1, nullable=False)
    qty_eaim = Column(Integer, default=0, nullable=False)

    # Campos de cliente para instalación
    cliente_nombre = Column(String(100), nullable=True)
    cliente_direccion = Column(String(200), nullable=True)

    categoria = Column(Enum(CategoriaEquipo), nullable=False)
    estado = Column(Enum(EstadoEquipo), default=EstadoEquipo.DISPONIBLE)
    ubicacion_actual = Column(Enum(UbicacionNodo), default=UbicacionNodo.ALMACEN_CENTRAL)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    historial = relationship("HistorialMovimiento", back_populates="equipo", cascade="all, delete-orphan")


class HistorialMovimiento(Base):
    __tablename__ = "historial_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_movimiento = Column(Enum(TipoMovimiento), nullable=False)
    ubicacion_origen = Column(Enum(UbicacionNodo), nullable=True)
    ubicacion_destino = Column(Enum(UbicacionNodo), nullable=False)
    observaciones = Column(Text, nullable=True)
    fecha_movimiento = Column(DateTime(timezone=True), server_default=func.now())

    # Registro de datos del cliente en el momento de la instalación
    cliente_nombre = Column(String(100), nullable=True)
    cliente_direccion = Column(String(200), nullable=True)

    equipo = relationship("Equipo", back_populates="historial")
    usuario = relationship("Usuario", back_populates="movimientos")


class LogSistema(Base):
    __tablename__ = "logs_sistema"

    id = Column(Integer, primary_key=True, index=True)
    usuario_username = Column(String(50), nullable=True, index=True)
    nivel = Column(Enum(NivelLog), default=NivelLog.INFO, nullable=False)
    accion = Column(String(100), nullable=False, index=True)
    detalle = Column(Text, nullable=False)
    ip_origen = Column(String(50), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())