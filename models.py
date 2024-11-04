from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, BigInteger

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(BigInteger, primary_key=True)
    chat_name = Column(String)
    date_added = Column(DateTime(timezone=True), default=func.now())


class ChatConfiguration(Base):
    __tablename__ = 'chat_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey('chat.id'))
    ssh_host = Column(String, nullable=True)
    ssh_port = Column(Integer, nullable=True)
    ssh_user = Column(String, nullable=True)
    ssh_password = Column(String, nullable=True)


