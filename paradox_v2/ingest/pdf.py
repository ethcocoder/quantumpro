"""
Paradox v2 — PDF Ingestion
=============================
Extracts text from PDF documents for knowledge base building.
"""

import os
from typing import Optional, Tuple


def extract_pdf(pdf_path: str) -> Optional[Tuple[str, str]]:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: path to the PDF file

    Returns:
        (filename, content) tuple or None on failure
    """
    if not os.path.exists(pdf_path):
        print(f"[PDF] File not found: {pdf_path}")
        return None

    try:
        import PyPDF2
    except ImportError:
        try:
            import pypdf as PyPDF2
        except ImportError:
            raise ImportError(
                "PyPDF2 or pypdf is required for PDF ingestion.\n"
                "Install: pip install pypdf"
            )

    try:
        text_parts = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 20:
                    text_parts.append(page_text.strip())

        if not text_parts:
            print(f"[PDF] No extractable text in: {pdf_path}")
            return None

        content = "\n\n".join(text_parts)
        content = _clean_pdf_text(content)
        filename = os.path.splitext(os.path.basename(pdf_path))[0]

        print(f"[PDF] Extracted: '{filename}' ({len(content):,} chars, {len(reader.pages)} pages)")
        return filename, content

    except Exception as e:
        print(f"[PDF] Failed to extract '{pdf_path}': {e}")
        return None


def extract_pdf_directory(dir_path: str):
    """
    Extract text from all PDFs in a directory.

    Returns:
        List of (filename, content) tuples.
    """
    results = []
    if not os.path.isdir(dir_path):
        print(f"[PDF] Directory not found: {dir_path}")
        return results

    pdf_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.pdf')]
    print(f"[PDF] Found {len(pdf_files)} PDF files in {dir_path}")

    for pdf_file in sorted(pdf_files):
        result = extract_pdf(os.path.join(dir_path, pdf_file))
        if result:
            results.append(result)

    print(f"[PDF] Batch complete: {len(results)}/{len(pdf_files)} PDFs extracted")
    return results


def _clean_pdf_text(text: str) -> str:
    """Clean common PDF extraction artifacts."""
    import re

    # Fix hyphenated line breaks
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # Fix line breaks within sentences
    text = re.sub(r'(?<=[a-z,])\n(?=[a-z])', ' ', text)

    # Remove page numbers (standalone numbers on a line)
    text = re.sub(r'\n\s*\d{1,4}\s*\n', '\n', text)

    # Collapse excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()
