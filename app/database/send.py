from connection import init_db, SessionLocal
from models import IA, Prompt, Lead, IAConfig
from crypto import encrypt_data

def insert_example_data():
    db = init_db()
    try:
        # Inserindo IAs de exemplo
        ia1 = IA(name="PythonBrasil", phone_number="558587234490")
        db.add(ia1)
        db.commit()
        db.refresh(ia1)


        # Inserindo Prompts para cada IA
        prompt1 = Prompt(ia_id=ia1.id, prompt_text="Você é Matheus Um ahgente especializado para dar aulas de Python, responda todas as questões dos usuários apenas de Python.", is_active=True)
       
        db.add(prompt1)
        db.commit()


        # Inserindo configuração com credenciais criptografadas
        # Exemplo de JSON de credenciais
        credentials = {
            "api_key": "apiKey",
            "api_secret": "openai"
        }
        encrypted_credentials = encrypt_data(credentials)
        config = IAConfig(
            ia_id=ia1.id,
            channel="WhatsApp Evolution",
            ai_api="Openai",
            encrypted_credentials=encrypted_credentials
        )

        db.add(config)

        db.commit()

        print("Dados de exemplo inseridos com sucesso!")
    except Exception as e:
        db.rollback()
        print("Erro ao inserir dados:", e)
    finally:
        db.close()

if __name__ == '__main__':
    # Cria as tabelas (caso ainda não existam)
    #init_db()
    # Insere os dados de exemplo
    insert_example_data()
