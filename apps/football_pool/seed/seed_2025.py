from flask import current_app
from football_pool import create_app
from football_pool.models import Owner, Team, db

ABBREVIATIONS = [
    "ARI",
    "ATL",
    "BAL",
    "BUF",
    "CAR",
    "CHI",
    "CIN",
    "CLE",
    "DAL",
    "DEN",
    "DET",
    "GB",
    "HOU",
    "IND",
    "JAX",
    "KC",
    "LAC",
    "LAR",
    "LV",
    "MIA",
    "MIN",
    "NE",
    "NO",
    "NYG",
    "NYJ",
    "PHI",
    "PIT",
    "SEA",
    "SF",
    "TB",
    "TEN",
    "WSH",
]

with create_app().app_context():
    ABBREVIATIONS_TO_TEAMS: dict[str, Team] = {abbr: Team.from_abbr(abbr) for abbr in ABBREVIATIONS}

    OWNERS: list[Owner] = []

    AARON = Owner(
        first_name="Aaron",
        last_name="Smith",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["ATL"],
        season_start_year=2025,
    )
    OWNERS.append(AARON)

    DAVE = Owner(
        first_name="Dave",
        last_name="Hasman",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["BAL"],
        season_start_year=2025,
    )
    OWNERS.append(DAVE)

    NATHAN = Owner(
        first_name="Nathan",
        last_name="Smith",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["BUF"],
        season_start_year=2025,
    )
    OWNERS.append(NATHAN)

    JEEP = Owner(
        first_name="Jeep",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["CAR"],
        season_start_year=2025,
    )
    OWNERS.append(JEEP)

    ASHLEY_D = Owner(
        first_name="Ashley",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["CIN"],
        season_start_year=2025,
    )
    OWNERS.append(ASHLEY_D)

    CHARLOTTE = Owner(
        first_name="Charlotte",
        last_name="Lippincott",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["CLE"],
        season_start_year=2025,
    )
    OWNERS.append(CHARLOTTE)

    AIDAN = Owner(
        first_name="Aidan",
        last_name="Grass",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["DAL"],
        season_start_year=2025,
    )
    OWNERS.append(AIDAN)

    KATHY = Owner(
        first_name="Kathy",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["DEN"],
        season_start_year=2025,
    )
    OWNERS.append(KATHY)

    MOIRA = Owner(
        first_name="Moira",
        last_name="Healy",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["DET"],
        season_start_year=2025,
    )
    OWNERS.append(MOIRA)

    MADISON = Owner(
        first_name="Madison",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["HOU"],
        season_start_year=2025,
    )
    OWNERS.append(MADISON)

    JANET = Owner(
        first_name="Janet",
        last_name="Lippincott",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["IND"],
        season_start_year=2025,
    )
    OWNERS.append(JANET)

    NATALIA = Owner(
        first_name="Natalia",
        last_name="Carlson",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["JAX"],
        season_start_year=2025,
    )
    OWNERS.append(NATALIA)

    ASHLEY_L = Owner(
        first_name="Ashley",
        last_name="Lippincott",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["KC"],
        season_start_year=2025,
    )
    OWNERS.append(ASHLEY_L)

    DENNIS = Owner(
        first_name="Dennis",
        last_name="Smith",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["LAC"],
        season_start_year=2025,
    )
    OWNERS.append(DENNIS)

    PAM = Owner(
        first_name="Pam",
        last_name="Smith",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["MIA"],
        season_start_year=2025,
    )
    OWNERS.append(PAM)

    JUDI = Owner(
        first_name="Judi",
        last_name="Carlson",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["MIN"],
        season_start_year=2025,
    )
    OWNERS.append(JUDI)

    CHIP = Owner(
        first_name="Chip",
        last_name="Lippincott",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["NE"],
        season_start_year=2025,
    )
    OWNERS.append(CHIP)

    ANNA = Owner(
        first_name="Anna",
        last_name="Lippincott-Hasman",  # TODO:
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["NO"],
        season_start_year=2025,
    )
    OWNERS.append(ANNA)

    DOUG = Owner(
        first_name="Doug",
        last_name="Carlson",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["NYJ"],
        season_start_year=2025,
    )
    OWNERS.append(DOUG)

    MATT = Owner(
        first_name="Matt",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["LV"],
        season_start_year=2025,
    )
    OWNERS.append(MATT)

    THOMAS = Owner(
        first_name="Thomas",
        last_name="Iodice",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["PHI"],
        season_start_year=2025,
    )
    OWNERS.append(THOMAS)

    MIKE = Owner(
        first_name="Mike",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["PIT"],
        season_start_year=2025,
    )
    OWNERS.append(MIKE)

    JEREMY = Owner(
        first_name="Jeremy",
        last_name="Carlson",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["SF"],
        season_start_year=2025,
    )
    OWNERS.append(JEREMY)

    JANICE = Owner(
        first_name="Janice",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["SEA"],
        season_start_year=2025,
    )
    OWNERS.append(JANICE)

    JULIA = Owner(
        first_name="Julia",
        last_name="Klein",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["TB"],
        season_start_year=2025,
    )
    OWNERS.append(JULIA)

    LAURYN = Owner(
        first_name="Lauryn",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["TEN"],
        season_start_year=2025,
    )
    OWNERS.append(LAURYN)

    COLIN = Owner(
        first_name="Colin",
        last_name="Lippincott",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["NYG"],
        season_start_year=2025,
    )
    OWNERS.append(COLIN)

    MISSY = Owner(
        first_name="Missy",
        last_name="Dies",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["ARI"],
        season_start_year=2025,
    )
    OWNERS.append(MISSY)

    ALEX = Owner(
        first_name="Alex",
        last_name="Lippincott",
        winnings=0,
        team=ABBREVIATIONS_TO_TEAMS["CHI"],
        season_start_year=2025,
    )
    OWNERS.append(ALEX)


def seed() -> None:
    # confirm number of owners
    if len(OWNERS) != 29:
        raise ValueError("Must be 29 owners.")

    # add everything to the database
    with current_app.app_context():
        db.session.add_all(OWNERS)
        db.session.commit()
