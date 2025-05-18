from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

# Enum pour les catégories d'agents
class AgentCategory(str, Enum):
    TRANSACTION = "transaction"
    CONSEIL = "conseil"

# Enum pour les statuts de tickets
class TicketStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

# Schémas pour les Agents
class AgentBase(BaseModel):
    nom: str
    prenoms: str
    annee_naissance: int
    categorie: AgentCategory
    email: str
    telephone: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    agent_id: int
    date_enregistrement: datetime

    class Config:
        from_attributes = True

# Schémas pour les Tickets
class TicketBase(BaseModel):
    agent_id: int  # requis à la création
    categorie_service: str
    description: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class Ticket(BaseModel):  # schéma de retour
    ticket_id: int
    agent_id: Optional[int] = None  # ← corrigé ici
    categorie_service: str
    description: Optional[str] = None
    date_creation: datetime

    class Config:
        from_attributes = True

# Schémas pour les événements de ticket
class TicketEventBase(BaseModel):
    agent_id: int
    ticket_id: int
    statut: TicketStatus

class TicketEventCreate(TicketEventBase):
    pass

class TicketEvent(BaseModel):
    event_id: int
    agent_id: Optional[int] = None  # ← corrigé ici aussi
    ticket_id: int
    statut: TicketStatus
    date: datetime
    heure: datetime

    class Config:
        from_attributes = True
