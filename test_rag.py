from rag_chain import RAGChain


def test_rag_system():
    print("="*60)
    print("RAG问答系统测试")
    print("="*60)
    
    rag = RAGChain()
    
    print("\n📚 加载知识库...")
    if not rag.load_knowledge_base():
        print("注意：未找到现有知识库，请先上传文档并构建知识库")
        return
    
    test_cases = [
        ("什么是自然语言处理？", "相关问题"),
        ("Transformer架构的主要组成部分是什么？", "相关问题"),
        ("什么是词嵌入？", "相关问题"),
        ("文本分类的常用方法有哪些？", "相关问题"),
        ("什么是注意力机制？", "相关问题"),
        ("今天天气怎么样？", "无关问题"),
        ("中国的首都是哪里？", "无关问题")
    ]
    
    print("\n🧪 开始测试...")
    print("-" * 60)
    
    for question, category in test_cases:
        print(f"\n【{category}】")
        print(f"问题: {question}")
        
        try:
            result = rag.ask(question)
            print(f"回答: {result['answer']}")
            
            if result['sources']:
                print(f"参考来源数: {len(result['sources'])}")
        except Exception as e:
            print(f"❌ 出错: {e}")
        
        print("-" * 60)
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    test_rag_system()
