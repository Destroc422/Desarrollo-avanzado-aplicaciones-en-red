from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import require_staff
from ..database.session import get_db
from ..models.service_addon import ServiceAddonModel
from ..models.user import UserModel
from ..schemas.service_addon import ServiceAddonCreate, ServiceAddonRead, ServiceAddonUpdate


router = APIRouter(prefix="/service-addons", tags=["service-addons"])


@router.get("", response_model=list[ServiceAddonRead])
def list_service_addons(db: Session = Depends(get_db)):
    return (
        db.query(ServiceAddonModel)
        .filter(ServiceAddonModel.is_active.is_(True))
        .order_by(ServiceAddonModel.name.asc())
        .all()
    )


@router.get("/admin", response_model=list[ServiceAddonRead])
def list_service_addons_admin(
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    return db.query(ServiceAddonModel).order_by(ServiceAddonModel.name.asc()).all()


@router.post("", response_model=ServiceAddonRead, status_code=status.HTTP_201_CREATED)
def create_service_addon(
    payload: ServiceAddonCreate,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = ServiceAddonModel(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un servicio adicional con ese nombre.")
    db.refresh(row)
    return row


@router.put("/{addon_id}", response_model=ServiceAddonRead)
def update_service_addon(
    addon_id: int,
    payload: ServiceAddonUpdate,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = db.query(ServiceAddonModel).filter(ServiceAddonModel.id == addon_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró el servicio adicional.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un servicio adicional con ese nombre.")
    db.refresh(row)
    return row


@router.delete("/{addon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_addon(
    addon_id: int,
    db: Session = Depends(get_db),
    staff: UserModel = Depends(require_staff),
):
    row = db.query(ServiceAddonModel).filter(ServiceAddonModel.id == addon_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No se encontró el servicio adicional.")
    # Soft-delete so that old order snapshots remain understandable.
    row.is_active = False
    db.commit()
