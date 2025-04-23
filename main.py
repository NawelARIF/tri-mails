import os
import base64
import json
import re
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

def clean_email_body(body):
    soup = BeautifulSoup(body, 'html.parser')
    return soup.get_text()

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

def trier_les_mails():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify'])
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])[:10]

    for i, msg in enumerate(messages):
        print(f"📨 Traitement de l’email {i+1} / {len(messages)}")
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

if __name__ == '__main__':
    trier_les_mails()
