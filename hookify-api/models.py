from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from db import Base

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(16), unique=True, index=True, nullable=False)
    url = Column(String(2048), nullable=False)
    utm_source = Column(String(64))
    utm_medium = Column(String(64))
    utm_campaign = Column(String(64))
    clicks = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("code", name="uq_links_code"),)
