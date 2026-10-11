# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1: Tennis Match Simulator

    Option D.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    I want to create a tennis match simulator that estimates the probability of each player winning a match based on their serving performance.

    This tool could be useful for tennis fans who want to compare players and understand how serving affects match results.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    1. Define two players and their probabilities of winning a point on serve.
    2. Use random numbers to simulate who wins each point.
    3. Use loops to calculate games, sets, and matches.
    4. Repeat the simulation many times and count each player's wins.
    5. Calculate the winning percentages and display them in a table.
    6. Compare the results when one player's serving probability changes.

    What do my loops carry?

    The loops keep track of points, games, sets, and matches won by each player.

    How will I check the results?

    I will test the simulator with one player having a 100% chance of winning every point and the other having 0%. The first player should win every match, so their total wins should equal the number of simulations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Add the players, probabilities, and number of matches here later.
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further
    """)
    return


if __name__ == "__main__":
    app.run()
