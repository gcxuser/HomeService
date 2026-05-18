from typing import Dict, Optional
from HomeService.agents.booking_agent import BookingAgent
from HomeService.agents.consultation_agent import ConsultationAgent
from HomeService.agents.recommendation_agent import RecommendationAgent
from HomeService.eval.bert_classifier import HybridIntentDetector

# 全局混合检测器实例
_hybrid_detector: Optional[HybridIntentDetector] = None


def get_hybrid_detector() -> HybridIntentDetector:
    """获取混合检测器单例"""
    global _hybrid_detector
    if _hybrid_detector is None:
        _hybrid_detector = HybridIntentDetector()
    return _hybrid_detector

# 意图优先级定义（数字越小优先级越高）
INTENT_PRIORITY = {
    "reschedule": 1,
    "cancel": 1,
    "booking": 2,
    "recommendation": 3,
    "consultation": 4,
}

# 高优先级意图关键词（优先级1）
HIGH_PRIORITY_KEYWORDS = {
    "reschedule": {"改约", "改时间", "修改预约", "预约改期", "变更预约", "换时间", "改期", "换约",
                   "换个时间", "调整时间", "改一下时间", "换一个时间", "时间改", "改时间预约",
                   "时间换", "改约时间", "预约换时间", "改预约", "预约日期改", "预约改日", "预约换日期",
                   "预约改时间", "预约时间调整", "预约时间需要改", "预约时间可以改", "预约时间变更",
                   "预约时间更改", "预约时间修改", "预约日期更改", "预约日期修改", "预约时段改",
                   "预约时段调整", "预约时段更换", "预约换时间", "预约换日期", "预约更换时间",
                   "预约可以改", "预约能改", "预约想改", "预约要改", "预约需改", "预约调整",
                   "预约换", "预约变更", "预约修改", "预约改", "预约变", "改一下预约时间",
                   "调整预约时间", "调整预约日", "预约调整时间", "预约调整日", "预约时间换",
                   "预约换时间", "换个预约时间", "换个预约日", "预约时间调", "预约调时间",
                   "预约调日", "预约时间改", "预约时间变更", "预约时间修改", "预约时间调整",
                   "预约时间更改", "换预约时间", "换预约日", "换预约时段"},
    "cancel": {"取消", "退预约", "退单", "不做了", "不要了", "撤回", "作废", "退掉", "废掉",
               "删掉", "撤销", "取消这个", "取消掉", "取消预约服务", "预约取消", "取消订单",
               "取消预约", "取消服务", "取消这次", "取消本次", "取消一下", "取消掉", "取消了",
               "取消掉预约", "取消掉订单", "取消掉服务", "取消掉家政", "取消掉保洁", "取消掉上门",
               "取消上门服务", "取消保洁预约", "取消家政预约", "取消这次预约", "取消上次"},
    "recommendation": {"推荐", "推荐服务", "有什么推荐", "推荐一下", "推荐点", "推荐一些",
                       "复购", "再次购买", "再买", "老客户", "历史", "历史订单", "我的订单",
                       "上次服务", "上次", "过去", "订单", "记录", "服务记录", "推荐内容",
                       "有推荐吗", "给我推荐", "建议", "推荐类型", "服务推荐", "上次做了什么",
                       "我上次", "推荐几次", "推荐几次服务", "推荐服务类型", "推荐服务内容",
                       "上次做了什么服务", "最近的服务", "最近做了什么", "上次的订单", "历史订单",
                       "过去订单", "订单记录", "服务记录", "复购", "再次购买", "再购买", "老客户",
                       "老客户服务", "会员服务", "推荐老客户"},
}

INTENT_MAP = {
    # =========================================
    # 预约相关意图 (booking)
    # =========================================
    "预约": "booking",
    "预约家政": "booking",
    "家政预约": "booking",
    "保洁预约": "booking",
    "预约保洁": "booking",
    "预约保洁服务": "booking",
    "需要预约": "booking",
    "想预约": "booking",
    "预定": "booking",
    "订": "booking",
    "下单": "booking",
    "下单家政": "booking",
    "家政下单": "booking",
    "叫保洁": "booking",
    "叫家政": "booking",
    "叫阿姨": "booking",
    "叫一个": "booking",
    "叫一名": "booking",
    "安排保洁": "booking",
    "安排家政": "booking",
    "安排一次": "booking",
    "请安排": "booking",
    "上门保洁": "booking",
    "上门家政": "booking",
    "找保洁": "booking",
    "找家政": "booking",
    # =========================================
    # 预约相关意图变体 (booking) - service variant
    # =========================================
    "家政服务预约": "booking",
    "保洁服务预约": "booking",
    "请保洁": "booking",
    "请家政": "booking",
    "保姆": "booking",
    "钟点工": "booking",
    "保洁员": "booking",
    "钟点": "booking",
    "小时工": "booking",
    "上门": "booking",
    "上门服务": "booking",
    " hire ": "booking",  # 英文
    # =========================================
    # 预约相关意图变体 (booking)
    # =========================================
    "预约一个": "booking",
    "预约一名": "booking",
    "预约一次": "booking",
    "预约家政服务": "booking",
    "预约一个保洁": "booking",
    "预约一个保洁服务": "booking",
    "预约一次保洁": "booking",
    "预约一名保洁": "booking",
    "预约一次家政": "booking",
    "预约一名家政": "booking",
    "预约一个家政": "booking",
    "预约一个家政服务": "booking",
    "预约一个保洁员": "booking",
    "预约一个钟点工": "booking",
    "预约一个钟点": "booking",
    "预约一次钟点工": "booking",
    "预约上门保洁": "booking",
    "预约上门家政": "booking",
    "预约一次上门": "booking",
    "预约上门": "booking",
    # =========================================
    # 咨询相关意图变体(设备家政/保洁服务等词，也要匹配为booking)
    # =========================================
    "家政服务": "booking",
    "保洁服务": "booking",
    "上门服务": "booking",
    # =========================================
    # 咨询相关意图(具体为咨询服务时才匹配)
    # =========================================
    "服务内容有哪些": "consultation",
    "服务项目有哪些": "consultation",
    "服务内容": "consultation",
    "服务项目": "consultation",
    "服务类型": "consultation",
    "服务种类": "consultation",
    "有什么服务": "consultation",
    "服务有哪些": "consultation",
    "家政服务项目": "consultation",
    "服务内容有哪些": "consultation",
    "服务项目有哪些": "consultation",
    "说明": "consultation",
    "介绍": "consultation",
    "详情": "consultation",
    "具体": "consultation",
    "明细": "consultation",
    "清单": "consultation",
    "项目": "consultation",
    "类型": "consultation",
    "种类": "consultation",
    "详情介绍": "consultation",
    # =========================================
    # 预约相关意图变体2 (booking) - with service
    # =========================================
    "预定家政服务": "booking",
    "预定保洁服务": "booking",
    "预定家政": "booking",
    "预定保洁": "booking",
    "预定一个家政服务": "booking",
    "预定一个保洁服务": "booking",
    "预定一次家政服务": "booking",
    "预定一次保洁服务": "booking",
    "预定一次家政": "booking",
    "预定一次保洁": "booking",
    "预定一名家政服务": "booking",
    "预定一名保洁服务": "booking",
    "预定一个家政": "booking",
    "预定一个保洁": "booking",
    "预定一次": "booking",
    "预定一名": "booking",
    "预定一个": "booking",
    "下单家政服务": "booking",
    "下单保洁服务": "booking",
    "下单一次家政": "booking",
    "下单一次保洁": "booking",
    "下单一个家政": "booking",
    "下单一个保洁": "booking",
    "下单一名家政": "booking",
    "下单一名保洁": "booking",
    "安排一个家政服务": "booking",
    "安排一个保洁服务": "booking",
    "安排一次家政": "booking",
    "安排一次保洁": "booking",
    "安排一次家政服务": "booking",
    "安排一次保洁服务": "booking",
    "安排一名家政": "booking",
    "安排一名保洁": "booking",
    "安排一个家政": "booking",
    "安排一个保洁": "booking",
    "请安排一个家政": "booking",
    "请安排一个保洁": "booking",
    "请安排一次家政": "booking",
    "请安排一次保洁": "booking",
    "请安排一名家政": "booking",
    "请安排一名保洁": "booking",
    "请安排一次家政服务": "booking",
    "请安排一次保洁服务": "booking",
    "请安排一个家政服务": "booking",
    "请安排一个保洁服务": "booking",

    # =========================================
    # 改约相关意图 (reschedule)
    # =========================================
    "改约": "reschedule",
    "改时间": "reschedule",
    "修改预约": "reschedule",
    "预约改期": "reschedule",
    "变更预约": "reschedule",
    "换时间": "reschedule",
    "改期": "reschedule",
    "换约": "reschedule",
    "换个时间": "reschedule",
    "调整时间": "reschedule",
    "改一下时间": "reschedule",
    "换一个时间": "reschedule",
    "时间改": "reschedule",
    "改时间预约": "reschedule",
    "时间换": "reschedule",
    "改约时间": "reschedule",
    "预约换时间": "reschedule",

    # =========================================
    # 取消相关意图 (cancel)
    # =========================================
    "取消": "cancel",
    "取消预约": "cancel",
    "取消订单": "cancel",
    "取消服务": "cancel",
    "退预约": "cancel",
    "退单": "cancel",
    "不做了": "cancel",
    "不要了": "cancel",
    "撤回": "cancel",
    "作废": "cancel",
    "退掉": "cancel",
    "废掉": "cancel",
    "删掉": "cancel",
    "撤销": "cancel",
    "取消这个": "cancel",
    "取消掉": "cancel",
    "取消预约服务": "cancel",
    "预约取消": "cancel",
    # =========================================
    # 取消相关意图变体 (cancel)
    # =========================================
    "取消上门服务": "cancel",
    "取消保洁预约": "cancel",
    "取消家政预约": "cancel",
    "取消这次预约": "cancel",
    "取消本次预约": "cancel",
    "取消一下预约": "cancel",
    "取消了预约": "cancel",
    "取消掉预约": "cancel",
    "取消掉家政": "cancel",
    "取消掉保洁": "cancel",
    "取消掉上门": "cancel",
    "取消掉服务": "cancel",
    "取消掉一次": "cancel",
    "取消掉一名": "cancel",
    "取消掉一个": "cancel",
    "取消掉保洁服务": "cancel",
    "取消掉上门服务": "cancel",
    "取消掉家政服务": "cancel",
    "取消掉一次服务": "cancel",
    "取消掉一次家政": "cancel",
    "取消掉一次保洁": "cancel",
    "取消掉一名家政": "cancel",
    "取消掉一名保洁": "cancel",
    "取消掉一个家政": "cancel",
    "取消掉一个保洁": "cancel",

    # =========================================
    # 价格/报价相关意图 - 映射到 booking
    # =========================================
    "价格": "booking",
    "多少钱": "booking",
    "价位": "booking",
    "定价": "booking",
    "费用": "booking",
    "报价": "booking",
    "多少钱一小时": "booking",
    "一小时多少钱": "booking",
    "价格是多少": "booking",
    "收费多少": "booking",
    "计费方式": "booking",
    "费用怎么算": "booking",
    "价格表": "booking",
    "收费标准": "booking",
    "付费": "booking",
    "付款": "booking",
    "怎么付款": "booking",
    "钱": "booking",
    "费用是多少": "booking",

    # =========================================
    # 咨询/服务相关意图 (consultation)
    # =========================================
    "服务": "consultation",
    "内容": "consultation",
    "详情": "consultation",
    "具体": "consultation",
    "介绍": "consultation",
    "说明": "consultation",
    "清单": "consultation",
    "明细": "consultation",
    "项目": "consultation",
    "类型": "consultation",
    "种类": "consultation",
    "服务项目": "consultation",
    "服务内容": "consultation",
    "服务类型": "consultation",
    "服务种类": "consultation",
    "服务内容有哪些": "consultation",
    "服务项目有哪些": "consultation",
    "有哪些服务": "consultation",
    "什么服务": "consultation",
    "提供什么": "consultation",
    "做什么": "consultation",
    "能做什么": "consultation",
    "有什么服务": "consultation",
    "家政服务": "consultation",
    "保洁服务": "consultation",
    "服务有哪些": "consultation",
    "家政服务项目": "consultation",
    "有什么": "consultation",
    "哪些": "consultation",
    "详情介绍": "consultation",
    # =========================================
    # 咨询相关意图变体 (consultation) - price/pricing variants
    # =========================================
    "收费价格": "consultation",
    "费用多少": "consultation",
    "服务定价": "consultation",
    "服务价格表": "consultation",
    "价格多少": "consultation",
    "计费多少": "consultation",

    # =========================================
    # 推荐/复购相关意图 (recommendation)
    # =========================================
    "推荐": "recommendation",
    "推荐服务": "recommendation",
    "有什么推荐": "recommendation",
    "推荐一下": "recommendation",
    "推荐点": "recommendation",
    "推荐一些": "recommendation",
    "复购": "recommendation",
    "再次购买": "recommendation",
    "再买": "recommendation",
    "老客户": "recommendation",
    "历史": "recommendation",
    "历史订单": "recommendation",
    "我的订单": "recommendation",
    "上次服务": "recommendation",
    "上次": "recommendation",
    "过去": "recommendation",
    "订单": "recommendation",
    "记录": "recommendation",
    "服务记录": "recommendation",
    "推荐内容": "recommendation",
    "有推荐吗": "recommendation",
    "给我推荐": "recommendation",
    "建议": "recommendation",
    "推荐类型": "recommendation",
    "服务推荐": "recommendation",
    # =========================================
    # 推荐/复购相关意图变体 (recommendation)
    # =========================================
    "推荐我": "recommendation",
    "推荐一下我": "recommendation",
    "给我推荐": "recommendation",
    "推荐点我": "recommendation",
    "推荐一点": "recommendation",
    "推荐一下服务": "recommendation",
    "推荐一下家政": "recommendation",
    "推荐一下保洁": "recommendation",
    "推荐家政服务": "recommendation",
    "推荐保洁服务": "recommendation",
    "推荐一些服务": "recommendation",
    "推荐一些家政": "recommendation",
    "有什么好推荐": "recommendation",
    "有没有推荐": "recommendation",
    "推荐什么": "recommendation",
    "可以推荐": "recommendation",
    "推荐试一下": "recommendation",
    "推荐一下试试": "recommendation",
    "推荐我试试": "recommendation",
    "上次做啥了": "recommendation",
    "上次做了啥": "recommendation",
    "上次的服务": "recommendation",
    "最近的服务": "recommendation",
    "最近做了什么": "recommendation",
    "最近有没有服务": "recommendation",
    "复购服务": "recommendation",
    "复购家政": "recommendation",
    "复购保洁": "recommendation",
    "再购买": "recommendation",
    "再买一次": "recommendation",
    "再约一次": "recommendation",
    "再次预约": "recommendation",
    "再次安排": "recommendation",
    "再安排一次": "recommendation",
    "老客户优惠": "recommendation",
    "老客户服务": "recommendation",
    "会员推荐": "recommendation",
    "上次的订单": "recommendation",
    "历史的订单": "recommendation",
    "过去订单": "recommendation",
}


def _detect_intent_with_priority(message: str) -> str:
    """基于优先级的意图检测"""
    # 首先检查高优先级关键词
    for intent, keywords in HIGH_PRIORITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message:
                return intent

    # 然后按关键词长度降序匹配（避免短词优先匹配问题）
    sorted_map = sorted(INTENT_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for keyword, intent in sorted_map:
        if keyword in message:
            return intent
    return "consultation"


class RouterAgent:
    def __init__(self):
        self.booking_agent = BookingAgent()
        self.consultation_agent = ConsultationAgent()
        self.recommendation_agent = RecommendationAgent()

    def detect_intent(self, message: str) -> str:
        """混合检测 - 关键词优先，BERT辅助"""
        detector = get_hybrid_detector()
        return detector.detect_intent(message)

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
