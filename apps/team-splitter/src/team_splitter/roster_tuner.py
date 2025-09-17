import argparse
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from .roster import Player, Role, load_players, save_players


def group_by_role(players: List[Player]) -> Dict[Role, List[int]]:
    idx_by_role: Dict[Role, List[int]] = {r: [] for r in Role}
    for idx, pl in enumerate(players):
        idx_by_role[pl.role].append(idx)
    return idx_by_role

def pick_pair_same_role(idx_by_role: Dict[Role, List[int]]) -> Tuple[int, int]:
    roles_with_two = [r for r, idxs in idx_by_role.items() if len(idxs) >= 2]
    if not roles_with_two:
        raise RuntimeError('Need at least 2 players per role.')
    role = random.choice(roles_with_two)
    a, b = random.sample(idx_by_role[role], 2)
    return (a, b)

def print_pair(a: Player, b: Player) -> None:
    print('\nCompare:')
    print(f' A) {a.name} [{a.role.value}] skill={a.skill}')
    print(f' B) {b.name} [{b.role.value}] skill={b.skill}')
    print('Choose: a / b / eq / no / save / quit')

def apply_judgement(players: List[Player], i: int, j: int, cmd: str) -> bool:
    pa, pb = players[i], players[j]
    if cmd == 'a':
        if pa.skill < pb.skill:
            # swap skills
            players[i] = Player(name=pa.name, role=pa.role, skill=pb.skill)
            players[j] = Player(name=pb.name, role=pb.role, skill=pa.skill)
            print('→ Updated: swapped skills (A stronger than B).')
            return True
        print('→ All good, no changes.')
        return False
    if cmd == 'b':
        if pb.skill < pa.skill:
            players[i] = Player(name=pa.name, role=pa.role, skill=pb.skill)
            players[j] = Player(name=pb.name, role=pb.role, skill=pa.skill)
            print('→ Updated: swapped skills (B stronger than A).')
            return True
        print('→ All good, no changes.')
        return False
    if cmd == 'eq':
        avg = round((pa.skill + pb.skill) * 0.5)
        if avg != pa.skill or avg != pb.skill:
            players[i] = Player(name=pa.name, role=pa.role, skill=avg)
            players[j] = Player(name=pb.name, role=pb.role, skill=avg)
            print(f'→ Updated: both are now {avg}.')
            return True
        print('→ All good, no changes.')
        return False
    if cmd == 'no':
        print('→ No changes.')
        return False
    raise ValueError('unknown cmd')

def main() -> None:
    parser = argparse.ArgumentParser(description='Interactive skill tuning for roster.json.')
    parser.add_argument('roster', type=Path, help='Path to roster.json')
    parser.add_argument('--seed', type=int, default=None, help='seed')
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    roster_path: Path = args.roster
    if not roster_path.exists():
        print(f'File not found: {roster_path}', file=sys.stderr)
        sys.exit(1)

    players = load_players(str(roster_path))
    if not players:
        print('The roster is empty.', file=sys.stderr)
        sys.exit(1)

    print(f'Loaded players: {len(players)} of {roster_path}')
    print('Teams: a, b, eq (equal), no (no change), save, quit')

    while True:
        try:
            idx_by_role = group_by_role(players)
            i, j = pick_pair_same_role(idx_by_role)
        except RuntimeError as e:
            print(f'Error: {e}')
            break

        print_pair(players[i], players[j])
        cmd = input('> ').strip().lower()

        if cmd in {'quit', 'q', 'exit'}:
            save_players(players, str(roster_path))
            print(f'Saved and exit: {roster_path}')
            break
        if cmd == 'save':
            save_players(players, str(roster_path))
            print(f'Saved: {roster_path}')
            continue
        if cmd not in {'a', 'b', 'eq', 'no'}:
            print('Incorrect cmd. Usage: a / b / eq / no / save / quit')
            continue

        changed = apply_judgement(players, i, j, cmd)
        if changed:
            save_players(players, str(roster_path))
            print(f'Autosave: {roster_path}')
