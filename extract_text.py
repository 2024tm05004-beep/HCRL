from pypdf import PdfReader
import os

pdf_file = 'Assignment/Assignment-AIML-AutomotiveIndustry.pdf'
txt_file = 'Assignment/Assignment-AIML-AutomotiveIndustry.txt'

# Initialize reader
reader = PdfReader(pdf_file)
full_text = ""

# Extract text from all pages
for page in reader.pages:
    text = page.extract_text()
    if text:
        full_text += text + "\n\n"

# Write to txt file
with open(txt_file, 'w', encoding='utf-8') as f:
    f.write(full_text)

if full_text.strip():
    print(f"Successfully extracted text to {txt_file}")
else:
    print(f"Warning: No text extracted. It might be a scanned PDF (requires OCR). Output file created but may be empty.")
