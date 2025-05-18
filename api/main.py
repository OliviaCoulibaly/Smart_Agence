from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from api.src import models, schemas, crud  # type: ignore
from api.src.database import engine, get_db  # type: ignore

# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Smart Agence API",
    description="API pour la gestion des agents et des tickets clients",
    version="1.0.0",
)

# ✅ Route de test
@app.get("/")
def root():
    return {"message": "Bienvenue dans Smart Agence API"}

# --- Routes Agents ---
@app.post("/agents/", response_model=schemas.Agent)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = crud.get_agent_by_email(db, email=agent.email)
    if db_agent:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    return crud.create_agent(db=db, agent=agent)

@app.get("/agents/", response_model=List[schemas.Agent])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_agents(db, skip=skip, limit=limit)

@app.get("/agents/{agent_id}", response_model=schemas.Agent)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return db_agent

@app.put("/agents/{agent_id}", response_model=schemas.Agent)
def update_agent(agent_id: int, agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = crud.update_agent(db, agent_id=agent_id, agent=agent)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return db_agent

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    success = crud.delete_agent(db, agent_id=agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return {"detail": "Agent supprimé avec succès"}

# --- Routes Tickets ---
@app.post("/tickets/", response_model=schemas.Ticket)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db=db, ticket=ticket)

@app.get("/tickets/", response_model=List[schemas.Ticket])
def read_tickets(
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[int] = None,
    categorie: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_tickets(db, skip=skip, limit=limit, agent_id=agent_id, categorie=categorie)

@app.get("/tickets/{ticket_id}", response_model=schemas.Ticket)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = crud.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    return db_ticket

@app.put("/tickets/{ticket_id}", response_model=schemas.Ticket)
def update_ticket(ticket_id: int, ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = crud.update_ticket(db, ticket_id=ticket_id, ticket=ticket)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    return db_ticket

@app.post("/tickets/{ticket_id}/status", response_model=schemas.TicketEvent)
def update_ticket_status(ticket_id: int, event: schemas.TicketEventCreate, db: Session = Depends(get_db)):
    db_ticket = crud.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket non trouvé")
    return crud.create_ticket_event(db=db, event=event)

@app.get("/tickets/{ticket_id}/events", response_model=List[schemas.TicketEvent])
def read_ticket_events(ticket_id: int, db: Session = Depends(get_db)):
    return crud.get_ticket_events(db, ticket_id=ticket_id)

#  Bloc de démarrage local corrigé
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
