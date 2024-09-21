import uuid
import os
from sqlalchemy import Column, DateTime, ForeignKey, String, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from dotenv import load_dotenv

load_dotenv()
API_VERSION = os.getenv('API_VERSION')

Base = declarative_base()

class UsrSession(Base):
    __tablename__ = "sessions"

    id = Column(UUID, primary_key=True)
    ts = Column(DateTime, default=func.now(), nullable=False)
    api_version = Column(String, nullable=True)
    
    messages = relationship("UsrMessages", back_populates="sessions")

    def __init__(self, id=None):
        if id:
            self.id = id
            self.api_version = API_VERSION
        else:
            self.id = str(uuid.uuid4())
            self.api_version = API_VERSION

class UsrMessages(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    session_id = Column(UUID, ForeignKey('sessions.id'), nullable=False)
    ts = Column(DateTime, default=func.now(), nullable=False)
    user_name = Column(String, nullable=True)
    user_message = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    language = Column(String, nullable=True)
    tokens_used = Column(JSON, nullable=False)
    state = Column(JSON, nullable=False)


    sessions = relationship("UsrSession", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "ts": self.ts,
            "user_name": self.user_name,
            "user_message": self.user_message,
            "answer": self.answer,
            "language": self.language,
            "tokens_used": self.tokens_used,
            "state": self.state,
        }

#product_models = {"answer_hogar": AnswerHogar}