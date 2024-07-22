from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts.prompt import PromptTemplate

# Load, chunk and index the contents of the blog

loader = PyMuPDFLoader('combined.pdf')
docs = loader.load()
embeddings = OllamaEmbeddings(model="llama3")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
llm = ChatOllama(model="llama3")

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()
template = """
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
"""
prompt = PromptTemplate.from_template(template)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(rag_chain.invoke("What are the scores for the given qualities in each of the letters of recommendation? Also give me a JSON response of the qualities and skills displayed in the SoP."))