from __future__ import annotations

from typing import Dict, List, TypedDict

from langchain_core.documents import Document
from langchain_core.embeddings.fake import FakeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph.state import START, StateGraph

from HomeService.models.claude_client import ClaudeClient
from HomeService.services.knowledge_service import KnowledgeService


class RagState(TypedDict, total=False):
    query: str
    documents: List[Dict]
    prompt: str
    response: str


class RagService:
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.embeddings = FakeEmbeddings(size=128)
        self.vectorstore = self._build_vector_store()
        self.graph = self._build_graph()
        self.llm = ClaudeClient()

    def _build_vector_store(self) -> InMemoryVectorStore:
        documents = []
        for item in self.knowledge_service.list_documents():
            documents.append(
                Document(
                    page_content=item["content"],
                    metadata={
                        "title": item["title"],
                        "service_type": item["service_type"],
                        "city": item["city"],
                    },
                )
            )
        store = InMemoryVectorStore(self.embeddings)
        if documents:
            store.add_documents(documents)
        return store

    def refresh_index(self) -> None:
        self.vectorstore = self._build_vector_store()

    def _build_graph(self) -> StateGraph[dict]:
        graph = StateGraph(RagState)
        graph.add_node(self._retrieve_documents)
        graph.add_node(self._build_prompt)
        graph.add_node(self._call_model)
        graph.add_edge(START, self._retrieve_documents)
        graph.add_edge(self._retrieve_documents, self._build_prompt)
        graph.add_edge(self._build_prompt, self._call_model)
        graph.set_finish_point(self._call_model)
        return graph.compile()

    def _retrieve_documents(self, state: RagState) -> RagState:
        query = state.get("query", "")
        if not query:
            state["documents"] = []
            return state

        hits = self.vectorstore.similarity_search(query, k=3)
        state["documents"] = [
            {
                "title": doc.metadata.get("title", ""),
                "content": doc.page_content,
                "service_type": doc.metadata.get("service_type", ""),
                "city": doc.metadata.get("city", ""),
            }
            for doc in hits
        ]
        return state

    def _build_prompt(self, state: RagState) -> RagState:
        docs = state.get("documents", [])
        if docs:
            knowledge_text = "\n\n".join(
                [f"{doc['title']}: {doc['content']}" for doc in docs]
            )
        else:
            knowledge_text = (
                "未检索到相关文章。请根据通用家政服务规则回答用户，并提示用户提供地址、面积、时间和联系电话。"
            )

        state["prompt"] = (
            "以下是检索到的知识摘要：\n"
            f"{knowledge_text}\n\n"
            f"用户问题：{state.get('query', '')}\n"
            "请用客户友好的语气回答，优先使用以上知识。"
        )
        return state

    def _call_model(self, state: RagState) -> RagState:
        prompt = state.get("prompt", "")
        if not prompt:
            state["response"] = "抱歉，未能生成回答，请稍后重试。"
            return state

        response = self.llm.chat(
            [{"role": "user", "content": prompt}],
        )
        state["response"] = response
        return state

    def generate_answer(self, query: str) -> str:
        state: RagState = {"query": query, "documents": [], "prompt": "", "response": ""}
        result = self.graph.invoke(state)
        return result.get("response", "抱歉，未能生成回答。")
