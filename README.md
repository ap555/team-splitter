# Team Splitter

A Python tool for creating balanced teams from a roster of players, optimized for sports team formation with skill-based and role-based balancing.

## Features

- ⚖️ **Balanced Team Creation**: Uses snake draft algorithm to distribute players fairly
- 🎯 **Role-Based Balancing**: Balances teams by player roles (Goalkeeper, Defender, Midfielder, Striker)
- 📊 **Skill Optimization**: Advanced role balancer with penalty system for optimal team composition
- 🔄 **Dynamic Versioning**: Git-based versioning using setuptools-scm
- 📝 **Comprehensive Logging**: Detailed logs of draft rounds and team balancing swaps
- 🎲 **Reproducible Results**: Seed-based random generation for testing and debugging

## How It Works

1. **Snake Draft**: Field players are distributed using a randomized snake draft pattern
2. **Goalie Distribution**: Goalies are assigned based on team size and total skill to maintain balance
3. **Role Balancing**: Iterative optimization swaps players between teams to:
   - Minimize skill differences
   - Balance defender counts (max difference: 1)
   - Balance striker counts (max difference: 1)

## Team Formation Rules

- **< 24 players**: Creates 2 teams (Red, Blue)
- **≥ 24 players**: Creates 4 teams (Red, Blue, White, Green)
- Team sizes never differ by more than 1 player

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/team-splitter.git
cd team-splitter/apps/team-splitter

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Usage

```bash
python main.py -r <roster.json> -p <players.txt> -o <output.txt>
```

### Arguments

- `-r, --roster`: Path to roster JSON file containing all available players
- `-p, --players`: Path to text file listing players to include in team split
- `-o, --output`: Path to output file for generated teams

### Example

```bash
python main.py -r tests/roster.epl.json -p players.txt -o teams.txt
```

## Roster Format

The roster JSON file should contain player information:

```json
[
  {
    "name": "Player Name",
    "skill": 85,
    "role": "STRIKER"
  }
]
```

**Supported Roles**: `GOALIE`, `DEFENDER`, `MIDFIELDER`, `STRIKER`

## Players File Format

Simple text file with player names (one per line):

```
Player One
Player Two
Player Three
```

## Output

The tool generates:
1. **Console output**: Team rosters with player details
2. **Output file**: Finalized team lists (goalies listed first, other players randomized)
3. **Log file**: Detailed draft and balancing process
   - Linux/Mac: `~/.local/we828/team-splitter/team-splitter.txt`
   - Windows: `%LOCALAPPDATA%\we828\team-splitter\team-splitter.txt`

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
pyrefly check
```

## Version

This project uses dynamic versioning based on git tags:
- Format: `<tag>.<commits>+g<hash>`
- Example: `1.0.5+g699a121`

## License

See LICENSE file for details.

## Author

**we828** - [ap555](https://github.com/ap555)
