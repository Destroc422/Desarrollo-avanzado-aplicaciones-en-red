import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_staff
from ..core.config import (
    FRONTEND_URL,
    WOMPI_ENVIRONMENT,
    WOMPI_EVENTS_SECRET,
    WOMPI_INTEGRITY_SECRET,
    WOMPI_PUBLIC_KEY,
)
from ..database.session import get_db
from ..models.cocktail import CocktailModel
from ..models.order import OrderModel
from ..models.service_addon import ServiceAddonModel
from ..models.user import UserModel
from ..schemas.order import OrderCreate, OrderRead, OrderStatusUpdate


router = APIRouter(prefix="/orders", tags=["orders"])
_CHECKOUT_BASE = "https://checkout.wompi.co/p/"


def _decode_snapshot(value: str) -> list[dict]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def _read_order(row: OrderModel, customer: UserModel | None = None) -> OrderRead:
    return OrderRead(
        id=row.id,
        items=_decode_snapshot(row.items_json),
        addons=_decode_snapshot(row.addons_json),
        total_cop=row.total_cop,
        payment_method=row.payment_method,
        payment_status=row.payment_status,
        status=row.status,
        delivery_address=row.delivery_address,
        delivery_scheduled_at=row.delivery_scheduled_at,
        delivery_notes=row.delivery_notes,
        additional_service=row.additional_service,
        created_at=row.created_at,
        customer_username=customer.username if customer else None,
        customer_name=customer.full_name if customer else None,
        customer_email=customer.email if customer else None,
        customer_phone=customer.phone if customer else None,
    )


def _order_for_user(db: Session, order_id: int, user: UserModel) -> OrderModel:
    row = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not row or (user.role not in {"admin", "editor"} and row.user_id != user.id):
        raise HTTPException(status_code=404, detail="No se encontró el pedido.")
    return row


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    quantities: dict[int, int] = {}
    for line in payload.items:
        quantities[line.cocktail_id] = quantities.get(line.cocktail_id, 0) + line.quantity
    if any(quantity > 30 for quantity in quantities.values()):
        raise HTTPException(status_code=422, detail="No puedes pedir más de 30 unidades del mismo producto.")
    products = {
        row.id: row
        for row in db.query(CocktailModel)
        .filter(CocktailModel.id.in_(quantities.keys()), CocktailModel.is_available.is_(True))
        .all()
    }
    if len(products) != len(quantities):
        raise HTTPException(status_code=409, detail="Uno o más productos ya no están disponibles.")

    addons = []
    if payload.addon_ids:
        addons = (
            db.query(ServiceAddonModel)
            .filter(ServiceAddonModel.id.in_(payload.addon_ids), ServiceAddonModel.is_active.is_(True))
            .all()
        )
        if len(addons) != len(payload.addon_ids):
            raise HTTPException(status_code=409, detail="Uno o más servicios adicionales ya no están disponibles.")

    item_snapshot = []
    total_cop = 0
    for product_id, quantity in quantities.items():
        row = products[product_id]
        line_total = row.price_cop * quantity
        total_cop += line_total
        item_snapshot.append({
            "cocktail_id": row.id,
            "name": row.name,
            "quantity": quantity,
            "unit_price_cop": row.price_cop,
            "line_total_cop": line_total,
        })
    addon_snapshot = []
    for addon in addons:
        total_cop += addon.price_cop
        addon_snapshot.append({"addon_id": addon.id, "name": addon.name, "price_cop": addon.price_cop})

    if payload.delivery_scheduled_at:
        scheduled = payload.delivery_scheduled_at
        now = datetime.now(timezone.utc)
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        if scheduled <= now:
            raise HTTPException(status_code=422, detail="La hora programada debe ser futura.")

    row = OrderModel(
        user_id=user.id,
        items_json=json.dumps(item_snapshot, ensure_ascii=False),
        addons_json=json.dumps(addon_snapshot, ensure_ascii=False),
        total_cop=total_cop,
        payment_method=payload.payment_method,
        payment_status="pending" if payload.payment_method == "wompi" else "cash_on_delivery",
        status="received",
        payment_reference="grillo-" + secrets.token_urlsafe(18),
        delivery_address=payload.delivery_address.strip(),
        delivery_scheduled_at=payload.delivery_scheduled_at,
        delivery_notes=payload.delivery_notes.strip(),
        additional_service=payload.additional_service.strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _read_order(row)


@router.get("/mine", response_model=list[OrderRead])
def list_my_orders(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    rows = (
        db.query(OrderModel)
        .filter(OrderModel.user_id == user.id)
        .order_by(OrderModel.created_at.desc())
        .all()
    )
    return [_read_order(row) for row in rows]


@router.get("/admin", response_model=list[OrderRead])
def list_all_orders(
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    rows = db.query(OrderModel).order_by(OrderModel.created_at.desc()).limit(500).all()
    users = {user.id: user for user in db.query(UserModel).filter(UserModel.id.in_({r.user_id for r in rows})).all()} if rows else {}
    return [_read_order(row, users.get(row.user_id)) for row in rows]


@router.get("/{order_id}/payment-config")
def payment_config(
    order_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    row = _order_for_user(db, order_id, user)
    if row.payment_method != "wompi":
        raise HTTPException(status_code=409, detail="Este pedido no usa pago en línea.")
    if row.payment_status == "paid":
        raise HTTPException(status_code=409, detail="El pedido ya aparece pagado.")
    if not WOMPI_PUBLIC_KEY or not WOMPI_INTEGRITY_SECRET:
        raise HTTPException(status_code=503, detail="El pago en línea aún no está configurado.")
    amount_in_cents = row.total_cop * 100
    signature_source = f"{row.payment_reference}{amount_in_cents}COP{WOMPI_INTEGRITY_SECRET}"
    integrity = hashlib.sha256(signature_source.encode("utf-8")).hexdigest()
    params = {
        "public-key": WOMPI_PUBLIC_KEY,
        "currency": "COP",
        "amount-in-cents": amount_in_cents,
        "reference": row.payment_reference,
        "signature:integrity": integrity,
        "redirect-url": f"{FRONTEND_URL}/?pedido={row.id}",
    }
    return {
        "public_key": WOMPI_PUBLIC_KEY,
        "currency": "COP",
        "amount_in_cents": amount_in_cents,
        "reference": row.payment_reference,
        "integrity_signature": integrity,
        "checkout_url": _CHECKOUT_BASE + "?" + urlencode(params),
        "environment": WOMPI_ENVIRONMENT,
        "payment_status": row.payment_status,
    }


def _nested_value(root: dict, dotted_path: str):
    current = root
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


@router.post("/wompi-webhook", status_code=status.HTTP_200_OK)
async def wompi_webhook(request: Request, db: Session = Depends(get_db)):
    if not WOMPI_EVENTS_SECRET:
        raise HTTPException(status_code=503, detail="El receptor de eventos de pago no está configurado.")
    try:
        event = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="El evento recibido no es válido.")
    if event.get("event") != "transaction.updated":
        return {"received": True}

    data = event.get("data") or {}
    transaction = data.get("transaction") or {}
    signature = event.get("signature") or {}
    properties = signature.get("properties")
    timestamp = event.get("timestamp")
    checksum = signature.get("checksum") or request.headers.get("X-Event-Checksum")
    if not isinstance(properties, list) or not timestamp or not checksum:
        raise HTTPException(status_code=400, detail="El evento no incluye una firma completa.")
    signed_values = []
    for prop in properties:
        if not isinstance(prop, str):
            raise HTTPException(status_code=400, detail="La firma del evento no es válida.")
        value = _nested_value(data, prop)
        if value is None:
            raise HTTPException(status_code=400, detail="La firma del evento no es válida.")
        signed_values.append(str(value))
    source = "".join(signed_values) + str(timestamp) + WOMPI_EVENTS_SECRET
    expected = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(expected.lower(), str(checksum).lower()):
        raise HTTPException(status_code=401, detail="La firma del evento de pago no es válida.")

    reference = transaction.get("reference")
    row = db.query(OrderModel).filter(OrderModel.payment_reference == reference).first()
    if not row:
        return {"received": True}
    if row.payment_transaction_id and row.payment_transaction_id != str(transaction.get("id", "")):
        raise HTTPException(status_code=409, detail="El pedido ya tiene una transacción asociada.")
    transaction_amount = transaction.get("amount_in_cents")
    transaction_currency = transaction.get("currency")
    if transaction_amount != row.total_cop * 100 or transaction_currency != "COP":
        raise HTTPException(status_code=409, detail="El valor de la transacción no coincide con el pedido.")
    row.payment_transaction_id = str(transaction.get("id") or "") or None
    transaction_status = str(transaction.get("status", "")).upper()
    if transaction_status == "APPROVED":
        row.payment_status = "paid"
        if row.status == "received":
            row.status = "confirmed"
    elif transaction_status in {"DECLINED", "ERROR", "VOIDED"}:
        row.payment_status = "failed"
    db.commit()
    return {"received": True}


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró el pedido.")
    if payload.status == "confirmed" and row.payment_method == "wompi" and row.payment_status != "paid":
        raise HTTPException(status_code=409, detail="Confirma el pedido cuando Wompi haya aprobado el pago.")
    row.status = payload.status
    db.commit()
    db.refresh(row)
    return _read_order(row, db.query(UserModel).filter(UserModel.id == row.user_id).first())
