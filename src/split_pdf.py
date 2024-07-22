import fitz  # PyMuPDF
import re
import os
from src.utils import ensure_directory

def split_pdf_by_headings(pdf_path, output_dir):
    ensure_directory(output_dir)
    
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count
    
    headings = ["Letter of Recommendation", "Statement of Purpose"]
    heading_patterns = [re.compile(heading, re.IGNORECASE) for heading in headings]

    splits = []
    current_start_page = 0
    current_heading = None

    def save_split(start_page, end_page, heading):
        if heading and start_page < end_page:
            split_pdf = fitz.open()
            for page_num in range(start_page, end_page):
                split_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            output_path = os.path.join(output_dir, f"{heading.replace(' ', '_')}_{start_page + 1}-{end_page}.pdf")
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

    save_split(current_start_page, num_pages, current_heading)
    pdf_document.close()
