import re
from typing import Dict, Optional

SERVICE_SYNONYMS = {
    "日常保洁": "daily_cleaning",
    "深度保洁": "deep_cleaning",
    "开荒保洁": "move_out_cleaning",
    "家电清洗": "appliance_cleaning",
    "擦玻璃": "window_cleaning",
}

REQUIRED_FIELDS = [
    "service_type",
    "area",
    "city",
    "district",
    "preferred_date",
    "contact_phone",
]

class BookingState:
    def __init__(self):
        self.data: Dict[str, Optional[str]] = {
            "service_type": None,
            "area": None,
            "city": None,
            "district": None,
            "preferred_date": None,
            "contact_name": None,
            "contact_phone": None,
            "extras": {},
        }

    def is_complete(self) -> bool:
        return all(self.data.get(field) for field in REQUIRED_FIELDS)

    def missing_fields(self) -> list:
        return [field for field in REQUIRED_FIELDS if not self.data.get(field)]

    def update_from_message(self, message: str) -> None:
        for keyword, value in SERVICE_SYNONYMS.items():
            if keyword in message:
                self.data["service_type"] = value
                break

        area_match = re.search(r"(\d+(?:\.\d+)?)\s*(平|平方米|m²)", message)
        if area_match:
            self.data["area"] = area_match.group(1)

        if "上海" in message:
            self.data["city"] = "上海"
        elif "北京" in message:
            self.data["city"] = "北京"
        elif "广州" in message:
            self.data["city"] = "广州"
        elif "深圳" in message:
            self.data["city"] = "深圳"

        district_match = re.search(r"([\u4e00-\u9fa5]{2,4}(区|市|县))", message)
        if district_match:
            self.data["district"] = district_match.group(1)

        date_keywords = ["今天", "明天", "后天", "周一", "周二", "周三", "周四", "周五", "周六", "周日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        if any(kw in message for kw in date_keywords):
            self.data["preferred_date"] = message.strip()

        phone_match = re.search(r"1\d{10}", message)
        if phone_match:
            self.data["contact_phone"] = phone_match.group(0)

        name_match = re.search(r"(我叫|我是)([\u4e00-\u9fa5]{2,4})", message)
        if name_match:
            self.data["contact_name"] = name_match.group(2)

        if "厨房" in message:
            self.data["extras"]["kitchen"] = True
        if "卫生间" in message or "洗手间" in message:
            self.data["extras"]["bathroom"] = True
        if "擦玻璃" in message or "玻璃" in message:
            self.data["extras"]["window"] = True
        if "宠物" in message:
            self.data["extras"]["pet"] = True

    def clear(self) -> None:
        self.__init__()
