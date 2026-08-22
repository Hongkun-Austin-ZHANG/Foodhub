from pydantic import BaseModel


class CapabilitiesResponse(BaseModel):
    demo_available: bool
    live_scan_available: bool
    supported_languages: list[str] = ["en", "zh", "fr"]
