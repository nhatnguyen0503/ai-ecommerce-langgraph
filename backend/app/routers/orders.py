from fastapi import APIRouter, Depends
from typing import Annotated

from app.dependencies import get_order_service
from app.services.order_service import OrderService
from app.schemas import OrderOut, ReturnEligibilityOut

router = APIRouter(prefix="/orders", tags=["orders"])

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.get("", response_model=list[OrderOut])
def list_orders(service: OrderServiceDep):
    return service.list_orders()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, service: OrderServiceDep):
    return service.get_order(order_id)


@router.get("/{order_id}/return-eligibility", response_model=ReturnEligibilityOut)
def get_return_eligibility(order_id: str, service: OrderServiceDep):
    return service.check_return(order_id)
