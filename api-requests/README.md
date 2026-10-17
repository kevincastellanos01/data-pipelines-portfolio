# API requests

A single-record ETL against [PokeAPI](https://pokeapi.co/). The script asks for one Pokemon, keeps the fields worth storing, and writes a JSON file next to the code.

`pokemon_data.json` is the output of a run for Gengar.

## Pipeline

1. **Extract.** `GET https://pokeapi.co/api/v2/pokemon/{name}` with a timeout. A non-200 response stops the run.
2. **Transform.** The raw document is large. The script keeps identity and physical stats, flattens move names and held-item names, and adds counts plus a UTC timestamp.
3. **Load.** The result is written to `pokemon_data.json` in this folder.

## Run

```bash
pip install -r requirements.txt
python pokemon_etl.py
```

Change `POKEMON_NAME` in `main()` to pull a different record.
