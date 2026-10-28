import pytest

from team_splitter.json_api import split_request


def request(count=6):
    return {'roster': [{'id': str(i), 'name': 'Namesake', 'skill': 10 + i, 'role': 'M'}
                       for i in range(count)],
            'squad': [{'id': str(i), 'name': 'Namesake'} for i in range(count)], 'seed': 42}


def test_ids_preserve_namesakes():
    result = split_request(request())
    players = [p for t in result['teams'] for p in t['players']]
    assert {p['id'] for p in players} == {str(i) for i in range(6)}
    assert len(players) == 6
    assert result == split_request(request())


def test_mean_uses_only_registered_rated_players():
    data = request()
    data['roster'].append({'id': 'unregistered', 'name': 'Other', 'skill': 100, 'role': 'S'})
    data['squad'].append({'id': 'guest:1', 'name': 'Guest'})
    data['unknown_policy'] = 'mean'
    result = split_request(data)
    guest = next(p for t in result['teams'] for p in t['players'] if p['id'] == 'guest:1')
    assert guest['skill'] == 12
    assert isinstance(guest['skill'], int)
    assert guest['role'] == 'M'


def test_unknown_default_is_error():
    data = request()
    data['roster'].pop()
    with pytest.raises(ValueError, match='Unknown player'):
        split_request(data)


@pytest.mark.parametrize('count', [6, 7, 23, 24, 25])
def test_all_guests_random_split(count):
    data = request(count)
    data.update(roster=[], unknown_policy='mean')
    result = split_request(data)
    teams = result['teams']
    assert len(teams) == (4 if count >= 24 else 2)
    sizes = [len(team['players']) for team in teams]
    assert max(sizes) - min(sizes) <= 1
    ids = [p['id'] for team in teams for p in team['players']]
    assert len(ids) == count
    assert set(ids) == {str(i) for i in range(count)}
    assert result == split_request(data)
    data['seed'] = 99
    assert result['teams'] != split_request(data)['teams']


def test_all_guests_error_policy():
    data = request()
    data['roster'] = []
    with pytest.raises(ValueError, match='Unknown player'):
        split_request(data)


def test_below_threshold_clears_teams():
    assert split_request(request(5)) == {'teams': []}


def test_four_teams():
    teams = split_request(request(25))['teams']
    assert len(teams) == 4
    assert sorted(len(t['players']) for t in teams) == [6, 6, 6, 7]


def test_duplicate_ids_rejected():
    data = request()
    data['squad'].append(data['squad'][0])
    with pytest.raises(ValueError, match='Duplicate squad ID'):
        split_request(data)


def test_json_process_protocol():
    import json
    import subprocess
    import sys

    result = subprocess.run([sys.executable, '-m', 'team_splitter.json_api'],
                            input=json.dumps(request()), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert len(json.loads(result.stdout)['teams']) == 2
    invalid = subprocess.run([sys.executable, '-m', 'team_splitter.json_api'],
                             input='{', text=True, capture_output=True)
    assert invalid.returncode == 2
    assert 'error' in json.loads(invalid.stdout)


@pytest.mark.parametrize('skill', [12.5, True, '12'])
def test_noninteger_skill_rejected(skill):
    data = request()
    data['roster'][0]['skill'] = skill
    with pytest.raises(ValueError, match='skill must be an integer'):
        split_request(data)
