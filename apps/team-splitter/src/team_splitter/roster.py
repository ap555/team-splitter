import random
from dataclasses import dataclass
from enum import Enum
from typing import List, final

from dataclasses_json import DataClassJsonMixin


class Role(Enum):
    """Player's role on the team."""
    GOALIE = 'G'
    DEFENDER = 'D'
    MIDFIELDER = 'M'
    STRIKER = 'S'


@final
@dataclass(frozen=True)
class Player(DataClassJsonMixin):
    """Immutable model representing a player with public properties."""
    name: str
    role: Role
    skill: int

    def __str__(self) -> str:
        return f'{self.name} {self.role.value} {self.skill}'


@final
class Team:
    __name: str
    __players: List[Player]
    __random: random.Random

    def __init__(self, name: str, rng: random.Random | None = None) -> None:
        self.__name = name
        self.__players = []
        self.__random = rng if rng is not None else random.Random()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def players(self) -> List[Player]:
        return self.__players

    def skill(self) -> int:
        return sum(p.skill for p in self.__players)

    def size(self):
        return len(self.__players)

    def role_count(self, role: Role) -> int:
        return sum(p.role == role for p in self.__players)

    def add_player(self, player: Player) -> None:
        assert player not in self.__players
        self.__players.append(player)

    def get_finalized(self) -> List[str]:
        finalized: List[str] = []
        finalized.append(f'Team {self.name}')
        goalies = [p.name for p in self.__players if p.role == Role.GOALIE]
        others = [p.name for p in self.__players if p.role != Role.GOALIE]
        self.__random.shuffle(others)
        finalized.extend(goalies + others)
        return finalized

    def __str__(self) -> str:
        s: str = f'Team {self.name}, total skill: {self.skill()}\n'
        for player in self.__players:
            s += str(player)+'\n'
        return s


def save_players(players: List[Player], filename: str) -> None:
    players_json = Player.schema().dumps(players, many=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(players_json)


def load_players(filename: str) -> List[Player]:
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return Player.schema().loads(text, many=True)
