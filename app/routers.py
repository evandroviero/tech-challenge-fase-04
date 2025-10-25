from fastapi import APIRouter, Depends, HTTPException, status
import joblib
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_session
from app.models import Ticker
from app.schemas import TickerList, TickerPartialUpdate, TickerPublic, TickerSchema, PredictSchema


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
    response_model=TickerPublic,
)
def create_ticker(ticker: TickerSchema, 
                 session: Session = Depends(get_session)):

    existing_ticker = session.query(Ticker).filter(
        Ticker.ticket == ticker.ticket,
        Ticker.date == ticker.date
    ).first()
    if existing_ticker:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ticker '{ticker.ticket}' already exists for date '{ticker.date}'."
        )
    
    ticker = Ticker(**ticker.model_dump())
    session.add(ticker)
    session.commit()
    session.refresh(ticker)
    return ticker

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
                 ticker: TickerSchema, 
                 session: Session = Depends(get_session)):
    query = session.get(Ticker, ticker_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="House not found")
    
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
    update_data = {k: v for k, v in house.model_dump(exclude_unset=True).items()}
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
    input_data = pd.DataFrame([ticker.model_dump()])
    predicted_rent = float(RENT_MODEL.predict(input_data)[0])
    ticker_db = Ticker(**ticker.model_dump(), rent_amount=predicted_rent)
    
    session.add(ticker_db)
    session.commit()
    session.refresh(ticker_db)
    return {"predicted_rent": predicted_rent}