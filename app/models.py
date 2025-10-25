from sqlalchemy import Column, Integer, String, Float, Date, BigInteger

from app.database import Base


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    ticket = Column(String, nullable=False)
    date = Column(Date, nullable=False) 
    open = Column(Float) 
    high = Column(Float) 
    low = Column(Float) 
    close = Column(Float) 
    volume = Column(BigInteger)
    