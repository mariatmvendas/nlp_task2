from fastapi import FastAPI, UploadFile, File, HTTPException
import requests
from lxml import etree
import os
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt_tab") 

app = FastAPI(title="Task 2 - From PDF file to sentences")


@app.post("/v1/extract-sentences")

def convert_pdf_to_tei(pdf_file: UploadFile = File(...)):
    
    #call  GROBID for text processing
    GROBID_URL = os.getenv("GROBID_URL", "http://localhost:8070")
    url = f"{GROBID_URL}/api/processFulltextDocument"
 
    files = { "input": (pdf_file.filename, pdf_file.file, "application/pdf") }
    response = requests.post(url, files=files)

    #from TEI XML to JSON
    #it is not finding <s>, use paragraphs

    tree = etree.fromstring(response.content)
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    paragraphs_elements = tree.xpath("//tei:p", namespaces=ns)
    paragraphs = [etree.tostring(p, method="text", encoding="unicode").strip() for p in paragraphs_elements]
    
    #to check what grobid is finding
    #print([etree.tostring(e, method="text", encoding="unicode")[:200] for e in paragraphs_elements[:5]])

    #paragraphs is a list of strings, where each string is a paragraph, not a sentence
    sentences = []
    for p in paragraphs:
        sentences.extend(sent_tokenize(p))
 
    return {"sentences": sentences}