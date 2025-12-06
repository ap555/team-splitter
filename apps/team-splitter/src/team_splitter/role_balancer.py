from typing import Dict, Final, List, Tuple

from .roster import Player, Role, Team
from .metrics import Metrics


class RoleBalancer:
    MAX_ITER: Final = 25

    __teams: List[Team]

    def __init__(self, teams: List[Team]) -> None:
        self.__teams = teams

    def balance(self) -> List[Team]:
        max_rounds: int = 100
        no_improvement_count = 0

        for _ in range(max_rounds):
            t1, t2, _ = Metrics.team_pair_by_max_score_diff(self.__teams)
            best_swap = self.__find_best_swap(t1, t2)

            if best_swap is not None:
                p1, p2 = best_swap
                # Execute swap
                t1.remove_player(p1)
                t2.add_player(p1)
                t2.remove_player(p2)
                t1.add_player(p2)

                no_improvement_count = 0

            else:
                no_improvement_count += 1

            if no_improvement_count >= 3:
                break

        return self.__teams

    def __find_best_swap(self, team_a: Team, team_b: Team) -> Tuple[Player, Player] | None:
        """
        Find the single best player swap between two teams that improves balance.

        Args:
            team_a: First team
            team_b: Second team

        Returns:
            Tuple of (player_from_a, player_from_b) or None if no improving swap exists
        """
        assert(team_a in self.__teams)
        assert(team_b in self.__teams)

        current_score = Metrics.team_pair_score(team_a, team_b)

        best_swap = None
        best_score = current_score

        # Try all possible swaps
        for player_a in team_a.players:
            for player_b in team_b.players:
                # Simulate swap
                team_a.remove_player(player_a)
                team_b.add_player(player_a)
                team_b.remove_player(player_b)
                team_a.add_player(player_b)

                # Calculate new score with fresh metrics
                new_score = Metrics.team_pair_score(team_a, team_b)

                # Track best improvement
                if new_score < best_score:
                    best_score = new_score
                    best_swap = (player_a, player_b)

                # Undo swap
                team_a.remove_player(player_b)
                team_b.add_player(player_b)
                team_b.remove_player(player_a)
                team_a.add_player(player_a)

        return best_swap


