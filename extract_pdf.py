import pypdf

def extract_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

pdf_file = "LES MATIERES .pdf"
text = extract_text(pdf_file)
with open("extracted_subjects.txt", "w", encoding="utf-8") as f:
    f.write(text)
print("Extraction complete. Text saved to extracted_subjects.txt")
