from sqlmodel import Session, text
from database import consulta_prueba, engine 

def verificar_conexion():
    try:
        with Session(engine) as session:
            resultado = session.exec(text("SELECT * FROM usuarios")).first()

            if resultado:
                print("conexión exitosa")

    except Exception as e:
        print("Error al conectarse a postgres")
        print(e)

if __name__ == "__main__":
    verificar_conexion()
    consulta_prueba()
    