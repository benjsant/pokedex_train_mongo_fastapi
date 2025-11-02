import os
import json
import aiohttp
import asyncio
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from aiohttp import ClientError

# Charger les variables d'environnement
load_dotenv()

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
options = os.getenv("MONGO_OPTIONS", "retryWrites=true&w=majority")
database_name = os.getenv("MONGO_DB", "retrodex")

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/?{options}"
POKEAPI_BASE = "https://pokeapi.co/api/v2"

# Connexion MongoDB asynchrone
client = AsyncIOMotorClient(MONGO_URI)
db = client[database_name]
collection = db["pokemons"]

# --- UTILITAIRES ------------------------------------------------------

async def fetch_json(session, url, retries=3):
    """Télécharge un JSON depuis une URL avec gestion d'erreur et retry."""
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    print(f"⚠️ Error {response.status} for {url}")
                    await asyncio.sleep(1)
                    continue
                return await response.json()
        except (asyncio.TimeoutError, ClientError) as e:
            print(f"⏳ Network error ({e}), attempt {attempt}/{retries}...")
            await asyncio.sleep(1)
    print(f"❌ Failed to fetch after {retries} attempts: {url}")
    return None


async def get_pokemon_data(session, poke_id):
    """Retrieve and merge data from /pokemon and /pokemon-species."""
    poke_url = f"{POKEAPI_BASE}/pokemon/{poke_id}"
    species_url = f"{POKEAPI_BASE}/pokemon-species/{poke_id}"

    pokemon = await fetch_json(session, poke_url)
    species = await fetch_json(session, species_url)

    if not pokemon or not species:
        return None

    # French description
    description_fr = next(
        (entry["flavor_text"].replace("\n", " ").replace("\f", " ")
         for entry in species["flavor_text_entries"]
         if entry["language"]["name"] == "fr"),
        "Aucune description disponible."
    )

    evolves_from = (
        species["evolves_from_species"]["name"]
        if species["evolves_from_species"]
        else None
    )

    return {
        "pokedex_id": pokemon["id"],
        "name": pokemon["name"],
        "name_fr": next(
            (n["name"] for n in species["names"] if n["language"]["name"] == "fr"),
            pokemon["name"]
        ),
        "types": [t["type"]["name"] for t in pokemon["types"]],
        "height_m": pokemon["height"] / 10,
        "weight_kg": pokemon["weight"] / 10,
        "stats": {s["stat"]["name"]: s["base_stat"] for s in pokemon["stats"]},
        "sprites": {
            "official": pokemon["sprites"]["other"]["official-artwork"]["front_default"],
            "thumbnail": pokemon["sprites"]["front_default"],
        },
        "description_fr": description_fr,
        "evolution_chain_url": species["evolution_chain"]["url"],
        "evolves_from": evolves_from,
    }

# --- MAIN -------------------------------------------------------------

async def main():
    print("🚀 Initializing Pokédex (Generation 1)...")

    async with aiohttp.ClientSession() as session:
        pokemons = []

        for i in tqdm(range(1, 152), desc="Fetching", unit="pokemon"):
            data = await get_pokemon_data(session, i)
            if data:
                pokemons.append(data)

    # Taille totale avant insertion
    json_bytes = json.dumps(pokemons, ensure_ascii=False).encode("utf-8")
    size_mb = len(json_bytes) / (1024 * 1024)
    print(f"\n📦 Total size: {size_mb:.2f} MB ({len(pokemons)} Pokémon)")

    # Sauvegarde locale
    os.makedirs("data", exist_ok=True)
    with open("data/pokedex_preview.json", "w", encoding="utf-8") as f:
        json.dump(pokemons, f, ensure_ascii=False, indent=2)
    print("💾 File saved: data/pokedex_preview.json")

    # --- Insertion asynchrone avec vérification
    inserted, skipped = 0, 0
    for p in tqdm(pokemons, desc="Inserting to DB", unit="pokemon"):
        if await collection.find_one({"pokedex_id": p["pokedex_id"]}):
            skipped += 1
            continue
        await collection.insert_one(p)
        inserted += 1

    print(f"\n✅ Inserted: {inserted}")
    print(f"🔁 Skipped (already in DB): {skipped}")
    print("🎉 Pokédex initialization completed successfully.")


# --- EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Manual interruption.")
        sys.exit(0)
