from ..models import WinningGame, WinningType, db
from .query import get_live_scores


def write_to_db() -> list[WinningGame]:
    """Computes the winners for the week and writes them to the database, returning them.

    Returns:
        list[WinningGame]: The list of WinningGame objects.
    """
    current_week = get_live_scores()
    # if it's Super Bowl week, the winner gets $25
    if current_week.is_super_bowl:
        winners = current_week.get_super_bowl_winner()
        winnings = 25
        winning_type = WinningType.SUPER_BOWL
    # if it's a postseason week, all winners get $10
    elif current_week.is_postseason:
        winners = current_week.get_postseason_winners()
        winnings = 10
        winning_type = WinningType.PLAYOFF
    # otherwise, the teams scoring most/least (appropriately) get $10
    else:
        winners = current_week.get_weekly_winning_teams()
        winnings = 10
        winning_type = current_week.winning_type
    # regardless, a 50-point scorer wins $50!
    fifty_point_teams = current_week.get_fifty_point_winners()

    # now lets start making the WinningGame objects
    winning_games: list[WinningGame] = []
    for team in winners:
        winning_games.append(
            WinningGame(
                week=current_week.week,
                winnings=winnings,
                winning_type=winning_type,
                team=team,
            )
        )
    for team in fifty_point_teams:
        winning_games.append(
            WinningGame(
                week=current_week.week,
                winnings=50,
                winning_type=WinningType.FIFTY,
                team=team,
            )
        )

    # add all of 'em and push em up!
    db.session.add_all(winning_games)
    db.session.commit()
    return winning_games


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    from .. import create_app

    app = create_app()

    with app.app_context():
        winning_games = write_to_db()
        for winning_game in winning_games:
            WinningGame.query.where(WinningGame.id == winning_game.id).delete()
        db.session.commit()
