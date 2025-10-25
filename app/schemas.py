from typing import Optional
from pydantic import BaseModel
from datetime import date
 
class TickerSchema(BaseModel):
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
    ticket: Optional[str] = None
    date: Optional[date] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None


class TickerList(BaseModel):
    tickers: list[TickerPublic]


class PredictSchema(BaseModel):
    ticket: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float