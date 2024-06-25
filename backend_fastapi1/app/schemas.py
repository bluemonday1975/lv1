# app/schemas.py

from pydantic import BaseModel
from typing import List, Optional

class ProductResponse(BaseModel):
    prd_id: int
    prd_code: str
    name: str
    price: int

    class Config:
        orm_mode = True

class TransactionDetailCreate(BaseModel):
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int

class TransactionCreate(BaseModel):
    emp_cd: Optional[str] = '9999999999'
    store_cd: str = '30'
    pos_no: str = '90'
    details: List[TransactionDetailCreate]
