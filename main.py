import os
from src.split_pdf import split_pdf_by_headings
from src.evaluate_docs import evaluate_documents
from src.utils import ensure_directory
from src.ocr import ocr_and_extract_text

def main():
    combined_pdf_dir = 'combined_pdfs'
    split_output_base_dir = 'output_splits'
    results_dir = 'evaluation_results'
    processed_docs_dir = 'processedDocuments'

    # Ensure output directories exist
    ensure_directory(split_output_base_dir)
    ensure_directory(results_dir)
    ensure_directory(processed_docs_dir)
    
    for pdf_file in os.listdir(combined_pdf_dir):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(combined_pdf_dir, pdf_file)
            
            # Run OCR and text extraction
            ocr_output_path, text_output_path = ocr_and_extract_text(pdf_path)
            
            # Create a directory for the student
            student_name = os.path.splitext(pdf_file)[0]
            student_split_dir = os.path.join(split_output_base_dir, student_name)
            
            # Ensure student directory exists
            ensure_directory(student_split_dir)
            
            # Split the OCR-processed PDF by headings
            split_pdf_by_headings(ocr_output_path, student_split_dir)
    
    for student_dir in os.listdir(split_output_base_dir):
        student_split_dir = os.path.join(split_output_base_dir, student_dir)
        if os.path.isdir(student_split_dir):
            evaluate_documents(student_split_dir, results_dir)

if __name__ == "__main__":
    main()
