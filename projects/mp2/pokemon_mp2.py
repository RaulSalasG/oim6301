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


if __name__ == "__main__":
    app.run()
