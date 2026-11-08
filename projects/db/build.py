import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # ArenaForge Sports — Database Project / Part A

    **Business question:** How can a community sports organizer manage soccer 7,
    basketball, padel and tennis competitions, including entrants, athletes,
    payments, match results and event profitability?

    This notebook builds a **DuckDB** database from **fictional CSV files**. The
    sample covers tournaments from November 2025 through October 2026.
    The design decisions and ERD are in `README.md`.
    """)
    return


@app.cell
def _(mo):
    from pathlib import Path
    import duckdb
    import polars as pl
    import matplotlib.pyplot as plt

    database = mo.notebook_dir() / "database.duckdb"
    data_dir = mo.notebook_dir() / "data"

    # Read-only and short-lived connection, as required by the assignment.
    def ask(sql):
        with duckdb.connect(str(database), read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, data_dir, database, duckdb, pl, plt


@app.cell
def _(mo):
    mo.md("""
    ## 1. The Tables

    Every table has a primary key and its foreign keys declared. Column-level rules use `NOT NULL`, `UNIQUE` and `CHECK`.
    """)
    return


@app.cell
def _():
    create_statements = [
        """
        CREATE TABLE entrants (
            entrant_id INTEGER PRIMARY KEY,
            entrant_name VARCHAR NOT NULL UNIQUE,
            sport VARCHAR NOT NULL
                CHECK (sport IN ('Soccer 7', 'Basketball', 'Padel', 'Tennis')),
            entrant_type VARCHAR NOT NULL CHECK (entrant_type IN ('team', 'pair', 'individual')),
            city VARCHAR NOT NULL,
            formed_on DATE NOT NULL,
            CHECK (
                (sport IN ('Soccer 7', 'Basketball') AND entrant_type = 'team')
                OR (sport = 'Padel' AND entrant_type = 'pair')
                OR (sport = 'Tennis' AND entrant_type = 'individual')
            )
        )
        """,
        """
        CREATE TABLE tournaments (
            tournament_id INTEGER PRIMARY KEY,
            tournament_name VARCHAR NOT NULL UNIQUE,
            sport VARCHAR NOT NULL
                CHECK (sport IN ('Soccer 7', 'Basketball', 'Padel', 'Tennis')),
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            venue_type VARCHAR NOT NULL CHECK (venue_type IN ('outdoor', 'indoor', 'sports_center')),
            entry_fee DECIMAL(12,2) NOT NULL CHECK (entry_fee > 0),
            prize_pool DECIMAL(12,2) NOT NULL CHECK (prize_pool > 0),
            event_budget DECIMAL(12,2) NOT NULL CHECK (event_budget > 0),
            CHECK (end_date >= start_date)
        )
        """,
        """
        CREATE TABLE sponsors (
            sponsor_id INTEGER PRIMARY KEY,
            sponsor_name VARCHAR NOT NULL UNIQUE,
            industry VARCHAR NOT NULL,
            country VARCHAR NOT NULL
        )
        """,
        """
        CREATE TABLE athletes (
            athlete_id INTEGER PRIMARY KEY,
            entrant_id INTEGER NOT NULL REFERENCES entrants(entrant_id),
            athlete_code VARCHAR NOT NULL UNIQUE,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR NOT NULL,
            joined_on DATE NOT NULL
        )
        """,
        """
        CREATE TABLE registrations (
            registration_id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
            entrant_id INTEGER NOT NULL REFERENCES entrants(entrant_id),
            registered_on DATE NOT NULL,
            fee_due DECIMAL(12,2) NOT NULL CHECK (fee_due > 0),
            UNIQUE (tournament_id, entrant_id)
        )
        """,
        """
        CREATE TABLE registration_payments (
            payment_id INTEGER PRIMARY KEY,
            registration_id INTEGER NOT NULL REFERENCES registrations(registration_id),
            paid_on DATE NOT NULL,
            method VARCHAR NOT NULL CHECK (method IN ('card', 'bank', 'paypal')),
            amount DECIMAL(12,2) NOT NULL CHECK (amount > 0)
        )
        """,
        """
        CREATE TABLE matches (
            match_id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
            home_registration_id INTEGER NOT NULL REFERENCES registrations(registration_id),
            away_registration_id INTEGER NOT NULL REFERENCES registrations(registration_id),
            starts_at TIMESTAMP NOT NULL,
            home_score INTEGER NOT NULL CHECK (home_score >= 0),
            away_score INTEGER NOT NULL CHECK (away_score >= 0),
            spectators INTEGER NOT NULL CHECK (spectators >= 0),
            CHECK (home_registration_id <> away_registration_id),
            CHECK (home_score <> away_score)
        )
        """,
        """
        CREATE TABLE sponsorships (
            sponsorship_id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
            sponsor_id INTEGER NOT NULL REFERENCES sponsors(sponsor_id),
            received_on DATE NOT NULL,
            amount_received DECIMAL(12,2) NOT NULL CHECK (amount_received > 0),
            UNIQUE (tournament_id, sponsor_id)
        )
        """,
        """
        CREATE TABLE event_expenses (
            expense_id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
            spent_on DATE NOT NULL,
            category VARCHAR NOT NULL
                CHECK (category IN ('venue', 'officials', 'marketing', 'staff', 'equipment')),
            amount DECIMAL(12,2) NOT NULL CHECK (amount > 0)
        )
        """,
        """
        CREATE TABLE prize_payouts (
            payout_id INTEGER PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
            registration_id INTEGER NOT NULL REFERENCES registrations(registration_id),
            placement INTEGER NOT NULL CHECK (placement IN (1, 2, 3)),
            paid_on DATE NOT NULL,
            amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
            UNIQUE (tournament_id, placement),
            UNIQUE (tournament_id, registration_id)
        )
        """,
    ]
    return (create_statements,)


@app.cell
def _(mo):
    mo.md("""
    ## 2. The Data

    The file make_data.py generates ten fictional CSV files reproducibly (random seed
    6301). There are more than 1,000 transactional rows. Soccer 7 has seven
    athletes per entrant, basketball five, padel two and tennis singles one.
    Match scores represent goals, points or sets respectively.

    **Intentional exceptions:** Registration `11` is short by **$17**, and
    registration `107` has **$20 extra**. These are the **only two** rows that
    break our cross-row payment rule. They remain in the database so Part B,
    Question 7, can find them. A positive-amount `CHECK` cannot catch either.
    """)
    return


@app.cell
def _():
    # Each view answers one simple question with GROUP BY.
    # Making the totals separately avoids multiplying amounts in joins.
    view_statements = [
        """
        CREATE VIEW vw_paid_entries AS
        SELECT r.tournament_id, SUM(p.amount) AS registration_revenue
        FROM registrations r
        JOIN registration_payments p ON r.registration_id = p.registration_id
        GROUP BY r.tournament_id
        """,
        """
        CREATE VIEW vw_sponsor_income AS
        SELECT tournament_id, SUM(amount_received) AS sponsor_revenue
        FROM sponsorships
        GROUP BY tournament_id
        """,
        """
        CREATE VIEW vw_operating_costs AS
        SELECT tournament_id, SUM(amount) AS operating_expenses
        FROM event_expenses
        GROUP BY tournament_id
        """,
        """
        CREATE VIEW vw_prize_costs AS
        SELECT tournament_id, SUM(amount) AS prize_expenses
        FROM prize_payouts
        GROUP BY tournament_id
        """,
        """
        CREATE VIEW vw_tournament_finances AS
        SELECT t.tournament_id, t.tournament_name, t.sport,
               t.start_date, t.end_date, t.event_budget,
               COALESCE(p.registration_revenue, 0) AS registration_revenue,
               COALESCE(s.sponsor_revenue, 0) AS sponsor_revenue,
               COALESCE(e.operating_expenses, 0) AS operating_expenses,
               COALESCE(pr.prize_expenses, 0) AS prize_expenses,
               COALESCE(p.registration_revenue, 0)
                 + COALESCE(s.sponsor_revenue, 0) AS total_revenue,
               COALESCE(e.operating_expenses, 0)
                 + COALESCE(pr.prize_expenses, 0) AS total_cost,
               COALESCE(p.registration_revenue, 0)
                 + COALESCE(s.sponsor_revenue, 0)
                 - COALESCE(e.operating_expenses, 0)
                 - COALESCE(pr.prize_expenses, 0) AS net_profit
        FROM tournaments t
        LEFT JOIN vw_paid_entries p ON t.tournament_id = p.tournament_id
        LEFT JOIN vw_sponsor_income s ON t.tournament_id = s.tournament_id
        LEFT JOIN vw_operating_costs e ON t.tournament_id = e.tournament_id
        LEFT JOIN vw_prize_costs pr ON t.tournament_id = pr.tournament_id
        """,
    ]
    return (view_statements,)


@app.cell
def _(create_statements, data_dir, database, duckdb, mo, view_statements):
    # The database file is deliberately rebuilt from scratch each time.
    if database.exists():
        database.unlink()
    _load_order = [
        "entrants", "tournaments", "sponsors", "athletes", "registrations",
        "registration_payments", "matches", "sponsorships",
        "event_expenses", "prize_payouts",
    ]
    with duckdb.connect(str(database)) as _con:
        for _statement in create_statements:
            _con.execute(_statement)
        for _table_name in _load_order:
            _csv = (data_dir / f"{_table_name}.csv").as_posix().replace("'", "''")
            _con.execute(
                f"INSERT INTO {_table_name} SELECT * FROM read_csv_auto('{_csv}', header=true)"
            )
        for _view in view_statements:
            _con.execute(_view)
    build_done = True
    mo.md("**Database built.** All CSVs loaded into `database.duckdb`, then the connection was closed.")
    return


@app.cell
def _(ask, mo):
    # Cross-table business rules cannot be enforced by a single-column CHECK.
    _invalid_registrations = int(ask("""
        SELECT COUNT(*) AS n FROM registrations r
        JOIN tournaments t ON t.tournament_id = r.tournament_id
        JOIN entrants e ON e.entrant_id = r.entrant_id
        WHERE t.sport <> e.sport
    """)["n"][0])
    _invalid_matches = int(ask("""
        SELECT COUNT(*) AS n FROM matches m
        JOIN registrations h ON h.registration_id = m.home_registration_id
        JOIN registrations a ON a.registration_id = m.away_registration_id
        WHERE h.tournament_id <> m.tournament_id
           OR a.tournament_id <> m.tournament_id
           OR h.entrant_id = a.entrant_id
    """)["n"][0])
    _wrong_rosters = int(ask("""
        SELECT COUNT(*) AS n FROM (
            SELECT e.entrant_id, e.sport, COUNT(a.athlete_id) AS athletes
            FROM entrants e LEFT JOIN athletes a ON a.entrant_id = e.entrant_id
            GROUP BY e.entrant_id, e.sport
        ) x
        WHERE athletes <> CASE sport
            WHEN 'Soccer 7' THEN 7 WHEN 'Basketball' THEN 5
            WHEN 'Padel' THEN 2 ELSE 1 END
    """)["n"][0])
    assert (_invalid_registrations, _invalid_matches, _wrong_rosters) == (0, 0, 0)
    mo.md(
        f"**Cross-table checks passed:** {_invalid_registrations} cross-sport registrations, "
        f"{_invalid_matches} mismatched match participants, and {_wrong_rosters} wrong roster sizes."
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. A Look at the Data

    I checked the number of tournament registrations by month. The activity is not exactly the same every month, but it stays reasonably steady because the company runs two events each month.
    """)
    return


@app.cell
def _(data_dir, pl, plt):
    _reg_csv = pl.read_csv(data_dir / "registrations.csv")
    _monthly_regs = (
        _reg_csv.with_columns(pl.col("registered_on").str.slice(0, 7).alias("month"))
        .group_by("month").len().sort("month")
    )
    _fig, _ax = plt.subplots(figsize=(9, 3.5))
    _ax.bar(_monthly_regs["month"].to_list(), _monthly_regs["len"].to_list())
    _ax.set_title("Competitor registrations by month (simulated)")
    _ax.set_xlabel("Month")
    _ax.set_ylabel("Registrations")
    _ax.tick_params(axis="x", labelrotation=55)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Row Counts

    All entities and transactional tables are included.
    """)
    return


@app.cell
def _(ask, mo, pl):
    _tables = [
        "entrants", "athletes", "tournaments", "registrations", "registration_payments",
        "matches", "sponsors", "sponsorships", "event_expenses", "prize_payouts",
    ]
    _rows = []
    for _table in _tables:
        _count = int(ask(f"SELECT COUNT(*) AS n FROM {_table}")["n"][0])
        _rows.append({"table": _table, "rows": _count})
    _row_counts = pl.DataFrame(_rows)
    # These six tables record business activities (not lists of people or events).
    _activity_names = ["registrations", "registration_payments", "matches",
                       "sponsorships", "event_expenses", "prize_payouts"]
    _activity_total = 0
    for _item in _rows:
        if _item["table"] in _activity_names:
            _activity_total += _item["rows"]
    mo.vstack([mo.ui.table(_row_counts),
               mo.md(f"**Activity rows:** {_activity_total:,}.")])
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. A Row It Refuses

    A negative operating expense violates the `CHECK (amount > 0)` constraint. The insert is wrapped in `try/except` and should leave the data unchanged.
    """)
    return


@app.cell
def _(database, duckdb, mo):
    try:
        with duckdb.connect(str(database)) as _con:
            _con.execute(
                "INSERT INTO event_expenses (expense_id, tournament_id, spent_on, category, amount) "
                "VALUES (999999, 1, '2026-01-10', 'staff', -10.00)"
            )
        _rejection = "ERROR: This row was accepted; the constraint is missing."
    except duckdb.ConstraintException as _error:
        _rejection = "Rejected by DuckDB, as expected: " + str(_error).split("\n")[0]
    mo.md(_rejection)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. Answers You Already Knew

    The generator deliberately creates 24 tournaments, 480 matches, and two sponsors with no deals. I wrote these expectations before running the queries.
    """)
    return


@app.cell
def _(ask, mo):
    _n_tournaments = int(ask("SELECT COUNT(*) AS n FROM tournaments")["n"][0])
    _n_matches = int(ask("SELECT COUNT(*) AS n FROM matches")["n"][0])
    _n_unused_sponsors = int(ask("""
        SELECT COUNT(*) AS n
        FROM sponsors s LEFT JOIN sponsorships sp ON sp.sponsor_id = s.sponsor_id
        WHERE sp.sponsorship_id IS NULL
    """)["n"][0])
    assert (_n_tournaments, _n_matches, _n_unused_sponsors) == (24, 480, 2)
    mo.md(
        f"1. **Events:** expected 24, found **{_n_tournaments}**.  "
        f"\n2. **Matches:** expected 480, found **{_n_matches}**.  "
        f"\n3. **Sponsors without deals:** expected 2, found **{_n_unused_sponsors}**.  "
        f"\n\nAll three expectations matched."
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7. A View

    I made four small views that total registration payments, sponsor money, operating costs and prizes. `vw_tournament_finances` joins those totals to show **one row per tournament**, without counting any payment twice. Part B Questions 1 and 2 use this view.
    """)
    return


@app.cell
def _(ask, mo):
    mo.vstack([
        mo.md("### Five tournaments from the finance view"),
        mo.ui.table(ask("""
            SELECT tournament_name, sport, registration_revenue,
                   sponsor_revenue, total_cost, net_profit
            FROM vw_tournament_finances
            ORDER BY net_profit DESC
            LIMIT 5
        """)),
    ])
    return


if __name__ == "__main__":
    app.run()
