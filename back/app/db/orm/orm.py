import os
from dotenv import load_dotenv
import time
from sqlalchemy import create_engine, select, desc, and_, or_, not_
from sqlalchemy.orm import sessionmaker
from db.orm.orm_models import Base, UsrSession, UsrMessages
from utils.logger import logger


load_dotenv()
POSTGRES_URL = os.getenv('POSTGRES_URL')


class PostgresOrm:
    def __init__(self):
        db_url = POSTGRES_URL
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        Base.metadata.create_all(self.engine)

    def save(self, data_model) -> None:
        """
        Guarda un modelo de datos en la base de datos seleccionada.

        Esta función intenta guardar un modelo de datos en la base de datos.
        Si la operación es exitosa, se confirma la transacción y se registra el tiempo de ejecución. 
        En caso de un error, se registra el error, se revierte la transacción y se muestra la excepción.

        Parámetros:
            data_model: El modelo de datos que se desea guardar en la base de datos. 
                        Debe ser una instancia de un modelo compatible con SQLAlchemy.

        Excepciones:
            Exception: Lanza cualquier excepción encontrada durante la operación de guardar, 
                    después de revertir la transacción.

        Registro:
            - Info: Registra el ID del modelo de datos guardado y el tiempo que tomó completar la operación.
            - Error: Registra cualquier error que ocurra durante la operación de guardado.
        """
        start_time = time.time()
        session = self.Session()
        try:
            session.add(data_model)
            session.commit()
            logger.info(f"ID de la sesión: '{data_model.id}'. Sesión guardada exitosamente en {round(time.time() - start_time, 2)} segundos.")
        except Exception as e:
            logger.error("Error al intentar guardar la sesión: %s", e)
            session.rollback()
            raise e
        finally:
            session.close()

    def get_last_message_dict(self) -> dict:
        """
        Recupera el último mensaje almacenado en la tabla 'messages'.

        Esta función consulta la base de datos para obtener el último mensaje registrado 
        en la tabla `UsrMessages`, ordenado de forma descendente por el campo `ts` (timestamp). 
        Si se encuentra un mensaje, se convierte a diccionario utilizando el método `to_dict()` 
        y se devuelve. Si no hay mensajes, devuelve un diccionario vacío.

        Retorno:
            dict: Un diccionario que contiene los datos del último mensaje, o un diccionario vacío si no hay mensajes.

        Excepciones:
            Exception: Si ocurre un error durante la consulta, se registra el error y se devuelve un diccionario vacío.

        Registro:
            - Info: Registra el ID de la sesión del último mensaje y el tiempo que tomó recuperar el mensaje.
            - Error: Registra cualquier error que ocurra durante la consulta.
        """
        start_time = time.time()
        session = db_engine.Session()
        try:
            # Consulta para obtener la última fila de la tabla messages ordenada por timestamp
            result = session.execute(
                select(UsrMessages)
                .order_by(UsrMessages.ts.desc())  # Ordenar de forma descendente por ts (timestamp)
                .limit(1)  # Limitar a una sola fila
            )
            # Obtener el primer resultado
            last_message = result.scalar_one_or_none()
            # Si existe un resultado, convertirlo a diccionario usando el método to_dict()
            if last_message:
                last_message_dict = last_message.to_dict() 
                logger.info(f"[orm][get_last_message_dict] ID de la sesión: '{last_message_dict["session_id"]}'. Último mensaje recuperado exitosamente en {round(time.time() - start_time, 2)} seconds.")
                return last_message_dict   
            else:
                return {}  # Si no hay resultados, retornar un diccionario vacío
            
        except Exception as e:
            logger.error("Error al intentar obtener el último mensaje: %s", e)
            return {}
        finally:
            session.close()

    def retrieve_history(self, session_id, model) -> list:
        """
        Recupera el historial de mensajes para una sesión específica.

        Esta función consulta la base de datos para obtener los últimos mensajes asociados 
        a un ID de sesión particular. Los mensajes se ordenan de forma descendente y se limita 
        el número de resultados a cinco.

        Parámetros:
            session_id (str): El ID de la sesión para la cual se desea recuperar el historial de mensajes.
            model: El modelo de datos que representa los mensajes en la base de datos.

        Retorno:
            list: Una lista de diccionarios que representan los mensajes recuperados, 
                o una lista vacía si no se encontraron mensajes o ocurrió un error.

        Excepciones:
            Exception: Si ocurre un error durante la consulta, se registra el error y se devuelve una lista vacía.

        Registro:
            - Info: Registra el ID de la sesión y el tiempo que tomó recuperar el historial de mensajes.
            - Error: Registra cualquier error que ocurra durante la operación de recuperación.
        """
        start_time = time.time()
        session = self.Session()
        try:
            conditions = [model.session_id == session_id]
            
            result = session.execute(
                select(model)
                .where(and_(*conditions))
                .order_by(model.id.desc())
                .limit(5)
            )
            
            previous_history = [row[0].to_dict() for row in result.fetchall()]
            logger.info(f"[orm][retrieve_history] ID de la sesión: '{session_id}'. Historial de mensajes recuperado exitosamente en {round(time.time() - start_time, 2)} segundos.")
        except Exception as e:
            logger.error("[orm][retrieve_history] Error al intentar recuperar el historial de mensajes: %s", e)
            previous_history = []
        finally:
            session.close()
        return previous_history

    def close(self):
        self.Session.close_all()

    # generic context manager support that closes session after use
    def __enter__(self):
        self._session = self.Session()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

# static instance for common usages
db_engine = PostgresOrm()

if __name__ == "__main__":
    # Inicializa la base de datos
    orm = PostgresOrm()
    logger.info("Base de datos y tablas inicializadas.")