"""BERT意图分类器 - 结合关键词和语义模型"""

import json
import os
from typing import Dict, List, Optional

# 懒加载变压器库，避免首次导入错误
BERT_AVAILABLE = False
torch = None
try:
    from transformers import BertTokenizer, BertForSequenceClassification
    import torch as torch_module
    torch = torch_module
    BERT_AVAILABLE = True
except ImportError:
    print("警告: transformers 未安装，使用关键词匹配模式")


class IntentBertClassifier:
    """BERT意图分类器"""

    INTENT_LABELS = {
        0: "booking",
        1: "reschedule",
        2: "cancel",
        3: "consultation",
        4: "recommendation",
        5: "others"
    }

    def __init__(self, model_path: Optional[str] = None):
        """初始化分类器

        Args:
            model_path: 模型保存路径，None表示使用预训练模型
        """
        self.model_path = model_path or "home_service_intent_bert"
        self.tokenizer = None
        self.model = None

        if BERT_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._load_model()
        else:
            self.device = None
            print("提示: 使用关键词匹配模式（BERT未安装）")

    def _load_model(self):
        """加载BERT模型"""
        if os.path.exists(self.model_path):
            # 加载本地微调模型
            self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
            self.model = BertForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            print(f"加载本地模型: {self.model_path}")
        else:
            # 使用预训练模型进行零样本分类
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
            print("使用预训练模型: bert-base-chinese (零样本分类)")

    def predict_with_keyword_boost(self, text: str, keyword_intent: Optional[str] = None) -> str:
        """使用关键词增强的BERT预测

        Args:
            text: 输入文本
            keyword_intent: 关键词检测到的意图（如果有）

        Returns:
            预测的意图标签
        """
        # 如果关键词有高置信度结果，优先使用
        if keyword_intent and keyword_intent != "consultation":
            return keyword_intent

        if not BERT_AVAILABLE:
            return "consultation"

        try:
            # tokenize
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=64,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                pred = torch.argmax(probs, dim=-1).item()

            # 置信度阈值
            confidence = probs[0][pred].item()

            # 低置信度时回退到consultation
            if confidence < 0.6:
                return "consultation"

            return self.INTENT_LABELS.get(pred, "consultation")

        except Exception as e:
            print(f"BERT预测错误: {e}")
            return "consultation"

    def train(self, texts: List[str], labels: List[str], epochs: int = 3):
        """训练BERT模型"""
        if not BERT_AVAILABLE:
            raise RuntimeError("transformers 未安装")

        from transformers import Trainer, TrainingArguments

        # 标签映射
        label_to_id = {v: k for k, v in self.INTENT_LABELS.items()}
        label_ids = [label_to_id.get(l, 5) for l in labels]  # 5 = others

        # tokenize
        encodings = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt"
        )

        # 转换为Dataset
        class IntentDataset(torch.utils.data.Dataset):
            def __init__(self, encodings, labels):
                self.encodings = encodings
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx])
                return item

            def __len__(self):
                return len(self.labels)

        dataset = IntentDataset(encodings, label_ids)

        # 训练参数
        training_args = TrainingArguments(
            output_dir='./models/intent_model',
            num_train_epochs=epochs,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=64,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
            evaluation_strategy="no",
            save_strategy="no",
        )

        # 创建模型
        num_labels = len(self.INTENT_LABELS)
        self.model = BertForSequenceClassification.from_pretrained(
            'bert-base-chinese',
            num_labels=num_labels
        )
        self.model.to(self.device)

        # 训练
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
        )

        trainer.train()

        # 保存模型
        os.makedirs(self.model_path, exist_ok=True)
        self.tokenizer.save_pretrained(self.model_path)
        self.model.save_pretrained(self.model_path)

        print(f"模型已保存到: {self.model_path}")

    def evaluate(self, texts: List[str], labels: List[str]) -> Dict:
        """评估模型"""
        if not BERT_AVAILABLE:
            return {"accuracy": 0}

        correct = 0
        total = len(texts)

        for text, true_label in zip(texts, labels):
            pred = self.predict_with_keyword_boost(text)
            if pred == true_label:
                correct += 1

        return {
            "accuracy": correct / total,
            "correct": correct,
            "total": total
        }


class HybridIntentDetector:
    """混合意图检测器 - 结合关键词和BERT"""

    def __init__(self, bert_classifier: Optional[IntentBertClassifier] = None):
        """初始化混合检测器"""
        self.bert_classifier = bert_classifier or IntentBertClassifier()

        # 关键词库（保留当前有效的INTENT_MAP）
        self.INTENT_MAP = self._build_intent_map()

        # 高优先级关键词（优先匹配）
        self.HIGH_PRIORITY_KEYWORDS = {
            "reschedule": {"改约", "改时间", "修改预约", "预约改期", "变更预约", "换时间", "改期", "换约",
                           "换个时间", "调整时间", "改一下时间", "换一个时间", "时间改", "改时间预约",
                           "时间换", "改约时间", "预约换时间", "改预约", "预约日期改", "预约改日", "预约换日期",
                           "预约改时间", "预约时间调整", "预约时间需要改", "预约时间可以改", "预约时间变更",
                           "预约时间更改", "预约时间修改", "预约日期更改", "预约日期修改", "预约时段改",
                           "预约时段调整", "预约时段更换", "预约换时间", "预约换日期", "预约更换时间",
                           "预约可以改", "预约能改", "预约想改", "预约要改", "预约需改", "预约调整",
                           "预约换", "预约变更", "预约修改", "预约改", "预约变", "改一下预约时间",
                           "调整预约时间", "调整预约日", "预约调整时间", "预约调整日", "预约时间换",
                           "换个预约时间", "换个预约日", "预约时间调", "预约调时间", "预约调日",
                           "预约时间改", "预约时间变更", "预约时间修改", "预约时间调整", "预约时间更改",
                           "换预约时间", "换预约日", "换预约时段"},
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

    def _build_intent_map(self) -> Dict[str, str]:
        """构建INTENT_MAP"""
        return {
            # booking
            "预约": "booking", "预约家政": "booking", "家政预约": "booking",
            "保洁预约": "booking", "预约保洁": "booking", "预约保洁服务": "booking",
            "需要预约": "booking", "想预约": "booking", "预定": "booking",
            "订": "booking", "下单": "booking", "下单家政": "booking",
            "家政下单": "booking", "叫保洁": "booking", "叫家政": "booking",
            "叫阿姨": "booking", "叫一个": "booking", "叫一名": "booking",
            "安排保洁": "booking", "安排家政": "booking", "安排一次": "booking",
            "请安排": "booking", "上门保洁": "booking", "上门家政": "booking",
            "找保洁": "booking", "找家政": "booking", "请保洁": "booking",
            "请家政": "booking", "保姆": "booking", "钟点工": "booking",
            "保洁员": "booking", "钟点": "booking", "小时工": "booking",
            "上门": "booking", "上门服务": "booking", " hire ": "booking",
            # booking变体
            "预约一个": "booking", "预约一名": "booking", "预约一次": "booking",
            "预约家政服务": "booking", "预约一个保洁": "booking", "预约一个保洁服务": "booking",
            "预约一次保洁": "booking", "预约一名保洁": "booking", "预约一次家政": "booking",
            "预约一名家政": "booking", "预约一个家政": "booking", "预约一个家政服务": "booking",
            "预约一个保洁员": "booking", "预约一个钟点工": "booking", "预约一个钟点": "booking",
            "预约一次钟点工": "booking", "预约上门保洁": "booking", "预约上门家政": "booking",
            "预约一次上门": "booking", "预约上门": "booking", "家政服务预约": "booking",
            "保洁服务预约": "booking", "家政服务": "booking", "保洁服务": "booking",
            "上门服务": "booking", "预定家政服务": "booking", "预定保洁服务": "booking",
            "预定家政": "booking", "预定保洁": "booking", "预定一个家政服务": "booking",
            "预定一个保洁服务": "booking", "预定一次家政服务": "booking", "预定一次保洁服务": "booking",
            "预定一次家政": "booking", "预定一次保洁": "booking", "预定一名家政服务": "booking",
            "预定一名保洁服务": "booking", "预定一个家政": "booking", "预定一个保洁": "booking",
            "预定一次": "booking", "预定一名": "booking", "预定一个": "booking",
            "下单家政服务": "booking", "下单保洁服务": "booking", "下单一次家政": "booking",
            "下单一次保洁": "booking", "下单一个家政": "booking", "下单一个保洁": "booking",
            "下单一名家政": "booking", "下单一名保洁": "booking", "安排一个家政服务": "booking",
            "安排一个保洁服务": "booking", "安排一次家政": "booking", "安排一次保洁": "booking",
            "安排一次家政服务": "booking", "安排一次保洁服务": "booking", "安排一名家政": "booking",
            "安排一名保洁": "booking", "安排一个家政": "booking", "安排一个保洁": "booking",
            "请安排一个家政": "booking", "请安排一个保洁": "booking", "请安排一次家政": "booking",
            "请安排一次保洁": "booking", "请安排一名家政": "booking", "请安排一名保洁": "booking",
            "请安排一次家政服务": "booking", "请安排一次保洁服务": "booking", "请安排一个家政服务": "booking",
            "请安排一个保洁服务": "booking",
            # cancel变体
            "取消上门服务": "cancel", "取消保洁预约": "cancel", "取消家政预约": "cancel",
            "取消这次预约": "cancel", "取消本次预约": "cancel", "取消一下预约": "cancel",
            "取消了预约": "cancel", "取消掉预约": "cancel", "取消掉家政": "cancel",
            "取消掉保洁": "cancel", "取消掉上门": "cancel", "取消掉服务": "cancel",
            "取消掉一次": "cancel", "取消掉一名": "cancel", "取消掉一个": "cancel",
            "取消掉保洁服务": "cancel", "取消掉上门服务": "cancel", "取消掉家政服务": "cancel",
            "取消掉一次服务": "cancel", "取消掉一次家政": "cancel", "取消掉一次保洁": "cancel",
            "取消掉一名家政": "cancel", "取消掉一名保洁": "cancel", "取消掉一个家政": "cancel",
            "取消掉一个保洁": "cancel",
            # consultation变体
            "家政服务": "consultation", "保洁服务": "consultation", "服务有哪些": "consultation",
            "家政服务项目": "consultation", "有什么": "consultation", "哪些": "consultation",
            "详情介绍": "consultation", "收费价格": "consultation", "费用多少": "consultation",
            "服务定价": "consultation", "服务价格表": "consultation", "价格多少": "consultation",
            "计费多少": "consultation",
            # recommendation变体
            "推荐一下家政": "recommendation", "推荐一下服务": "recommendation",
            "推荐服务类型": "recommendation", "推荐服务内容": "recommendation",
            "上次的服务": "recommendation", "最近的服务": "recommendation",
            "老客户服务": "recommendation", "会员服务": "recommendation",
            "推荐老客户": "recommendation", "复购服务": "recommendation",
        }

    def detect_keyword(self, text: str) -> Optional[str]:
        """关键词匹配检测"""
        # 高优先级关键词
        for intent, keywords in self.HIGH_PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return intent

        # 按长度降序匹配
        sorted_map = sorted(self.INTENT_MAP.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, intent in sorted_map:
            if keyword in text:
                return intent

        return None

    def detect_intent(self, text: str) -> str:
        """混合检测 - 关键词优先，BERT辅助"""
        # 1. 关键词匹配
        keyword_intent = self.detect_keyword(text)
        if keyword_intent:
            return keyword_intent

        # 2. BERT语义分类
        return self.bert_classifier.predict_with_keyword_boost(text, None)

    def train_bert(self, texts: List[str], labels: List[str]):
        """训练BERT模型"""
        self.bert_classifier.train(texts, labels)

    def get_bert_stats(self, texts: List[str], labels: List[str]) -> Dict:
        """获取BERT分类器的统计信息"""
        return self.bert_classifier.evaluate(texts, labels)


# 单例全局实例
_hybrid_detector: Optional[HybridIntentDetector] = None


def get_hybrid_detector() -> HybridIntentDetector:
    """获取混合检测器单例"""
    global _hybrid_detector
    if _hybrid_detector is None:
        _hybrid_detector = HybridIntentDetector()
    return _hybrid_detector
