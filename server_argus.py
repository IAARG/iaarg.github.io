import asyncio
import json
from websockets.asyncio.server import serve

async def argus_brain(websocket):
    print("🚀 Vendedor conectado à IA ARGUS!")
    insights = [
        "DETECÇÃO: Cliente achou caro. Sugira o parcelamento em 12x sem juros.",
        "ALERTA: Tom de voz positivo. Peça o fechamento agora!",
        "TÁTICA: O cliente citou concorrência. Foque no suporte 24h exclusivo."
    ]
    
    try:
        index = 0
        while True:
            await asyncio.sleep(8)  # Simula a IA analisando
            msg = {"sugestao": insights[index % len(insights)]}
            await websocket.send(json.dumps(msg))
            print(f"Enviado: {insights[index % len(insights)]}")
            index += 1
    except Exception as e:
        print(f"Conexão encerrada.")

async def main():
    print("📡 Cérebro do ARGUS online na porta 8765...")
    async def with_log(ws):
        await argus_brain(ws)
        
    async with serve(argus_brain, "localhost", 8765) as server:
        await asyncio.get_running_loop().create_future()  # Roda para sempre

if __name__ == "__main__":
    asyncio.run(main())
