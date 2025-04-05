from datetime import datetime
import os
import re
from flask import Blueprint, jsonify, request
import pandas as pd
import pdfplumber
from app.database import db
from app.models.models import Categoria, Spesa

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
utils_bp = Blueprint("utils", __name__)


@utils_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    # Gestione del file delle spese
    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    extracted_data = extract_data(os.path.join(UPLOAD_FOLDER, file.filename))
    os.remove(os.path.join(UPLOAD_FOLDER, file.filename))

    print(f"Dati estrapolati: {extracted_data}")
    for entry in extracted_data:
        # Imposto la tipologia di pagamento se è presente, altrimenti imposto "Altro"
        tipologia = entry["tipologia"] if entry["tipologia"] else "Altro"
        
        categoria_transazione = Categoria.query.filter_by(nome=tipologia).first()
        print(f"Spesa= {entry}")
        # Se la categoria non esiste, la creo
        if not categoria_transazione:
            categoria_transazione = Categoria(nome=tipologia)
            db.session.add(categoria_transazione)
            db.session.commit()
        # Formatto l'importo e la data prima di salvarla nel database
        importo_formattato = format_importo(entry["importo"])
        data_operazione_formattata = datetime.strptime(entry["data_operazione"], "%d/%m/%Y")
        
        # Controllo se la spesa esiste già nel database, se non esiste l'aggiungo al database
        existing_spesa = Spesa.query.filter_by(
            nome=entry["nome"],
            descrizione=entry["descrizione"],
            tipologia_pagamento=tipologia,
            importo=importo_formattato, 
            data_operazione=data_operazione_formattata,
            categoria_id = categoria_transazione.id 
        ).first()

        if existing_spesa:
            print(f"Spesa già presente: {existing_spesa}")
            continue
        else:
            new_spesa = Spesa(
                nome=entry["nome"],
                descrizione=entry["descrizione"],
                tipologia_pagamento=tipologia,  
                data_operazione=data_operazione_formattata,
                importo=importo_formattato,
                categoria_id=categoria_transazione.id
            )
            db.session.add(new_spesa)
            db.session.commit()

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully"}), 200


def format_importo(importo):
    return importo.replace("€", "").replace(",", ".").replace("+","").replace("-","")

def format_text(text):
    # text = text.replace("\n", " ")
    pattern = (
        r"(?<!\*\*)"  # Assicura che non ci siano già "**" prima
        r"\b(?P<first_date>\d{2}/\d{2}/\d{4})"  # Prima data
        r"\s+(?P<second_date>(?:\d{2}/\d{2}/\d{4}|---))"  # Seconda data oppure '---'
        r"(?P<body>.*?)"  # Qualsiasi testo in mezzo (non greedy)
        r"(?P<euro>€)"  # Il simbolo euro: qui fermiamo il match
    )
    # La sostituzione inserisce "**" prima della prima data e "**" subito dopo il simbolo "€"
    modified_text = re.sub(
        pattern,
        r"**\g<first_date> \g<second_date>\g<body>\g<euro>**",
        text,
        flags=re.DOTALL,
    )
    return modified_text

def extract_data(pdf_path):
    first_phase_pattern = re.compile(
        r"""
        \s*\*\*                                         # Asterischi iniziali con spazi opzionali
        (?P<data_operazione>\d{2}/\d{2}/\d{4})\s+       # Data operazione
        (?P<data_contabile>\d{2}/\d{2}/\d{4}|---)\s+    # Data contabile
        (?P<tipologia>Arrotondamento|Bollettini|Addebito\ diretto|Denaro\ ricevuto|Risparmi|Pagamento|Prelievo|Bonifico\ ordinario|Denaro\ inviato|Bonifico)?\s*  # Tipologia (opzionale)
        (?P<nome>[^\n+\-]+?)\s+                         # Nome: non contiene \n, + o -
        (?P<descrizione>                                # Descrizione
        (?:                                         
            (?!\*\*|                                 # Esclude "**"
            \d{1,2}[-/]\d{1,2}[-/]\d{2,4}|         # o una data nel formato dd/mm/yyyy
            \d{4}[-/]\d{1,2}[-/]\d{1,2}|           # o un importo con segno
            \s*[+-]?\s*\d+(?:[\.,]\d+)?€)          # o un importo con segno e simbolo euro
            [^\n]+?                                # Cattura il testo finché non incontra un'esclusione
        )*                                         
        )
        \s*(?P<segno>[-+])?                          # Cattura il segno + o -
        \s*(?P<importo>\s*\d+(?:[.,]\d+)?(?:\s*\+\s*\d+(?:[.,]\d+)?)?€)  # Importo con possibili decimali e "+ N"
        \s*\*\*\s*                                   # Asterischi finali con spazi opzionali
        """,
        re.VERBOSE | re.DOTALL,
    )

    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text

    relevant_text = format_text(all_text)
    relevant_text = relevant_text.replace("\n", " ")
    print("Testo formattato: ", relevant_text)
    all_data = []
    first_matches = list(first_phase_pattern.finditer(relevant_text))
    for i, match in enumerate(first_matches):
        if match:
            (
                data_operazione,
                data_contabile,
                tipologia,
                nome,
                descrizione,
                segno,
                importo,
            ) = match.groups()
            print(f"SEGNO {segno}")
            if segno is None:
                tipologia = "Addebito"
            elif "-" in segno:
                tipologia = "Addebito"
            elif "+" in segno:
                tipologia = "Accredito"
                
            all_data.append(
                {
                    "data_operazione": data_operazione,
                    "data_contabile": data_contabile,
                    "tipologia": tipologia,
                    "nome": nome,
                    "descrizione": descrizione.strip(),
                    "importo": importo.replace(".", ""),
                }
            )

    return all_data
