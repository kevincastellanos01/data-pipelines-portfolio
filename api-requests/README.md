# API requests

This script pulls one Pokemon from [PokeAPI](https://pokeapi.co/) and writes the record I actually want to keep. `pokemon_data.json` is a run for Gengar.

The API document is large and nested: moves, held items, sprites, game indices. Storing it whole would keep fields this pipeline never reads. The transform keeps identity and body stats, replaces the move and item objects with name lists, and adds `moves_count` and `held_items_count` so a later check does not have to measure the lists again.

`timestamp` is UTC at transform time. The file can be overwritten on the next run, and the timestamp says which pull produced it.

The load step writes `pokemon_data.json` beside the script. One record does not need a database. The contract is the JSON shape: if the name, the lists, or the counts change, this file shows it.

A non-200 response stops the run. Writing an empty file would look like a successful extract of a Pokemon that was never returned.

## Run

```bash
pip install -r requirements.txt
python pokemon_etl.py
```

`POKEMON_NAME` in `main()` selects the record. The default is `gengar`.
