from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import db
from app.routes import pokemon_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application.
    - Exécuté au démarrage : création des index MongoDB.
    - Exécuté à la fermeture : fermeture éventuelle de la connexion.
    """
    # === STARTUP ===
    try:
        from app.services.pokemon_service import create_indexes
        await create_indexes()
        print("✅ Index MongoDB créés avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des index : {e}")

    yield  # Application en cours d'exécution

    # === SHUTDOWN ===
    try:
        if db:
            await db.client.close()
            print("🧹 Connexion MongoDB fermée proprement.")
    except Exception as e:
        print(f"⚠️ Erreur à la fermeture de MongoDB : {e}")


app = FastAPI(
    title="Retrodex API",
    description="API Pokédex rétro avec MongoDB et FastAPI",
    version="1.0.0",
    lifespan=lifespan,  # 🔹 Nouveau système de gestion du cycle de vie
)

# --- ROUTES ---
app.include_router(pokemon_routes.router)


@app.get("/ping")
async def ping_db():
    """Vérifie la connexion à la base MongoDB."""
    try:
        await db.command("ping")
        return {"status": "✅ Connexion MongoDB OK"}
    except Exception as e:
        return {"status": "❌ Échec de connexion", "error": str(e)}
