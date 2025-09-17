import logging
import random
import re
from collections import defaultdict
from typing import Final, List, final

from .roster import Player, Role, Team

log = logging.getLogger('file')


@final
class TeamSplitter:
    """Class responsible for balancing players into teams."""

    MIN_PLAYER_NUMBER_FOR_4_TEAMS: Final = 24
    TEAM_COLORS: Final[list[str]] = ['Red', 'Blue', 'White', 'Green']
    __roster: List[Player]

    def __init__(self, roster: List[Player]) -> None:
        self.__roster = roster

    def __read_player_names(self, file_path: str) -> List[str]:
        """Read unique player names from a file, stripping leading numbers and dots."""
        pattern = re.compile(r'^\d+\.?\s*')
        names: List[str] = []
        seen = set()
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                name = pattern.sub('', line).strip()
                if name and name not in seen:
                    seen.add(name)
                    names.append(name)
        return names

    def __validate_players(self, names: List[str]) -> List[Player]:
        """Ensure all names exist in the roster and return Player instances."""
        validated: List[Player] = []
        for name in names:
            match = next((p for p in self.__roster if p.name == name), None)
            if not match:
                raise ValueError(f"Player '{name}' not found in roster")
            validated.append(match)

        players_sorted = sorted(validated, key=lambda p: p.skill, reverse=True)
        return players_sorted

    def __split_into_teams(self, players: List[Player], num_teams: int) -> List[Team]:
        grouped: dict[Role, List[Player]] = defaultdict(list)
        for p in players:
            grouped[p.role].append(p)

        teams: List[Team] = [Team(TeamSplitter.TEAM_COLORS[colorIdx])
                             for colorIdx in range(num_teams)]

        num_goalie_rounds = 0
        goalie_group = grouped[Role.GOALIE]
        goalie_count = len(goalie_group)
        if goalie_count > 0:
            num_goalie_rounds = (goalie_count + num_teams - 1) // num_teams

        goalie_pick_order: List[List[int]] = TeamSplitter.generate_pick_order(
            num_teams, num_goalie_rounds)
        for pick_order in goalie_pick_order:
            for team_idx in pick_order:
                if not goalie_group:
                    break
                teams[team_idx].add_player(goalie_group.pop(0))

        non_goalies = [p for p in players if p.role != Role.GOALIE]
        field_player_count = len(non_goalies)
        num_player_rounds = (field_player_count + num_teams - 1) // num_teams

        player_pick_order: List[List[int]] = TeamSplitter.generate_pick_order(
            num_teams, num_player_rounds)
        for pick_order in player_pick_order:
            for team_idx in pick_order:
                if not non_goalies:
                    break
                teams[team_idx].add_player(non_goalies.pop(0))

        return teams

    def __print_teams(self, teams: List[Team]) -> None:
        """Print teams with index, name, role, and skill."""
        for team in teams:
            print(str(team))
            print('')

    def __save_finalized(self, final_teams: List[str], output_file: str) -> None:
        """Save finalized player lists to a text file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for team in final_teams:
                for s in team:
                    f.write(f'{s}\n')
                f.write("\n")

    @staticmethod
    def generate_pick_order(num_teams: int, num_rounds: int) -> List[List[int]]:
        """
        Generate a combined random + snake draft order:
        - For odd-numbered rounds (0-based), use a random shuffle of teams.
        - For even-numbered rounds, use the reverse of the previous (snake) order.

        Returns a list of pick orders, one list per round, where each list contains team indices (0..num_teams-1).
        """
        orders: List[List[int]] = []
        teams = list(range(num_teams))
        use_snake = False

        for _ in range(num_rounds):
            if use_snake:
                # Reverse the last order for snake draft
                last = orders[-1]
                current = list(reversed(last))
            else:
                # Random order for this round
                current = teams.copy()
                random.shuffle(current)
            orders.append(current)
            use_snake = not use_snake

        return orders

    def split_and_save(self, file_path: str, output_file: str) -> None:
        """
        Public method: read input names, validate, split teams, and save output.
        """
        names = self.__read_player_names(file_path)
        players = self.__validate_players(names)
        num_teams = 4 if len(
            players) >= TeamSplitter.MIN_PLAYER_NUMBER_FOR_4_TEAMS else 2
        teams = self.__split_into_teams(players, num_teams)
        self.__print_teams(teams)
        final_teams: List[str] = []
        for team in teams:
            final_teams.append(team.get_finalized())

        self.__save_finalized(final_teams, output_file)
        print(f'Done. Teams are saved as {output_file}')
