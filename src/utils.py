import os

def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
