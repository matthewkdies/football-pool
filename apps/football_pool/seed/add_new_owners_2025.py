from football_pool import create_app
from football_pool.models import Owner, Team, db

KATHERINE = Owner(
    first_name="Katherine",
    last_name="Hatton",
    winnings=10,
    team_id=Team.from_abbr("GB").one().id,
    season_start_year=2025,
)
db.session.add(KATHERINE)

RICHARD = Owner(
    first_name="Richard",
    last_name="Hatton",
    winnings=0,
    team_id=Team.from_abbr("LAR").id,
    season_start_year=2025,
)
db.session.add(RICHARD)
db.session.commit()


