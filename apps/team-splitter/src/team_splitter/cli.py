from team_splitter.version import __version__
import argparse
import logging

from .roster import load_players, save_players
from .team_splitter import TeamSplitter


log = logging.getLogger('file')

def test_me(text: str, key: int) -> str:
    data = text.encode('utf-8')
    enc = [b ^ key for b in data]
    cpp = ', '.join(f'0x{b:02X}' for b in enc)
    return f'{{ {cpp} }}  // len = {len(enc)}'

def main() -> None:
    log.info('')
    log.info('********************START*********************************************')
    log.info('%s, version %s, Copyright(C) %s', 'Team Splitter', __version__, 'we828')

    parser = argparse.ArgumentParser(description='Split players into 2 or 4 teams')
    parser.add_argument('-r','--roster', help='The roster of all players with skill.')
    parser.add_argument('-p','--players', help='Text file with player names for todays game.')
    parser.add_argument('-o', '--output', default='final_teams.txt', help='Output file for finalized lists.')
    args = parser.parse_args()

    roster = load_players(args.roster)
    log.info('Loaded roster: %d players', len(roster))
    #save_players(roster, args.roster)

    splitter = TeamSplitter(roster)
    splitter.split_and_save(args.players, args.output)
