from pathlib import Path

from flask import url_for

from . import create_app, db
from .models import Conference, Division, Owner, Team

STATIC_DIR = Path(__file__).parent / "static"


def get_logo_url(team_name: str) -> str:
    """Gets the URL to the logo image after confirming it exists.

    Args:
        team_name (str): The name of the team `f"{<city>.lower()}-{<name>.lower()}"`.

    Raises:
        FileNotFoundError: If the file doesn't exist at this location.

    Returns:
        str: The correct link to the image.
    """
    filename = STATIC_DIR / f"logos/{team_name}-logo-transparent.png"
    if not filename.exists():
        raise FileNotFoundError(filename)
    return url_for("static", filename=filename.relative_to(STATIC_DIR))


app = create_app()
with app.app_context():
    # -----------------------------------
    # add the teams and all of their info
    # -----------------------------------

    PATRIOTS = Team(
        city="New England",
        name="Patriots",
        abbreviation="NE",
        logo_url=get_logo_url("new-england-patriots"),
        conference=Conference.AFC,
        division=Division.EAST,
    )

    BILLS = Team(
        city="Buffalo",
        name="Bills",
        abbreviation="BUF",
        logo_url=get_logo_url("buffalo-bills"),
        conference=Conference.AFC,
        division=Division.EAST,
    )

    DOLPHINS = Team(
        city="Miami",
        name="Dolphins",
        abbreviation="MIA",
        logo_url=get_logo_url("miami-dolphins"),
        conference=Conference.AFC,
        division=Division.EAST,
    )

    JETS = Team(
        city="New York",
        name="Jets",
        abbreviation="NYJ",
        logo_url=get_logo_url("new-york-jets"),
        conference=Conference.AFC,
        division=Division.EAST,
    )

    STEELERS = Team(
        city="Pittsburgh",
        name="Steelers",
        abbreviation="PIT",
        logo_url=get_logo_url("pittsburgh-steelers"),
        conference=Conference.AFC,
        division=Division.NORTH,
    )

    RAVENS = Team(
        city="Baltimore",
        name="Ravens",
        abbreviation="BAL",
        logo_url=get_logo_url("baltimore-ravens"),
        conference=Conference.AFC,
        division=Division.NORTH,
    )

    BENGALS = Team(
        city="Cincinnati",
        name="Bengals",
        abbreviation="CIN",
        logo_url=get_logo_url("cincinnati-bengals"),
        conference=Conference.AFC,
        division=Division.NORTH,
    )

    BROWNS = Team(
        city="Cleveland",
        name="Browns",
        abbreviation="CLE",
        logo_url=get_logo_url("cleveland-browns"),
        conference=Conference.AFC,
        division=Division.NORTH,
    )

    TEXANS = Team(
        city="Houston",
        name="Texans",
        abbreviation="HOU",
        logo_url=get_logo_url("houston-texans"),
        conference=Conference.AFC,
        division=Division.SOUTH,
    )

    COLTS = Team(
        city="Indianapolis",
        name="Colts",
        abbreviation="IND",
        logo_url=get_logo_url("indianapolis-colts"),
        conference=Conference.AFC,
        division=Division.SOUTH,
    )

    JAGUARS = Team(
        city="Jacksonville",
        name="Jaguars",
        abbreviation="JAX",
        logo_url=get_logo_url("jacksonville-jaguars"),
        conference=Conference.AFC,
        division=Division.SOUTH,
    )

    TITANS = Team(
        city="Tennessee",
        name="Titans",
        abbreviation="TEN",
        logo_url=get_logo_url("tennessee-titans"),
        conference=Conference.AFC,
        division=Division.SOUTH,
    )

    BRONCOS = Team(
        city="Denver",
        name="Broncos",
        abbreviation="DEN",
        logo_url=get_logo_url("denver-broncos"),
        conference=Conference.AFC,
        division=Division.WEST,
    )

    CHIEFS = Team(
        city="Kansas City",
        name="Chiefs",
        abbreviation="KC",
        logo_url=get_logo_url("kansas-city-chiefs"),
        conference=Conference.AFC,
        division=Division.WEST,
    )

    RAIDERS = Team(
        city="Las Vegas",
        name="Raiders",
        abbreviation="LV",
        logo_url=get_logo_url("las-vegas-raiders"),
        conference=Conference.AFC,
        division=Division.WEST,
    )

    CHARGERS = Team(
        city="Los Angeles",
        name="Chargers",
        abbreviation="LAC",
        logo_url=get_logo_url("los-angeles-chargers"),
        conference=Conference.AFC,
        division=Division.WEST,
    )

    COWBOYS = Team(
        city="Dallas",
        name="Cowboys",
        abbreviation="DAL",
        logo_url=get_logo_url("dallas-cowboys"),
        conference=Conference.NFC,
        division=Division.EAST,
    )

    GIANTS = Team(
        city="New York",
        name="Giants",
        abbreviation="NYG",
        logo_url=get_logo_url("new-york-giants"),
        conference=Conference.NFC,
        division=Division.EAST,
    )

    EAGLES = Team(
        city="Philadelphia",
        name="Eagles",
        abbreviation="PHI",
        logo_url=get_logo_url("philadelphia-eagles"),
        conference=Conference.NFC,
        division=Division.EAST,
    )

    COMMANDERS = Team(
        city="Washington",
        name="Commanders",
        abbreviation="WAS",
        logo_url=get_logo_url("washington-commanders"),
        conference=Conference.NFC,
        division=Division.EAST,
    )

    BEARS = Team(
        city="Chicago",
        name="Bears",
        abbreviation="CHI",
        logo_url=get_logo_url("chicago-bears"),
        conference=Conference.NFC,
        division=Division.NORTH,
    )

    LIONS = Team(
        city="Detroit",
        name="Lions",
        abbreviation="DET",
        logo_url=get_logo_url("detroit-lions"),
        conference=Conference.NFC,
        division=Division.NORTH,
    )

    PACKERS = Team(
        city="Green Bay",
        name="Packers",
        abbreviation="GB",
        logo_url=get_logo_url("green-bay-packers"),
        conference=Conference.NFC,
        division=Division.NORTH,
    )

    VIKINGS = Team(
        city="Minnesota",
        name="Vikings",
        abbreviation="MIN",
        logo_url=get_logo_url("minnesota-vikings"),
        conference=Conference.NFC,
        division=Division.NORTH,
    )

    FALCONS = Team(
        city="Atlanta",
        name="Falcons",
        abbreviation="ATL",
        logo_url=get_logo_url("atlanta-falcons"),
        conference=Conference.NFC,
        division=Division.SOUTH,
    )

    PANTHERS = Team(
        city="Carolina",
        name="Panthers",
        abbreviation="CAR",
        logo_url=get_logo_url("carolina-panthers"),
        conference=Conference.NFC,
        division=Division.SOUTH,
    )

    SAINTS = Team(
        city="New Orleans",
        name="Saints",
        abbreviation="NO",
        logo_url=get_logo_url("new-orleans-saints"),
        conference=Conference.NFC,
        division=Division.SOUTH,
    )

    BUCCANEERS = Team(
        city="Tampa Bay",
        name="Buccaneers",
        abbreviation="TB",
        logo_url=get_logo_url("tampa-bay-buccaneers"),
        conference=Conference.NFC,
        division=Division.SOUTH,
    )

    CARDINALS = Team(
        city="Arizona",
        name="Cardinals",
        abbreviation="ARI",
        logo_url=get_logo_url("arizona-cardinals"),
        conference=Conference.NFC,
        division=Division.WEST,
    )

    RAMS = Team(
        city="Los Angeles",
        name="Rams",
        abbreviation="LAR",
        logo_url=get_logo_url("los-angeles-rams"),
        conference=Conference.NFC,
        division=Division.WEST,
    )

    FORTYNINERS = Team(
        city="San Francisco",
        name="49ers",
        abbreviation="SF",
        logo_url=get_logo_url("san-francisco-49ers"),
        conference=Conference.NFC,
        division=Division.WEST,
    )

    SEAHAWKS = Team(
        city="Seattle",
        name="Seahawks",
        abbreviation="SEA",
        logo_url=get_logo_url("seattle-seahawks"),
        conference=Conference.NFC,
        division=Division.WEST,
    )

    TEAMS: list[Team] = [
        PATRIOTS,
        BILLS,
        DOLPHINS,
        JETS,
        STEELERS,
        RAVENS,
        BENGALS,
        BROWNS,
        TEXANS,
        COLTS,
        JAGUARS,
        TITANS,
        CHIEFS,
        CHARGERS,
        RAIDERS,
        BRONCOS,
        COMMANDERS,
        COWBOYS,
        GIANTS,
        EAGLES,
        PACKERS,
        VIKINGS,
        LIONS,
        BEARS,
        BUCCANEERS,
        SAINTS,
        FALCONS,
        PANTHERS,
        SEAHAWKS,
        FORTYNINERS,
        RAMS,
        CARDINALS,
    ]

    # ---------------------------------------
    # add the owners, referring back to teams
    # ---------------------------------------

    MADISON = Owner(
        first_name="Madison",
        last_name="Dies",
        team=FALCONS,
    )

    MIKE = Owner(
        first_name="Mike",
        last_name="Dies",
        team=RAVENS,
    )

    JEEP = Owner(
        first_name="Jeep",
        last_name="Dies",
        team=BILLS,
    )

    AARON = Owner(
        first_name="Aaron",
        last_name="Smith",
        team=PANTHERS,
    )

    THOMAS = Owner(
        first_name="Thomas",
        last_name="Iodice",
        team=BENGALS,
    )

    JANET = Owner(
        first_name="Janet",
        last_name="Lippincott",
        team=BROWNS,
    )

    KATHY = Owner(
        first_name="Kathy",
        last_name="Dies",
        team=COWBOYS,
    )

    JUDI = Owner(
        first_name="Judi",
        last_name="Carlson",
        team=BRONCOS,
    )

    CHARLOTTE = Owner(
        first_name="Charlotte",
        last_name="Lippincott",
        team=LIONS,
    )

    AIDAN = Owner(
        first_name="Aidan",
        last_name="Grass",
        team=PACKERS,
    )

    PAM = Owner(
        first_name="Pam",
        last_name="Smith",
        team=TEXANS,
    )

    MISSY = Owner(
        first_name="Missy",
        last_name="Dies",
        team=COLTS,
    )

    NATHAN = Owner(
        first_name="Nathan",
        last_name="Smith",
        team=JAGUARS,
    )

    MATT = Owner(
        first_name="Matt",
        last_name="IodDiesice",
        team=CHIEFS,
    )

    COLIN = Owner(
        first_name="Colin",
        last_name="Lippincott",
        team=CHARGERS,
    )

    DENNIS = Owner(
        first_name="Dennis",
        last_name="Smith",
        team=RAMS,
    )

    DAVE = Owner(
        first_name="Dave",
        last_name="Hasman",
        team=DOLPHINS,
    )

    NATALIA = Owner(
        first_name="Natalia",
        last_name="Carlson",
        team=VIKINGS,
    )

    DOUG = Owner(
        first_name="Doug",
        last_name="Carlson",
        team=PATRIOTS,
    )

    ASHLEY_D = Owner(
        first_name="Ashley",
        last_name="Dies",
        team=SAINTS,
    )

    ANNA = Owner(
        first_name="Anna",
        last_name="Lippincott",
        team=JETS,
    )

    JULIA = Owner(
        first_name="Julia",
        last_name="Klein",
        team=RAIDERS,
    )

    ALEX = Owner(
        first_name="Alex",
        last_name="Lippincott",
        team=EAGLES,
    )

    JANICE = Owner(
        first_name="Janice",
        last_name="Dies",
        team=STEELERS,
    )

    LAURYN = Owner(
        first_name="Lauryn",
        last_name="Dies",
        team=FORTYNINERS,
    )

    JEREMY = Owner(
        first_name="Jeremy",
        last_name="Carlson",
        team=SEAHAWKS,
    )

    ASHLEY_L = Owner(
        first_name="Ashley",
        last_name="Lippincott",
        team=BUCCANEERS,
    )

    CHIP = Owner(
        first_name="Chip",
        last_name="Lippincott",
        team=TITANS,
    )

    MOIRA = Owner(
        first_name="Moira",
        last_name="Healy",
        team=COMMANDERS,
    )

    OWNERS: list[Owner] = [
        MADISON,
        MIKE,
        JEEP,
        AARON,
        THOMAS,
        JANET,
        KATHY,
        JUDI,
        CHARLOTTE,
        AIDAN,
        PAM,
        MISSY,
        NATHAN,
        MATT,
        COLIN,
        DENNIS,
        DAVE,
        NATALIA,
        DOUG,
        ASHLEY_D,
        ANNA,
        JULIA,
        ALEX,
        JANICE,
        LAURYN,
        JEREMY,
        ASHLEY_L,
        CHIP,
        MOIRA,
    ]


if __name__ == "__main__":
    # confirm number of teams
    if len(TEAMS) != 32:
        raise ValueError("Must be 32 teams.")

    # confirm number of owners
    if len(OWNERS) != 29:
        raise ValueError("Must be 29 owners.")

    # add everything to the database
    app = create_app()
    with app.app_context():
        db.session.add_all(TEAMS)
        db.session.add_all(OWNERS)
        db.session.commit()