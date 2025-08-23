from football_pool import create_app
from football_pool.models import Owner, Team, db
from sqlalchemy import and_

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

    AARON = Owner.query.where(Owner.first_name == "Aaron").filter(Owner.season_start_year == 2024).one()
    AARON.team_id = Team.from_abbr("CAR").id

    AIDAN = Owner.query.where(Owner.first_name == "Aidan").filter(Owner.season_start_year == 2024).one()
    AIDAN.team_id = Team.from_abbr("GB").id

    ALEX = Owner.query.where(Owner.first_name == "Alex").filter(Owner.season_start_year == 2024).one()
    ALEX.team_id = Team.from_abbr("PHI").id

    ANNA = Owner.query.where(Owner.first_name == "Anna").filter(Owner.season_start_year == 2024).one()
    ANNA.last_name = "Hasman"
    ANNA.team_id = Team.from_abbr("NYJ").id

    ASHLEY_D = (
        Owner.query.where(and_(Owner.first_name == "Ashley", Owner.last_name == "Dies"))
        .filter(Owner.season_start_year == 2024)
        .one()
    )
    ASHLEY_D.team_id = Team.from_abbr("NO").id

    ASHLEY_L = (
        Owner.query.where(and_(Owner.first_name == "Ashley", Owner.last_name == "Lippincott"))
        .filter(Owner.season_start_year == 2024)
        .one()
    )
    ASHLEY_L.team_id = Team.from_abbr("TB").id

    CHARLOTTE = Owner.query.where(Owner.first_name == "Charlotte").filter(Owner.season_start_year == 2024).one()
    CHARLOTTE.team_id = Team.from_abbr("DET").id

    CHIP = Owner.query.where(Owner.first_name == "Chip").filter(Owner.season_start_year == 2024).one()
    CHIP.team_id = Team.from_abbr("TEN").id

    COLIN = Owner.query.where(Owner.first_name == "Colin").filter(Owner.season_start_year == 2024).one()
    COLIN.team_id = Team.from_abbr("LAC").id

    DAVE = Owner.query.where(Owner.first_name == "Dave").filter(Owner.season_start_year == 2024).one()
    DAVE.team_id = Team.from_abbr("MIA").id

    DENNIS = Owner.query.where(Owner.first_name == "Dennis").filter(Owner.season_start_year == 2024).one()
    DENNIS.team_id = Team.from_abbr("GB").id

    DOUG = Owner.query.where(Owner.first_name == "Doug").filter(Owner.season_start_year == 2024).one()
    DOUG.team_id = Team.from_abbr("NE").id

    JANET = Owner.query.where(Owner.first_name == "Janet").filter(Owner.season_start_year == 2024).one()
    JANET.team_id = Team.from_abbr("CLE").id

    JANICE = Owner.query.where(Owner.first_name == "Janice").filter(Owner.season_start_year == 2024).one()
    JANICE.team_id = Team.from_abbr("PIT").id

    JEEP = Owner.query.where(Owner.first_name == "Jeep").filter(Owner.season_start_year == 2024).one()
    JEEP.team_id = Team.from_abbr("BUF").id

    JEREMY = Owner.query.where(Owner.first_name == "Jeremy").filter(Owner.season_start_year == 2024).one()
    JEREMY.team_id = Team.from_abbr("SEA").id

    JUDI = Owner.query.where(Owner.first_name == "Judi").filter(Owner.season_start_year == 2024).one()
    JUDI.team_id = Team.from_abbr("DEN").id

    JULIA = Owner.query.where(Owner.first_name == "Julia").filter(Owner.season_start_year == 2024).one()
    JULIA.team_id = Team.from_abbr("LV").id

    KATHY = Owner.query.where(Owner.first_name == "Kathy").filter(Owner.season_start_year == 2024).one()
    KATHY.team_id = Team.from_abbr("DAL").id

    LAURYN = Owner.query.where(Owner.first_name == "Lauryn").filter(Owner.season_start_year == 2024).one()
    LAURYN.team_id = Team.from_abbr("SF").id

    MADISON = Owner.query.where(Owner.first_name == "Madison").filter(Owner.season_start_year == 2024).one()
    MADISON.team_id = Team.from_abbr("ATL").id

    MATT = Owner.query.where(Owner.first_name == "Matt").filter(Owner.season_start_year == 2024).one()
    MATT.team_id = Team.from_abbr("KC").id

    MIKE = Owner.query.where(Owner.first_name == "Mike").filter(Owner.season_start_year == 2024).one()
    MIKE.team_id = Team.from_abbr("BAL").id

    MISSY = Owner.query.where(Owner.first_name == "Missy").filter(Owner.season_start_year == 2024).one()
    MISSY.team_id = Team.from_abbr("IND").id

    MOIRA = Owner.query.where(Owner.first_name == "Moira").filter(Owner.season_start_year == 2024).one()
    MOIRA.team_id = Team.from_abbr("WSH").id

    NATALIA = Owner.query.where(Owner.first_name == "Natalia").filter(Owner.season_start_year == 2024).one()
    NATALIA.team_id = Team.from_abbr("MIN").id

    NATHAN = Owner.query.where(Owner.first_name == "Nathan").filter(Owner.season_start_year == 2024).one()
    NATHAN.team_id = Team.from_abbr("JAX").id

    PAM = Owner.query.where(Owner.first_name == "Pam").filter(Owner.season_start_year == 2024).one()
    PAM.team_id = Team.from_abbr("HOU").id

    THOMAS = Owner.query.where(Owner.first_name == "Thomas").filter(Owner.season_start_year == 2024).one()
    THOMAS.team_id = Team.from_abbr("CIN").id

    # ---

    db.session.commit()
