from fastapi import APIRouter

from ..core.config import (
    BUSINESS_ADDRESS,
    BUSINESS_EMAIL,
    BUSINESS_FACEBOOK,
    BUSINESS_INSTAGRAM,
    BUSINESS_NAME,
    BUSINESS_PHONE,
    BUSINESS_TIKTOK,
)


router = APIRouter(prefix="/business-info", tags=["business"])


@router.get("")
def read_business_info():
    return {
        "name": BUSINESS_NAME,
        "about": (
            "El Grillo reúne en un catálogo digital sus bebidas, cócteles y servicios "
            "para facilitar la consulta y la gestión de pedidos."
        ),
        "phone": BUSINESS_PHONE or None,
        "email": BUSINESS_EMAIL or None,
        "address": BUSINESS_ADDRESS or None,
        "instagram": BUSINESS_INSTAGRAM or None,
        "facebook": BUSINESS_FACEBOOK or None,
        "tiktok": BUSINESS_TIKTOK or None,
    }
