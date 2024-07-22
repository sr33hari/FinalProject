import os
import fitz  # PyMuPDF
import re
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

def split_pdf_by_headings(pdf_path, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count
    
    # Regex patterns for headings
    headings = [
        "Letter of Recommendation",
        "Statement of Purpose"
    ]
    
    heading_patterns = [re.compile(heading, re.IGNORECASE) for heading in headings]

    # Initialize variables
    splits = []
    current_start_page = 0
    current_heading = None

    def save_split(start_page, end_page, heading):
        if heading and start_page < end_page:
            split_pdf = fitz.open()
            for page_num in range(start_page, end_page):
                split_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            output_path = f"{output_dir}/{heading.replace(' ', '_')}_{start_page + 1}-{end_page}.pdf"
            split_pdf.save(output_path)
            split_pdf.close()

    for page_num in range(num_pages):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        
        for pattern in heading_patterns:
            if pattern.search(text):
                if current_heading:
                    save_split(current_start_page, page_num, current_heading)
                current_start_page = page_num
                current_heading = pattern.pattern
                break

    # Save the last split
    save_split(current_start_page, num_pages, current_heading)

    # Close the original PDF document
    pdf_document.close()

# Example usage
pdf_path = "combined.pdf"
output_dir = "output_splits"
split_pdf_by_headings(pdf_path, output_dir)

# Load, chunk and index the contents of each split document
embeddings = OllamaEmbeddings(model="llama3")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
llm = ChatOllama(model="llama3")

# Templates for each document type
templates = {
    "Letter_of_Recommendation": """
        You are an assistant for evaluating student profiles. Use the following pieces of retrieved context to answer the questions. Ensure you are unbiased and fair in your evaluation.
        Given letters of recommendation, evaluate them based on qualities such as Leadership, Extra Curriculars, Initiative, Admiration, Approval, Pride, Neutral, Excitement, Joy, and Gratitude.
        Here are 5 example sentences that demonstrate the tone of desired qualities that I am looking for in an LoR
            1) He was a chair of the IEEE computer society. This sentence displays Leadership
            2) They actively participated in dance competitions. This sentence displays Extra Curriculars
            3) He went above and beyond the project requirements. This sentence displays Initiative
            4) She was an absolute joy to work with. This sentence displays Approval
            5) I am happy to have known her. This sentence displays Pride. 


        Question: {question} 

        Context: {context} 

        Answer:
            Give each of the qualities a score from 1 to 10 based on the following scale:
            1 - No exhibition of the quality
            10 - Atleast 2 sentences exhibiting the quality

            Your response should be in a JSON format with the following keys:
            "Leadership": "<Score out of 10>",
            "Extra Curriculars": "<Score out of 10>",
            "Initiative": "<Score out of 10>",
            "Admiration": "<Score out of 10>",
            "Approval": "<Score out of 10>",
            "Pride": "<Score out of 10>",
            "Neutral": "<Score out of 10>",
            "Excitement": "<Score out of 10>",
            "Joy": "<Score out of 10>",
            "Gratitude": "<Score out of 10>"
    """,
    "Statement_of_Purpose": """
        You are an assistant for evaluating student profiles. Use the following pieces of retrieved context to answer the questions. Ensure you are unbiased and fair in your evaluation.
        Evaluate the statement of purpose based on qualities such as Goals, Motivation, Experience, Fit for the Program, Clarity of Purpose, Academic Background, Work Experience, Research Interests, Extracurricular Activities, and Personal Characteristics.

        Question: {question} 

        Context: {context} 

        Answer:
            Give each of the qualities a score from 1 to 10 based on the following scale:
            1 - No exhibition of the quality
            10 - Atleast 2 sentences exhibiting the quality

            Your response should be in a JSON format with the following keys:
            "Goals": "<Score out of 10>",
            "Motivation": "<Score out of 10>",
            "Experience": "<Score out of 10>",
            "Fit for the Program": "<Score out of 10>",
            "Clarity of Purpose": "<Score out of 10>",
            "Academic Background": "<Score out of 10>",
            "Work Experience": "<Score out of 10>",
            "Research Interests": "<Score out of 10>",
            "Extracurricular Activities": "<Score out of 10>",
            "Personal Characteristics": "<Score out of 10>"
    """
}

results = []

for file_name in os.listdir(output_dir):
    if file_name == '.DS_Store':  # Skip .DS_Store file
        continue

    file_path = os.path.join(output_dir, file_name)
    doc_type_key = "_".join(file_name.split('_')[:3])  # Extract the document type key

    if doc_type_key not in templates:  # Skip unrecognized document types
        print(f"Skipping unrecognized document type: {file_name}")
        continue

    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    splits = text_splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    
    retriever = vectorstore.as_retriever()
    prompt = PromptTemplate.from_template(templates[doc_type_key])
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
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
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response for file: {file_name}")
        print(f"Response: {response}")
        continue
    
    result = {
        "file_name": file_name,
        **response_json
    }
    
    results.append(result)

# Save results to CSV
df = pd.DataFrame(results)
df.to_csv('evaluation_results.csv', index=False)

print("Evaluation results saved to evaluation_results.csv")
