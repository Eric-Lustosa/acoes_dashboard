from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yfinance as yf
from datetime import datetime, timedelta
import os

app = FastAPI()

# Permite acesso do frontend (por exemplo: localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos da pasta 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def servir_index():
    caminho = os.path.join("static", "index.html")
    return FileResponse(caminho)

class StockResponse(BaseModel):
    nome: str
    preco_atual: float | None
    dividend_yield: float | None
    lucro_por_acao: float | None
    setor: str | None
    mercado: str | None

@app.get("/empresa/{ticker}", response_model=StockResponse)
def get_stock_info(ticker: str):
    try:
        t = yf.Ticker(ticker)

        # Tenta obter info
        info = t.info
        nome = info.get("longName", ticker) if info else ticker
        preco = info.get("currentPrice") if info else None
        dividend_yield = info.get("dividendYield") if info else None
        eps = info.get("trailingEps") if info else None
        setor = info.get("sector") if info else None
        mercado = info.get("market") if info else None

        # Se info falhar, tenta pelo menos pegar o último preço do histórico
        if preco is None:
            hist = t.history(period="1d")
            if not hist.empty:
                preco = hist["Close"].iloc[-1]

        return StockResponse(
            nome=nome,
            preco_atual=preco,
            dividend_yield=dividend_yield,
            lucro_por_acao=eps,
            setor=setor,
            mercado=mercado,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")

@app.get("/historico/{ticker}")
def get_price_history(ticker: str):
    try:
        t = yf.Ticker(ticker)
        hoje = datetime.today()
        trinta_dias_atras = hoje - timedelta(days=30)
        df = t.history(start=trinta_dias_atras, end=hoje)

        if df.empty:
            return JSONResponse(content=[])

        historico = [
            {"data": str(index.date()), "preco_fechamento": row["Close"]}
            for index, row in df.iterrows()
        ]

        return JSONResponse(content=historico)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {str(e)}")
