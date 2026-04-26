import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from config import FAISS_INDEX_PATH, GEMINI_API_KEY

def build_knowledge_base(reel_id: str, transcript: str, visual_description: str):
    """
    Combines transcript and visual descriptions, chunks the text, and stores in FAISS.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    combined_text = f"--- Reel Visual Content ---\n{visual_description}\n\n--- Reel Transcript ---\n{transcript}"
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(combined_text)
    
    # Generate embeddings and store in FAISS
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=GEMINI_API_KEY)
    
    vectorstore = FAISS.from_texts(chunks, embeddings)
    
    # Save the index specific to this reel
    index_path = f"{FAISS_INDEX_PATH}_{reel_id}"
    vectorstore.save_local(index_path)
    
    return index_path

def ask_question(reel_id: str, question: str) -> str:
    """
    Loads the FAISS index for the given reel and answers the question using Gemini LLM.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    index_path = f"{FAISS_INDEX_PATH}_{reel_id}"
    if not os.path.exists(index_path):
        return "Knowledge base for this reel not found. Please process the reel first."
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=GEMINI_API_KEY)
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    from langchain.prompts import PromptTemplate
    
    prompt_template = """You are an AI assistant that analyzes Instagram reels based on the following extracted video transcript and visual descriptions. 
    Use the following pieces of context to answer the user's question about the reel. 
    If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY, temperature=0.2)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    response = qa_chain.invoke({"query": question})
    return response.get("result", "Sorry, I couldn't find an answer.")
