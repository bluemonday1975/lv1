# app/main.py

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from .database import SessionLocal, engine
from . import models, crud, schemas

# データベースセッションの依存性注入用関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 商品検索APIエンドポイント
@app.get("/products/{prd_code}", response_model=Optional[schemas.ProductResponse])
def get_product_by_code(prd_code: str, db: Session = Depends(get_db)):
    product = crud.get_product_by_code(db, prd_code)
    if product is None:
        return None  # 対象が見つからなかった場合はNoneを返す
    return product

# 購入APIエンドポイント
@app.post("/transactions/", response_model=dict)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    try:
        # 1-1 取引テーブルへの登録
        new_transaction = models.Transaction(
            datetime=datetime.utcnow(),
            emp_cd=transaction.emp_cd,
            store_cd=transaction.store_cd,
            pos_no=transaction.pos_no,
            total_amt=0  # 初期値として0を設定
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        print(f"New transaction ID: {new_transaction.trd_id}")  # デバッグ用のprint文
        
        total_amount = 0

        # 1-2 取引明細テーブルへの登録と合計金額計算 (1-3も含む)
        for detail in transaction.details:
            new_detail = models.TransactionDetail(
                trd_id=new_transaction.trd_id,
                prd_id=detail.prd_id,
                prd_code=detail.prd_code,
                prd_name=detail.prd_name,
                prd_price=detail.prd_price,
                tax_cd='10',  # 税率10%を固定として設定
                ttl_amt_ex_tax=int(detail.prd_price * 1.1)  # 税込み金額を計算
            )
            db.add(new_detail)
            total_amount += detail.prd_price * 1.1  # 税込み金額を合計に追加
        
        # 1-4 取引テーブルの合計金額を更新
        new_transaction.total_amt = total_amount
        db.commit()

        # 1-5 合計金額をフロントエンドに返す
        return {"success": True, "total_amount": total_amount}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
