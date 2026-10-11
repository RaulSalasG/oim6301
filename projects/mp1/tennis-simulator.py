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
    import random

    return mo, random


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1: Tennis Match Simulator

    Option D - My own tool.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question
    Which player is more likely to win a tennis match based on their probability of winning points on serve?

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

    These serve percentages are examples, not real player statistics.
    """)
    return


@app.cell
def _():
    player_a = "Alcaraz"
    player_b = "Sinner"
    serve_win_percent_a = 65
    serve_win_percent_b = 62
    number_of_matches = 1000
    random_seed = 2026
    extra_serve_percentage_points = 5
    return (
        extra_serve_percentage_points,
        number_of_matches,
        player_a,
        player_b,
        serve_win_percent_a,
        serve_win_percent_b,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Simulate points, games, sets and matches. A match ends when someone wins two sets.
    """)
    return


@app.cell
def _(random):
    def play_point(server, percent_a, percent_b):
        number = random.random()

        if server == "A":
            if number < percent_a / 100:
                return "A"
            return "B"

        if number < percent_b / 100:
            return "B"
        return "A"


    def play_game(server, percent_a, percent_b):
        points_a = 0
        points_b = 0

        while True:
            winner = play_point(server, percent_a, percent_b)

            if winner == "A":
                points_a += 1
            else:
                points_b += 1

            if max(points_a, points_b) >= 4 and abs(points_a - points_b) >= 2:
                return winner


    def play_tiebreak(server, percent_a, percent_b):
        points_a = 0
        points_b = 0
        first_server = server
        played = 0

        while max(points_a, points_b) < 7 or abs(points_a - points_b) < 2:
            winner = play_point(server, percent_a, percent_b)

            if winner == "A":
                points_a += 1
            else:
                points_b += 1

            played += 1

            if played % 2 == 1:
                server = "B" if server == "A" else "A"


        return "A" if points_a > points_b else "B"


    def play_match(percent_a, percent_b):
        sets_a = 0
        sets_b = 0
        server = "A"
        scores = []

        while sets_a < 2 and sets_b < 2:
            games_a = 0
            games_b = 0

        
            while max(games_a, games_b) < 6 or abs(games_a - games_b) < 2:
                if games_a == 6 and games_b == 6:
                    winner = play_tiebreak(server, percent_a, percent_b)
                else:
                    winner = play_game(server, percent_a, percent_b)
        
                if winner == "A":
                    games_a += 1
                else:
                    games_b += 1
        
                if server == "A":
                    server = "B"
                else:
                    server = "A"


            scores.append((games_a, games_b))

            if games_a > games_b:
                sets_a += 1
            else:
                sets_b += 1

        return ("A", scores) if sets_a > sets_b else ("B", scores)


    def simulate_many(percent_a, percent_b, matches):
        wins_a = 0
        wins_b = 0
        examples = []

        for i in range(matches):
            winner, scores = play_match(percent_a, percent_b)

            if winner == "A":
                wins_a += 1
            else:
                wins_b += 1

            if i < 10:
                examples.append((i + 1, winner, scores))

        return wins_a, wins_b, examples


    return (simulate_many,)


@app.cell
def _(
    number_of_matches,
    serve_win_percent_a,
    serve_win_percent_b,
    simulate_many,
):
    wins_a, wins_b, examples = simulate_many(
        serve_win_percent_a, serve_win_percent_b, number_of_matches)
    chance_a = wins_a * 100 / number_of_matches
    chance_b = wins_b * 100 / number_of_matches
    return chance_a, chance_b, examples, wins_a, wins_b


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    First 10 matches and overall win percentages.
    """)
    return


@app.cell
def _(chance_a, chance_b, examples, player_a, player_b, wins_a, wins_b):
    print("MATCH RESULTS")

    for match, winner, sets in examples:
        if winner == "A":
            name = player_a
        else:
            name = player_b

        print(f'Match {match}: {name} wins {sets}')

    print("\nFINAL RESULTS")
    print(f'{player_a}: {wins_a} wins ({chance_a}%)')
    print(f'{player_b}: {wins_b} wins ({chance_b}%)')

    if wins_a > wins_b:
        print(f'{player_a} is more likely to win.')
    elif wins_b > wins_a:
        print(f'{player_b} is more likely to win.')
    else:
        print('Both players have the same chance of winning.')

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    If A wins every point, the score should always be 6-0, 6-0.
    I also test the opposite case and check the total number of matches.
    """)
    return


@app.cell
def _(number_of_matches, simulate_many, wins_a, wins_b):
    test_count = 10

    a_wins, b_wins, a_games = simulate_many(100, 0, test_count)
    a2_wins, b2_wins, b_games = simulate_many(0, 100, test_count)

    print(f'A wins: Expected {test_count}, Actual {a_wins}')
    print(f'B wins: Expected {test_count}, Actual {b2_wins}')

    print(f'Total matches: Expected {number_of_matches}, Actual {wins_a + wins_b}')

    print(a_wins == test_count)
    print(b2_wins == test_count)
    print(wins_a + wins_b == number_of_matches)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    AI helped with the organization of the code (suggesting to make it by running different functions inside other functions) and the tiebreak code.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    What happens if Player A improves their serve by 5 percentage points?
    """)
    return


@app.cell
def _(
    chance_a,
    chance_b,
    extra_serve_percentage_points,
    number_of_matches,
    player_a,
    player_b,
    serve_win_percent_a,
    serve_win_percent_b,
    simulate_many,
):

    improved_serve = serve_win_percent_a + extra_serve_percentage_points

    new_wins_a, new_wins_b, examples_new = simulate_many(
        improved_serve, serve_win_percent_b, number_of_matches
    )

    new_chance_a = new_wins_a * 100 / number_of_matches
    new_chance_b = new_wins_b * 100 / number_of_matches

    print("ORIGINAL RESULTS")
    print(f'{player_a}: {chance_a}%')
    print(f'{player_b}: {chance_b}%')

    print("RESULTS WITH BETTER SERVE")
    print(f'{player_a}: {new_chance_a}%')
    print(f'{player_b}: {new_chance_b}%')

    print(f'Improvement for {player_a}: {round(new_chance_a - chance_a,2)} percentage points')

    return


if __name__ == "__main__":
    app.run()
