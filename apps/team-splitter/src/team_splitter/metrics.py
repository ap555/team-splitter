from typing import Dict, List, Tuple

from .roster import Role, Team


class Metrics:
    DEFENDER_IMPORTANCE_COEF = 1.3
    STRIKER_IMPORTANCE_COEF = 1.2

    __teams: List[Team]
    __pairwise_skill: Dict[Tuple[Team, Team], int]
    __pairwise_role: Dict[Tuple[Team, Team], Dict[Role, int]]
    __max_role_delta: int
    __role_for_max_delta: Role
    __teams_for_max_role: Tuple[Team, Team]
    __min_player_skill: int
    __role_target: Dict[Role, int]

    def __init__(self, teams: List[Team]) -> None:
        self.__teams = teams
        self.__pairwise_skill = {}
        self.__pairwise_role = {}
        self.__role_target = {}

        self.__compute_pairwise()

        # Find global max skill delta and corresponding teams
        max_skill: int = -1
        teams_for_skill: Tuple[Team, Team] = (teams[0], teams[0])
        for (t1, t2), ds in self.__pairwise_skill.items():
            if ds > max_skill:
                max_skill = ds
                teams_for_skill = (t1, t2)
        self._max_skill_delta: int = max_skill
        self._teams_for_max_skill: Tuple[Team, Team] = teams_for_skill

        # Find global max role delta, the role, and the teams
        max_role: int = -1
        role_for_max: Role = None  # type: ignore
        teams_for_role: Tuple[Team, Team] = (teams[0], teams[0])
        for pair, drs in self.__pairwise_role.items():
            for role, dr in drs.items():
                if dr > max_role:
                    max_role = dr
                    role_for_max = role
                    teams_for_role = pair

        self.__max_role_delta = max_role
        self.__role_for_max_delta = role_for_max
        self.__teams_for_max_role = teams_for_role
        self.__min_player_skill = self.__compute_min_player_skill()

        for r in Role:
            self.__role_target[r] = self.__compute_target_for_role(r)

    def __compute_pairwise(self) -> None:
        for idx, t1 in enumerate(self.__teams):
            for t2 in self.__teams[idx + 1:]:
                delta_skill = abs(t1.total_skill() - t2.total_skill())
                self.__pairwise_skill[(t1, t2)] = delta_skill

                # Role deltas
                delta_roles: Dict[Role, int] = {}
                for role in Role:
                    delta_roles[role] = abs(
                        t1.role_count(role) - t2.role_count(role))
                self.__pairwise_role[(t1, t2)] = delta_roles

    def __compute_min_player_skill(self) -> int:
        '''Global minimum skill among all players in all teams.'''
        return min(
            player.skill
            for team in self.__teams
            for player in team.players
        )

    def __compute_target_for_role(self, role: Role) -> int:
        team_count = len(self.__teams)
        if team_count == 0:
            return 0

        role_total = sum(team.role_count(role) for team in self.__teams)

        avg = role_total / team_count
        target = round(avg)

        return target

    @property
    def max_skill_diff_between_any_teams(self) -> int:
        '''Global maximum difference in total skill between any two teams.'''
        return self._max_skill_delta

    @property
    def teams_for_max_skill_diff(self) -> Tuple[Team, Team]:
        '''Pair of teams where skill delta is maximal.'''
        return self._teams_for_max_skill

    @property
    def max_role_diff_between_any_teams(self) -> int:
        '''Global maximum difference in role count for any role between any two teams.'''
        return self.__max_role_delta

    @property
    def role_for_max_role_diff(self) -> Role:
        '''Role for which the difference is maximal.'''
        return self.__role_for_max_delta

    @property
    def teams_for_max_role_diff(self) -> Tuple[Team, Team]:
        '''Pair of teams where role delta is maximal.'''
        return self.__teams_for_max_role

    @property
    def min_player_skill(self) -> int:
        '''Global minimum skill among all players in all teams.'''
        return self.__min_player_skill

    def teams_for_max_role_imbalance(self, role: Role) -> Tuple[Team, Team, int]:
        """
        Find the two teams with largest imbalance for a given role.

        Args:
            role: The role to check

        Returns:
            Tuple of (team1, team2, delta) where delta is the role count difference
        """
        max_delta = -1
        result_teams = (self.__teams[0], self.__teams[0])

        for pair, deltas in self.__pairwise_role.items():
            delta = deltas[role]
            if delta > max_delta:
                max_delta = delta
                result_teams = pair

        return (result_teams[0], result_teams[1], max_delta)

    @property
    def skill_diff(self) -> int:
        """Global maximum difference in total skill between any two teams."""
        return self._max_skill_delta

    @property
    def defender_diff(self) -> int:
        """Global maximum difference in defender count between any two teams."""
        max_diff = 0
        for _, deltas in self.__pairwise_role.items():
            diff = deltas.get(Role.DEFENDER, 0)
            if diff > max_diff:
                max_diff = diff
        return max_diff

    @property
    def striker_diff(self) -> int:
        """Global maximum difference in striker count between any two teams."""
        max_diff = 0
        for _, deltas in self.__pairwise_role.items():
            diff = deltas.get(Role.STRIKER, 0)
            if diff > max_diff:
                max_diff = diff
        return max_diff

    @staticmethod
    def team_pair_score(team_one: Team, team_two: Team) -> float:
        # Calculate role-weighted score for each team
        team_one_role_score = (team_one.skill_by_role(Role.DEFENDER) * Metrics.DEFENDER_IMPORTANCE_COEF
                               + team_one.skill_by_role(Role.STRIKER) * Metrics.STRIKER_IMPORTANCE_COEF)
        team_two_role_score = (team_two.skill_by_role(Role.DEFENDER) * Metrics.DEFENDER_IMPORTANCE_COEF
                               + team_two.skill_by_role(Role.STRIKER) * Metrics.STRIKER_IMPORTANCE_COEF)

        # Total score for each team
        team_one_total_score = team_one_role_score + team_one.total_skill()
        team_two_total_score = team_two_role_score + team_two.total_skill()

        # Final balance score is the absolute difference
        balance_score = abs(team_one_total_score - team_two_total_score)

        return balance_score

    @staticmethod
    def team_pair_by_max_score_diff(teams: list[Team]) -> Tuple[Team, Team, float]:
        best_score = float('inf')
        best_pair: Tuple[Team, Team, float] | None = None

        for idx, t1 in enumerate(teams):
            for t2 in teams[idx + 1:]:
                local_score = Metrics.team_pair_score(t1, t2)
                if local_score < best_score:
                    best_pair = (t1, t2, local_score)

        assert best_pair is not None, 'Need at least 2 teams to find worst pair'
        return best_pair
