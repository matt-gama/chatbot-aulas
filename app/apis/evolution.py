import os
import time
import openai
import requests

from langchain_openai import OpenAI
from langchain.schema import Document
from langchain_openai.chat_models import ChatOpenAI

from pydub import AudioSegment

from dotenv import load_dotenv

load_dotenv()

# Configuração do modelo OpenAI Vision
host = os.getenv('HOST_API')
api_key = os.getenv('API_KEY')
    
def processar_imagem(instance, message_id, ia_infos) -> str:
    print("Processando Imagem")
    imagem_transcript = "Imagem enviada : Não consegui transcrever essa imagem fale para o usuário que sua internet esta ruim e que não pode baixar a imagem"

    try:
        url = host+'chat/getBase64FromMediaMessage/'+instance
        body = {
                "message": {
                    "key": {"id": message_id}
                },
                "convertToMp4": False
            }
        
        data = post_request(url, body)

        if data.get("status_code") in [200, 201]:
            image_base64 = data.get("response")['base64']
            # Enviar para OpenAI
            api_key = ia_infos.ia_config.credentials.get("api_key")
            openai_model = ChatOpenAI(model="gpt-4-vision-preview", openai_api_key=api_key)

            imagem_transcript = openai_model.invoke([
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{image_base64}"
                },
                {
                    "type": "text",
                    "text": "Faça uma interpretação da imagem enviada"
                }
            ])
            print(imagem_transcript)
            imagem_transcript += "Imagem enviada : "+ imagem_transcript
    except Exception as ex:
        print(f"Erro ao transcrever imagem : {ex}")

    return imagem_transcript

def processar_audio(instance, message_id, ia_infos) -> str:
    print("Processando Audio")
    audio_transcript = "Audio enviado : Não consegui transcrever esse audio fale para o usuário que sua internet esta ruim e que não pode ouvir"
    try:
        timestamp = str(time.time())
        audio_path = f"audio_{timestamp}.ogg"
        mp3_path = f"audio_{timestamp}.mp3"

        url = host+'chat/getBase64FromMediaMessage/'+instance

        body = {
                "message": {
                    "key": {"id": message_id}
                },
                "convertToMp4": False
            }
        data = post_request(url, body)

        if data.get("status_code") in [200, 201]:
            audio_base64 = data.get("response")['base64']
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(audio_base64)

            def convert_ogg_to_mp3(input_path, output_path):
                audio = AudioSegment.from_ogg(input_path)
                audio.export(output_path, format="mp3")
            
            convert_ogg_to_mp3(audio_path, mp3_path)

            with open(mp3_path, 'rb') as audio_file:
                api_key = ia_infos.ia_config.credentials.get("api_key")
                openai.api_key = api_key
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                audio_transcript = f"Audio enviado : {response.text}"
    except Exception as ex:
        print(f"Erro ao transcrever audio : {ex}")

    return audio_transcript

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