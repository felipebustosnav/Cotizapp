import PyPDF2
import sys

def extract_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += f"\n--- Página {page_num + 1} ---\n"
            text += page.extract_text()
        return text

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    text = extract_pdf_text(pdf_path)
    print(text)
