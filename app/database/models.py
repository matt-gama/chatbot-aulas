from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.service.crypto import decrypt_data

Base = declarative_base()

class IA(Base):
    __tablename__ = 'ias'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prompts = relationship("Prompt", back_populates="ia")
    ia_config = relationship("IAConfig", back_populates="ia", uselist=False)
    leads = relationship("Lead", back_populates="ia", uselist=False)

    @property
    def active_prompt(self):
        active = [p for p in self.prompts if p.is_active]
        return active[0] if active else None
    

class IAConfig(Base):
    __tablename__ = 'ia_config'
    id = Column(Integer, primary_key=True, index=True)
    ia_id = Column(Integer, ForeignKey('ias.id'), nullable=False)
    channel = Column(String, nullable=False)
    ai_api = Column(String, nullable=False)
    # Armazena as credenciais criptografadas em formato JSON
    encrypted_credentials = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento com a IA correspondente
    ia = relationship("IA", back_populates="ia_config")

    @property
    def credentials(self):
        """
        Retorna as credenciais já descriptografadas.
        """
        return decrypt_data(self.encrypted_credentials)


class Prompt(Base):
    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True, index=True)
    ia_id = Column(Integer, ForeignKey('ias.id'), nullable=False)
    prompt_text = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento inverso com IA
    ia = relationship("IA", back_populates="prompts")


class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True, index=True)
    ia_id = Column(Integer, ForeignKey('ias.id'), nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True, unique=True)
    # O campo 'message' armazenará uma lista de dicionários
    message = Column(MutableList.as_mutable(JSON), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    ia = relationship("IA", back_populates="leads")