"""Build or rebuild the Chroma vectorstore from PDF or text sources.

Usage examples:
    python backend/scripts/build_vectorstore.py --pdf backend/data/faq.pdf --reset
    python backend/scripts/build_vectorstore.py --text backend/data/FAQtxt.txt
    VECTORSTORE_DIR=./backend/vectorstore_alt python backend/scripts/build_vectorstore.py --pdf backend/data/faq.pdf

Requirements:
    - pypdf
    - langchain, chromadb, tiktoken, python-dotenv

The script will:
    1. Load PDF or text content
    2. Chunk it using RecursiveCharacterTextSplitter
    3. Embed with OpenAIEmbeddings (text-embedding-3-small)
    4. Persist a Chroma collection named 'bundesfaq_rag_collection'

Environment variables:
    OPENAI_API_KEY   Required
    VECTORSTORE_DIR  Optional override of output directory (default: ./backend/vectorstore)
"""
from __future__ import annotations
import os
import argparse
import shutil
import logging
from dotenv import load_dotenv
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

try:
    from pypdf import PdfReader  # prefer pypdf
except ImportError:  # fallback
    from PyPDF2 import PdfReader  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_vectorstore")

COLLECTION_NAME = "bundesfaq_rag_collection"


def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    texts: List[str] = []
    for i, page in enumerate(reader.pages):
        try:
            texts.append(page.extract_text() or "")
        except Exception as e:
            logger.warning("Failed to extract page %s: %s", i, e)
    return "\n".join(texts)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(raw: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", ".", "?", "!", ",", " "]
    )
    return splitter.split_text(raw)


def build(docs: List[str], out_dir: str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    logger.info("Creating Chroma collection in %s", out_dir)
    Chroma.from_texts(
        texts=docs,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
        persist_directory=out_dir,
    )
    logger.info("Vectorstore build complete (%d chunks).", len(docs))


def parse_args():
    p = argparse.ArgumentParser(description="Build the BundesFAQ Chroma vectorstore")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--pdf", help="Path to FAQ PDF source")
    g.add_argument("--text", help="Path to FAQ text source")
    p.add_argument("--out", help="Override output directory (else VECTORSTORE_DIR or default)")
    p.add_argument("--reset", action="store_true", help="Delete existing directory before building")
    return p.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    out_dir = args.out or os.getenv("VECTORSTORE_DIR", "./backend/vectorstore")

    if args.reset and os.path.exists(out_dir):
        logger.info("--reset supplied: removing %s", out_dir)
        shutil.rmtree(out_dir)

    src_path = args.pdf or args.text
    logger.info("Reading source: %s", src_path)
    raw = read_pdf(src_path) if args.pdf else read_text(src_path)
    chunks = chunk_text(raw)
    logger.info("Chunked into %d segments", len(chunks))

    os.makedirs(out_dir, exist_ok=True)
    build(chunks, out_dir)

    logger.info("Done. Persisted collection '%s' in %s", COLLECTION_NAME, out_dir)


if __name__ == "__main__":  # pragma: no cover
    main()
