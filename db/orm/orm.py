import time
import os
from sqlalchemy import create_engine, select, desc, and_, or_, not_
from sqlalchemy.orm import sessionmaker
from db.orm.orm_models import Base, UsrSession, UsrMessages
from utils.logger import logger
from dotenv import load_dotenv

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

    def save(self, data_model):
        start_time = time.time()
        session = self.Session()
        try:
            session.add(data_model)
            session.commit()
            logger.info(f"session_id: {data_model.id} guardada exitosamente en {round(time.time() - start_time, 2)} segundos.")
        except Exception as e:
            logger.error("Error al intentar guardar los datos: %s", e)
            session.rollback()
            raise e
        finally:
            session.close()

    def get_last_message_dict(self):
        session = db_engine.Session()  # Crear sesión con la base de datos
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
                return last_message.to_dict()
            else:
                return {}  # Si no hay resultados, retornar un diccionario vacío
        except Exception as e:
            logger.error("Error al obtener el último mensaje: %s", e)
            return {}
        finally:
            session.close()

    def retrieve_history(self, session_id, model, exclude_intents=None):
        start_time = time.time()
        session = self.Session()
        try:
            conditions = [model.session_id == session_id]
            
            result = session.execute(
                select(model)
                .where(and_(*conditions))
                .order_by(model.id.desc())
                .limit(3)
            )
            
            previous_history = [row[0].to_dict() for row in result.fetchall()]
            logger.info(f"[orm][retrieve_history] ID: {session_id} retrieved history successfully in {round(time.time() - start_time, 2)} seconds.")
        except Exception as e:
            logger.error("[orm][retrieve_history] Error while retrieving the history: %s", e)
            previous_history = []
        finally:
            session.close()
        return previous_history

    def close(self):
        self.Session.close_all()

    def empty_table(self, model):
        start_time = time.time()
        session = self.Session()
        try:
            session.query(model).delete()
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

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
    print("Base de datos y tablas inicializadas.")