from typing import Final, List, Tuple, Optional

from .roster import Player, Team
from .metrics import Metrics


class RoleBalancer:
    MAX_ITER: Final = 100
    DEFENDER_IMBALANCE_PENALTY: Final = 15
    STRIKER_IMBALANCE_PENALTY: Final = 10

    __teams: List[Team]

    def __init__(self, teams: List[Team]) -> None:
        self.__teams = teams

    def balance(self) -> List[Team]:
        """
        Iteratively improve team balance by swapping players.
        Stops when no swap improves the balance score or max iterations reached.
        """
        for _ in range(self.MAX_ITER):
            current_metrics = Metrics(self.__teams)
            current_score = self.__calculate_score(current_metrics)

            best_swap = self.__find_best_global_swap(current_score)

            if best_swap:
                # Apply the best swap found
                t1, t2, p1, p2 = best_swap
                t1.remove_player(p1)
                t2.add_player(p1)
                t2.remove_player(p2)
                t1.add_player(p2)
            else:
                # No improvement found, we are done
                break

        return self.__teams

    def __calculate_score(self, metrics: Metrics) -> float:
        """
        Calculate the balance score. Lower is better.
        score = skill_diff + (def_penalty * 15) + (striker_penalty * 10)
        """
        skill_diff = metrics.skill_diff

        # Penalties apply if difference > 1
        def_diff = metrics.defender_diff
        def_penalty = max(0, def_diff - 1)

        striker_diff = metrics.striker_diff
        striker_penalty = max(0, striker_diff - 1)

        return (skill_diff * 1.0) + \
               (def_penalty * self.DEFENDER_IMBALANCE_PENALTY) + \
               (striker_penalty * self.STRIKER_IMBALANCE_PENALTY)

    def __find_best_global_swap(self, current_score: float) -> Optional[Tuple[Team, Team, Player, Player]]:
        """
        Find the single best swap across all team pairs that improves the score.
        Returns (team1, team2, player1, player2) or None.
        """
        best_swap = None
        best_new_score = current_score

        # Iterate through all unique pairs of teams
        for i in range(len(self.__teams)):
            for j in range(i + 1, len(self.__teams)):
                t1 = self.__teams[i]
                t2 = self.__teams[j]

                # Try all player swaps between these two teams
                for p1 in t1.players:
                    for p2 in t2.players:
                        # Optimization: Skip if swapping same role and similar skill (optional, but speeds up)
                        # But for now, let's be exhaustive to be safe.

                        # Simulate swap
                        t1.remove_player(p1)
                        t2.add_player(p1)
                        t2.remove_player(p2)
                        t1.add_player(p2)

                        # Check new score
                        new_metrics = Metrics(self.__teams)
                        new_score = self.__calculate_score(new_metrics)

                        if new_score < best_new_score:
                            best_new_score = new_score
                            best_swap = (t1, t2, p1, p2)

                        # Revert swap
                        t1.remove_player(p2)
                        t2.add_player(p2)
                        t2.remove_player(p1)
                        t1.add_player(p1)

        return best_swap
