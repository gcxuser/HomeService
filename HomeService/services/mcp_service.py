from typing import Dict, Optional
from datetime import datetime
import hashlib

class MCPService:
    def get_location(self, city: str, district: str, community: str = "", detail_address: str = "") -> Dict[str, Optional[float]]:
        normalized = f"{city} {district} {community} {detail_address}".strip()
        key = hashlib.md5(normalized.encode("utf-8")).hexdigest()
        lat = (int(key[:6], 16) % 9000) / 100.0 + 10.0
        lng = (int(key[6:12], 16) % 18000) / 100.0 + 100.0
        return {
            "address": normalized,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "map_hint": f"已解析地址为 {normalized}，经纬度({round(lat,6)},{round(lng,6)})",
        }

    def schedule_calendar_event(self, user_id: int, order_id: int, title: str, start: datetime, end: datetime, description: str) -> Dict:
        return {
            "user_id": user_id,
            "order_id": order_id,
            "title": title,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": description,
            "status": "scheduled",
            "calendar_source": "MCP Calendar Connector (模拟)",
        }

    def send_notification(self, user_id: int, phone: str, title: str, message: str) -> Dict:
        return {
            "user_id": user_id,
            "phone": phone,
            "title": title,
            "message": message,
            "delivered": True,
            "channel": "SMS/通知中心 (模拟)",
        }
