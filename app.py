from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import csv
from math import ceil
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import spacy

app = FastAPI()
templates = Jinja2Templates(directory="templates")
nlp = spacy.load("custom_nlp_model4")

# CSV dosyasından verileri oku
def read_csv(file_path):
    products = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            products.append(row)
    return products

def spacy_result(query_doc, products):
    # SpaCy modeli tarafından işlenmiş sorgudan önemli kelimeleri al
    

    # Ürünleri filtreleme
    filtered_results = []
    for product in products:
        # Ürün başlığından önemli kelimeleri al
        product_keywords = product["title"].lower()
        print(f"product keywords: {product_keywords}")
        # SpaCy modeli tarafından işlenmiş sorgu ve ürün başlığından alınan önemli kelimeleri karşılaştırma
        # if query_keywords.intersection(product_keywords):
        #     filtered_results.append(product)
        #     print(f"product keywords: {product_keywords}")
        #     print(f"product: {product}\n")

    return filtered_results
        
   
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # CSV dosyasından verileri oku
    products = read_csv("karaca.csv")

    # Her satırda 4 ürün olacak şekilde düzenle
    products_per_row = 4
    rows = [products[i:i + products_per_row] for i in range(0, len(products), products_per_row)]

    # Ürün ismini 10 kelimeden sonra kes ve ... ekle
    for row in rows:
        for product in row:
            words = product["title"].split()[:10]
            product["truncated_title"] = ' '.join(words) + (' ...' if len(words) > 10 else '')

    return templates.TemplateResponse("index.html", {"request": request, "products": rows})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str):
    
    doc = nlp(query)  

    products = read_csv("karaca.csv")
    filtered_results = spacy_result(doc, products)

    return templates.TemplateResponse("search_results.html", {"request": request, "results": filtered_results})