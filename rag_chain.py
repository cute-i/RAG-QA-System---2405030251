from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from knowledge_base import KnowledgeBase


class RAGChain:
    def __init__(self, model_name: str = "deepseek-r1:7b"):
        self.model_name = model_name
        self.llm = Ollama(model=model_name)
        self.knowledge_base = KnowledgeBase()
        self.conversation_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def load_knowledge_base(self) -> bool:
        return self.knowledge_base.load_vector_store()

    def build_knowledge_base_from_directory(self, directory: str):
        docs = self.knowledge_base.load_documents_from_directory(directory)
        split_docs = self.knowledge_base.split_documents(docs)
        self.knowledge_base.build_vector_store(split_docs)

    def add_documents_from_files(self, file_paths: list):
        docs = []
        for file_path in file_paths:
            docs.extend(self.knowledge_base.load_document(file_path))
        
        if docs:
            split_docs = self.knowledge_base.split_documents(docs)
            self.knowledge_base.add_documents(split_docs)
            self._create_conversation_chain()
            return len(split_docs)
        return 0

    def _create_conversation_chain(self):
        if self.knowledge_base.vector_store is None:
            raise ValueError("Knowledge base not loaded. Call load_knowledge_base or build_knowledge_base_from_directory first.")

        template = """基于提供的参考文档回答问题。如果文档中没有相关信息，请明确说明"文档中未找到相关答案"。

        参考文档：
        {context}

        历史对话：
        {chat_history}

        问题：{question}

        回答："""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )

        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.knowledge_base.vector_store.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True
        )

    def ask(self, question: str) -> dict:
        if self.knowledge_base.vector_store is None:
            return {
                "answer": "知识库为空，请先上传文档并构建知识库后再提问。",
                "sources": []
            }
        
        if self.conversation_chain is None:
            self._create_conversation_chain()

        result = self.conversation_chain({"question": question})
        
        answer = result["answer"]
        if not answer.strip() or "未找到相关答案" not in answer and len(answer) < 10:
            answer = "文档中未找到相关答案"
        
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                if isinstance(doc, Document):
                    sources.append({
                        "content": doc.page_content[:300],
                        "metadata": doc.metadata
                    })

        return {
            "answer": answer,
            "sources": sources
        }

    def get_knowledge_base_stats(self) -> dict:
        return {
            "document_count": self.knowledge_base.get_document_count()
        }

    def clear_memory(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        if self.conversation_chain:
            self.conversation_chain.memory = self.memory


def main():
    rag = RAGChain()
    
    print("Loading knowledge base...")
    if not rag.load_knowledge_base():
        print("No existing knowledge base found. Building from documents...")
        rag.build_knowledge_base_from_directory("./documents")
    
    print("Knowledge base loaded. Starting conversation...")
    
    while True:
        question = input("请输入问题（输入 'exit' 退出）：")
        if question.lower() == "exit":
            break
        
        result = rag.ask(question)
        print(f"\n回答：{result['answer']}")
        
        if result['sources']:
            print("\n参考来源：")
            for i, source in enumerate(result['sources']):
                print(f"{i+1}. {source['content'][:100]}...")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
