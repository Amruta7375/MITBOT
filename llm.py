import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA  
from vectorstore import load_vectorstore
from settings import get_settings

def load_llm(model_name: str):
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=os.environ.get("GEMINI_API_KEY", ""))

def set_custom_prompt(template: str):
    return PromptTemplate(template=template, input_variables=["context", "question"])

def get_qa_response(user_q: str):
    try:
        settings = get_settings()
        model_name = settings["model"]
        k_docs = settings["k"]
        llm = load_llm(model_name)
        vectorstore = load_vectorstore()
        CUSTOM_PROMPT = """
        Use the context to answer the question.
        If you don't know, say 'I don't know.' Do not hallucinate.
        Context: {context}
        Question: {question}
        Answer:
        """
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": k_docs}),
            return_source_documents=True,  
            chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT)}
        )
        response = qa_chain.invoke({"query": user_q})
        answer = response["result"]
        sources = []
        for doc in response["source_documents"]:
            source_file = doc.metadata.get("source", "Unknown")
            page_num = doc.metadata.get("page", "Unknown")
            sources.append(f"File: {os.path.basename(source_file)}, Page: {page_num + 1}")
        sources_str = "\n".join(sources) if sources else "No sources found."
        return f"{answer}\n\n**Sources:**\n{sources_str}"
    except Exception as e:
        return f"❌ Error during QA: {e}"