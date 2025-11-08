from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
  
def today() -> date:
    return date.today()

class TickerSchema(BaseModel):
    ticket: str
    date: date
    # open: float
    # high: float
    # low: float
    # close: float
    # volume: float

class TickerSchemaPut(BaseModel):
    ticket: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float

class TickerPublic(BaseModel):
    id: int
    ticket: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float

class TickerPartialUpdate(BaseModel):
    ticket: str = Field(default="PETR4.SA")  
    trade_date: date = Field(default_factory=date.today, alias="date")
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None

    class Config:
        allow_population_by_field_name = True  


class TickerList(BaseModel):
    tickers: list[TickerPublic]


class PredictSchema(BaseModel):
    ticket: str