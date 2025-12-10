
from bs4 import BeautifulSoup
import re
import pandas as pd
import requests



# 1. Récupérer la page d'accueil 

url = "http://books.toscrape.com"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "lxml")

# 2. Pour chaque livre sur la page, extraire : - Titre - Prix (convertir en float) - Note (étoiles → nombre) - Disponibilité (In stock / Out of stock) - URL de l'image '

div = soup.find("ol", class_="row")


articles_data =[]



for q in div.find_all(class_='product_pod'):

  
    Titre = q.find("h3").get_text(strip=True)

    prix = q.find("p", class_="price_color").get_text(strip=True)
    prix_clean = prix.replace("Â", "")
    prix_float = float(re.findall(r'[\d.]+', prix_clean)[0])
    

    rating_text = q.find("p", class_="star-rating")
    rating_class = rating_text.get("class")
    rating_word = rating_class[1]

    rating_map = {
    "ZERO" :0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
     }
    rating = rating_map.get(rating_word)
    print (rating)
    availability_tag = q.find("p", class_="instock availability")
    availability = availability_tag.get_text(strip=True)
    img = q.find("img", class_="thumbnail")
    lien_images = img.get("src")
     


    articles_data.append({
        "Titre": Titre,
        "Prix": prix_float,
        "Avis" : rating,
        "Disponibilite":availability,
        "Lien_img" : lien_images

    })

    for item in articles_data:
   
        print("Citation :", item["Titre"])
        print("Auteur :", item["Prix"])
        print ("Note :" ,item ["Avis"])
        print ("Disponibilité :" ,item ["Disponibilite"])
        print ("Lien d'image :" ,item ["Lien_img"])
        
        print("-" * 40)




# '3. Créer un DataFrame Pandas '
    
    df = pd.DataFrame(articles_data)
    print(df)

# '4. Calculer : - Prix moyen - Livre le plus cher - Livre le moins cher - Répartition par note '


    df_prix_moyen = df['Prix'].mean()
    df ['Prix moyen'] = df_prix_moyen
    print(df)
    
    livre_plus_cher = df.nlargest(1, 'Prix').iloc[0]
    print(f"Le livre le plus cher : {livre_plus_cher['Titre']} avec le prix : {livre_plus_cher['Prix']} ")
    # print (livre_plus_cher)
    
    livre_moins_cher = df.nsmallest(1, 'Prix').iloc[0]
    print(f"Le livre le moins cher : {livre_moins_cher['Titre']} avec le prix : {livre_moins_cher['Prix']} ")
    # print (livre_moins_cher)


    df_notes = df["Avis"].value_counts().reset_index()
    df_notes.columns = ["Note", "Nombre"]
    print(df_notes)

    df.to_csv('books.csv', index=False)


