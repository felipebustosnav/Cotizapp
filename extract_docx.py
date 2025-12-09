import docx
import sys

def extract_docx_text(docx_path):
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

if __name__ == "__main__":
    docx_path = sys.argv[1]
    text = extract_docx_text(docx_path)
    print(text)
