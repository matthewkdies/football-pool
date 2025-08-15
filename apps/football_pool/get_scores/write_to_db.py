from flask import Flask

from ..models import Pot, Team, WinningGame, WinningType, db
from .query import get_live_scores

NUM_WEEKS_IN_REG_SEASON = 18


def week_has_real_winners(winners: list[Team]) -> bool:
    return any(winner.owner is not None for winner in winners)


def write_to_db(current_app: Flask) -> None:
    """Computes the winners for the week and writes them to the database, returning them.

    Returns:
        list[WinningGame]: The list of WinningGame objects.
    """
    with current_app.app_context():
        current_app.logger.info("Beginning the writing of the week's results to the database.")
        current_week = get_live_scores()
        if current_week.is_pro_bowl:  # nobody wins anything on pro bowl week
            return  # if it's the pro bowl, just exit early
        # if it's Super Bowl week, the winner gets $25
        if current_week.is_super_bowl:
            winners = current_week.get_super_bowl_winners()
            winnings = 25
            winning_type = WinningType.SUPER_BOWL
        # if it's a postseason week, all winners get $10
        elif current_week.is_postseason:
            winners = current_week.get_postseason_winners()
            winnings = 10
            winning_type = WinningType.PLAYOFF
        # otherwise, the teams scoring most/least (appropriately) get $10
        else:
            pot: Pot = Pot.query.one()
            winners = current_week.get_weekly_winning_teams()
            winnings = pot.amount
            winning_type = current_week.winning_type
            # increase the pot amount, if needed
            if week_has_real_winners(winners):
                # this week has winners, set the pot to 10
                pot.amount = 10
            elif not current_week.is_preseason:
                # no winners here, increase the pot by 10
                pot.amount += 10
        current_app.logger.info("Winners: %s", [team.abbreviation for team in winners])
        current_app.logger.info("Winnings: %s", winnings)
        current_app.logger.info("Winning Type: %s", winning_type.name_str)
        # regardless, a 50-point scorer wins $50!
        fifty_point_teams = current_week.get_fifty_point_winners()
        current_app.logger.info("50 point winners: %s", [team.abbreviation for team in fifty_point_teams])

        # now lets start making the WinningGame objects
        current_week_num = current_week.week
        if current_week.is_postseason:
            current_week_num += NUM_WEEKS_IN_REG_SEASON

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
            if team.owner is not None:
                team.owner.winnings += winnings
        for team in fifty_point_teams:
            winning_games.append(
                WinningGame(
                    week=current_week.week,
                    winnings=50,
                    winning_type=WinningType.FIFTY,
                    team=team,
                )
            )
            if team.owner is not None:
                team.owner.winnings += 50

        # add all of 'em and push em up!
        db.session.add_all(winning_games)
        db.session.commit()
        current_app.logger.info("Information written to the database. Exiting.")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    from .. import create_app

    app = create_app()

    with app.app_context():
        write_to_db(app)
