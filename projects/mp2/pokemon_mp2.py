# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "requests",
# ]
# ///

"""Pokemon Battle Advisor."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. The Question

    A player has a team of six randomly chosen Pokemon and faces one random opponent.
    Which Pokemon should they send into battle, and which move should they use to get
    the highest estimated attack score? This tool compares the moves' power,
    accuracy and type effectiveness to help the player choose.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. My Plan Before AI



    1. Pick seven different Pokemon IDs at random from the first 151 Pokemon.
    2. Request each Pokemon from the API and save its name, types and moves.
    3. Use the first six Pokemon as my team and the seventh as the opponent.
    4. Get the opponent's type weaknesses and resistances from the API.
    5. For each team member, look up moves it can learn and keep up to four attacks.
    6. Give each attack a score using power, accuracy, type effectiveness and STAB.
    7. Show a table of the six best moves and recommend the Pokemon with the top score.
    8. Save the table to CSV and verify the winner's type multiplier in a second way.

    **Functions and their inputs/outputs:**

    - `get_pokemon(ids)` takes a list of IDs and returns a list of Pokemon records.
    - `get_usable_moves(pokemon, count, limit, cache)` takes a Pokemon and returns
      a list of up to `count` attacking moves from at most `limit` checked moves.
    - `get_defender_types(types)` takes the opponent's types and returns their
      damage relations. `type_advantage` turns those relations into one multiplier.

    **API addresses:** `https://pokeapi.co/api/v2/pokemon/{id}/`,
    `https://pokeapi.co/api/v2/move/{name}/`,
    `https://pokeapi.co/api/v2/type/{name}/`.

    I will check that the API returns information for all seven Pokémon. The final table should have six rows because the seventh Pokémon is the opponent.

    I will calculate the winning move's type multiplier once
    from the defending type and again from the attacking type. Both numbers should agree.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Inputs

    Change the seed to get a different team and opponent.
    The first 151 Pokemon are used. Four is the maximum number of attacking moves
    considered for each Pokemon. We check at most 12 random moves to limit API calls.
    """)
    return


@app.cell
def _():
    max_pokemon_id = 151
    random_seed = 1234
    moves_per_pokemon = 4
    max_moves_checked = 12
    return max_moves_checked, max_pokemon_id, moves_per_pokemon, random_seed


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. The Work
    """)
    return


@app.cell
def _():
    import random
    import requests
    import csv
    import json

    return csv, json, random, requests


@app.cell
def _(max_pokemon_id, random, random_seed):
    if max_pokemon_id < 7:
        raise ValueError("max_pokemon_id must be at least 7")
    random.seed(random_seed)
    selected_ids = random.sample(range(1, max_pokemon_id + 1), 7)
    return (selected_ids,)


@app.cell
def _(requests):
    def get_pokemon(ids):
        records = []
        for pokemon_id in ids:
            reply = requests.get(
                f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/",
                timeout=10,
            )
            if reply.status_code != 200:
                raise ValueError(f"Pokemon request failed: {pokemon_id}")
            data = reply.json()
            types = []
            moves = []
            for item in data["types"]:
                types.append(item["type"]["name"])
            for item in data["moves"]:
                moves.append(item["move"]["name"])
            records.append({"name": data["name"], "types": types, "moves": moves})
        return records

    return (get_pokemon,)


@app.cell
def _(random, requests):
    def get_usable_moves(pokemon, count, limit, cache):
        usable = []
        checked = 0
        random_moves = random.sample(pokemon["moves"], len(pokemon["moves"]))
        for move_name in random_moves:
            if len(usable) == count or checked == limit:
                break
            checked += 1
            if move_name not in cache:
                reply = requests.get(
                    f"https://pokeapi.co/api/v2/move/{move_name}/",
                    timeout=10,
                )
                if reply.status_code != 200:
                    raise ValueError(f"Move request failed: {move_name}")
                cache[move_name] = reply.json()
            move = cache[move_name]
            if move.get("power") is not None and move["power"] > 0:
                if move["damage_class"]["name"] != "status":
                    accuracy = move["accuracy"]
                    if accuracy is None:
                        accuracy = 100
                    usable.append({
                        "name": move["name"],
                        "type": move["type"]["name"],
                        "power": move["power"],
                        "accuracy": accuracy,
                    })
        return usable

    return (get_usable_moves,)


@app.cell
def _(requests):
    def get_defender_types(types):
        relations = []
        for type_name in types:
            reply = requests.get(
                f"https://pokeapi.co/api/v2/type/{type_name}/",
                timeout=10,
            )
            if reply.status_code != 200:
                raise ValueError(f"Type request failed: {type_name}")
            relations.append(reply.json()["damage_relations"])
        return relations

    return (get_defender_types,)


@app.function
def type_advantage(attack_type, defender_relations):
    multiplier = 1
    for relation in defender_relations:
        for item in relation["double_damage_from"]:
            if item["name"] == attack_type:
                multiplier *= 2
        for item in relation["half_damage_from"]:
            if item["name"] == attack_type:
                multiplier *= 0.5
        for item in relation["no_damage_from"]:
            if item["name"] == attack_type:
                multiplier *= 0
    return multiplier


@app.cell
def _(
    get_defender_types,
    get_pokemon,
    get_usable_moves,
    max_moves_checked,
    moves_per_pokemon,
    random,
    random_seed,
    selected_ids,
):
    random.seed(random_seed + 1)
    pokemon_records = get_pokemon(selected_ids)
    team = pokemon_records[:6]
    opponent = pokemon_records[6]
    defender_relations = get_defender_types(opponent["types"])
    move_cache = {}
    results = []

    for member in team:
        attacks = get_usable_moves(member, moves_per_pokemon, max_moves_checked, move_cache)
        best_attack = None
        best_score = -1
        best_effectiveness = 0
        best_stab = 1
        for attack in attacks:
            effectiveness = type_advantage(attack["type"], defender_relations)
            stab = 1
            if attack["type"] in member["types"]:
                stab = 1.5
            score = attack["power"] * attack["accuracy"] / 100 * effectiveness * stab
            if score > best_score:
                best_score = score
                best_attack = attack
                best_effectiveness = effectiveness
                best_stab = stab

        if best_attack is None:
            results.append({
                "pokemon": member["name"], "pokemon_types": "/".join(member["types"]),
                "opponent": opponent["name"], "move": "none", "move_type": "-",
                "power": 0, "accuracy": 0, "effectiveness": 0, "stab": 1, "score": 0,
            })
        else:
            results.append({
                "pokemon": member["name"], "pokemon_types": "/".join(member["types"]),
                "opponent": opponent["name"], "move": best_attack["name"],
                "move_type": best_attack["type"], "power": best_attack["power"],
                "accuracy": best_attack["accuracy"],
                "effectiveness": best_effectiveness, "stab": best_stab,
                "score": round(best_score, 2),
            })
    return opponent, pokemon_records, results


@app.cell
def _(json, mo, pokemon_records):
    raw_path = mo.notebook_dir() / "data" / "pokemon-fetched.json"
    raw_path.parent.mkdir(exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as _file:
        json.dump(pokemon_records, _file, indent=2)
    print(f"Saved: {raw_path}")
    return


@app.cell
def _(csv, mo, results):
    columns = [
        "pokemon", "pokemon_types", "opponent", "move", "move_type",
        "power", "accuracy", "effectiveness", "stab", "score",
    ]
    file_path = mo.notebook_dir() / "data" / "pokemon-results.csv"
    file_path.parent.mkdir(exist_ok=True)
    with open(file_path, "w", newline="", encoding="utf-8") as _file:
        writer = csv.DictWriter(_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved: {file_path}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. The Answer

    This is a simple attack score, NOT a probability of winning. It does not
    simulate HP, speed, items, abilities or the opponent's counterattack.
    The available attacks come from Pokemon's overall learnable move list,
    not a specific game or generation.
    """)
    return


@app.cell
def _(opponent, results):
    print(f"Opponent: {opponent['name']} ({'/'.join(opponent['types'])})")
    print()
    print(f"{'Pokemon':<15} {'Best move':<20} {'Type':<12} {'Type x':>7} {'Score':>8}")
    for _row in results:
        print(f"{_row['pokemon']:<15} {_row['move']:<20} {_row['move_type']:<12} {_row['effectiveness']:>7.1f} {_row['score']:>8.2f}")

    winner = results[0]
    for _row in results:
        if _row["score"] > winner["score"]:
            winner = _row
    print()
    if winner["move"] == "none":
        print("No usable attacking moves were found. Try a different seed or a higher move check limit.")
    else:
        print(f"Against {opponent['name']}, choose {winner['pokemon']} and use {winner['move']} (score: {winner['score']:.2f}).")
    return (winner,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 6. How I Know These Numbers Are Right

    First, check that the API returned seven Pokemon and we have six result rows.
    Then check the winning move's type multiplier from the attacking type's data.
    The score above used the defending type's data, so these are two different routes.
    """)
    return


@app.cell
def _(opponent, pokemon_records, requests, results, selected_ids, winner):
    print(f"Pokemon IDs selected: {len(selected_ids)} / returned: {len(pokemon_records)}")
    print(f"Team members: 6 / result rows: {len(results)}")
    if winner["move"] != "none":
        reply_check = requests.get(
            f"https://pokeapi.co/api/v2/type/{winner['move_type']}/",
            timeout=10,
        )
        if reply_check.status_code != 200:
            raise ValueError("Check request failed")
        attacking_relations = reply_check.json()["damage_relations"]
        check_multiplier = 1
        for defender_type in opponent["types"]:
            for item in attacking_relations["double_damage_to"]:
                if item["name"] == defender_type:
                    check_multiplier *= 2
            for item in attacking_relations["half_damage_to"]:
                if item["name"] == defender_type:
                    check_multiplier *= 0.5
            for item in attacking_relations["no_damage_to"]:
                if item["name"] == defender_type:
                    check_multiplier *= 0
        print(f"From defender types: {winner['effectiveness']}")
        print(f"From attack type:   {check_multiplier}")
        print(f"Do they agree? {winner['effectiveness'] == check_multiplier}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 7. Working With the Agent

    I told AI which data I wanted to use to rank the Pokemon: move power, accuracy, type effectiveness and STAB. AI helped me create a formula using these values and wrote the functions to calculate the scores.

    I also asked AI to write the code to get each Pokemon's weaknesses from the API, using the damage relations of their types.

    I reviewed the code to understand how the score was calculated. AI also suggested a way to verify the type effectiveness by calculating it in two different ways: using the defending Pokemon's type and the attacking move's type.

    As shown in section 6, both calculations returned 2, which confirmed that the type multiplier was correct for the selected move.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 8. Reading It Back

    **get_defender_types**

    This function takes the opponent's types and returns their damage relations from the API, which are used to identify its weaknesses and resistances.

    I reviewed the entire function, but the line I focused on the most was `reply.json()["damage_relations"]`, because I didn't know that `damage_relations` was available in the API.

    **type_advantage**

    This function takes the attacking move's type and the opponent's damage relations. It returns a multiplier based on how effective the attack is.

    I reviewed the entire function. The line I focused on was `multiplier *= 0.5`, because I wanted to check how a resistance changes the multiplier, especially when the opponent has two types. I also checked how accuracy is used later in the main score calculation.

    **Previous test (seed 7 to 1234)**

    The opponent changed from Pikachu to Fearow, and the recommendation changed from Exeggcute to Mewtwo with Ice Punch (score: 150). The prediction and result were saved in the same commit, so this did not demonstrate a prediction made before the change.

    **New prediction (before the change)**

    I will change `random_seed` from 1234 to 5678. I expect the selected Pokemon and opponent to change. This may also change the recommended Pokemon and move, but it is not guaranteed.

    I will commit this prediction before changing the seed or running the program again.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 9. Going Further

    Sometimes your first-choice Pokemon is unavailable. This extra step finds
    the second-best Pokemon and its best move from the same six results.
    """)
    return


@app.cell
def _(results, winner):
    second_choice = None
    for _row in results:
        if _row["pokemon"] != winner["pokemon"]:
            if second_choice is None or _row["score"] > second_choice["score"]:
                second_choice = _row
    print(f"Backup choice: {second_choice['pokemon']} with {second_choice['move']} (score: {second_choice['score']:.2f}).")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **What I found:** Arbok's score (135) is close to Mewtwo's (150), with a difference of 15 points. They also use different move types: Poison and Ice.

    # 10. Time Spent

    **Hours outside class:**7
    """)
    return


if __name__ == "__main__":
    app.run()
