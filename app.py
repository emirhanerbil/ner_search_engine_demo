from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import csv
from math import ceil
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import spacy
import pandas as pd

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

def standartization(list):
    new_list = [word.replace("I", "ı").replace("İ", "i").lower() for word in list]
    return new_list

def spacy_result(results):
    df = pd.read_csv("karaca.csv")
    product_list = df["title"].tolist()
    product_list = standartization(product_list)
    
    
    source_results = {}
    for idx,row in df[["id","title"]].iterrows():
        id = row["id"]
        title = row["title"].replace("I","ı").replace("İ","i").lower()
        source_doc = nlp(title)
        source_results[id] = {}
        for ent in source_doc.ents:
            source_results[id][ent.label_] = ent.text
    
    
    
    matching_dict = {}

    # results sözlüğündeki her bir anahtar-değer çiftini kontrol et
    for key, value in results.items():
        # source_results sözlüğündeki her bir alt sözlüğü kontrol et
        for idx, source_dict in source_results.items():
            
            # Eğer eşleşen bir değer bulunursa, eşleşen key ve value'yu matching_dict'e ekle
            if key in source_dict and source_dict[key] == value:
                if idx not in matching_dict:
                    matching_dict[idx] = {}
                matching_dict[idx][key] = value
                
    inner_dict_counts = {key: len(value) for key, value in matching_dict.items()}
    sorted_keys = sorted(inner_dict_counts, key=inner_dict_counts.get, reverse=True)
    
    sorted_results = {}

    for key in sorted_keys:
        sorted_results[key] = source_results[key]
    
    
    return_result = {}

    for key in sorted_results.keys():
        # DataFrame'de ilgili "id" değerini bul
        row = df[df['id'] == key]
        
        # Eğer ilgili "id" değeri bulunamazsa atlamak için bir kontrol
        if not row.empty:
            # DataFrame'den çekilen veriyi sözlüğe ekle
            return_result[key] = dict(row.iloc[0].to_dict())

    return return_result.values()

    
        
   
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
    
    doc = nlp(query.replace("I", "ı").replace("İ", "i").lower())
    results = {}
    for ent in doc.ents:
        results[ent.label_] = ent.text

    print(results)
    filtered_results = spacy_result(results)
    
    return templates.TemplateResponse("search_results.html", {"request": request, "results": filtered_results})