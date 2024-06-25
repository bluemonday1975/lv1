# app/crud.py

from sqlalchemy.orm import Session
from . import models

def get_product_by_code(db: Session, prd_code: str):
    return db.query(models.Product).filter(models.Product.prd_code == prd_code).first()

def create_transaction(db: Session, transaction: models.Transaction):
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def create_transaction_detail(db: Session, transaction_detail: models.TransactionDetail):
    db.add(transaction_detail)
    db.commit()
    return transaction_detail
