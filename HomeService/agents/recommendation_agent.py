from HomeService.services.user_behavior_service import UserBehaviorService
from typing import Dict

class RecommendationAgent:
    def __init__(self):
        self.behavior_service = UserBehaviorService()

    def recommend(self, user_id: int, message: str) -> str:
        insights = self.behavior_service.analyze_user_behavior(user_id)
        repeat = self.behavior_service.recommend_repeat_service(user_id)

        if "复购" in message or "推荐" in message or "下次" in message:
            return (
                f"根据您的历史订单，系统建议：{repeat['recommendation']}\n"
                f"常见原因：{'; '.join(repeat['reasons'])}\n"
                f"最近一次服务：{repeat['last_order']['service_item'] if repeat.get('last_order') else '无'}"
            )

        return (
            f"用户行为分析：{insights.get('total_orders',0)} 次订单，完成 {insights.get('completed_orders',0)} 次。"
            f" 最常预约服务：{insights.get('frequent_service','暂无')}."
        )
