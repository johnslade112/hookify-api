"""
Sistema de quota e rate limiting por plano
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import User, Subscription, Generation, GenerationType, PLAN_QUOTAS
import json

class QuotaExceeded(HTTPException):
    """Exceção customizada para quota excedida"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota mensal excedida. Faça upgrade do seu plano para continuar.",
            headers={"X-Quota-Exceeded": "true"}
        )

def check_and_update_quota(
    user: User,
    db: Session,
    generation_type: GenerationType,
    input_data: dict = None,
    output_data: dict = None
) -> int:
    """
    Verifica se o usuário tem quota disponível e atualiza o contador.
    Retorna a quota restante após a operação.
    
    Raises:
        QuotaExceeded: Se a quota mensal foi excedida
    """
    
    subscription = user.subscription
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem assinatura ativa"
        )
    
    # Verifica se precisa resetar a quota (novo mês)
    if should_reset_quota(subscription):
        reset_monthly_quota(subscription, db)
    
    # Verifica se ainda tem quota
    if not subscription.can_generate():
        raise QuotaExceeded()
    
    # Incrementa o uso
    subscription.used_quota += 1
    
    # Registra a geração no histórico
    generation = Generation(
        user_id=user.id,
        type=generation_type,
        input_data=json.dumps(input_data, ensure_ascii=False) if input_data else None,
        output_data=json.dumps(output_data, ensure_ascii=False) if output_data else None,
        tokens_used=0  # Pode ser atualizado depois se necessário
    )
    db.add(generation)
    db.commit()
    db.refresh(subscription)
    
    return subscription.remaining_quota()

def should_reset_quota(subscription: Subscription) -> bool:
    """Verifica se a quota deve ser resetada (novo mês)"""
    if not subscription.last_reset:
        return True
    
    now = datetime.utcnow()
    last_reset = subscription.last_reset
    
    # Reseta se passou mais de 30 dias
    return (now - last_reset) > timedelta(days=30)

def reset_monthly_quota(subscription: Subscription, db: Session):
    """Reseta a quota mensal"""
    subscription.used_quota = 0
    subscription.last_reset = datetime.utcnow()
    db.commit()

def get_quota_info(user: User) -> dict:
    """Retorna informações sobre a quota do usuário"""
    subscription = user.subscription
    
    if not subscription:
        return {
            "plan": "NONE",
            "monthly_quota": 0,
            "used_quota": 0,
            "remaining_quota": 0,
            "percentage_used": 0
        }
    
    # Verifica se precisa resetar
    if should_reset_quota(subscription):
        return {
            "plan": subscription.plan_type.value,
            "monthly_quota": subscription.monthly_quota,
            "used_quota": 0,
            "remaining_quota": subscription.monthly_quota,
            "percentage_used": 0,
            "needs_reset": True
        }
    
    remaining = subscription.remaining_quota()
    percentage = (subscription.used_quota / subscription.monthly_quota * 100) if subscription.monthly_quota > 0 else 0
    
    return {
        "plan": subscription.plan_type.value,
        "monthly_quota": subscription.monthly_quota,
        "used_quota": subscription.used_quota,
        "remaining_quota": remaining,
        "percentage_used": round(percentage, 2),
        "last_reset": subscription.last_reset.isoformat() if subscription.last_reset else None
    }

def upgrade_plan(user: User, new_plan: str, db: Session) -> Subscription:
    """Faz upgrade do plano do usuário"""
    from models import PlanType
    
    subscription = user.subscription
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinatura não encontrada"
        )
    
    try:
        plan_type = PlanType(new_plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plano inválido. Opções: {[p.value for p in PlanType]}"
        )
    
    # Atualiza o plano
    subscription.plan_type = plan_type
    subscription.monthly_quota = PLAN_QUOTAS[plan_type]
    subscription.is_active = True
    
    # Se for upgrade, mantém o uso atual
    # Se for downgrade, reseta (pode ser ajustado conforme regra de negócio)
    if PLAN_QUOTAS[plan_type] < subscription.monthly_quota:
        subscription.used_quota = min(subscription.used_quota, PLAN_QUOTAS[plan_type])
    
    db.commit()
    db.refresh(subscription)
    
    return subscription
