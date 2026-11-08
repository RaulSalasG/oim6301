"""Make fictional CSV files for the ArenaForge Sports database.

Run from your course repository:
    uv run python projects/db/make_data.py

The same random seed creates the same data every time.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
SPORTS = ["Soccer 7", "Basketball", "Padel", "Tennis"]
ROSTER_SIZES = {"Soccer 7": 7, "Basketball": 5, "Padel": 2, "Tennis": 1}
ENTRANT_TYPES = {"Soccer 7": "team", "Basketball": "team", "Padel": "pair", "Tennis": "individual"}
VENUES = {"Soccer 7": "outdoor", "Basketball": "indoor", "Padel": "sports_center", "Tennis": "sports_center"}
CITIES = ["Boston", "Cambridge", "Newton", "Quincy", "Brookline", "Somerville", "Waltham", "Needham", "Wellesley", "Norwood", "Medford", "Milton"]
NICKNAMES = ["Falcons", "Wolves", "Rockets", "Tigers", "Titans", "Eagles", "Cyclones", "Panthers", "Chargers", "Lions", "Hawks", "Comets"]
FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Riley", "Jamie", "Casey", "Avery", "Sam", "Cameron", "Drew", "Logan", "Harper", "Hayden", "Robin", "Reese", "Kai", "Milan", "Nico", "Leo"]
LAST_NAMES = ["Santos", "Morris", "Nguyen", "Kim", "Patel", "Rivera", "Torres", "Smith", "Garcia", "Wilson", "Lopez", "Martin", "Li", "Chen", "Brown", "Johnson", "Taylor", "Anderson", "Singh", "Perez"]
SPONSOR_NAMES = [
    "Momentum Sportswear", "CourtSide Drinks", "Stride Footwear", "Northside Physio",
    "Pulse Hydration", "Ace Fitness", "Community Credit Union", "Active Nutrition",
    "Peak Performance", "Metro Sports Shop", "City Bike Co", "GameDay Snacks",
    "BlueSky Insurance", "Baseline Health", "Future Fuel", "Harbor Travel",
]
CATEGORIES = ["venue", "officials", "marketing", "staff", "equipment"]
ENTRY_FEES = {"Soccer 7": [180, 200, 220], "Basketball": [160, 190, 210], "Padel": [60, 75, 90], "Tennis": [35, 45, 60]}
PRIZE_POOLS = {"Soccer 7": [1200, 1500, 1800], "Basketball": [1100, 1400, 1750], "Padel": [500, 650, 800], "Tennis": [400, 550, 700]}
BUDGETS = {"Soccer 7": [6500, 7500, 8500], "Basketball": [6000, 7000, 8000], "Padel": [3600, 4200, 4900], "Tennis": [3200, 3900, 4500]}
BASE_EXPENSES = {"venue": 550, "officials": 280, "marketing": 190, "staff": 290, "equipment": 90}


def save_csv(filename, rows, columns):
    """Write a list of dictionaries to a CSV file."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def make_score(sport, rng):
    """Soccer scores are goals; basketball scores are points; racket scores are sets."""
    home_wins = rng.random() < 0.5
    if sport == "Soccer 7":
        winner = rng.randint(1, 6)
        loser = rng.randint(0, 4)
        winner = max(winner, loser + 1)
    elif sport == "Basketball":
        winner = rng.randint(70, 110)
        loser = rng.randint(48, winner - 1)
    else:
        winner = 2
        loser = rng.choice([0, 1])

    if home_wins:
        return winner, loser
    return loser, winner


def main():
    rng = random.Random(6301)

    entrants = []
    athletes = []
    tournaments = []
    registrations = []
    payments = []
    matches = []
    sponsors = []
    sponsorships = []
    expenses = []
    payouts = []

    # 1. Make 12 entrants for each sport, with the correct number of athletes.
    for sport_index in range(len(SPORTS)):
        sport = SPORTS[sport_index]
        for entrant_no in range(12):
            entrant_id = sport_index * 12 + entrant_no + 1
            city = CITIES[(entrant_no + sport_index) % len(CITIES)]
            members = []
            for roster_slot in range(ROSTER_SIZES[sport]):
                athlete_id = len(athletes) + 1
                first = FIRST_NAMES[(athlete_id * 3) % len(FIRST_NAMES)]
                last = LAST_NAMES[(athlete_id * 7) % len(LAST_NAMES)]
                members.append((first, last))
                athletes.append({
                    "athlete_id": athlete_id,
                    "entrant_id": entrant_id,
                    "athlete_code": f"ATH{athlete_id:03d}",
                    "first_name": first,
                    "last_name": last,
                    "joined_on": date(2025, 1 + (athlete_id - 1) % 10, 3 + (athlete_id - 1) % 20).isoformat(),
                })

            if sport == "Tennis":
                name = f"{members[0][0]} {members[0][1]} (Singles {entrant_no + 1:02d})"
            elif sport == "Padel":
                name = f"{city} Padel Pair {entrant_no + 1:02d}"
            else:
                name = f"{city} {NICKNAMES[entrant_no]} {sport.replace(' ', '')}"

            entrants.append({
                "entrant_id": entrant_id,
                "entrant_name": name,
                "sport": sport,
                "entrant_type": ENTRANT_TYPES[sport],
                "city": city,
                "formed_on": date(2023 + entrant_no % 3, 1 + entrant_no % 10, 5).isoformat(),
            })

    # 2. Make sponsors. Sponsors 15 and 16 will have no agreements.
    industries = ["sports", "health", "retail", "finance"]
    countries = ["United States", "Spain", "Canada", "Germany"]
    for i in range(len(SPONSOR_NAMES)):
        sponsor_id = i + 1
        sponsors.append({
            "sponsor_id": sponsor_id,
            "sponsor_name": SPONSOR_NAMES[i],
            "industry": industries[sponsor_id % 4],
            "country": countries[sponsor_id % 4],
        })

    # Group entrants by sport, leaving the last entrant in each sport unused.
    available = {}
    for sport in SPORTS:
        available[sport] = []
        for entrant in entrants:
            if entrant["sport"] == sport and (entrant["entrant_id"] - 1) % 12 != 11:
                available[sport].append(entrant["entrant_id"])

    registration_id = 0
    payment_id = 0
    match_id = 0
    sponsorship_id = 0
    expense_id = 0
    payout_id = 0

    # 3. Two tournaments per month, November 2025 through October 2026.
    year = 2025
    month = 11
    for month_number in range(12):
        for event_no in range(2):
            tournament_id = month_number * 2 + event_no + 1
            sport = SPORTS[(tournament_id - 1) % len(SPORTS)]
            day = [10, 22][event_no]
            start = date(year, month, day)
            end = start + timedelta(days=3)
            entry_fee = rng.choice(ENTRY_FEES[sport])
            prize_pool = rng.choice(PRIZE_POOLS[sport])
            budget = rng.choice(BUDGETS[sport])

            tournaments.append({
                "tournament_id": tournament_id,
                "tournament_name": f"ArenaForge {sport} Open {year}-{month:02d}-{event_no + 1}",
                "sport": sport,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "venue_type": VENUES[sport],
                "entry_fee": f"{entry_fee:.2f}",
                "prize_pool": f"{prize_pool:.2f}",
                "event_budget": f"{budget:.2f}",
            })

            # 4. Registrations and one or two payments per registration.
            participants = rng.sample(available[sport], rng.randint(8, 10))
            event_regs = []
            for entrant_id in participants:
                registration_id += 1
                event_regs.append(registration_id)
                registered_on = start - timedelta(days=rng.randint(2, 8))
                registrations.append({
                    "registration_id": registration_id,
                    "tournament_id": tournament_id,
                    "entrant_id": entrant_id,
                    "registered_on": registered_on.isoformat(),
                    "fee_due": f"{entry_fee:.2f}",
                })

                if registration_id % 3 == 0:
                    first_payment = round(entry_fee * 0.6, 2)
                    amounts = [first_payment, round(entry_fee - first_payment, 2)]
                else:
                    amounts = [entry_fee]

                for part_no in range(len(amounts)):
                    amount = amounts[part_no]
                    # These two errors are intentional for SQL Question 7.
                    if part_no == len(amounts) - 1 and registration_id == 11:
                        amount = amount - 17
                    if part_no == len(amounts) - 1 and registration_id == 107:
                        amount = amount + 20
                    payment_id += 1
                    payments.append({
                        "payment_id": payment_id,
                        "registration_id": registration_id,
                        "paid_on": (registered_on + timedelta(days=part_no)).isoformat(),
                        "method": ["card", "bank", "paypal"][registration_id % 3],
                        "amount": f"{amount:.2f}",
                    })

            # 5. Build every possible pair with two loops, and choose 20 matches.
            possible_pairs = []
            for i in range(len(event_regs)):
                for j in range(i + 1, len(event_regs)):
                    possible_pairs.append((event_regs[i], event_regs[j]))
            rng.shuffle(possible_pairs)

            wins = {}
            for reg in event_regs:
                wins[reg] = 0
            for slot in range(20):
                home_reg, away_reg = possible_pairs[slot]
                match_id += 1
                match_day = start + timedelta(days=slot // 5)
                hour = 10 + 2 * (slot % 5)
                home_score, away_score = make_score(sport, rng)
                if home_score > away_score:
                    wins[home_reg] += 1
                else:
                    wins[away_reg] += 1

                # Draw possible audience sizes for the four sports, then pick one.
                # Keeping this order also reproduces the original CSV files.
                crowds = {
                    "Soccer 7": rng.randint(45, 300),
                    "Basketball": rng.randint(70, 420),
                    "Padel": rng.randint(15, 95),
                    "Tennis": rng.randint(20, 140),
                }
                audience = crowds[sport]

                matches.append({
                    "match_id": match_id,
                    "tournament_id": tournament_id,
                    "home_registration_id": home_reg,
                    "away_registration_id": away_reg,
                    "starts_at": f"{match_day.isoformat()} {hour:02d}:00:00",
                    "home_score": home_score,
                    "away_score": away_score,
                    "spectators": audience,
                })

            # 6. Rank registrations by wins. The smallest ID wins a tie.
            ranking = []
            for reg in event_regs:
                ranking.append((-wins[reg], reg))
            ranking.sort()
            shares = [0.50, 0.30, 0.20]
            for place_index in range(3):
                reg = ranking[place_index][1]
                payout_id += 1
                payouts.append({
                    "payout_id": payout_id,
                    "tournament_id": tournament_id,
                    "registration_id": reg,
                    "placement": place_index + 1,
                    "paid_on": (end + timedelta(days=1)).isoformat(),
                    "amount": f"{prize_pool * shares[place_index]:.2f}",
                })

            # 7. Sponsors and expenses for the tournament.
            chosen_sponsors = rng.sample(range(1, 15), rng.randint(2, 4))
            for sponsor_id in chosen_sponsors:
                sponsorship_id += 1
                sponsorships.append({
                    "sponsorship_id": sponsorship_id,
                    "tournament_id": tournament_id,
                    "sponsor_id": sponsor_id,
                    "received_on": (start - timedelta(days=rng.randint(1, 7))).isoformat(),
                    "amount_received": f"{rng.randint(10, 35) * 100:.2f}",
                })

            for i in range(10):
                expense_id += 1
                category = CATEGORIES[i % len(CATEGORIES)]
                expenses.append({
                    "expense_id": expense_id,
                    "tournament_id": tournament_id,
                    "spent_on": (start + timedelta(days=rng.randint(0, 3))).isoformat(),
                    "category": category,
                    "amount": f"{BASE_EXPENSES[category] + rng.randint(40, 290):.2f}",
                })

        # Move to the following month.
        month += 1
        if month == 13:
            month = 1
            year += 1

    # Save every table. Column names stay in the same order as in build.py.
    tables = {
        "entrants.csv": (entrants, ["entrant_id", "entrant_name", "sport", "entrant_type", "city", "formed_on"]),
        "athletes.csv": (athletes, ["athlete_id", "entrant_id", "athlete_code", "first_name", "last_name", "joined_on"]),
        "tournaments.csv": (tournaments, ["tournament_id", "tournament_name", "sport", "start_date", "end_date", "venue_type", "entry_fee", "prize_pool", "event_budget"]),
        "registrations.csv": (registrations, ["registration_id", "tournament_id", "entrant_id", "registered_on", "fee_due"]),
        "registration_payments.csv": (payments, ["payment_id", "registration_id", "paid_on", "method", "amount"]),
        "matches.csv": (matches, ["match_id", "tournament_id", "home_registration_id", "away_registration_id", "starts_at", "home_score", "away_score", "spectators"]),
        "sponsors.csv": (sponsors, ["sponsor_id", "sponsor_name", "industry", "country"]),
        "sponsorships.csv": (sponsorships, ["sponsorship_id", "tournament_id", "sponsor_id", "received_on", "amount_received"]),
        "event_expenses.csv": (expenses, ["expense_id", "tournament_id", "spent_on", "category", "amount"]),
        "prize_payouts.csv": (payouts, ["payout_id", "tournament_id", "registration_id", "placement", "paid_on", "amount"]),
    }
    for filename, table in tables.items():
        rows, columns = table
        save_csv(filename, rows, columns)
        print(f"{filename}: {len(rows)} rows")

    # Final check with regular dictionaries (no extra Python libraries).
    totals = {}
    for payment in payments:
        reg = payment["registration_id"]
        totals[reg] = round(totals.get(reg, 0) + float(payment["amount"]), 2)
    wrong = []
    for registration in registrations:
        reg = registration["registration_id"]
        if totals.get(reg, 0) != float(registration["fee_due"]):
            wrong.append(reg)
    assert wrong == [11, 107], f"Unexpected payment errors: {wrong}"
    assert len(tournaments) == 24
    assert len(matches) == 480
    print("Intentionally wrong payment totals:", wrong)


if __name__ == "__main__":
    main()
