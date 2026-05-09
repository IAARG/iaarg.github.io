#!/usr/bin/env python3
"""
Servidor ARGUS AI com Google Gemini (GRATUITO)
Executar: python server_argus_gratis.py
"""

import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# Tentar importar Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Instale o Google Gemini: pip install google-generativeai")

# Configurar Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Se não tiver API key, usar simulação local
USE_GEMINI = GEMINI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != "sua_chave_aqui"

if USE_GEMINI:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')  # Modelo gratuito
    print("✅ Google Gemini configurado com sucesso!")

class ArgusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/argus_web.html':
            self.serve_html()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/analyze':
            self.handle_analyze()
    
    def serve_html(self):
        html_content = self.get_html_content()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_analyze(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        message = data.get('message', '')
        history = data.get('history', [])
        
        if USE_GEMINI:
            analysis = self.analyze_with_gemini(message, history)
        else:
            analysis = self.analyze_with_local_ai(message, history)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(analysis).encode('utf-8'))
    
    def analyze_with_gemini(self, message, history):
        """Usa Google Gemini GRATUITO"""
        try:
            # Preparar contexto da conversa
            context = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in history[-5:]])
            
            prompt = f"""
            Você é o ARGUS AI, um assistente de vendas especialista em análise de conversas comerciais.
            
            Histórico da conversa:
            {context}
            
            Última mensagem do cliente: "{message}"
            
            Analise esta conversa e retorne APENAS UM OBJETO JSON com estes campos:
            {{
                "tone": "positivo|negativo|neutro|interessado|frustrado",
                "objection": {{"type": "price|timing|feature|trust|competitor", "text": "descrição curta"}} ou null,
                "suggestion": "sugestão prática para o vendedor (máximo 100 caracteres)",
                "probability_change": número de -20 a +20
            }}
            
            Regras:
            - Se falou de preço/caro: tone=negativo, objection=price
            - Se falou de gostou/quero: tone=positivo, probability_change=+15
            - Se falou de pensar/depois: tone=neutro, objection=timing
            - Se falou de concorrente: tone=interessado, objection=competitor
            - Sugestão deve ser acionável e prática
            
            Responda APENAS com o JSON, sem texto extra.
            """
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Limpar e extrair JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            analysis = json.loads(result_text)
            return analysis
            
        except Exception as e:
            print(f"Erro no Gemini: {e}")
            return self.analyze_with_local_ai(message, history)
    
    def analyze_with_local_ai(self, message, history):
        """IA local GRATUITA (não precisa de API)"""
        lower_msg = message.lower()
        
        analysis = {
            "tone": "neutro",
            "objection": None,
            "suggestion": "",
            "probability_change": 0
        }
        
        # Regras de negócio inteligentes
        if any(word in lower_msg for word in ['caro', 'preço', 'orçamento', '$', 'dinheiro']):
            analysis["tone"] = "negativo"
            analysis["objection"] = {"type": "price", "text": "Cliente questionou o valor"}
            analysis["suggestion"] = "💰 Mostre o ROI: quanto ele economiza/gganha com a solução"
            analysis["probability_change"] = -10
            
        elif any(word in lower_msg for word in ['gostei', 'quero', 'comprar', 'ótimo', 'excelente', 'bom']):
            analysis["tone"] = "positivo"
            analysis["suggestion"] = "🎯 Avance para o fechamento! Peça a confirmação da compra"
            analysis["probability_change"] = 15
            
        elif any(word in lower_msg for word in ['pensar', 'depois', 'preciso ver', 'analisar', 'avaliar']):
            analysis["tone"] = "neutro"
            analysis["objection"] = {"type": "timing", "text": "Cliente quer mais tempo"}
            analysis["suggestion"] = "📅 Ofereça um case de sucesso e agende follow-up em 2 dias"
            analysis["probability_change"] = -5
            
        elif any(word in lower_msg for word in ['concorrente', 'outro', 'melhor', 'comparar', 'diferente']):
            analysis["tone"] = "interessado"
            analysis["objection"] = {"type": "competitor", "text": "Comparando com concorrência"}
            analysis["suggestion"] = "⚡ Liste 3 benefícios que só você oferece"
            analysis["probability_change"] = 0
            
        elif any(word in lower_msg for word in ['funciona', 'integral', 'suporte', 'instalar', 'configurar']):
            analysis["tone"] = "neutro"
            analysis["suggestion"] = "📞 Agende uma demonstração técnica personalizada"
            analysis["probability_change"] = 5
            
        elif any(word in lower_msg for word in ['urgente', 'preciso agora', 'rápido', 'hoje']):
            analysis["tone"] = "interessado"
            analysis["suggestion"] = "⚡ Priorize este cliente! Potencial de fechamento rápido"
            analysis["probability_change"] = 10
            
        elif any(word in lower_msg for word in ['não gostei', 'ruim', 'problema', 'erro']):
            analysis["tone"] = "negativo"
            analysis["objection"] = {"type": "trust", "text": "Insatisfação com algo"}
            analysis["suggestion"] = "🤝 Peça desculpas e ofereça resolver o problema primeiro"
            analysis["probability_change"] = -15
            
        else:
            analysis["tone"] = "neutro"
            analysis["suggestion"] = "👂 Faça perguntas abertas: 'O que é mais importante para você?'"
            analysis["probability_change"] = 0
        
        return analysis
    
    def get_html_content(self):
        return '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARGUS AI - Assistente de Vendas (GRÁTIS)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .dashboard {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .header h1 { font-size: 1.8rem; }
        .header h1 span { color: #00d4ff; }
        .status-badge {
            background: #00d4ff;
            color: #1a1a2e;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
        }
        .free-badge {
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-left: 10px;
        }
        .content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        .card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }
        .card h3 {
            color: #1a1a2e;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        .metric { font-size: 2rem; font-weight: bold; color: #667eea; }
        .conversation-area {
            grid-column: 1 / -1;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }
        .messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background: white;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px 12px;
            border-radius: 10px;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            background: #667eea;
            color: white;
            text-align: right;
        }
        .message.argus {
            background: #e9ecef;
            color: #1a1a2e;
            border-left: 4px solid #667eea;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }
        .input-area button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        .input-area button:hover { background: #5a67d8; }
        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            background: linear-gradient(90deg, #00d4ff, #667eea);
            height: 100%;
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .objection-item {
            background: #ffe0e0;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #ff4757;
        }
        .typing-indicator {
            padding: 8px 12px;
            color: #999;
            font-style: italic;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .suggestions-list li {
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
            list-style: none;
        }
        @media (max-width: 768px) {
            .content { padding: 15px; }
            .header { flex-direction: column; gap: 10px; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="dashboard">
            <div class="header">
                <div>
                    <h1>ARGUS <span>AI</span></h1>
                    <span class="free-badge">🎁 GRÁTIS</span>
                </div>
                <div class="status-badge" id="status-badge">🎯 IA Ativa</div>
            </div>
            
            <div class="content">
                <div class="card">
                    <h3>📊 Contexto</h3>
                    <p><strong>Cliente:</strong> <span id="cliente">Em conversa</span></p>
                    <p><strong>Duração:</strong> <span id="duracao">00:00</span></p>
                    <p><strong>Status:</strong> Conversa Ativa</p>
                </div>
                
                <div class="card">
                    <h3>🎯 Fechamento</h3>
                    <div class="metric" id="probabilidade">45%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill" style="width: 45%">45%</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>😊 Tom</h3>
                    <div class="metric" id="tom">Neutro</div>
                </div>
                
                <div class="card">
                    <h3>💡 Sugestões</h3>
                    <ul class="suggestions-list" id="sugestoes">
                        <li>👋 Inicie a conversa</li>
                    </ul>
                </div>
                
                <div class="card">
                    <h3>⚠️ Objeções</h3>
                    <div id="objecoes-lista">
                        <p style="color: #999;">Nenhuma ainda</p>
                    </div>
                    <p><strong>Total:</strong> <span id="total-objecoes">0</span></p>
                </div>
                
                <div class="conversation-area">
                    <h3>💬 Conversa</h3>
                    <div class="messages" id="messages-area">
                        <div class="message argus">🤖 ARGUS: Pronto para ajudar! Diga a fala do cliente...</div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="message-input" placeholder="Digite a fala do cliente..." onkeypress="if(event.key=='Enter') sendMessage()">
                        <button onclick="sendMessage()">Enviar</button>
                    </div>
                    <p style="font-size: 0.7rem; color: #999; margin-top: 10px;">💡 Dica: Teste frases como "está caro", "gostei", "preciso pensar"</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let conversationHistory = [];
        let currentProbability = 45;
        let objectionsCount = 0;
        let isProcessing = false;
        
        async function sendMessage() {
            if (isProcessing) return;
            
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            conversationHistory.push({text: message, sender: 'user'});
            input.value = '';
            
            showTypingIndicator();
            isProcessing = true;
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, history: conversationHistory})
                });
                
                const analysis = await response.json();
                removeTypingIndicator();
                
                addMessage(analysis.suggestion, 'argus');
                conversationHistory.push({text: analysis.suggestion, sender: 'argus'});
                updateDashboard(analysis);
                
            } catch (error) {
                removeTypingIndicator();
                addMessage('Erro na conexão', 'argus');
            }
            
            isProcessing = false;
        }
        
        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('messages-area');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.textContent = (sender === 'user' ? '👤 Cliente: ' : '🤖 ARGUS: ') + text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showTypingIndicator() {
            const messagesDiv = document.getElementById('messages-area');
            const indicator = document.createElement('div');
            indicator.className = 'typing-indicator';
            indicator.id = 'typing-indicator';
            indicator.innerHTML = '🤖 ARGUS analisando <span class="loading"></span>';
            messagesDiv.appendChild(indicator);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function removeTypingIndicator() {
            const indicator = document.getElementById('typing-indicator');
            if (indicator) indicator.remove();
        }
        
        function updateDashboard(analysis) {
            const toneMap = {'positivo':'😊 Positivo','negativo':'😟 Negativo','neutro':'😐 Neutro','interessado':'🤔 Interessado','frustrado':'😤 Frustrado'};
            document.getElementById('tom').textContent = toneMap[analysis.tone] || analysis.tone;
            
            currentProbability += analysis.probability_change;
            currentProbability = Math.max(0, Math.min(100, currentProbability));
            document.getElementById('probabilidade').textContent = Math.round(currentProbability) + '%';
            document.getElementById('progress-fill').style.width = currentProbability + '%';
            document.getElementById('progress-fill').textContent = Math.round(currentProbability) + '%';
            
            if (analysis.objection) {
                objectionsCount++;
                document.getElementById('total-objecoes').textContent = objectionsCount;
                const objecoesDiv = document.getElementById('objecoes-lista');
                if (objecoesDiv.querySelector('p')) objecoesDiv.innerHTML = '';
                const div = document.createElement('div');
                div.className = 'objection-item';
                div.innerHTML = `<strong>${analysis.objection.type.toUpperCase()}</strong><br>${analysis.objection.text}`;
                objecoesDiv.prepend(div);
            }
            
            const sugestoesList = document.getElementById('sugestoes');
            sugestoesList.innerHTML = '';
            [analysis.suggestion, '🎯 Foque no valor da solução', '📊 Pergunte sobre as dores'].slice(0,3).forEach(s => {
                const li = document.createElement('li');
                li.textContent = s;
                sugestoesList.appendChild(li);
            });
        }
        
        let minutos = 0;
        setInterval(() => {
            minutos++;
            document.getElementById('duracao').textContent = `${Math.floor(minutos/60)}:${(minutos%60).toString().padStart(2,'0')}`;
        }, 60000);
    </script>
</body>
</html>'''

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ArgusHandler)
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🚀 ARGUS AI - Versão GRATUITA                         ║
║                                                          ║
║   📍 Acesse: http://localhost:{port}                      ║
║   🤖 IA: {"Google Gemini (GRÁTIS)" if USE_GEMINI else "IA Local (100% GRÁTIS)"}
║   💡 Pressione Ctrl+C para parar                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if not USE_GEMINI:
        print("\n💡 DICA: Para usar Gemini (mais inteligente), instale e configure:")
        print("   pip install google-generativeai")
        print("   export GEMINI_API_KEY='sua_chave_gratuita'")
        print("   Obtenha chave em: https://aistudio.google.com/apikey\n")
        print("🎯 Enquanto isso, a IA Local já está funcionando!\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado!")

if __name__ == '__main__':
    run_server()
