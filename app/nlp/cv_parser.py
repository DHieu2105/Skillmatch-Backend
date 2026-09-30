import pymupdf


def extract_pdf_text(content: bytes) -> str:
    document = pymupdf.open(stream=content, filetype="pdf")
    try:
        return "\n".join(page.get_text() for page in document).strip()
    finally:
        document.close()