"""数据增强脚本 - 生成大量意图测试数据用于评估"""

import json
import random
from typing import List, Dict

# 意图模板定义
INTENT_TEMPLATES = {
    "booking": [
        # 基础预约
        "我想预约家政服务",
        "预约保洁",
        "预约家政",
        "我要预约保洁服务",
        "需要预约一个保洁",
        "预约上门保洁",
        "预约家政保洁",
        "家政预约",
        "保洁预约",
        "上门保洁预约",
        # 详细预约
        "我想预约一个保洁服务，怎么操作",
        "请问可以预约保洁吗",
        "预约家政服务需要什么流程",
        "预约保洁安排在什么时候",
        "预约完后怎么付款",
        # 各种表达方式
        "订一个保洁服务",
        "下个保洁单子",
        "安排一次保洁",
        "叫一个保洁上门",
        "预约一次家政",
        "预约家政服务",
        # 地域相关
        "北京预约保洁",
        "上海家政预约",
        "杭州预约家政服务",
        "广州保洁预约",
        # 时间相关
        "这周预约保洁",
        "周末预约家政",
        "下周预约保洁服务",
        "明天预约一个保洁",
        # 服务类型
        "预约日常保洁",
        "预约深度保洁",
        "预约开荒保洁",
        "预约家电清洗",
    ],

    "reschedule": [
        # 基础改约
        "我想改约时间",
        "预约时间可以改吗",
        "改预约",
        "改预约时间",
        "修改预约",
        "变更预约",
        "预约要改期",
        "预约时间调整",
        # 详细改约
        "之前预约的时间可以改吗",
        "能不能换一个时间",
        "预约时间需要调整一下",
        "改约服务时间",
        "预约时间有变动",
        # 其他表达
        "换时间预约",
        "换个时段",
        "改个时间",
        "预约时间变了",
        "预约需要改期",
    ],

    "cancel": [
        # 基础取消
        "取消预约",
        "取消服务",
        "取消订单",
        "取消家政",
        "取消保洁",
        " cancellation",
        "取消上门服务",
        # 详细取消
        "我想取消预约的服务",
        "预约的服务能取消吗",
        "取消预约订单",
        "取消这个家政预约",
        "预约取消流程",
        # 其他表达
        "不做了，取消预约",
        "取消这次预约",
        "预约不作了",
        "取消服务预约",
        "预约作废",
    ],

    "consultation": [
        # 基础咨询
        "有什么服务",
        "服务项目有哪些",
        "家政服务内容",
        "能提供什么服务",
        "有哪些保洁服务",
        "服务种类",
        "服务类型",
        "服务项目",
        # 详细咨询
        "你们提供哪些服务",
        "家政都能做什么",
        "服务包括哪些内容",
        "服务范围是什么",
        "服务有哪些类别",
        # 其他表达
        "服务怎么收费",
        "收费价格",
        "怎么计费",
        "费用多少",
        "服务定价",
        "服务价格表",
    ],

    "recommendation": [
        # 基础推荐
        "推荐服务",
        "有什么推荐",
        "推荐我一些服务",
        "家政推荐",
        "推荐家政服务",
        "推荐保洁",
        # 历史推荐
        "我上次做了什么服务",
        "我的历史订单",
        "最近的服务",
        "以前的订单",
        "服务记录",
        # 复购推荐
        "复购服务",
        "再次购买",
        "老客户优惠",
        "会员服务",
        "推荐老客户",
        # 其他表达
        "有什么好推荐",
        "推荐几次服务",
        "服务推荐",
        "家政推荐服务",
        "保洁推荐",
    ],
}

# 关键词增强
KEYWORD_EXTENSIONS = {
    "booking": ["上门", "家庭", "保洁员", "阿姨", "师傅", "专业", "正规", "高质量", "优质", "靠谱"],
    "reschedule": ["换", "改", "调整", "变更", "挪", "推迟", "延后", "提前", "换个时间"],
    "cancel": ["不做了", "不要了", "撤回", "作废", "退掉", "废掉", "删掉", "撤销"],
    "consultation": ["详情", "具体", "详细", "介绍", "说明", "内容", "项目", "清单", "明细"],
    "recommendation": ["好的", "不错", "推荐一下", "看看", "介绍", "介绍服务", "介绍家政"],
}


def generate_intent_training_data(intent: str, num_samples: int = 400) -> List[str]:
    """为指定意图生成大量训练样本"""
    templates = INTENT_TEMPLATES.get(intent, [])
    extensions = KEYWORD_EXTENSIONS.get(intent, [])
    samples = []

    for i in range(num_samples):
        template = random.choice(templates)

        # 随机添加后缀（更少的后缀，保持句子规范性）
        if random.random() > 0.85 and extensions:
            suffix = random.choice(extensions)
            sample = template + suffix
        else:
            sample = template

        # 随机替换部分词语（更少的替换，保持句子规范性）
        replacements = {
            "家政": ["保洁", "清洁"],
            "预约": ["预定", "下单", "安排"],
            "服务": ["项目", "内容"],
        }
        for original, alternatives in replacements.items():
            if original in sample and random.random() > 0.6:
                sample = sample.replace(original, random.choice(alternatives), 1)

        # 随机添加前缀（更少的前缀，保持句子规范性）
        prefixes = ["我", "我想", "请问"]
        if random.random() > 0.5:
            sample = random.choice(prefixes) + sample

        # 随机添加后缀（更少的后缀，保持句子规范性）
        suffixes = ["一下", "。", "谢谢"]
        if random.random() > 0.5:
            sample = sample + random.choice(suffixes)

        samples.append(sample)

    return samples


def generate_all_training_data() -> List[Dict]:
    """生成所有意图的训练数据"""
    all_data = []
    intent_list = ["booking", "reschedule", "cancel", "consultation", "recommendation"]

    for intent in intent_list:
        samples = generate_intent_training_data(intent, num_samples=400)
        for sample in samples:
            all_data.append({
                "text": sample,
                "intent": intent,
            })

    # 打乱数据
    random.shuffle(all_data)
    return all_data


def save_training_data(data: List[Dict], filepath: str):
    """保存训练数据到文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_test_query_dataset() -> List[Dict]:
    """生成用于评估的查询数据集"""
    test_cases = []

    intent_samples = {
        "booking": 200,
        "reschedule": 100,
        "cancel": 100,
        "consultation": 200,
        "recommendation": 100,
    }

    for intent, count in intent_samples.items():
        samples = generate_intent_training_data(intent, num_samples=count)
        for sample in samples:
            test_cases.append({
                "original_text": sample,
                "expected_intent": intent,
            })

    random.shuffle(test_cases)
    return test_cases


if __name__ == "__main__":
    # 生成训练数据
    training_data = generate_all_training_data()
    save_training_data(training_data, "training_data.json")
    print(f"生成训练数据: {len(training_data)} 条")

    # 生成测试数据
    test_data = generate_test_query_dataset()
    save_training_data(test_data, "test_query_data.json")
    print(f"生成测试数据: {len(test_data)} 条")
