from pathlib import Path
from typing import List

import pytest

from team_splitter.roster import Player, Role, load_players
from team_splitter.team_splitter import TeamSplitter


@pytest.fixture
def roster_epl() -> List[Player]:
    """Load the EPL roster for testing."""
    roster_path = Path(__file__).parent / 'roster.epl.json'
    return load_players(str(roster_path))


@pytest.fixture
def player_list(tmp_path: Path) -> str:
    """Create a players.txt file with predefined players."""
    # Select players: 2 goalies, 5 defenders, 6 midfielders, 3 strikers
    player_names = [
        'Ederson',                # G
        'David Raya',             # G
        'William Saliba',         # D
        'Gabriel Magalhaes',      # D
        'Ruben Dias',             # D
        'Kyle Walker',            # D
        'Ben White',              # D
        'Kevin De Bruyne',        # M
        'Bukayo Saka',            # M
        'Martin Odegaard',        # M
        'Phil Foden',             # M
        'Rodri',                  # M
        'Bernardo Silva',         # M
        'Erling Haaland',         # S
        'Gabriel Jesus',          # S
        'Julian Alvarez',         # S
    ]

    players_file = tmp_path / 'players.txt'
    players_file.write_text('\n'.join(player_names), encoding='utf-8')
    return str(players_file)


def test_deterministic_split_same_seed(roster_epl: List[Player], player_list: str) -> None:
    """Test that same seed produces identical team assignments."""
    splitter1 = TeamSplitter(roster_epl, seed=42)
    splitter2 = TeamSplitter(roster_epl, seed=42)

    teams1 = splitter1.split_teams(player_list)
    teams2 = splitter2.split_teams(player_list)

    # Verify same number of teams
    assert len(teams1) == len(teams2) == 2

    # Verify identical team compositions
    for t1, t2 in zip(teams1, teams2):
        assert t1.name == t2.name
        assert len(t1.players) == len(t2.players)
        assert [p.name for p in t1.players] == [p.name for p in t2.players]


def test_deterministic_split_different_seed(roster_epl: List[Player], player_list: str) -> None:
    """Test that different seeds produce different team assignments."""
    splitter1 = TeamSplitter(roster_epl, seed=42)
    splitter2 = TeamSplitter(roster_epl, seed=99)

    teams1 = splitter1.split_teams(player_list)
    teams2 = splitter2.split_teams(player_list)

    # Teams should have different compositions (with high probability)
    team1_composition = [p.name for p in teams1[0].players]
    team2_composition = [p.name for p in teams2[0].players]

    assert team1_composition != team2_composition


def test_team_balance_basic(roster_epl: List[Player], player_list: str) -> None:
    """Test that teams are reasonably balanced in terms of size."""
    splitter = TeamSplitter(roster_epl, seed=42)
    teams = splitter.split_teams(player_list)

    # Both teams should have 8 players
    assert teams[0].size() == 8
    assert teams[1].size() == 8

    # Each team should have at least 1 goalie
    assert teams[0].role_count(Role.GOALIE) >= 1
    assert teams[1].role_count(Role.GOALIE) >= 1


def test_all_players_assigned(roster_epl: List[Player], player_list: str) -> None:
    """Test that all players are assigned to teams."""
    splitter = TeamSplitter(roster_epl, seed=42)
    teams = splitter.split_teams(player_list)

    # Collect all assigned players
    assigned_players = []
    for team in teams:
        assigned_players.extend(team.players)

    # Should have 16 players total
    assert len(assigned_players) == 16

    # All original players should be assigned (no duplicates)
    assigned_names = {p.name for p in assigned_players}
    assert len(assigned_names) == 16


def test_no_seed_still_works(roster_epl: List[Player], player_list: str) -> None:
    """Test that TeamSplitter works without a seed (non-deterministic)."""
    splitter = TeamSplitter(roster_epl)  # No seed
    teams = splitter.split_teams(player_list)

    # Basic sanity checks
    assert len(teams) == 2
    assert teams[0].size() + teams[1].size() == 16
    assert teams[0].role_count(Role.GOALIE) + teams[1].role_count(Role.GOALIE) == 2


def test_team_size_difference_rule(roster_epl: List[Player], player_list: str) -> None:
    """Test that team sizes differ by at most 1 player."""
    splitter = TeamSplitter(roster_epl, seed=42)
    teams = splitter.split_teams(player_list)

    team_sizes = [team.size() for team in teams]
    min_size = min(team_sizes)
    max_size = max(team_sizes)

    # Team size difference must not exceed 1
    assert max_size - min_size <= 1
