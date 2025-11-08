from fastapi import APIRouter, Depends, HTTPException, status
import joblib
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_session
from app.models import Ticker
from app.schemas import TickerList, TickerPartialUpdate, TickerPublic, TickerSchema, PredictSchema, TickerSchemaPut
from src.data_ingestion import download_stock_data
from datetime import datetime
import os
from src.predict import get_prediction

router = APIRouter(
    prefix="/api/v1/tickers",
    tags=["tickers"],
)

# RENT_MODEL = joblib.load("model/rent_model.pkl")
RENT_MODEL = "model/rent_model.pkl"

@router.post(
    path="register/",
    summary="Create a new ticker",
    response_description="The created ticker",  
    status_code=status.HTTP_201_CREATED,
    response_model=TickerSchema,
)
def create_ticker(ticker: TickerSchema, 
                 session: Session = Depends(get_session)):

    df = download_stock_data(ticker.ticket, ticker.date)
    if df is None or df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível obter dados para o ticker '{ticker.ticket}'."
        )

    # 🔹 Busca todas as datas existentes de uma vez (evita queries dentro do loop)
    existing_dates = {
        t.date for t in session.query(Ticker.date)
                            .filter(Ticker.ticket == ticker.ticket)
                            .all()
    }

    tickers_to_insert = []

    for _, row in df.iterrows():
        row_date = datetime.strptime(row["date"], "%Y-%m-%d").date()

        if row_date in existing_dates:
            continue

        ticker_data = Ticker(
            ticket=ticker.ticket,
            date=row_date,
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
            volume=row["volume"],
        )
        tickers_to_insert.append(ticker_data)

    if not tickers_to_insert:
        existing_ticker = (
            session.query(Ticker)
            .filter(Ticker.ticket == ticker.ticket)
            .order_by(Ticker.date.desc())
            .first()
        )
        return existing_ticker
    session.add_all(tickers_to_insert)
    session.commit()
    return tickers_to_insert[-1]

@router.get(
    path="register/",
    summary="List all tickers",
    response_description="A list of tickers",
    response_model=TickerList,
    status_code=status.HTTP_200_OK,
)
def list_ticker(session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    query = session.scalars(select(Ticker).offset(offset).limit(limit))
    tickers = query.all()
    return {"tickers": tickers}

@router.get(
    path="register/{ticker_id}",
    summary="List a ticker by ID",
    response_description="A ticker by ID",
    response_model=TickerPublic,
    status_code=status.HTTP_200_OK,
)
def get_ticker(ticker_id: int, session: Session = Depends(get_session)):
    query = session.get(Ticker, ticker_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticker not found") 
    return query

@router.put(
    path="register/{ticker_id}",
    summary="Update a ticker by ID",
    response_description="The updated ticker",
    response_model=TickerPublic,
    status_code=status.HTTP_201_CREATED,
)
def update_ticker(ticker_id: int, 
                 ticker: TickerSchemaPut, 
                 session: Session = Depends(get_session)):
    query = session.get(Ticker, ticker_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticker not found")
    
    for field, value in ticker.model_dump().items():
        setattr(query, field, value)
    
    session.commit()
    session.refresh(query)
    return query

@router.patch(
    path="register/{ticker_id}",
    summary="Partially update a ticker by ID",
    response_description="The updated ticker",
    response_model=TickerPublic,
    status_code=status.HTTP_201_CREATED,
)
def patch_ticker(ticker_id: int, 
                ticker: TickerPartialUpdate, 
                session: Session = Depends(get_session)):
    query = session.get(Ticker, ticker_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticker not found")
    update_data = {k: v for k, v in ticker.model_dump(exclude_unset=True).items()}
    for field, value in update_data.items():
        setattr(query, field, value)
    
    session.commit()
    session.refresh(query)
    return query

@router.delete(
    path="register/{ticker_id}",
    summary="Delete a ticker by ID",
    response_description="A message confirming deletion",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticker(ticker_id: int, session: Session = Depends(get_session)):
    query = session.get(Ticker, ticker_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="House not found")
    session.delete(query)
    session.commit()

@router.post(
    path="predict/",
    summary="Predict rental cost based on property features",
    response_description="Predicted rental cost",  
    status_code=status.HTTP_200_OK,
)
def predict_ticker(ticker: PredictSchema, session: Session = Depends(get_session)):
    return get_prediction(ticker.ticket, session)

    # input_data = pd.DataFrame([ticker.model_dump()])
    # predicted_rent = float(RENT_MODEL.predict(input_data)[0])
    # ticker_db = Ticker(**ticker.model_dump(), rent_amount=predicted_rent)
    
    # session.add(ticker_db)
    # session.commit()
    # session.refresh(ticker_db)
    # return {"predicted_rent": predicted_rent}

