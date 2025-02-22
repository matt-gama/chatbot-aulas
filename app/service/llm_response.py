from langchain.memory import ConversationBufferWindowMemory
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.conversation.base import ConversationChain
from langchain.prompts import PromptTemplate


class IAResponse:
    def __init__(self, api_key:str, ia_model:str, system_prompt:str):
        self.api_key = api_key
        self.ia_model = ia_model
        self.system_prompt = system_prompt

        response_prompt = """
            Histórico da conversa:
            {history}
            Usuário: {input}
        """

        self.system_prompt += response_prompt

        if not self.ia_model:
            print("Nenhum modelo passado, pegando um default")
            self.ia_model = "gpt-4o-mini"
    
    def generate_response(self, message_lead: str, history_message:list=[]) -> str:
        try:
            chat = ChatOpenAI(model=self.ia_model, api_key=self.api_key)
            memory = ConversationBufferWindowMemory(k=60)
            review_template = PromptTemplate.from_template(self.system_prompt)
            conversation = ConversationChain(
                llm=chat,
                memory=memory,
                prompt=review_template
            )

            # Alimenta a memória com cada mensagem do histórico
            if not history_message:
                conversation.memory.chat_memory.add_user_message(message_lead)
            else:
                for msg in history_message:

                    #Adicionando memoria do User
                    if msg["role"] == "user":
                        conversation.memory.chat_memory.add_user_message(msg.get("content") or "")
                    
                    #Adicionando memoria da IA
                    elif msg["role"] == "assistant":
                        conversation.memory.chat_memory.add_ai_message(msg.get("content") or "")

            print(f"Total de {len(history_message)} interações")   
            resposta = conversation.predict(input=message_lead)
            print(f"Resposta da IA   : {resposta}")
            
            return resposta
        except Exception as ex:
            print(f"❌ Erro ao processar resposta: {ex}")
            return None