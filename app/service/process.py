import time
from ..database.manipulations import ia_manipulations, lead_manioulations
from app.apis.evolution import *
from app.service.llm_response import IAResponse
from app.service.quebra_mensagens import quebrar_mensagens, calculate_typing_delay
from app.service.queue_manager import get_phone_lock


def process_webhook_data(data: dict):
    """
    Função para processar os dados recebidos do webhook.
    Executa a tarefa garantindo que apenas um processo por telefone (lead_phone) ocorra por vez.
    """
    try:
        # Identificar a IA 
        ia_phone = data["sender"].split('@')[0]
        ia_name = data["instance"]
        ia_infos = ia_manipulations.filter_ia(ia_phone)
        if not ia_infos:
            raise(Exception("IA Não foi localizada com esse telefone")) 

        # Extraindo conteudo da mensagem
        message_id = data["data"]["key"]["id"]
        message_type = data["data"]["messageType"]
        message_content = processar_mensagem(data, ia_name, message_id, message_type, ia_infos)

        # Atualizar com novas infos no banco de dados
        lead_name = data['data']['pushName']
        lead_phone = data["data"]["key"]["remoteJid"].split('@')[0]
        # Obtém o lock para o lead_phone e o adquire
        lock = get_phone_lock(lead_phone)
        with lock:
            message_atual_lead = {
                "role": "user",
                "name": lead_name,
                "content":message_content
            }
            lead_db = lead_manioulations.filter_lead(lead_phone, message_atual_lead)
            if not lead_db:
                lead_db = lead_manioulations.new_lead(ia_infos.id, lead_name, lead_phone, [message_atual_lead])

            # Gerando resposta com LLM
            historico = lead_db.message
            api_key = ia_infos.ia_config.credentials.get("api_key")
            ai_model = ia_infos.ia_config.credentials.get("ai_model", "")
            system_prompt = ia_infos.active_prompt.prompt_text
            llm = IAResponse(api_key, ai_model, system_prompt)
            response_lead = llm.generate_response(message_content, historico)
            if not response_lead:
                raise(Exception("Erro ao gerar resposta da llm"))

            # Tratar mensagem da IA
            list_messages_to_send = quebrar_mensagens(response_lead)
            if not list_messages_to_send:
                list_messages_to_send = [response_lead]

            # Enviando mensagem para o lead
            for msg in list_messages_to_send:
                delay = calculate_typing_delay(msg)
                print(f"DELAY: {delay}")
                response_canal = send_message(ia_name, lead_phone, msg, delay)
                if response_canal.get("status_code") not in [200, 201]:
                    raise(Exception(f"Erro ao enviar mensagem ao lead > {msg}"))
                
            # Atualizando no banco de dados
            message_ia = {
                "role":"assistant",
                "content":response_lead
            }
            lead_updated =  lead_manioulations.update_lead(lead_db.id, message_ia)
            if not lead_updated:
                raise(Exception(f"Ocorreu algum problema ao atualizar lead : {lead_db.id}"))
            
            print(f"SUCESSO AO PROCESSAR LEAD {lead_db.phone}")

    except Exception as ex:
        print(f"ERROR IN PROCESS : {ex}")

def processar_mensagem(data, instance, message_id, message_type, ia_infos):
    if message_type == "conversation":
        return data["data"]["message"]["conversation"]
    
    elif message_type == "extendedTextMessage":
        return data["data"]["message"]["extendedTextMessage"]["text"]
    
    elif message_type == "imageMessage":
        print("Imagem detectada!")
        return processar_imagem(instance, message_id, ia_infos)
    
    elif message_type == "audioMessage":
        print("Áudio identificado!")
        return processar_audio(instance, message_id, ia_infos)
    elif message_type == "documentWithCaptionMessage":
        print("Documento identificado!")
        type_file = data.get("data").get("message").get("documentWithCaptionMessage").get("message").get("documentMessage").get("mimetype").split("/")[1]
        return processar_documento(instance, message_id, type_file, ia_infos), type_file
    else:
        print(f"Tipo de mensagem não identificada: {message_type} retornando...")
        return "Mensagem não odentificada"
