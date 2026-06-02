# RAG-QA-System

基于本地知识库的RAG智能问答系统，利用Ollama本地大模型、LangChain框架和Streamlit开发工具构建。

## 功能特点

- 📚 支持PDF和DOCX文档的批量加载与解析
- 🔍 基于Chroma向量数据库的文档检索
- 💬 支持多轮对话，具备上下文记忆功能
- 🖥️ 友好的Web交互界面
- 🔒 完全本地化部署，数据安全可控

## 环境要求

- Python 3.9+
- Ollama (用于运行本地大模型)
- 至少8GB内存（推荐16GB+）

## 安装步骤

### 1. 安装Ollama

访问 [Ollama官方网站](https://ollama.com/) 下载并安装Ollama。

### 2. 下载模型

```bash
# 下载DeepSeek-R1模型（主要推理模型）
ollama pull deepseek-r1:7b

# 下载嵌入模型
ollama pull nomic-embed-text
```

### 3. 创建虚拟环境

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用说明

### 运行测试脚本

```bash
python test_ollama.py
```

### 运行命令行版本

```bash
python rag_chain.py
```

### 运行Web应用

```bash
streamlit run app.py
```

### 使用Web界面

1. **上传文档**: 在左侧面板上传PDF或DOCX格式的文档
2. **构建知识库**: 点击"构建/更新知识库"按钮处理上传的文档
3. **提问**: 在右侧对话区输入问题并发送
4. **查看来源**: 展开"查看参考来源"可以查看回答依据的文档片段

## 项目结构

```
RAG-QA-System/
├── app.py                 # Streamlit Web应用主文件
├── rag_chain.py           # RAG问答链核心模块
├── knowledge_base.py      # 知识库构建模块
├── test_ollama.py         # Ollama测试脚本
├── requirements.txt       # 依赖列表
├── .gitignore             # Git忽略配置
├── documents/             # 文档存放目录（可选）
└── chroma/                # Chroma向量数据库（自动生成）
```

## 关键技术点

### RAG流程

1. **文档加载**: 使用PyPDFLoader和Docx2txtLoader加载文档
2. **文本分块**: 使用RecursiveCharacterTextSplitter进行文档分块（chunk_size=1000, chunk_overlap=200）
3. **向量化**: 使用Ollama的nomic-embed-text模型将文本块向量化
4. **存储**: 将向量存入Chroma向量数据库
5. **检索**: 使用相似性检索获取相关文档片段
6. **生成**: 将检索结果和问题送入大模型生成回答

### 所用模型

- **推理模型**: deepseek-r1:7b
- **嵌入模型**: nomic-embed-text

### 提示词设计

系统提示词要求模型基于提供的参考文档回答问题，如果文档中没有相关信息，则明确说明"文档中未找到相关答案"。

## 打包部署

使用PyInstaller将应用打包为独立的exe文件：

```bash
pyinstaller --onefile --windowed app.py
```

## 测试问答示例

**相关问题：**
- 什么是自然语言处理？
- Transformer架构的主要组成部分是什么？
- 什么是词嵌入？
- 文本分类的常用方法有哪些？
- 什么是注意力机制？

**无关问题：**
- 今天天气怎么样？
- 中国的首都是哪里？

## 许可证

MIT License

## 作者

姓名 - 学号
