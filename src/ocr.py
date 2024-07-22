import ocrmypdf
from ocrmypdf.exceptions import PriorOcrFoundError
import fitz  # PyMuPDF
import os

processed_docs_dir = 'processedDocuments'
os.makedirs(processed_docs_dir, exist_ok=True)

def extract_text_from_pdf(pdf_path, output_text_file):
    # Open the PDF file
    with fitz.open(pdf_path) as doc:
        # Open the text file for writing
        with open(output_text_file, "w") as text_file:
            # Iterate through each page of the PDF
            for page_num in range(len(doc)):
                # Get a page
                page = doc.load_page(page_num)
                # Extract text from the page
                text = page.get_text()
                # Write the text to the file
                text_file.write(text)
                # Optionally, add a page break between pages
                text_file.write("\n--- Page break ---\n")

def ocr_and_extract_text(pdf_path):
    ocr_output_path = os.path.join(processed_docs_dir, "ocr_" + os.path.basename(pdf_path))
    text_output_path = os.path.join(processed_docs_dir, os.path.splitext(os.path.basename(pdf_path))[0] + ".txt")
    
    try:
        # Attempt to OCR the PDF, skipping text where it's found
        ocrmypdf.ocr(pdf_path, ocr_output_path, skip_text=True)
        print(f"OCR processing completed for {pdf_path}. Processed PDF saved to {ocr_output_path}")
    except PriorOcrFoundError as e:
        print(f"OCR process skipped for '{pdf_path}' as it contains pre-existing text. Error: {e}")
        ocr_output_path = pdf_path  # Use the original file if OCR was skipped

    # Extract text from the OCR-processed PDF
    extract_text_from_pdf(ocr_output_path, text_output_path)
    print(f"Text extraction completed for {ocr_output_path}. Extracted text saved to {text_output_path}")

    return ocr_output_path, text_output_path
