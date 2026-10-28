"""ID-based JSON boundary for website integrations."""

import argparse
import json
import random
import sys
from typing import Any

from .roster import Player, Role, Team
from .team_splitter import TeamSplitter


def split_request(request: dict[str, Any]) -> dict[str, Any]:
    """Resolve registered IDs and split them using error or mean unknown handling."""
    policy = request.get('unknown_policy', 'error')
    if policy not in ('error', 'mean'):
        raise ValueError('unknown_policy must be error or mean')
    roster = request.get('roster')
    squad = request.get('squad')
    if not isinstance(roster, list) or not isinstance(squad, list):
        raise ValueError('roster and squad must be arrays')
    known: dict[str, Player] = {}
    for item in roster:
        player_id, name = _identity(item)
        skill = item.get('skill')
        if isinstance(skill, bool) or not isinstance(skill, int):
            raise ValueError('skill must be an integer')
        if player_id in known:
            raise ValueError(f'Duplicate roster ID: {player_id}')
        known[player_id] = Player(name, Role(item.get('role')), skill, player_id)
    identities = [_identity(item) for item in squad]
    ids = [player_id for player_id, _ in identities]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate squad ID')
    if len(ids) < 6:
        return {'teams': []}
    unknown = [player_id for player_id in ids if player_id not in known]
    if unknown and policy == 'error':
        raise ValueError(f'Unknown player IDs: {", ".join(unknown)}')
    skills = [known[player_id].skill for player_id in ids if player_id in known]
    average = sum(skills) // len(skills) if skills else 0
    players = [known[player_id] if player_id in known else
               Player(name, Role.MIDFIELDER, average, player_id)
               for player_id, name in identities]
    seed = request.get('seed')
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise ValueError('seed must be an integer')
    splitter = TeamSplitter(players, seed=seed)
    if not skills:
        rng = random.Random(splitter.seed)
        rng.shuffle(players)
        count = 4 if len(players) >= TeamSplitter.MIN_PLAYER_NUMBER_FOR_4_TEAMS else 2
        teams = [Team(color, rng) for color in TeamSplitter.TEAM_COLORS[:count]]
        for index, player in enumerate(players):
            teams[index % count].add_player(player)
    else:
        teams = splitter.split_players(players)
    return {'seed': splitter.seed, 'teams': [
        {'name': team.name, 'players': [
            {'id': p.id, 'name': p.name, 'role': p.role.value, 'skill': p.skill}
            for p in team.players]} for team in teams]}


def _identity(item: Any) -> tuple[str, str]:
    if not isinstance(item, dict):
        raise ValueError('Player must be an object')
    player_id, name = item.get('id'), item.get('name')
    if not isinstance(player_id, str) or not player_id.strip():
        raise ValueError('Player ID must be a nonempty string')
    if not isinstance(name, str) or not name.strip():
        raise ValueError('Player name must be a nonempty string')
    return player_id, name


def main() -> None:
    """Read one UTF-8 JSON request on stdin and emit one JSON response."""
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError('Request must be an object')
        response = split_request(request)
    except (ValueError, TypeError) as error:
        json.dump({'error': str(error)}, sys.stdout, ensure_ascii=False)
        sys.stdout.write('\n')
        raise SystemExit(2)
    json.dump(response, sys.stdout, ensure_ascii=False, allow_nan=False)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
