"""Extract, transform, and save a Pokemon profile from PokeAPI."""

import json
from pathlib import Path
from datetime import datetime, timezone

import requests


def extract_pokemon_data(pokemon_name: str):
    pokemon_name = pokemon_name.lower().strip()
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url, timeout=20)

    if response.status_code == 200:
        return response.json()

    print(f"Error al pedir el API. Status code: {response.status_code}")
    return None


def transform_pokemon_data(pokemon_data: dict) -> dict:
    # 1) comprehension list for moves
    moves_names = [m["move"]["name"] for m in pokemon_data.get("moves", [])]

    # 2) comprehension list for held items names
    held_items_names = [h["item"]["name"] for h in pokemon_data.get("held_items", [])]

    # 3) key to count how many held items names we have
    held_items_count = len(held_items_names)

    # 4) key for timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    parsed_data = {
        "pokemon": pokemon_data.get("name"),
        "id": pokemon_data.get("id"),
        "height": pokemon_data.get("height"),
        "weight": pokemon_data.get("weight"),
        "base_experience": pokemon_data.get("base_experience"),
        "moves_list_comprehension": moves_names,
        "moves_count": len(moves_names),
        "held_items_names_comprehension": held_items_names,
        "held_items_count": held_items_count,
        "timestamp": timestamp,
    }

    return parsed_data


def load_pokemon_data(parsed_data: dict):
    # Esto guarda el JSON SIEMPRE en la misma carpeta del .py
    output_path = Path(__file__).with_name("pokemon_data.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4, ensure_ascii=False)

    print("JSON guardado en:", output_path.resolve())


def main():
    POKEMON_NAME = "gengar" 

    data = extract_pokemon_data(POKEMON_NAME)
    if data is None:
        print("No se pudo obtener data del API. Revisa internet o el nombre del pokemon.")
        return

    parsed = transform_pokemon_data(data)
    load_pokemon_data(parsed)


if __name__ == "__main__":
    main()
