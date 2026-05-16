from HomeService.services.pricing_service import PricingService
from HomeService.services.scheduling_service import SchedulingService
from HomeService.services.catalog_service import CatalogService
from HomeService.services.worker_service import WorkerService
from HomeService.agents.booking_state import BookingState
from typing import Dict

class BookingAgent:
    def __init__(self):
        self.pricing_service = PricingService()
        self.scheduling_service = SchedulingService()
        self.catalog_service = CatalogService()
        self.worker_service = WorkerService()
        self.states: Dict[int, BookingState] = {}

    def _get_state(self, user_id: int) -> BookingState:
        if user_id not in self.states:
            self.states[user_id] = BookingState()
        return self.states[user_id]

    def handle_booking(self, user_id: int, message: str) -> str:
        state = self._get_state(user_id)
        state.update_from_message(message)

        if not state.data["service_type"]:
            return "请问您需要哪种家政服务？例如：日常保洁、深度保洁、开荒保洁、家电清洗。"
        if not state.data["area"]:
            return "请告诉我房屋大概多少平米，便于我估算时长和价格。"
        if not state.data["city"] or not state.data["district"]:
            return "请提供服务地址所在城市和区，例如：上海浦东或北京朝阳。"
        if not state.data["preferred_date"]:
            return "请告诉我您希望的服务时间，比如“周六上午”或“明天下午”。"
        if not state.data["contact_phone"]:
            return "请提供一个联系电话，我们需要用于订单确认和服务通知。"

        service_type = state.data["service_type"]
        area = float(state.data["area"])
        estimate = self.pricing_service.estimate_price(service_type, area, state.data["extras"])
        slots = self.scheduling_service.get_available_slots(
            state.data["city"], state.data["district"], service_type, state.data["preferred_date"]
        )
        workers = self.worker_service.find_workers(state.data["city"], state.data["district"], service_type)
        worker_names = ", ".join([worker["name"] for worker in workers[:2]]) if workers else "暂无推荐师傅"

        summary = [
            f"服务类型：{service_type}",
            f"房屋面积：{area} 平米",
            f"服务区域：{state.data['city']} {state.data['district']}",
            f"预约时间：{state.data['preferred_date']}",
            f"预计价格：{estimate['price']} 元",
            f"预计时长：{estimate['duration']} 小时",
            f"推荐师傅：{worker_names}",
        ]

        return (
            "我已帮您初步整理预约信息：\n"
            + "\n".join(summary)
            + "\n\n如果您确认这些信息无误，请回复“确认预约”，我会帮您继续创建订单；"
            + "如需修改某项内容，请直接告诉我。"
        )

    def reset_booking(self, user_id: int) -> None:
        if user_id in self.states:
            self.states[user_id].clear()
