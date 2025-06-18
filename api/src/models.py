from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .database import engine
from .database import Base

class AgentCategory(str, enum.Enum):
    TRANSACTION = "transaction"
    CONSEIL = "conseil"

class TicketStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenoms = Column(String, index=True)
    annee_naissance = Column(Integer)
    categorie = Column(String, Enum(AgentCategory))
    date_enregistrement = Column(DateTime, default=datetime.now)
    email = Column(String, unique=True, index=True)
    telephone = Column(String)

    tickets = relationship("Ticket", back_populates="agent", cascade="all, delete-orphan")
    events = relationship("TicketEvent", back_populates="agent", cascade="all, delete-orphan")

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id", ondelete="CASCADE"))
    date_creation = Column(DateTime, default=datetime.now)
    categorie_service = Column(String)
    description = Column(String, nullable=True)

    agent = relationship("Agent", back_populates="tickets")
    events = relationship("TicketEvent", back_populates="ticket", cascade="all, delete-orphan")

class TicketEvent(Base):
    __tablename__ = "ticket_events"

    event_id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id", ondelete="CASCADE"))
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now().date)
    heure = Column(DateTime, default=datetime.now)
    statut = Column(String, Enum(TicketStatus))

    agent = relationship("Agent", back_populates="events")
    ticket = relationship("Ticket", back_populates="events")

Base.metadata.create_all(bind=engine)
