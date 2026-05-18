from HomeService.services.rag_service import RagService
from HomeService.services.knowledge_service import KnowledgeService

class ConsultationAgent:
    def __init__(self):
        self.rag_service = RagService()
        self.knowledge_service = KnowledgeService()

    def handle_consultation(self, message: str) -> str:
        try:
            return self.rag_service.generate_answer(message)
        except Exception:
            docs = self.knowledge_service.find_relevant_docs(message, top_k=3)
            if docs:
                knowledge_text = "\n\n".join([f"{doc['title']}: {doc['content']}" for doc in docs])
                return (
                    "我为您查到以下相关信息：\n"
                    f"{knowledge_text}\n\n"
                    "如果您对服务详情还有疑问，请继续告诉我您的需求。"
                )
            return "抱歉，当前无法直接检索到相关信息。请告诉我您想了解的服务类型和期望预约时间。"
