from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from db import Base
import enum

class PlanType(str, enum.Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"
    PREMIUM = "PREMIUM"

class GenerationType(str, enum.Enum):
    HOOK = "hook"
    CAPTION = "caption"
    HASHTAG = "hashtag"
    EMOTION = "emotion"
    COMPLETE = "complete"

# Quotas mensais por plano
PLAN_QUOTAS = {
    PlanType.FREE: 10,
    PlanType.BASIC: 100,
    PlanType.PRO: 500,
    PlanType.PREMIUM: 2000
}

# Preços mensais em reais
PLAN_PRICES = {
    PlanType.FREE: 0,
    PlanType.BASIC: 29,
    PlanType.PRO: 79,
    PlanType.PREMIUM: 199
}

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    api_keys = relationship("ApiKey", back_populates="user")
    generations = relationship("Generation", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    plan_type = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    monthly_quota = Column(Integer, default=10, nullable=False)
    used_quota = Column(Integer, default=0, nullable=False)
    last_reset = Column(DateTime, server_default=func.now())
    
    # Relacionamento
    user = relationship("User", back_populates="subscription")
    
    def reset_quota(self):
        """Reseta a quota mensal"""
        self.used_quota = 0
        self.last_reset = func.now()
    
    def can_generate(self) -> bool:
        """Verifica se ainda tem quota disponível"""
        return self.used_quota < self.monthly_quota
    
    def remaining_quota(self) -> int:
        """Retorna quota restante"""
        return max(0, self.monthly_quota - self.used_quota)

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), default="Default Key")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_used = Column(DateTime)
    
    # Relacionamento
    user = relationship("User", back_populates="api_keys")

class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(GenerationType), nullable=False)
    input_data = Column(String(4096))  # JSON string
    output_data = Column(String(8192))  # JSON string
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamento
    user = relationship("User", back_populates="generations")

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
