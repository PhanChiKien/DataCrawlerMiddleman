from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings
import uuid

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Company(Base):
    __tablename__ = "company"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    company_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)

    # Relationship
    job_postings = relationship("JobPosting", back_populates="company")


class JobPosting(Base):
    __tablename__ = "job_posting"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.company_id'), nullable=True)
    job_title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    salary = Column(Integer, nullable=True)
    pay_period = Column(String, nullable=True)  # hourly, monthly, yearly
    work_type = Column(String, nullable=True)  # Fulltime, Parttime, Contract, Season
    experience_level = Column(String, nullable=True)  # Intern, Fresher, Junior, Senior, Executive
    location = Column(String, nullable=True)
    applies = Column(Integer, nullable=True)
    listed_time = Column(DateTime, nullable=True)
    currency = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    url = Column(String, nullable=True)
    crawled_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="job_postings")
    benefits = relationship("Benefit", back_populates="job_posting")


class Benefit(Base):
    __tablename__ = "benefit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey('job_posting.job_id'), nullable=False)
    type = Column(String, nullable=True)
    inferred = Column(String, nullable=True)

    # Relationship
    job_posting = relationship("JobPosting", back_populates="benefits")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
