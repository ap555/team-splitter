from typing import List
import pytest
from team_splitter.roster import Player, Role, Team
from team_splitter.role_balancer import RoleBalancer
from team_splitter.metrics import Metrics


def create_player(name: str, role: Role, skill: int) -> Player:
    return Player(name=name, role=role, skill=skill)


def test_rebalancing_fixes_defender_imbalance():
    """
    Test that rebalancing fixes a defender imbalance even if it costs some skill.
    Team A: 3 Defenders (80, 80, 80), 1 Striker (80) -> Skill 320
    Team B: 1 Defender (80), 3 Strikers (80, 80, 80) -> Skill 320

    Swap D(80) <-> S(80) fixes roles perfectly with 0 skill cost.
    """
    t1 = Team("A")
    t1.add_player(create_player("D1", Role.DEFENDER, 80))
    t1.add_player(create_player("D2", Role.DEFENDER, 80))
    t1.add_player(create_player("D3", Role.DEFENDER, 80))
    t1.add_player(create_player("S1", Role.STRIKER, 80))

    t2 = Team("B")
    t2.add_player(create_player("D4", Role.DEFENDER, 80))
    t2.add_player(create_player("S2", Role.STRIKER, 80))
    t2.add_player(create_player("S3", Role.STRIKER, 80))
    t2.add_player(create_player("S4", Role.STRIKER, 80))

    teams = [t1, t2]
    balancer = RoleBalancer(teams)
    balancer.balance()

    # Should be 2 Defenders each
    assert t1.role_count(Role.DEFENDER) == 2
    assert t2.role_count(Role.DEFENDER) == 2


def test_rebalancing_accepts_small_skill_cost():
    """
    Test that rebalancing accepts a small skill cost to fix defender imbalance.
    Team A: D(90), D(90), D(90), S(80)
    Team B: D(80), S(80), S(80), S(80)

    Swap D(90) from A with S(80) from B.
    New A: D(90), D(90), S(80), S(80) -> Skill 340
    New B: D(80), D(90), S(80), S(80) -> Skill 330
    Skill Diff: 10.
    Defender Imbalance: 0 (was 2).
    Penalty reduction: (2-1)*15 = 15.
    Cost increase: 10.
    Net improvement: 15 - 10 = 5. Should swap.
    """
    t1 = Team("A")
    t1.add_player(create_player("D1", Role.DEFENDER, 90))
    t1.add_player(create_player("D2", Role.DEFENDER, 90))
    t1.add_player(create_player("D3", Role.DEFENDER, 90))
    t1.add_player(create_player("S1", Role.STRIKER, 80))

    t2 = Team("B")
    t2.add_player(create_player("D4", Role.DEFENDER, 80))
    t2.add_player(create_player("S2", Role.STRIKER, 80))
    t2.add_player(create_player("S3", Role.STRIKER, 80))
    t2.add_player(create_player("S4", Role.STRIKER, 80))

    teams = [t1, t2]
    balancer = RoleBalancer(teams)
    balancer.balance()

    # Should swap
    assert t1.role_count(Role.DEFENDER) == 2
    assert t2.role_count(Role.DEFENDER) == 2

    # Check skill diff is 10
    metrics = Metrics(teams)
    assert metrics.skill_diff == 10


def test_rebalancing_rejects_large_skill_cost():
    """
    Test that rebalancing REJECTS a large skill cost to fix defender imbalance.
    Team A: D(95), D(95), D(95), S(80)
    Team B: D(60), S(80), S(80), S(80)

    Swap D(95) from A with S(80) from B.
    Skill gap: 15.
    Skill Diff change: 2 * 15 = 30.
    Defender Imbalance reduction: 1.
    Penalty saved: 15.
    Cost incurred: 30.
    Net: 15 - 30 = -15. Should NOT swap.
    """
    t1 = Team("A")
    t1.add_player(create_player("D1", Role.DEFENDER, 95))
    t1.add_player(create_player("D2", Role.DEFENDER, 95))
    t1.add_player(create_player("D3", Role.DEFENDER, 95))
    t1.add_player(create_player("S1", Role.STRIKER, 80))

    t2 = Team("B")
    t2.add_player(create_player("D4", Role.DEFENDER, 60))
    t2.add_player(create_player("S2", Role.STRIKER, 80))
    t2.add_player(create_player("S3", Role.STRIKER, 80))
    t2.add_player(create_player("S4", Role.STRIKER, 80))

    teams = [t1, t2]
    balancer = RoleBalancer(teams)
    balancer.balance()

    # Should NOT swap
    assert t1.role_count(Role.DEFENDER) == 3
    assert t2.role_count(Role.DEFENDER) == 1
