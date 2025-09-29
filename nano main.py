# main.py - VERSÃO SIMPLIFICADA
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class ArgusSimple:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            print("❌ DEEPSEEK_API_KEY não encontrada no arquivo .env")
            return
        
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.conversation = []
    
    def analyze_tone(self, text):
        """Análise simples de tom"""
        prompt = f"""
        Analise o tom emocional deste texto e responda em uma linha:
        "{text}"
        """
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 50
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Erro: {e}"
    
    def run_demo(self):
        """Demo interativa"""
        print("🤖 ARGUS AI - Demo com DeepSeek")
        print("Digite 'sair' para encerrar")
        
        while True:
            user_input = input("\nVocê: ")
            if user_input.lower() == 'sair':
                break
                
            self.conversation.append(user_input)
            analysis = self.analyze_tone(user_input)
            print(f"ARGUS: {analysis}")

if __name__ == "__main__":
    argus = ArgusSimple()
    argus.run_demo()
