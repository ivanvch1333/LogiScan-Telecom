import enum
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

# Importar las enumeraciones desde el modelo
from app.models import RolUsuario, CategoriaEquipo, EstadoEquipo, UbicacionNodo, TipoMovimiento


# ==========================================
# ESQUEMAS PARA USUARIOS
# ==========================================

class UsuarioBase(BaseModel):
    nombre_completo: str
    username: str
    email: EmailStr
    rol: Optional[RolUsuario] = RolUsuario.TECNICO


class UsuarioCreate(UsuarioBase):
    password: str

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
            raise ValueError('La contraseña debe incluir al menos un carácter especial (ej. !@#$%^&*...).')
        return v


class UsuarioResponse(UsuarioBase):
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioLogin(BaseModel):
    username: str
    password: str


class UsuarioUpdateRol(BaseModel):
    rol: RolUsuario


class Token(BaseModel):
    access_token: str
    token_type: str


# ==========================================
# ESQUEMAS PARA EQUIPOS DE TELECOMUNICACIONES
# ==========================================

class EquipoBase(BaseModel):
    nombre: str
    marca: str
    modelo: str
    numero_serie: str
    plant: str
    material: str
    asset_tag: str
    qty_sap: int
    qty_eaim: int
    cliente_nombre: Optional[str] = None
    cliente_direccion: Optional[str] = None
    categoria: CategoriaEquipo
    estado: Optional[EstadoEquipo] = EstadoEquipo.DISPONIBLE
    ubicacion_actual: Optional[UbicacionNodo] = UbicacionNodo.ALMACEN_CENTRAL


class EquipoCreate(EquipoBase):
    pass


class EquipoResponse(EquipoBase):
    id: int
    fecha_registro: datetime
    desviacion: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        instance.desviacion = instance.qty_sap - instance.qty_eaim
        return instance


# ==========================================
# ESQUEMAS PARA HISTORIAL Y MOVIMIENTOS
# ==========================================

class HistorialBase(BaseModel):
    equipo_id: int
    tipo_movimiento: TipoMovimiento
    ubicacion_destino: UbicacionNodo
    nuevo_estado: Optional[EstadoEquipo] = None
    observaciones: Optional[str] = None
    cliente_nombre: Optional[str] = None
    cliente_direccion: Optional[str] = None


class HistorialCreate(HistorialBase):
    pass


class HistorialResponse(BaseModel):
    id: int
    equipo_id: int
    usuario_id: int
    tipo_movimiento: TipoMovimiento
    ubicacion_origen: Optional[UbicacionNodo] = None
    ubicacion_destino: UbicacionNodo
    observaciones: Optional[str] = None
    cliente_nombre: Optional[str] = None
    cliente_direccion: Optional[str] = None
    fecha_movimiento: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA CONFIGURACIÓN DE MARCA
# ==========================================

class ConfigResponse(BaseModel):
    nombre_empresa: str
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None