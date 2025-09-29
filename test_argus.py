# test_argus.py - VERSÃO SIMPLIFICADA PARA TESTE
import os
import requests
import json

# Configuração básica
DEEPSEEK_API_KEY = "sua_chave_aqui"  # ← Coloque sua chave aqui

class DeepSeekTest:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        """Testa a conexão com a API"""
        prompt = "Responda apenas com 'CONEXÃO OK' se esta mensagem foi recebida."
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        try:
            print("🔌 Testando conexão com DeepSeek API...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Resposta da API: {content}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False

# Executar teste
if __name__ == "__main__":
    if DEEPSEEK_API_KEY == "sua_chave_aqui":
        print("⚠️  Configure sua DEEPSEEK_API_KEY no código primeiro!")
    else:
        tester = DeepSeekTest()
        tester.test_connection()
