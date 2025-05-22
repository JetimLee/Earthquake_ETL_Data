from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    BigInteger,
    DateTime,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create the base class for declarative models
Base = declarative_base()


class Earthquake(Base):
    __tablename__ = "earthquakes"

    id = Column(Integer, primary_key=True)
    time = Column(BigInteger)
    place = Column(String)
    magnitude = Column(Float)
    longitude = Column(Float)
    latitude = Column(Float)
    depth = Column(Float)
    file_name = Column(String)

    def __repr__(self):
        return f"<Earthquake(time={self.time}, place='{self.place}', magnitude={self.magnitude})>"


class StageEarthquake(Base):
    __tablename__ = "stage_earthquakes"

    id = Column(Integer, primary_key=True)
    dt = Column(DateTime, index=True)
    region = Column(String(255))
    place = Column(String(255))
    magnitude = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    depth = Column(Float)
    raw_time = Column(BigInteger)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<StageEarthquake(dt={self.dt}, place='{self.place}', magnitude={self.magnitude})>"
