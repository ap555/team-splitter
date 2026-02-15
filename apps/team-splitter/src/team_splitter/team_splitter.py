from .role_balancer import RoleBalancer
import logging
import random
import re
from collections import defaultdict
from typing import Final, List, Optional, final

from .roster import Player, Role, Team

log = logging.getLogger('file')


@final
class TeamSplitter:
    """Class responsible for balancing players into teams."""

    MIN_PLAYER_NUMBER_FOR_4_TEAMS: Final = 24
    TEAM_COLORS: Final[list[str]] = ['Red', 'Blue', 'White', 'Green']
    __roster: List[Player]
    __random: random.Random
    __seed: int

    def __init__(self, roster: List[Player], seed: Optional[int] = None) -> None:
        self.__roster = roster
        self.__seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.__random = random.Random(self.__seed)
        log.info('Using seed: %d', self.__seed)

    @property
    def seed(self) -> int:
        return self.__seed

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

    def __validate_team_size_balance(self, teams: List[Team]) -> None:
        """Validate that team sizes differ by at most 1 player."""
        if not teams:
            return

        team_sizes = [team.size() for team in teams]
        min_size = min(team_sizes)
        max_size = max(team_sizes)

        if max_size - min_size > 1:
            raise ValueError(
                f'Team size imbalance: sizes range from {min_size} to {max_size}. '
                f'Difference must not exceed 1 player.'
            )

    def __split_into_teams(self, players: List[Player], num_teams: int) -> List[Team]:
        grouped: dict[Role, List[Player]] = defaultdict(list)
        for p in players:
            grouped[p.role].append(p)

        teams: List[Team] = [Team(TeamSplitter.TEAM_COLORS[colorIdx], self.__random)
                             for colorIdx in range(num_teams)]

        # Distribute field players first using snake draft
        non_goalies = [p for p in players if p.role != Role.GOALIE]
        field_player_count = len(non_goalies)
        num_player_rounds = (field_player_count + num_teams - 1) // num_teams

        log.info('Starting field player distribution via snake draft')
        log.info('Total field players: %d, Rounds: %d', field_player_count, num_player_rounds)

        player_pick_order: List[List[int]] = self.__generate_pick_order(
            num_teams, num_player_rounds)
        for round_idx, pick_order in enumerate(player_pick_order):
            is_final_round = (round_idx == num_player_rounds - 1)
            remaining_players = len(non_goalies)

            # For final round: if remaining players < num_teams, pick by lowest skill
            if is_final_round and remaining_players < num_teams:
                sorted_teams = sorted(
                    enumerate(teams),
                    key=lambda t: t[1].total_skill()
                )
                pick_order = [idx for idx, _ in sorted_teams]
                log.info('Round %d (final, %d players left): Pick order by skill %s',
                         round_idx + 1, remaining_players,
                         [teams[idx].name for idx in pick_order])
            else:
                team_names = [teams[idx].name for idx in pick_order]
                log.info('Round %d: Pick order %s', round_idx + 1, team_names)

            for team_idx in pick_order:
                if not non_goalies:
                    break
                player = non_goalies.pop(0)
                teams[team_idx].add_player(player)
                log.info('  %s picks %s (skill=%d, role=%s)',
                         teams[team_idx].name, player.name,
                         player.skill, player.role.name)

            # Log team skills after this round
            team_skills = ', '.join([f'{t.name}={t.total_skill()}' for t in teams])
            log.info('  After round %d: Team skills [%s]', round_idx + 1, team_skills)

        # Log teams after snake rounds complete
        log.info('Teams after snake draft rounds:')
        for team in teams:
            log.info('%s', str(team))

        # Distribute goalies based on team size (asc) and skill (asc)
        goalies = grouped[Role.GOALIE]
        log.info('Starting goalie distribution')
        log.info('Total goalies: %d', len(goalies))

        goalie_round = 0
        while goalies:
            goalie_round += 1
            # Sort teams: smallest size first, then lowest total skill
            sorted_teams = sorted(
                enumerate(teams),
                key=lambda t: (t[1].size(), t[1].total_skill())
            )
            team_order = [f'{idx}({teams[idx].name},size={teams[idx].size()},skill={teams[idx].total_skill()})'
                          for idx, _ in sorted_teams]
            log.info('Goalie round %d: Team order (by size,skill) %s',
                     goalie_round, team_order)

            for team_idx, _ in sorted_teams:
                if not goalies:
                    break
                goalie = goalies.pop(0)
                teams[team_idx].add_player(goalie)
                log.info('  Team %d (%s) gets goalie %s (skill=%d)',
                         team_idx, teams[team_idx].name, goalie.name, goalie.skill)

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

    def __generate_pick_order(self, num_teams: int, num_rounds: int) -> List[List[int]]:
        """
        Generate a combined random + snake draft order:
        - For odd-numbered rounds (0-based), use a random shuffle of teams.
        - For even-numbered rounds, use the reverse of the previous (snake) order.

        Returns a list of pick orders, one list per round, where each list
        contains team indices (0..num_teams-1).
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
                self.__random.shuffle(current)
            orders.append(current)
            use_snake = not use_snake

        return orders

    def split_teams(self, file_path: str) -> List[Team]:
        """
        Public method: read input names, validate, and split into teams.

        Args:
            file_path: Path to file containing player names

        Returns:
            List of Team objects with assigned players
        """
        names = self.__read_player_names(file_path)
        players = self.__validate_players(names)
        log.info('Number of actual players: %d', len(names))
        num_teams = 4 if len(
            players) >= TeamSplitter.MIN_PLAYER_NUMBER_FOR_4_TEAMS else 2
        teams = self.__split_into_teams(players, num_teams)

        # Rebalance teams
        balancer = RoleBalancer(teams)
        teams = balancer.balance()
        self.__validate_team_size_balance(teams)

        return teams

    def __save_teams(self, teams: List[Team], output_file: str) -> None:
        """Save teams to output file."""
        final_teams: List[str] = []
        for team in teams:
            final_teams.append(team.get_finalized())
        self.__save_finalized(final_teams, output_file)

    def split_and_save(self, file_path: str, output_file: str) -> None:
        """
        Public method: read input names, validate, split teams, and save output.
        """
        teams = self.split_teams(file_path)
        self.__print_teams(teams)
        self.__save_teams(teams, output_file)
        print(f'Done. Teams are saved as {output_file}')
