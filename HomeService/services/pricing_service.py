from typing import Dict

SERVICE_BASE_PRICES = {
    "daily_cleaning": 120.0,
    "deep_cleaning": 220.0,
    "move_out_cleaning": 280.0,
    "appliance_cleaning": 150.0,
}

class PricingService:
    def estimate_price(self, service_type: str, area: float, extras: Dict[str, bool]) -> Dict[str, float]:
        base_price = SERVICE_BASE_PRICES.get(service_type, 140.0)
        price_per_sqm = 2.5 if service_type == "daily_cleaning" else 3.5
        area_price = max(area, 20.0) * price_per_sqm
        extra_fee = 0.0
        note_parts = [f"基础服务：{service_type}"]

        if extras.get("kitchen"):
            extra_fee += 80.0
            note_parts.append("包含厨房清洗")
        if extras.get("bathroom"):
            extra_fee += 60.0
            note_parts.append("包含卫生间除垢")
        if extras.get("window"):
            extra_fee += 50.0
            note_parts.append("包含擦玻璃")
        if extras.get("pet"):
            extra_fee += 40.0
            note_parts.append("宠物友好服务")

        estimated_price = round(base_price + area_price + extra_fee, 2)
        estimated_duration = round(max(2.0, area / 30.0 + len([k for k, v in extras.items() if v]) * 0.5), 1)
        note = "; ".join(note_parts)

        return {
            "price": estimated_price,
            "duration": estimated_duration,
            "note": note
        }
