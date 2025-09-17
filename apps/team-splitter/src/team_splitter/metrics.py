from typing import Dict, List, Tuple

from .roster import Role, Team


class Metrics:
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
                delta_skill = abs(t1.skill() - t2.skill())
                self.__pairwise_skill[(t1, t2)] = delta_skill

                # Role deltas
                delta_roles: Dict[Role, int] = {}
                for role in Role:
                    delta_roles[role] = abs(t1.role_count(role) - t2.role_count(role))
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
    def max_skill_delta(self) -> int:
        '''Global maximum difference in total skill between any two teams.'''
        return self._max_skill_delta

    @property
    def teams_for_max_skill(self) -> Tuple[Team, Team]:
        '''Pair of teams where skill delta is maximal.'''
        return self._teams_for_max_skill

    @property
    def max_role_delta(self) -> int:
        '''Global maximum difference in role count for any role between any two teams.'''
        return self.__max_role_delta

    @property
    def role_for_max_delta(self) -> Role:
        '''Role for which the difference is maximal.'''
        return self.__role_for_max_delta

    @property
    def teams_for_max_role(self) -> Tuple[Team, Team]:
        '''Pair of teams where role delta is maximal.'''
        return self.__teams_for_max_role

    @property
    def min_player_skill(self) -> int:
        '''Global minimum skill among all players in all teams.'''
        return self.__min_player_skill
