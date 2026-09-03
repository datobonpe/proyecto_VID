from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from models import (
    InteraccionEvento, DatosClinicos, Usuario, Obra, Especialidad, Evento, 
    Servicio, EventoEspecialidad, Experiencia, EventoExperiencia, ParticipacionExperiencia
)
from fastapi import FastAPI, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func
from database import get_session

class EventoCreate(BaseModel):
    nombre_evento: str
    lugar_evento: str
    fecha_evento: date
    id_obra: Optional[int] = None
    modulos: List[int] = []
    experiencias: List[int] = []

class ModuloCreate(BaseModel):
    nombre_modulo: str

class ModuloUpdate(BaseModel):
    nombre_modulo: str

class ExperienciaCreate(BaseModel):
    nombre_experiencia: str
    descripcion: Optional[str] = None

class ExperienciaUpdate(BaseModel):
    nombre_experiencia: str
    descripcion: Optional[str] = None

class GuardarExperienciasUsuario(BaseModel):
    id_evento: int
    numero_documento: str
    experiencias: List[int] = []

class RegistroUsuario(BaseModel):
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    fecha_nacimiento: date
    sexo: Optional[str] = None
    email: str
    celular: str
    lugar_residencia: Optional[str] = None
    ocupacion: Optional[str] = None
    preferencia_contacto: Optional[str] = None
    autorizacion_tratamiento_datos: bool = False

class GuardarModulo(BaseModel):
    numero_documento: str
    modulo: str
    datos: Optional[dict] = None

app = FastAPI(title="Ruta del Cuidado VID")

templates = Jinja2Templates(directory="templates")

@app.get("/dashboard", response_class=HTMLResponse)
def cargar_dashboard(request: Request, db: Session = Depends(get_session)):
    obras = db.exec(select(Obra)).all()
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={"obras": obras}
    )

@app.get("/eventos")
def listar_eventos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_session)
):
    eventos = db.exec(select(Evento).offset(skip).limit(limit)).all()
    lista = []
    for e in eventos:
        modulos = db.exec(
            select(Especialidad.nombre_especialidad)
            .join(EventoEspecialidad, EventoEspecialidad.id_especialidad == Especialidad.id_especialidad)
            .where(EventoEspecialidad.id_evento == e.id_evento)
        ).all()
        experiencias = db.exec(
            select(Experiencia.nombre_experiencia)
            .join(EventoExperiencia, EventoExperiencia.id_experiencia == Experiencia.id_experiencia)
            .where(EventoExperiencia.id_evento == e.id_evento)
        ).all()
        lista.append({
            "id_evento": e.id_evento,
            "nombre_evento": e.nombre_evento,
            "lugar_evento": e.lugar_evento,
            "fecha_evento": str(e.fecha_evento),
            "id_obra": e.id_obra,
            "modulos": modulos,
            "experiencias": experiencias
        })
    return lista

@app.post("/crear_evento")
def crear_evento(data: EventoCreate, db: Session = Depends(get_session)):
    nuevo_evento = Evento(
        nombre_evento=data.nombre_evento,
        lugar_evento=data.lugar_evento,
        fecha_evento=data.fecha_evento,
        id_obra=data.id_obra
    )
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)

    for modulo_id in data.modulos:
        relacion = EventoEspecialidad(
            id_evento=nuevo_evento.id_evento,
            id_especialidad=modulo_id
        )
        db.add(relacion)

    for exp_id in data.experiencias:
        relacion_exp = EventoExperiencia(
            id_evento=nuevo_evento.id_evento,
            id_experiencia=exp_id
        )
        db.add(relacion_exp)

    db.commit()

    return {"message": "Evento creado exitosamente", "id_evento": nuevo_evento.id_evento}

@app.get("/modulos")
def listar_modulos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_session)
):
    query = select(Especialidad).offset(skip).limit(limit)
    modulos = db.exec(query).all()
    return [
        {"id_especialidad": m.id_especialidad, "nombre_modulo": m.nombre_especialidad}
        for m in modulos
    ]

@app.post("/crear_modulo")
def crear_modulo(data: ModuloCreate, db: Session = Depends(get_session)):
    nuevo = Especialidad(nombre_especialidad=data.nombre_modulo)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"message": "Módulo creado exitosamente", "id_especialidad": nuevo.id_especialidad}

@app.put("/modulos/{modulo_id}")
def editar_modulo(modulo_id: int, data: ModuloUpdate, db: Session = Depends(get_session)):
    modulo = db.exec(select(Especialidad).where(Especialidad.id_especialidad == modulo_id)).first()
    if not modulo:
        return JSONResponse(status_code=404, content={"message": "Módulo no encontrado"})
    modulo.nombre_especialidad = data.nombre_modulo
    db.commit()
    return {"message": "Módulo actualizado exitosamente"}

@app.delete("/modulos/{modulo_id}")
def eliminar_modulo(modulo_id: int, db: Session = Depends(get_session)):
    modulo = db.exec(select(Especialidad).where(Especialidad.id_especialidad == modulo_id)).first()
    if not modulo:
        return JSONResponse(status_code=404, content={"message": "Módulo no encontrado"})
    db.delete(modulo)
    db.commit()
    return {"message": "Módulo eliminado exitosamente"}

@app.get("/experiencias")
def listar_experiencias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_session)
):
    query = select(Experiencia).offset(skip).limit(limit)
    experiencias = db.exec(query).all()
    return [
        {
            "id_experiencia": e.id_experiencia,
            "nombre_experiencia": e.nombre_experiencia,
            "descripcion": e.descripcion
        }
        for e in experiencias
    ]

@app.post("/crear_experiencia")
def crear_experiencia(data: ExperienciaCreate, db: Session = Depends(get_session)):
    nueva = Experiencia(
        nombre_experiencia=data.nombre_experiencia,
        descripcion=data.descripcion
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"message": "Experiencia creada exitosamente", "id_experiencia": nueva.id_experiencia}

@app.put("/experiencias/{experiencia_id}")
def editar_experiencia(experiencia_id: int, data: ExperienciaUpdate, db: Session = Depends(get_session)):
    exp = db.exec(select(Experiencia).where(Experiencia.id_experiencia == experiencia_id)).first()
    if not exp:
        return JSONResponse(status_code=404, content={"message": "Experiencia no encontrada"})
    exp.nombre_experiencia = data.nombre_experiencia
    if data.descripcion is not None:
        exp.descripcion = data.descripcion
    db.commit()
    return {"message": "Experiencia actualizada exitosamente"}

@app.delete("/experiencias/{experiencia_id}")
def eliminar_experiencia(experiencia_id: int, db: Session = Depends(get_session)):
    exp = db.exec(select(Experiencia).where(Experiencia.id_experiencia == experiencia_id)).first()
    if not exp:
        return JSONResponse(status_code=404, content={"message": "Experiencia no encontrada"})
    db.delete(exp)
    db.commit()
    return {"message": "Experiencia eliminada exitosamente"}

@app.get("/buscar_usuario_api")
def buscar_usuario_api(numero_documento: str, db: Session = Depends(get_session)):
    statement = select(Usuario).where(Usuario.numero_documento == numero_documento)
    usuario = db.exec(statement).first()
    if usuario:
        return {
            "encontrado": True,
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "tipo_documento": usuario.tipo_documento,
                "numero_documento": usuario.numero_documento,
                "nombre_completo": usuario.nombre_completo,
                "celular": usuario.celular,
                "email": usuario.email,
                "fecha_nacimiento": str(usuario.fecha_nacimiento),
                "sexo": usuario.sexo,
                "lugar_residencia": usuario.lugar_residencia,
                "ocupacion": usuario.ocupacion,
                "preferencia_contacto": usuario.preferencia_contacto
            }
        }
    return {"encontrado": False}

@app.post("/guardar_bienvenida_api")
def guardar_bienvenida_api(data: RegistroUsuario, db: Session = Depends(get_session)):
    statement = select(Usuario).where(Usuario.numero_documento == data.numero_documento)
    usuario = db.exec(statement).first()

    if not usuario:
        usuario = Usuario(
            tipo_documento=data.tipo_documento,
            numero_documento=data.numero_documento,
            nombre_completo=data.nombre_completo,
            celular=data.celular,
            email=data.email,
            fecha_nacimiento=data.fecha_nacimiento,
            sexo=data.sexo,
            lugar_residencia=data.lugar_residencia,
            ocupacion=data.ocupacion,
            preferencia_contacto=data.preferencia_contacto,
            autorizacion_tratamiento_datos=data.autorizacion_tratamiento_datos,
            metodo_registro="Web"
        )
        db.add(usuario)
    else:
        usuario.nombre_completo = data.nombre_completo
        usuario.celular = data.celular
        usuario.email = data.email
        usuario.fecha_nacimiento = data.fecha_nacimiento
        usuario.sexo = data.sexo
        usuario.lugar_residencia = data.lugar_residencia
        usuario.ocupacion = data.ocupacion
        usuario.preferencia_contacto = data.preferencia_contacto

    db.commit()
    db.refresh(usuario)

    return {
        "message": "Usuario guardado exitosamente",
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "tipo_documento": usuario.tipo_documento,
            "numero_documento": usuario.numero_documento,
            "nombre_completo": usuario.nombre_completo,
            "celular": usuario.celular,
            "email": usuario.email,
            "fecha_nacimiento": str(usuario.fecha_nacimiento),
            "sexo": usuario.sexo,
            "lugar_residencia": usuario.lugar_residencia,
            "ocupacion": usuario.ocupacion,
            "preferencia_contacto": usuario.preferencia_contacto
        }
    }

@app.post("/guardar_modulo_api")
def guardar_modulo_api(data: GuardarModulo, db: Session = Depends(get_session)):
    usuario = db.exec(select(Usuario).where(Usuario.numero_documento == data.numero_documento)).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"message": "Usuario no encontrado"})
    
    return {
        "message": f"Módulo '{data.modulo}' guardado exitosamente",
        "usuario": data.numero_documento,
        "modulo": data.modulo
    }


@app.get("/", response_class=HTMLResponse)
def home():
    """Redirige directamente al panel administrativo (dashboard)."""
    return RedirectResponse(url="/dashboard")

@app.get("/evento/{evento_id}", response_class=HTMLResponse)
def cargar_evento(request: Request, evento_id: int, db: Session = Depends(get_session)):
    evento = db.exec(select(Evento).where(Evento.id_evento == evento_id)).first()
    if not evento:
        return JSONResponse(status_code=404, content={"message": "Evento no encontrado"})
    
    modulos_query = select(Especialidad).join(
        EventoEspecialidad, EventoEspecialidad.id_especialidad == Especialidad.id_especialidad
    ).where(EventoEspecialidad.id_evento == evento_id)
    modulos = db.exec(modulos_query).all()

    experiencias_query = select(Experiencia).join(
        EventoExperiencia, EventoExperiencia.id_experiencia == Experiencia.id_experiencia
    ).where(EventoExperiencia.id_evento == evento_id)
    experiencias = db.exec(experiencias_query).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"evento": evento, "modulos": modulos, "experiencias": experiencias}
    )

@app.get("/usuario_experiencias_api")
def obtener_usuario_experiencias(
    id_evento: int,
    numero_documento: str,
    db: Session = Depends(get_session)
):
    usuario = db.exec(select(Usuario).where(Usuario.numero_documento == numero_documento)).first()
    if not usuario:
        return {"experiencias": []}
    
    participaciones = db.exec(
        select(ParticipacionExperiencia.id_experiencia).where(
            ParticipacionExperiencia.id_evento == id_evento,
            ParticipacionExperiencia.id_usuario == usuario.id_usuario
        )
    ).all()
    return {"experiencias": participaciones}

@app.post("/guardar_experiencias_api")
def guardar_experiencias_api(data: GuardarExperienciasUsuario, db: Session = Depends(get_session)):
    usuario = db.exec(select(Usuario).where(Usuario.numero_documento == data.numero_documento)).first()
    if not usuario:
        return JSONResponse(status_code=404, content={"message": "Usuario no encontrado"})

    # Eliminar participaciones previas en este evento para este usuario
    anteriores = db.exec(
        select(ParticipacionExperiencia).where(
            ParticipacionExperiencia.id_evento == data.id_evento,
            ParticipacionExperiencia.id_usuario == usuario.id_usuario
        )
    ).all()
    for p in anteriores:
        db.delete(p)
    db.flush()

    # Guardar las experiencias seleccionadas
    for exp_id in data.experiencias:
        nueva_p = ParticipacionExperiencia(
            id_evento=data.id_evento,
            id_usuario=usuario.id_usuario,
            id_experiencia=exp_id
        )
        db.add(nueva_p)

    db.commit()
    return {"message": "Experiencias guardadas exitosamente", "guardadas": len(data.experiencias)}

@app.get("/buscar_usuario", response_class=HTMLResponse)
def buscar_usuario(request: Request,
                   numero_documento: str,
                   db: Session = Depends(get_session)
):
    statement = select(Usuario).where(Usuario.numero_documento == numero_documento)
    usuario = db.exec(statement).first()

    if usuario:
        return templates.TemplateResponse(request=request, name="partials/usuario_encontrado.html"
            #{"request": request, "usuario": usuario}
        )
    else:
        return templates.TemplateResponse(request=request, name="partials/usuario_no_encontrado.html"
            #{"cedula": numero_documento}
        )

@app.post("/guardar_bienvenida", response_class=HTMLResponse)
def guardar_bienvenida(
    request: Request,
    tipo_documento: str = Form(...),
    numero_documento: str = Form(...),
    nombre_completo: str = Form(...),
    celular: str = Form(...),
    email: str = Form(...),
    fecha_nacimiento: date = Form(...),
    sexo: str = Form(...),
    lugar_residencia: str = Form(...),
    ocupacion: str = Form(...),
    preferencia_contacto: str = Form(...),
    autorizacion_tratamiento_datos: bool = Form(...),
    metodo_registro: str = Form(...),
    db: Session = Depends(get_session)
):
    user_agent = request.headers.get("user-agent", "").lower()
    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        metodo_registrado="Celular"
    else: 
        metodo_registrado="Computador"

    statement = select(Usuario).where(Usuario.numero_documento == numero_documento)
    usuario = db.exec(statement).first()

    if not usuario:
        usuario = Usuario(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            nombre_completo=nombre_completo,
            celular=celular,
            email=email,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            lugar_residencia=lugar_residencia,
            ocupacion=ocupacion,
            preferencia_contacto=preferencia_contacto,
            autorizacion_tratamiento_datos=autorizacion_tratamiento_datos,
            metodo_registro=metodo_registrado
        )
        db.add(usuario)
    else:
        usuario.nombre_completo = nombre_completo
        usuario.celular = celular
        usuario.email = email
        usuario.fecha_nacimiento = fecha_nacimiento
        usuario.sexo = sexo
        usuario.lugar_residencia = lugar_residencia
        usuario.ocupacion = ocupacion
        usuario.preferencia_contacto = preferencia_contacto
        usuario.autorizacion_tratamiento_datos = autorizacion_tratamiento_datos

    db.commit()
    db.refresh(usuario)

    return templates.TemplateResponse(request=request, name="partials/banner_desbloqueo.html"
        #{"request": request, "usuario": usuario}
    )

@app.post("/guardar_cardiovascular", response_class=HTMLResponse)
def guardar_cardiovascular(
    request: Request,
    numero_documento: str = Form(...),
    peso: float = Form(None),
    estatura: float = Form(None),
    imc: float = Form(None),
    fumador: bool = Form(...),
    presion_arterial: str = Form(None),
    glicemia: float = Form(None),
    dislipedemia: str = Form(None),
    db: Session = Depends(get_session)
):
    statement_user = select(Usuario).where(Usuario.numero_documento == numero_documento)
    usuario = db.exec(statement_user).first()

    if not usuario:
        return HTMLResponse("<div style='color: red; padding: 10px;'> Usuario no encontrado. Por favor, registre al usuario antes de continuar.</div>")
    statement_prof = select(Profesional).where(Profesional.id_profesional == id_profesional_actual)
    profesional = db.exec(statement_prof).first()

    if not profesional:
        return HTMLResponse("<div style='color: red; padding: 10px;'> Profesional no autorizado.</div>")

    interaccion = InteraccionEvento(
        id_usuario=usuario.id_usuario,
        id_profesional=profesional.id_profesional,
        id_especialidad=profesional.id_especialidad
    )
    db.add(interaccion)
    db.commit()
    db.refresh(interaccion)



    datos_clinicos = DatosClinicos(
        id_interaccion=interaccion.id_interaccion,
        peso=peso,
        estatura=estatura,
        imc=imc,
        fumador=fumador,
        presion_arterial=presion_arterial,
        glicemia=glicemia,
        dislipidemia=dislipedemia
    )

    db.add(datos_clinicos)
    db.commit()
    db.refresh(datos_clinicos)

    return templates.TemplateResponse("<div style='color: green;'> Estacion Cardiovascular completada.</div>")