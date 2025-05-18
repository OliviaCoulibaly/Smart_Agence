from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas

# CRUD operations for Agents
def get_agent(db: Session, agent_id: int):
    return db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()

def get_agent_by_email(db: Session, email: str):
    return db.query(models.Agent).filter(models.Agent.email == email).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Agent).offset(skip).limit(limit).all()

def create_agent(db: Session, agent: schemas.AgentCreate):
    db_agent = models.Agent(
        nom=agent.nom,
        prenoms=agent.prenoms,
        annee_naissance=agent.annee_naissance,
        categorie=agent.categorie,
        email=agent.email,
        telephone=agent.telephone,
        date_enregistrement=datetime.now()
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_agent(db: Session, agent_id: int, agent: schemas.AgentCreate):
    db_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if db_agent:
        for key, value in agent.dict().items():
            setattr(db_agent, key, value)
        db.commit()
        db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: int):
    db_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False

# CRUD operations for Tickets
def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()

def get_tickets(db: Session, skip: int = 0, limit: int = 100, agent_id: int = None, categorie: str = None):
    query = db.query(models.Ticket)
    
    if agent_id:
        query = query.filter(models.Ticket.agent_id == agent_id)
    if categorie:
        query = query.filter(models.Ticket.categorie_service == categorie)
        
    return query.offset(skip).limit(limit).all()

def create_ticket(db: Session, ticket: schemas.TicketCreate):
    db_ticket = models.Ticket(
        agent_id=ticket.agent_id,
        categorie_service=ticket.categorie_service,
        description=ticket.description,
        date_creation=datetime.now()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Création automatique d'un premier événement avec statut "pending"
    db_event = models.TicketEvent(
        agent_id=ticket.agent_id,
        ticket_id=db_ticket.ticket_id,
        statut=models.TicketStatus.PENDING,
        date=datetime.now().date(),
        heure=datetime.now()
    )
    db.add(db_event)
    db.commit()
    
    return db_ticket

def update_ticket(db: Session, ticket_id: int, ticket: schemas.TicketCreate):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket:
        for key, value in ticket.dict().items():
            setattr(db_ticket, key, value)
        db.commit()
        db.refresh(db_ticket)
    return db_ticket

# CRUD operations for Ticket Events
def create_ticket_event(db: Session, event: schemas.TicketEventCreate):
    db_event = models.TicketEvent(
        agent_id=event.agent_id,
        ticket_id=event.ticket_id,
        statut=event.statut,
        date=datetime.now().date(),
        heure=datetime.now()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_ticket_events(db: Session, ticket_id: int):
    return db.query(models.TicketEvent).filter(models.TicketEvent.ticket_id == ticket_id).all()

def get_latest_ticket_status(db: Session, ticket_id: int):
    return db.query(models.TicketEvent).filter(
        models.TicketEvent.ticket_id == ticket_id
    ).order_by(models.TicketEvent.heure.desc()).first()