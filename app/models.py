from sqlalchemy import Column, Integer, String, Float, BigInteger, create_engine
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
