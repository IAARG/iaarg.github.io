import asyncio
import json
import websockets
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading

def run_web():
    with TCPServer(("", 8080), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

async def argus_brain(websocket):
    print("🚀 Sessão Iniciada. Monitorando performance...")
    historico_conversa = []
    probabilidade = 50
    
    async for message in websocket:
        data = json.loads(message)
        fala = data.get("texto_falado", "").lower()
        if not fala: continue
        
        historico_conversa.append(fala)
        
        # Lógica de Pontuação Comercial
        ganho = any(word in fala for word in ["bom", "ótimo", "fechar", "interessante", "sim"])
        perda = any(word in fala for word in ["caro", "difícil", "concorrente", "não"])
        
        if ganho: probabilidade += 7
        if perda: probabilidade -= 7
        probabilidade = max(0, min(100, probabilidade))

        # Sugestões Inteligentes
        sugestao = None
        if "preço" in fala or "caro" in fala:
            sugestao = {"tipo": "ALERTA: PREÇO", "texto": "Mostre o gráfico de economia anual agora."}
        elif "concorrente" in fala:
            sugestao = {"tipo": "TÁTICA: RIVAL", "texto": "Destaque nossa exclusividade em Real-Time."}
        elif "fechar" in fala:
            sugestao = {"tipo": "AÇÃO: FECHAMENTO", "texto": "Perfeito! Envie o contrato digital agora."}

        # Envia tudo de volta para a Dashboard
        await websocket.send(json.dumps({
            "prob": probabilidade,
            "tipo": sugestao["tipo"] if sugestao else None,
            "texto": sugestao["texto"] if sugestao else None,
            "total_frases": len(historico_conversa)
        }))

async def main():
    async with websockets.serve(argus_brain, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    asyncio.run(main())

