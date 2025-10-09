import os
import json
import aiohttp
import asyncio
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

# Charger les variables d'environnement
load_dotenv()

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
options = os.getenv("MONGO_OPTIONS")
database_name = os.getenv("MONGO_DB", "retrodex")

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/?{options}"
POKEAPI_BASE = "https://pokeapi.co/api/v2"

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client[database_name]
collection = db["pokemons"]

# --- UTILITAIRES ------------------------------------------------------

async def fetch_json(session, url):
    """Télécharge un JSON depuis une URL avec gestion d'erreur."""
    async with session.get(url) as response:
        if response.status != 200:
            print(f"⚠️ Erreur {response.status} pour {url}")
            return None
        return await response.json()

async def get_pokemon_data(session, poke_id):
    """Récupère et fusionne les données de /pokemon et /pokemon-species."""
    poke_url = f"{POKEAPI_BASE}/pokemon/{poke_id}"
    species_url = f"{POKEAPI_BASE}/pokemon-species/{poke_id}"

    pokemon = await fetch_json(session, poke_url)
    species = await fetch_json(session, species_url)

    if not pokemon or not species:
        return None

    # Description en français
    description = next(
        (entry["flavor_text"].replace("\n", " ").replace("\f", " ")
         for entry in species["flavor_text_entries"]
         if entry["language"]["name"] == "fr"),
        "Aucune description disponible."
    )

    # Chaîne d'évolution
    evolution_url = species["evolution_chain"]["url"]

    # Pokémon d’origine
    evolves_from = (
        species["evolves_from_species"]["name"]
        if species["evolves_from_species"]
        else None
    )

    data = {
        "pokedex_num": pokemon["id"],  # Numéro officiel du Pokédex
        "nom": next(
            (name["name"] for name in species["names"] if name["language"]["name"] == "fr"),
            pokemon["name"]
        ),
        "nom_anglais": pokemon["name"],
        "types": [t["type"]["name"] for t in pokemon["types"]],
        "taille_m": pokemon["height"] / 10,
        "poids_kg": pokemon["weight"] / 10,
        "stats": {s["stat"]["name"]: s["base_stat"] for s in pokemon["stats"]},
        "sprites": {
            "officiel": pokemon["sprites"]["other"]["official-artwork"]["front_default"],
            "miniature": pokemon["sprites"]["front_default"],
        },
        "description": description,
        "evolution_chain_url": evolution_url,
        "evolue_de": evolves_from,
    }


    return data

# --- MAIN -------------------------------------------------------------

async def main():
    print("🚀 Initialisation du Pokédex (151 Pokémon)...")

    async with aiohttp.ClientSession() as session:
        pokemons = []

        for i in tqdm(range(1, 152), desc="Téléchargement", unit="pokémon"):
            data = await get_pokemon_data(session, i)
            if data:
                pokemons.append(data)

    # Taille totale avant insertion
    json_bytes = json.dumps(pokemons, ensure_ascii=False).encode("utf-8")
    size_mb = len(json_bytes) / (1024 * 1024)
    print(f"\n📦 Taille totale : {size_mb:.2f} Mo ({len(pokemons)} Pokémon)")

    # Sauvegarde locale pour vérification
    os.makedirs("data", exist_ok=True)
    with open("data/pokedex_preview.json", "w", encoding="utf-8") as f:
        json.dump(pokemons, f, ensure_ascii=False, indent=2)
    print("💾 Fichier enregistré : data/pokedex_preview.json")

    # --- Vérification et insertion conditionnelle
    inserted, skipped = 0, 0
    for p in tqdm(pokemons, desc="Insertion en base", unit="pokémon"):
        # On cherche si le pokémon est déjà présent via pokedex_num
        if collection.find_one({"pokedex_num": p["pokedex_num"]}):
            skipped += 1
            continue
        # Décommenter la ligne ci-dessous pour activer l'insertion
        collection.insert_one(p)
        inserted += 1
    
    print(f"\n✅ Nouveaux Pokémon insérés : {inserted}")
    print(f"🔁 Pokémon déjà présents : {skipped}")
    print("🎉 Initialisation terminée avec succès.")


# --- EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Interruption manuelle.")
        sys.exit(0)
