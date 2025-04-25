import base64
import requests
import json
import re
import time
import threading
from pynput import mouse
from concurrent.futures import ThreadPoolExecutor
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email import message_from_bytes
from bs4 import BeautifulSoup

# === CONFIGURATION ===

INACTIVITY_LIMIT = 60  # 1 minute (60 sec)
last_move_time = time.time()

# Chemin vers le token d’authentification Gmail
TOKEN_PATH = '/Users/nawelarif/Desktop/tri-mails/token.json'

# === NETTOYAGE HTML DU MAIL ===

def clean_email_body(body):
    soup = BeautifulSoup(body, 'html.parser')
    return soup.get_text()

# === CATÉGORISATION PAR OLLAMA ===

def classer_mail_avec_ollama(sujet, contenu):
    prompt = f"""
Tu es un assistant qui trie les mails automatiquement.
Voici un exemple :
Sujet : {sujet}
Contenu : {contenu[:500]}
Catégories possibles : [emploi, shopping, publicité, autres]
Réponds uniquement par le nom de la catégorie la plus adaptée.
"""
    response = requests.post(
        "http://localhost:11434/api/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": "mistral",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        })
    )
    result = response.json()
    matches = re.findall(r"(emploi|shopping|publicité|autres)", result['message']['content'].lower())
    return matches[0] if matches else "autres"

# === TRAITEMENT D’UN MAIL ===

def traiter_un_email(msg, i, total, service):
    print(f"📨 Traitement de l’email {i+1} / {total}")
    txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
    payload = txt['payload']
    headers = payload['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "Sans sujet")

    parts = payload.get('parts', [])
    data = ''
    for part in parts:
        if part['mimeType'] == 'text/html':
            data = part['body']['data']
            break
        elif part['mimeType'] == 'text/plain':
            data = part['body']['data']

    decoded_data = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors="ignore")
    texte_propre = clean_email_body(decoded_data)

    label = classer_mail_avec_ollama(subject, texte_propre)

    print(f"🏷️ Label trouvé : {label}")

    existing_labels = service.users().labels().list(userId='me').execute().get('labels', [])
    label_ids = [l['id'] for l in existing_labels if l['name'].lower() == label]

    if not label_ids:
        new_label = service.users().labels().create(userId='me', body={
            "name": label,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }).execute()
        label_ids = [new_label['id']]

    service.users().messages().modify(userId='me', id=msg['id'], body={'addLabelIds': label_ids}).execute()

# === LANCEMENT DU TRI COMPLET ===

def lancer_tri():
    print("🚀 Lancement du tri des mails...")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/gmail.modify'])
    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])[:100]
    total = len(messages)

    with ThreadPoolExecutor(max_workers=3) as executor:
        for i, msg in enumerate(messages):
            executor.submit(traiter_un_email, msg, i, total, service)

# === DÉTECTION DE L’INACTIVITÉ SOURIS ===

def on_move(x, y):
    global last_move_time
    last_move_time = time.time()
    print("🖱️ Mouvement souris détecté, timer réinitialisé.")

def monitor_inactivity():
    global last_move_time
    while True:
        now = time.time()
        if now - last_move_time > INACTIVITY_LIMIT:
            print("⏰ Inactivité de 1 minute détectée.")
            lancer_tri()
            last_move_time = time.time()
        time.sleep(10)

# === MAIN ===

if __name__ == "__main__":
    print("🕵️ Surveillance en cours... Le script lancera le tri après 1 min d'inactivité.")
    mouse_listener = mouse.Listener(on_move=on_move)
    mouse_listener.start()

    monitor_thread = threading.Thread(target=monitor_inactivity)
    monitor_thread.start()

    mouse_listener.join()
    monitor_thread.join()
