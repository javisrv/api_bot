import time
import os
from sqlalchemy import create_engine, select, desc, and_, or_, not_
from sqlalchemy.orm import sessionmaker
from db.orm.orm_models import Base, UsrSession, UsrMessages
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
        print("Tablas creadas correctamente")

    def save(self, data_model):
        start_time = time.time()
        session = self.Session()
        try:
            session.add(data_model)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def read(self, session_id, model):
        start_time = time.time()
        session = self.Session()
        try:
            result = session.execute(select(model).where(model.id == session_id))
            result = result.fetchone()[0]
        except Exception as e:
            result = None
        finally:
            session.close()
        return result
    
    def read_messages(self, session_id, model):
        start_time = time.time()
        session = self.Session()
        try:
            result = session.execute(select(model).where(model.session_id == session_id))
            result = [row[0].to_dict() for row in result.fetchall()]
        except Exception as e:
            result = None
        finally:
            session.close()
        return result

    def retrieve_history(self, session_id, model, exclude_intents=None):
        start_time = time.time()
        session = self.Session()
        try:
            conditions = [model.session_id == session_id]
            
            if exclude_intents:  # Excluir intents de intents_list
                intent_conditions = [model.intent == intent for intent in exclude_intents]
                conditions.append(not_(or_(*intent_conditions)))
            
            result = session.execute(
                select(model)
                .where(and_(*conditions))
                .order_by(model.id.desc())
                .limit(3)
            )
            
            previous_history = [row[0].to_dict() for row in result.fetchall()]
        except Exception as e:
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