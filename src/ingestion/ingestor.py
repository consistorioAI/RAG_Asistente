from typing import List, Dict
from pathlib import Path
import fitz  # PyMuPDF
import docx
import uuid
import datetime

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]

def extract_text_from_pdf(file_path: Path) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: Path) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text(file_path: Path) -> str:
    if file_path.suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_path.suffix == ".docx":
        return extract_text_from_docx(file_path)
    elif file_path.suffix == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

def process_documents(input_folder: Path, output_folder: Path) -> List[Dict]:
    output_folder.mkdir(parents=True, exist_ok=True)
    processed_docs = []

    for file in input_folder.iterdir():
        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        print(f"Procesando: {file.name}")
        try:
            content = extract_text(file)
            doc_id = str(uuid.uuid4())
            metadata = {
                "doc_id": doc_id,
                "filename": file.name,
                "created": datetime.datetime.now().isoformat(),
                "source": str(file.resolve())
            }


            with open(output_folder / f"{doc_id}.txt", "w", encoding="utf-8") as f_out:
                f_out.write(content)

            processed_docs.append({"text": content, "metadata": metadata})

        except Exception as e:
            print(f"Error procesando {file.name}: {e}")
    
    return processed_docs
