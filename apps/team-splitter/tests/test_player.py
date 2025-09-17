import json

from team_splitter.roster import Player, Role, save_players, load_players


def test_player_to_dict_and_back():
    p = Player('Diego Maradona', Role.STRIKER, 100)
    d = p.to_dict()
    assert isinstance(d, dict)
    assert d == {'name': 'Diego Maradona', 'role': Role.STRIKER, 'skill': 100}

    p2 = Player.from_dict(d)
    assert p2 == p

def test_player_json_roundtrip():
    p = Player('David Beckhum', Role.MIDFIELDER, 82)
    json_str = p.to_json()
    data = json.loads(json_str)
    assert data['name'] == 'David Beckhum'
    assert data['role'] == 'M'
    assert data['skill'] == 82

    p2 = Player.from_json(json_str)
    assert p2 == p

def test_save_and_load_players(tmp_path):
    roster = [
        Player('A', Role.GOALIE,   10),
        Player('B', Role.DEFENDER, 20),
        Player('C', Role.MIDFIELDER, 30),
    ]
    fn = tmp_path / 'players.json'

    save_players(roster, str(fn))
    assert fn.exists()

    text = fn.read_text(encoding='utf-8')
    data = json.loads(text)
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)

    loaded = load_players(str(fn))
    assert loaded == roster
