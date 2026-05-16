from typing import Dict
from HomeService.agents.booking_agent import BookingAgent
from HomeService.agents.consultation_agent import ConsultationAgent
from HomeService.agents.recommendation_agent import RecommendationAgent

INTENT_MAP = {
    "预约": "booking",
    "改约": "reschedule",
    "取消": "cancel",
    "价格": "pricing",
    "报价": "pricing",
    "咨询": "consultation",
    "服务": "consultation",
    "推荐": "recommendation",
    "复购": "recommendation",
    "历史": "recommendation",
}

class RouterAgent:
    def __init__(self):
        self.booking_agent = BookingAgent()
        self.consultation_agent = ConsultationAgent()
        self.recommendation_agent = RecommendationAgent()

    def detect_intent(self, message: str) -> str:
        for keyword, intent in INTENT_MAP.items():
            if keyword in message:
                return intent
        return "consultation"

    def route(self, user_id: int, message: str) -> Dict:
        intent = self.detect_intent(message)

        if intent == "booking":
            reply = self.booking_agent.handle_booking(user_id, message)
        elif intent == "recommendation":
            reply = self.recommendation_agent.recommend(user_id, message)
        else:
            reply = self.consultation_agent.handle_consultation(message)

        return {
            "intent": intent,
            "reply": reply,
            "metadata": {"route": intent}
        }
