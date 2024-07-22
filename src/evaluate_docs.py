import os
import json
import pandas as pd
from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts.prompt import PromptTemplate
from src.constants import TEMPLATES
from src.utils import ensure_directory, format_docs
from src.ai_content import detect_ai_content
# from src.ocr import perform_ocr
# # from src.plagiarism_check import check_plagiarism
from src.conference_eval import evaluate_conferences
from src.recommender_eval import extract_recommender_info, evaluate_recommenders

def evaluate_documents(output_dir, result_dir):
    ensure_directory(result_dir)
    
    embeddings = OllamaEmbeddings(model="llama3")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    llm = ChatOllama(model="llama3")
    
    results = []

    for file_name in os.listdir(output_dir):
        if file_name == '.DS_Store':
            continue

        file_path = os.path.join(output_dir, file_name)
        doc_type_key = "_".join(file_name.split('_')[:3])

        if doc_type_key not in TEMPLATES:
            print(f"Skipping unrecognized document type: {file_name}")
            continue

        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        splits = text_splitter.split_documents(docs)
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        
        retriever = vectorstore.as_retriever()
        prompt = PromptTemplate.from_template(TEMPLATES[doc_type_key])
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        question = "What are the scores for the given qualities?"
        response = rag_chain.invoke(question)

        if not response:
            print(f"Received empty response for file: {file_name}")
            continue

        try:
            response_json = json.loads(response)
            print(f"Response for file: {file_name} is {response_json}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response for file: {file_name}")
            print(f"Response: {response}")
            continue
        
        result = {
            "file_name": file_name,
            **response_json
        }
        
        # Additional evaluations
        ai_content_result = detect_ai_content(docs)
        # ocr_result = perform_ocr(file_path)
        # plagiarism_result = check_plagiarism(docs)
        conference_result = evaluate_conferences(docs)
        recommender_info = extract_recommender_info(docs)
        recommender_eval_result = evaluate_recommenders(recommender_info)

        result.update({
            "AI_Content": ai_content_result,
            # "OCR_Result": ocr_result,
            # "Plagiarism_Result": plagiarism_result,
            "Conference_Result": conference_result,
            "Recommender_Eval": recommender_eval_result
        })

        results.append(result)

    df = pd.DataFrame(results)
    csv_path = os.path.join(result_dir, 'evaluation_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"Evaluation results saved to {csv_path}")
