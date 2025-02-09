from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import Contact
from database import SessionLocal, engine, Base
from sqlalchemy import or_
import uvicorn

class IdentifyRequest(BaseModel):
    email: str|None = None
    phoneNumber: str|None = None

app = FastAPI()

@app.post("/identify")
def identify_contact(request: IdentifyRequest):
    db = SessionLocal()
    try:
        if not request.email and not request.phoneNumber:
            raise HTTPException(status_code=400, detail="At least one of email or phoneNumber is required")

        filters = []
        if request.email:
            filters.append(Contact.email == request.email)
        if request.phoneNumber:
            filters.append(Contact.phoneNumber == request.phoneNumber)

        existing_contacts = db.query(Contact).filter(or_(*filters)).all() if filters else []
        
        if existing_contacts:
            ## Existing contact
            primary_contacts = {}
            emails = set()
            phone_numbers = set()
            primary_contact = None
            secondaryContactIds = []

            for contact in existing_contacts:
                if contact.linkPrecedence == "primary":
                    primary_contacts[contact.id] = contact
                else:
                    if contact.linkedId not in primary_contacts:
                        primary_contacts[contact.linkedId] = contact.linked_contact

                emails.add(contact.email)
                phone_numbers.add(contact.phoneNumber)
            
            if len(primary_contacts) > 1:
                ## If there are multiple primary contacts, we assign the oldest one as primary and the rest as secondary
                sorted_primaries = sorted(primary_contacts.values(), key=lambda c: c.createdAt)
                oldest_primary = sorted_primaries[0]
                newer_primary = sorted_primaries[1]

                newer_primary.linkPrecedence = "secondary"
                newer_primary.linkedId = oldest_primary.id
                db.commit()
                
                # Update all secondary contacts linked to newer primary to point to oldest primary
                db.query(Contact).filter(Contact.linkedId == newer_primary.id).update({"linkedId": oldest_primary.id})
                db.commit()

                primary_contact = oldest_primary
            else:
                primary_contact = list(primary_contacts.values())[0]
            
            if (request.email and request.email not in emails) or (request.phoneNumber and request.phoneNumber not in phone_numbers):
                ## If new information is introduced, create a new secondary contact
                new_contact = Contact(
                    phoneNumber=request.phoneNumber,
                    email=request.email,
                    linkedId=primary_contact.id,
                    linkPrecedence="secondary"
                )
                db.add(new_contact)
                db.commit()
                db.refresh(new_contact)

                emails.add(new_contact.email)
                phone_numbers.add(new_contact.phoneNumber)
            
            secondary_contacts = db.query(Contact).filter(Contact.linkedId == primary_contact.id).all()
            
            for contact in secondary_contacts:
                emails.add(contact.email)
                phone_numbers.add(contact.phoneNumber)
                secondaryContactIds.append(contact.id)
            
            if primary_contact.email in emails:
                emails.remove(primary_contact.email)
            if primary_contact.phoneNumber in phone_numbers:
                phone_numbers.remove(primary_contact.phoneNumber)
            emails = [primary_contact.email] + list(filter(None, emails))
            phone_numbers = [primary_contact.phoneNumber] + list(filter(None, phone_numbers))

            return {
                "contact": {
                    "primaryContactId": primary_contact.id,
                    "emails": emails,
                    "phoneNumbers": phone_numbers,
                    "secondaryContactIds": secondaryContactIds
                }
            }
        else:
            ## Not an existing contact
            new_contact = Contact(
                phoneNumber=request.phoneNumber,
                email=request.email,
                linkPrecedence="primary"
            )
            db.add(new_contact)
            db.commit()
            db.refresh(new_contact)
        
            return {
                "contact": {
                    "primaryContactId": new_contact.id,
                    "emails": [new_contact.email] if new_contact.email else [],
                    "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
                    "secondaryContactIds": []
                }
            }
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    