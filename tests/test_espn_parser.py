"""Tests for ESPN JSON parsing and scoreboard rules."""

import json
from pathlib import Path

import pytest

from apps.football_pool.models.enums import GameStatus, SeasonType, WinningType
from apps.football_pool.schemas.scoreboard import ScoreboardGame
from apps.football_pool.services.scoreboard import (
    compute_pool_winners,
    determine_winning_type,
    get_team_summary,
    parse_scoreboard_data,
)


@pytest.fixture
def example_json() -> dict:
    json_path = Path(__file__).parent / "example.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_get_team_summary():
    kc = get_team_summary("KC")
    assert kc.abbreviation == "KC"
    assert kc.name == "Chiefs"
    assert "Kansas City" in kc.full_name

    pit = get_team_summary("PIT")
    assert pit.abbreviation == "PIT"
    assert pit.city == "Pittsburgh"

    unknown = get_team_summary("XYZ")
    assert unknown.abbreviation == "XYZ"


def test_determine_winning_type():
    # Odd regular week -> MOST
    assert determine_winning_type(SeasonType.REGULAR_SEASON, 1) == WinningType.MOST
    assert determine_winning_type(SeasonType.REGULAR_SEASON, 3) == WinningType.MOST
    # Even regular week -> LEAST
    assert determine_winning_type(SeasonType.REGULAR_SEASON, 2) == WinningType.LEAST
    assert determine_winning_type(SeasonType.REGULAR_SEASON, 4) == WinningType.LEAST
    # Postseason
    assert determine_winning_type(SeasonType.POSTSEASON, 1) == WinningType.PLAYOFF
    assert determine_winning_type(SeasonType.POSTSEASON, 5) == WinningType.SUPER_BOWL


def test_parse_scoreboard_with_example_fixture(example_json):
    week_data = parse_scoreboard_data(example_json, pot_amount=20)
    assert week_data.pot_amount == 20
    assert week_data.week > 0
    assert len(week_data.games) > 0

    first_game = week_data.games[0]
    assert isinstance(first_game, ScoreboardGame)
    assert first_game.home_team.abbreviation != ""
    assert first_game.away_team.abbreviation != ""
    assert first_game.espn_url != ""


def test_compute_pool_winners_50_points():
    from datetime import datetime

    g1 = ScoreboardGame(
        id="1",
        home_team=get_team_summary("BAL"),
        home_team_score=50,
        away_team=get_team_summary("CLE"),
        away_team_score=17,
        gametime=datetime.now(),
        status=GameStatus.FINAL,
    )
    g2 = ScoreboardGame(
        id="2",
        home_team=get_team_summary("KC"),
        home_team_score=24,
        away_team=get_team_summary("BUF"),
        away_team_score=21,
        gametime=datetime.now(),
        status=GameStatus.FINAL,
    )
    # Week 1 (Odd: MOST)
    winners = compute_pool_winners([g1, g2], SeasonType.REGULAR_SEASON, 1)
    # BAL scored 50 AND most points
    assert "BAL" in winners


def test_compute_pool_winners_least_points():
    from datetime import datetime

    g1 = ScoreboardGame(
        id="1",
        home_team=get_team_summary("CHI"),
        home_team_score=6,
        away_team=get_team_summary("GB"),
        away_team_score=20,
        gametime=datetime.now(),
        status=GameStatus.FINAL,
    )
    g2 = ScoreboardGame(
        id="2",
        home_team=get_team_summary("PIT"),
        home_team_score=14,
        away_team=get_team_summary("CIN"),
        away_team_score=10,
        gametime=datetime.now(),
        status=GameStatus.FINAL,
    )
    # Week 2 (Even: LEAST)
    winners = compute_pool_winners([g1, g2], SeasonType.REGULAR_SEASON, 2)
    assert winners == ["CHI"]
