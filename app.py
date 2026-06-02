import os
import tempfile
import streamlit as st

from rag_chain import RAGChain


def init_session_state():
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = RAGChain()
        st.session_state.rag_chain.load_knowledge_base()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []


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
            st.session_state.uploaded_files = uploaded_files
        
        if st.button("🔄 构建/更新知识库"):
            if not st.session_state.uploaded_files:
                st.warning("请先上传文档")
            else:
                with st.spinner("正在处理文档..."):
                    temp_dir = tempfile.mkdtemp()
                    file_paths = []
                    
                    for uploaded_file in st.session_state.uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                    
                    chunks_count = st.session_state.rag_chain.add_documents_from_files(file_paths)
                    st.success(f"成功处理 {len(file_paths)} 个文档，生成 {chunks_count} 个文本块")
        
        stats = st.session_state.rag_chain.get_knowledge_base_stats()
        st.info(f"知识库文本块数量: {stats['document_count']}")
        
        if st.button("🗑️ 清空对话历史"):
            st.session_state.chat_history = []
            st.session_state.rag_chain.clear_memory()
            st.success("对话历史已清空")
    
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
                    result = st.session_state.rag_chain.ask(user_input)
                
                st.markdown(result["answer"])
                
                if result["sources"]:
                    with st.expander("查看参考来源"):
                        for i, source in enumerate(result["sources"]):
                            st.markdown(f"**来源 {i+1}:**")
                            st.markdown(source["content"])
            
            st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})


if __name__ == "__main__":
    main()
