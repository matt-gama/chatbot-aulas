import os
import time
import requests

from dotenv import load_dotenv

load_dotenv()

host = os.getenv('HOST_API')
api_key = os.getenv('API_KEY')
    
def processar_imagem(instance, message_id, ia_infos) -> str:
    print("Processando Imagem")
    print(instance)
    print(message_id)
    print(ia_infos)
    return "Imagem enviada"

def processar_audio(instance, message_id, ia_infos) -> str:
    print("Processando Audio")
    print(instance)
    print(message_id)
    print(ia_infos)
    return "Audio enviada"

def processar_documento(instance, message_id, ia_infos) -> str:
    print("Processando Docs")
    print(instance)
    print(message_id)
    print(ia_infos)
    return "Documento enviada"

def send_message(instance:str, lead_phone:str, message:str, delay:int) -> dict:
    url = host+'message/sendText/'+instance
    body = {
        "number": lead_phone,
        "options": {
            "delay": int(delay)*1000,
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": str(message)
        }
    }
    
    data = post_request(url, body)
    return data

def post_request(url:str, body:dict, max_retries:int=5, wait_seconds:int=5) -> dict:
    # Inicializando variáveis
    attempt = 0
    lead = body["number"]
    response_post = {"status_code": None, "response":None}

    headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
    #Inicio do laço de repetição
    while attempt < max_retries:
        attempt += 1  # Incrementa o número de tentativas
        print(f"Tentativa {attempt} de {max_retries}")
        
        response = requests.post(url, json=body, headers=headers, timeout=120)

        try:
            response_return = response.json()
        except Exception as ex:
            print(f"Erro ao converter response em json, convertendo para texto:\n > {ex}")
            response_return = response.text
                
        # Verifica se o status code é sucesso
        if response.status_code in [200, 201]:
            print(f"Mensagem enviada com sucesso pela EVOLUTION para o lead » {lead}")
            response_post = {"status_code": response.status_code, "response": response_return}
            return response_post

        if attempt < max_retries:
            print(f"Aguardando {wait_seconds} segundos antes de tentar novamente...")
            time.sleep(wait_seconds)  # Pausa antes da próxima tentativa

    return response_post