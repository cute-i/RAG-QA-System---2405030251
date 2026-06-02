import os
import tempfile
import streamlit as st
from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text_from_docx(file_path):
    doc = DocxDocument(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def split_text(text, chunk_size=500, chunk_overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def init_session_state():
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = {}


def build_knowledge_base():
    all_text = ""
    for doc in st.session_state.documents:
        all_text += doc["content"] + "\n\n"
    return all_text


def search_documents(query, top_k=5):
    if not st.session_state.documents:
        return []
    
    results = []
    query_lower = query.lower()
    
    for doc in st.session_state.documents:
        score = 0
        content_lower = doc["content"].lower()
        if query_lower in content_lower:
            score += 10
        for char in query_lower:
            if char in content_lower:
                score += 1
        if score > 0:
            results.append((score, doc))
    
    results.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in results[:top_k]]


def generate_answer(query, context, has_knowledge_base):
    if not has_knowledge_base:
        return "知识库为空，请先上传文档并构建知识库后再提问。"
    
    if not context:
        context_text = "（未检索到高度相关的文档片段）"
    else:
        context_text = "\n\n".join([doc["content"] for doc in context[:3]])
    
    prompt = f"""基于以下参考文档回答问题。如果文档中没有相关信息，请明确说明"文档中未找到相关答案"。

参考文档：
{context_text[:2000]}

问题：{query}

回答："""
    
    try:
        import ollama
        response = ollama.generate(
            model="deepseek-r1:7b",
            prompt=prompt,
            options={"temperature": 0.7}
        )
        return response["response"]
    except Exception as e:
        return f"生成回答时出错: {str(e)}"


def main():
    st.set_page_config(page_title="RAG智能问答系统", layout="wide")
    
    init_session_state()
    
    st.title("📚 基于本地知识库的RAG智能问答系统")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📁 文档管理")
        
        uploaded_files = st.file_uploader(
            "上传PDF或DOCX文档",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            with st.spinner("正在处理文档..."):
                temp_dir = tempfile.mkdtemp()
                new_docs = []
                
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        if uploaded_file.name.endswith(".docx"):
                            text = extract_text_from_docx(file_path)
                        elif uploaded_file.name.endswith(".pdf"):
                            text = extract_text_from_pdf(file_path)
                        else:
                            continue
                        
                        chunks = split_text(text)
                        for i, chunk in enumerate(chunks):
                            new_docs.append({
                                "name": uploaded_file.name,
                                "chunk_id": i,
                                "content": chunk[:500]
                            })
                    except Exception as e:
                        st.error(f"处理 {uploaded_file.name} 时出错: {e}")
                
                if new_docs:
                    st.session_state.documents.extend(new_docs)
                    st.success(f"成功添加 {len(new_docs)} 个文本块")
        
        st.info(f"知识库文本块数量: {len(st.session_state.documents)}")
        
        if st.button("🗑️ 清空知识库"):
            st.session_state.documents = []
            st.session_state.chat_history = []
            st.success("知识库已清空")
            st.rerun()
        
        if st.button("🔄 清空对话历史"):
            st.session_state.chat_history = []
            st.success("对话历史已清空")
            st.rerun()
    
    with col2:
        st.subheader("💬 问答交互")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        user_input = st.chat_input("请输入您的问题")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            with st.chat_message("assistant"):
                with st.spinner("正在思考..."):
                    has_kb = len(st.session_state.documents) > 0
                    context = search_documents(user_input)
                    answer = generate_answer(user_input, context, has_kb)
                
                st.markdown(answer)
                
                if context:
                    with st.expander("查看参考来源"):
                        for i, source in enumerate(context[:3]):
                            st.markdown(f"**来源 {i+1} ({source['name']}):**")
                            st.markdown(source["content"][:300])
            
            st.session_state.chat_history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
