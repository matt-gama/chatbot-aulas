from ..models import *
from ..connection import init_db



def filter_lead(phone:str, message:list) -> Lead:
    db = init_db()
    if not db:
        raise(Exception("Não consegui conectar com database"))
    
    try:
        lead = db.query(Lead).filter(Lead.phone == phone).first()
        if not lead:
            print(f"Nenhum Lead encontrada com esse telefone {phone}")
            return None
        
        historico = lead.message
        if not historico:
            historico = []
        
        historico.append(message)

        lead.message = historico
        db.commit()
        db.refresh(lead)

        print(f"Lead Localizado e conversa atalizada: {lead.name} - {lead.phone}")

        return lead
    
    except Exception as ex:
        print(f"Error > {ex}")
    
    finally:
        if db:
            db.close()

    return None

def update_lead(lead_id:int, message:list) -> bool:
    db = init_db()
    if not db:
        raise(Exception("Não consegui conectar com database"))
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            print(f"Nenhum Lead encontrada com esse id {lead_id}")
            return False
        
        historico = lead.message
        if not historico:
            historico = []
        
        historico.append(message)

        lead.message = historico
        db.commit()
        db.refresh(lead)

        print(f"Lead Localizado e conversa atalizada: {lead.name} - {lead.phone}")

        return True
    
    except Exception as ex:
        print(f"Error > {ex}")
    
    finally:
        if db:
            db.close()

    return False

def new_lead(ia_id:int, name:str, phone:str, message:list) -> Lead:
    db = init_db()
    if not db:
        raise(Exception("Não consegui conectar com database"))
    
    try:
        lead = Lead(
            ia_id = int(ia_id),
            phone=phone,
            name = name,
            message = message
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        print(f"Novo Lead [id: {lead.id}, Name: {lead.name}] da IA {lead.ia_id} Cadastrado com sucesso!")
        
        return lead
    
    except Exception as ex:
        print(f"Error > {ex}")
    
    finally:
        if db:
            db.close()

    return None