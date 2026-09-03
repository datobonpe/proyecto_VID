from typing import Optional
from datetime import date, datetime, timezone
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint

SCHEMA_NAME = "prueba_evento"

class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "numero_documento", name="unq_documento_usuario"),
        {"schema": SCHEMA_NAME}
    )

    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    tipo_documento: str = Field(max_length=5, index=True)
    numero_documento: str = Field(max_length=20, index=True)
    nombre_completo: str = Field(max_length=50)
    celular: str = Field(max_length=10)
    email: str = Field(max_length=50)
    fecha_nacimiento: date
    sexo: Optional[str] = Field(default=None, max_length=1)
    lugar_residencia: Optional[str] = Field(default=None, max_length=25)
    ocupacion: Optional[str] = Field(default=None, max_length=15)
    metodo_registro: Optional[str] = Field(default=None, max_length=20)
    preferencia_contacto: Optional[str] = Field(default=None, max_length=20)
    fecha_hora_registro: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    autorizacion_tratamiento_datos: bool = Field(default=False)

class Obra(SQLModel, table=True):
    __tablename__ = "obras"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id_obra: Optional[int] = Field(default=None, primary_key=True)
    nombre_obra: str = Field(max_length=50)

class Especialidad(SQLModel, table=True):
    __tablename__ = "especialidades"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id_especialidad: Optional[int] = Field(default=None, primary_key=True)
    nombre_especialidad: str = Field(max_length=50)

class Evento(SQLModel, table=True):
    __tablename__ = "eventos"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id_evento: Optional[int] = Field(default=None, primary_key=True)
    id_obra: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.obras.id_obra")
    nombre_evento: str = Field(max_length=50)
    lugar_evento: str = Field(max_length=50)
    fecha_evento: date

class Servicio(SQLModel, table=True):
    __tablename__ = "servicios"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id_servicio: Optional[int] = Field(default=None, primary_key=True)
    fk_id_obra: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.obras.id_obra")
    id_especialidad: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.especialidades.id_especialidad")
    nombre_servicio: str = Field(max_length=50)

class EventoEspecialidad(SQLModel, table=True):
    __tablename__ = "evento_especialidades"
    __table_args__ = (
        UniqueConstraint("id_evento", "id_especialidad", name="unq_evento_especialidad"),
        {"schema": SCHEMA_NAME}
    )
    
    id_configuracion: Optional[int] = Field(default=None, primary_key=True)
    id_evento: int = Field(foreign_key=f"{SCHEMA_NAME}.eventos.id_evento")
    id_especialidad: int = Field(foreign_key=f"{SCHEMA_NAME}.especialidades.id_especialidad")

class InteraccionEvento(SQLModel, table=True):
    __tablename__ = "interacciones_evento"
    __table_args__ = (
        UniqueConstraint("id_evento", "id_usuario", "id_especialidad", name="uniq_interaccion_evento_usuario"),
        {"schema": SCHEMA_NAME}
    )
    
    id_interaccion: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.usuarios.id_usuario")
    id_obra: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.obras.id_obra")
    id_profesional: str = Field(max_length=11)
    id_especialidad: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.especialidades.id_especialidad")
    servicio_recomendado: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.servicios.id_servicio")
    observaciones: Optional[str] = None
    id_evento: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.eventos.id_evento")
    fecha_hora_atencion: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    estado_evaluacion: Optional[str] = Field(default=None, max_length=50)

class DatosClinicos(SQLModel, table=True):
    __tablename__ = "datos_clinicos"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id_tamizaje: Optional[int] = Field(default=None, primary_key=True)
    id_interaccion: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.interacciones_evento.id_interaccion", unique=True)
    peso: Optional[float] = None
    estatura: Optional[int] = None
    imc: Optional[float] = None
    fumador: Optional[bool] = None
    presion_arterial: Optional[str] = Field(default=None, max_length=10)
    glicemia: Optional[float] = None
    dislipidemia: Optional[str] = Field(default=None, max_length=10)

class SeguimientoTamizaje(SQLModel, table=True):
    __tablename__ = "seguimiento_tamizaje"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    id_seguimiento: Optional[int] = Field(default=None, primary_key=True)
    id_interaccion: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.interacciones_evento.id_interaccion")
    id_servicio: Optional[int] = Field(default=None, foreign_key=f"{SCHEMA_NAME}.servicios.id_servicio")
    fecha_servicio: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class Experiencia(SQLModel, table=True):
    __tablename__ = "experiencias"
    __table_args__ = {"schema": SCHEMA_NAME}

    id_experiencia: Optional[int] = Field(default=None, primary_key=True)
    nombre_experiencia: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)

class EventoExperiencia(SQLModel, table=True):
    __tablename__ = "evento_experiencias"
    __table_args__ = (
        UniqueConstraint("id_evento", "id_experiencia", name="unq_evento_experiencia"),
        {"schema": SCHEMA_NAME}
    )

    id_configuracion: Optional[int] = Field(default=None, primary_key=True)
    id_evento: int = Field(foreign_key=f"{SCHEMA_NAME}.eventos.id_evento")
    id_experiencia: int = Field(foreign_key=f"{SCHEMA_NAME}.experiencias.id_experiencia")

class ParticipacionExperiencia(SQLModel, table=True):
    __tablename__ = "participacion_experiencias"
    __table_args__ = (
        UniqueConstraint("id_evento", "id_usuario", "id_experiencia", name="unq_participacion_usuario_evento_exp"),
        {"schema": SCHEMA_NAME}
    )

    id_participacion: Optional[int] = Field(default=None, primary_key=True)
    id_evento: int = Field(foreign_key=f"{SCHEMA_NAME}.eventos.id_evento")
    id_usuario: int = Field(foreign_key=f"{SCHEMA_NAME}.usuarios.id_usuario")
    id_experiencia: int = Field(foreign_key=f"{SCHEMA_NAME}.experiencias.id_experiencia")
    fecha_hora: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
