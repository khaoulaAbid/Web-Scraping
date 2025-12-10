from bs4 import BeautifulSoup
import re
import pandas as pd
import requests
from urllib.parse import urljoin
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_URL = "http://quotes.toscrape.com"



def fetch_url(url):
   
    
    try:
        logging.info(f"GET {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Erreur lors du chargement de {url}: {e}")
        return None



def detect_number_of_pages():

    logging.info("===  Détecte automatiquement le nombre de pages ===")

    html = fetch_url(BASE_URL)
    if html is None:
        return 1

    soup = BeautifulSoup(html, "lxml")
    next_btn = soup.find("li", class_="next")

    if not next_btn:
        return 1

    # dernière page = /page/10  
    all_links = soup.find_all("a", href=True)
    max_page = 1
    for a in all_links:
        match = re.search(r"/page/(\d+)/?", a["href"])
        if match:
            page_num = int(match.group(1))
            max_page = max(max_page, page_num)

    logging.info(f"Nombre de pages détectées : {max_page}")
    return max_page



def scrape_page(url):

    logging.info("===  Scrape l'url ===")
    html = fetch_url(url)
    if html is None:
        return []

    soup = BeautifulSoup(html, "lxml")
    quotes_elements = soup.find_all("div", class_="quote")

    data = []
    for q in quotes_elements:
        text = q.find("span", class_="text").text
        author = q.find("small", class_="author").text
        tags = [tag.text for tag in q.find_all("a", class_="tag")]
        url_auteur = q.find("a").get("href")

        data.append({
            "Citations": text,
            "Auteurs": author,
            "Tags": tags,
            "url_auteur": url_auteur
        })

    return data



def scrape_all_pages(max_pages=10):
    
    logging.info("===  Scrape toutes les pages (jusqu'à 10 max) ===")

    pages_to_scrape = min(detect_number_of_pages(), max_pages)
    logging.info(f"Scraping de {pages_to_scrape} pages")

    all_data = []

    for page in range(1, pages_to_scrape + 1):
        url = f"{BASE_URL}/page/{page}/"
        logging.info(f"Scraping Page {page}/{pages_to_scrape}")

        page_data = scrape_page(url)
        all_data.extend(page_data)

        time.sleep(1)  # respect du délai

    return pd.DataFrame(all_data)



def export_excel(df, filename="output_tp2.xlsx"):

    logging.info("=== un fichier Excel avec 3 feuilles : Citations || Par auteur || Frequence tags ===")

    auteurs = df.groupby("Auteurs")["Citations"].count().reset_index()
    tags = df.explode("Tags")["Tags"].value_counts()

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Citations", index=False)
        auteurs.to_excel(writer, sheet_name="Par auteur", index=False)
        tags.to_excel(writer, sheet_name="Frequence tags")

    


def statistiques(df):
    auteurs = df.groupby("Auteurs")["Citations"].count().sort_values(ascending=False)
    tags = df.explode("Tags")["Tags"].value_counts()
    longueur_moyenne = df["Citations"].apply(len).mean()

    print("\nTOP 5 AUTEURS ")
    print(auteurs.head(5))

    print("\nTOP 10 TAGS")
    print(tags.head(10))

    print("\nLONGUEUR MOYENNE DES CITATIONS")
    print(longueur_moyenne)

    return auteurs, tags, longueur_moyenne




if __name__ == "__main__":
    df = scrape_all_pages(max_pages=10)
    logging.info(f"Total de citations collectées : {len(df)}")

    export_excel(df)
    statistiques(df)
