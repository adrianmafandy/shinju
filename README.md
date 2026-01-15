# Shinju 神樹

A Python 3 remake of the classic `tree` command with powerful search functionality.

```
    ▄▄▄ ▐▌   ▄ ▄▄▄▄     ▗▖█  ▐▌
   ▀▄▄  ▐▌   ▄ █   █    ▗▖▀▄▄▞▘
   ▄▄▄▀ ▐▛▀▚▖█ █   █ ▄  ▐▌     
        ▐▌ ▐▌█       ▀▄▄▞▘

   神樹(GodTree) + Search Tool
```

## Features

- 🌳 **Tree Display** - Classic directory tree visualization
- 🔍 **Content Search** - Search for keywords/regex in file contents
- 📛 **Name Search** - Find files/directories by name pattern
- 🎨 **Color Highlighting** - Visual distinction for matches
- 📋 **Match Snippets** - Shows first match context inline
- ⚡ **Match-Only Mode** - Filter output to show only matches

## Installation

```bash
# Clone or copy shinju.py to your system
chmod +x shinju.py

# Run directly
./shinju.py [OPTIONS] [DIRECTORY]

# Or with Python
python3 shinju.py [OPTIONS] [DIRECTORY]
```

## Usage

```bash
shinju [OPTIONS] [DIRECTORY]
```

### Options

| Flag | Description |
|------|-------------|
| `-a, --all` | Show hidden files and directories |
| `-d, --dirs-only` | List directories only |
| `-L, --level DEPTH` | Limit the depth of the tree |
| `-s, --search PATTERN` | Search for pattern in file contents |
| `-n, --name PATTERN` | Search for pattern in file/directory names |
| `-r, --regex` | Treat search pattern as regex |
| `-i, --ignore-case` | Case-insensitive search |
| `-m, --matches-only` | Show only matching files/directories |

### Examples

```bash
# Basic tree
shinju

# Show hidden files
shinju -a

# Limit depth to 2 levels
shinju -L 2 /path/to/dir

# Search file contents for keyword
shinju -s "password"

# Search with comma-separated keywords
shinju -s "password,secret,api_key"

# Regex search (case-insensitive)
shinju -s "def\s+\w+" -r -i

# Find files by name
shinju -n "config"

# Combine name + content search
shinju -n ".txt" -s "TODO"

# Show only matches (reduce output)
shinju -s "import" -m
```

## Output Examples

### Content Search (`-s`)
```
├── config/
│   └── database.yml [2 matches] ['password' => 'password: secret123']
```

### Name Search (`-n`)
```
├── .env [match]
├── config/
│   └── .env.local [match]
```

### Combined Search (`-n` + `-s`)
```
├── secrets.txt ['api_key' => 'api_key=sk-12345...']
```

## Excluded Extensions

The following file extensions are automatically skipped during content search:

```
gz, zip, tar, rar, 7z, bz2, xz, deb, img, iso, vmdk, dll, ovf, ova
```

## Color Legend

| Color | Meaning |
|-------|---------|
| 🔵 Blue | Directories |
| 🟢 Green | Name matches |
| 🟣 Magenta | Content matches |
| 🟡 Yellow | Match count |
| 🔵 Cyan | Match snippet |
| ⚫ Dim | Non-matching files (when searching) |

## License

MIT
