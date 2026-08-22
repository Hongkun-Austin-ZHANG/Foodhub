from fastapi import APIRouter

from core.config import get_settings
from schemas.system import CapabilitiesResponse

router = APIRouter(tags=["system"])


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def capabilities() -> CapabilitiesResponse:
    settings = get_settings()
    return CapabilitiesResponse(
        demo_available=settings.demo_available,
        live_scan_available=settings.live_scan_available,
    )
