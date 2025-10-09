from fastapi import FastAPI
from app.db.connection import db

app = FastAPI(title="RetroDex API")

@app.get("/ping")
async def ping_db():
    try:
        # Simple requête de test
        await db.command("ping")
        return {"status": "✅ Connexion MongoDB OK"}
    except Exception as e:
        return {"status": "❌ Échec de connexion", "error": str(e)}
