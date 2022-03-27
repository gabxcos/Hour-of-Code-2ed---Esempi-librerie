from asyncio import exceptions
from json import JSONDecodeError
import requests

"""
N.B. seguendo questo link: https://github.com/public-apis/public-apis
sarà possibile trovare una lunga lista di API pubbliche utilizzabili.
Quelle con "Auth=No" non richiedono autenticazione delle richieste.

API scelta: 
OPEN LIBRARY
Doc: https://openlibrary.org/developers/api

Questa API permette di cercare su un vasto database di libri qualunque
informazione ad essi associata: titolo, autore, anno di stesura,
nonché info per ogni edizione pubblicata (anno, paese, copertina, etc.)
"""

# Le ricerche saranno del tipo: BASE_URL+"il+signore+degli+anelli"
BASE_URL = "http://openlibrary.org/search.json?q="

while True:

    search_string = input("Quale libro vuoi cercare?\n")
    # Esci se la stringa data è vuota ("INVIO" senza scrivere nulla)
    if len(search_string) <= 0:
        print("Grazie per aver cercato!")
        exit()

    search_string = "+".join((search_string.lower()).split())
    search_url = BASE_URL+search_string
    print(f"\nProvo a cercare qui: {search_url}\n")

    r = requests.get(search_url)

    # Se non è STATUS 200: OK, la richiesta è fallita
    if r.status_code!=200:
        print(f"La richiesta è fallita con codice: {r.status_code}\n")
    
    else:
        result = None

        try:
            result = r.json()
        except Exception as ex:
            print("La risposta non è pervenuta in formato JSON! : "+str(ex))
            continue

        # filtriamo per i soli libri che hanno gli attributi che ci interessano
        books = [book for book in result["docs"] if set(book.keys()).issuperset(set(["title", "first_publish_year", "author_name", "language"]))]

        numFound = len(books) # numero di risultati (filtrato)
        print(f"Ho trovato {numFound} risultati"+(':' if numFound<11 else '.\nEcco i primi 10:')+"\n")
        books = books if numFound<11 else books[:10] # limita ai primi 10 libri
        for book in books:
            title = book["title"]
            year = book["first_publish_year"]
            author = book["author_name"][0]
            hasIta = "ita" in book["language"] # controlla se esiste in Italiano
            print(f"- {title} ({year}), di {author}{'' if hasIta else ' [inedito]'}"+"\n")

        print("\n------------------------------------------------------\n")