from collections import defaultdict

from flask import Flask

from ..models import Pot, Team, WinningGame, WinningType, db
from .query import get_live_scores


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
            else:
                # no winners here, increase the pot by 10
                pot.amount += 10
        current_app.logger.info("Winners: %s", [team.abbreviation for team in winners])
        current_app.logger.info("Winnings: %s", winnings)
        current_app.logger.info("Winning Type: %s", winning_type.name_str)
        # regardless, a 50-point scorer wins $50!
        fifty_point_teams = current_week.get_fifty_point_winners()
        current_app.logger.info(
            "50 point winners: %s", [team.abbreviation for team in fifty_point_teams]
        )

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


def clean_db(current_app: Flask) -> None:
    """Cleans the database, since the above function writes like 100 times.

    This will clean the `WinningGame`s in the database after the above function call.
    When the above function writes in the scheduled job, it creates more than it should.
    This is a band-aid fix, but easier to me than actually resolving the problem.
    It should be fine that this runs multiple times, since it will preserve a single
    `WinningGame` if it's correct.

    Methodology:
    - Get the `WinningGame`s for the current week.
    - Map the teams to these objects, for each team:
        - Map the winning type to the `WinningGame`s
        - If this list is more than 1 long, it's a duplicate -> delete it!

    Args:
        current_app (Flask): The list of WinningGame objects.
    """
    with current_app.app_context():
        current_app.logger.info("Beginning the cleaning of the week's results to the database.")
        current_week = get_live_scores()
        winning_games: list[WinningGame] = WinningGame.query.where(
            WinningGame.week == current_week.week
        ).all()

        # gets a map of the teams to their WinningGame objects
        team_to_wgs_map: dict[Team, list[WinningGame]] = defaultdict(list)
        for winning_game in winning_games:
            team_to_wgs_map[winning_game.team].append(winning_game)

        # now we need to map the winning types to the WinningGames and delete duplicates
        for team, winning_game_list in team_to_wgs_map.items():
            current_app.logger.info("Cleaning the results for '%s'.", team.abbreviation)
            type_to_wgs_map: dict[WinningType, list[WinningGame]] = defaultdict(list)
            for winning_game in winning_game_list:
                type_to_wgs_map[winning_game.winning_type].append(winning_game)
            for winning_type, winning_game_list in type_to_wgs_map.items():
                current_app.logger.debug("Cleaning the results for type '%s'.", winning_type.value)
                # if there is only one WinningGame, great! We don't have to do anything
                if len(winning_game_list) == 1:
                    continue

                # finally, we can delete all of the relevant games
                for winning_game in winning_game_list[1:]:
                    db.session.delete(winning_game)

        db.session.commit()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    from .. import create_app

    app = create_app()

    with app.app_context():
        write_to_db()
