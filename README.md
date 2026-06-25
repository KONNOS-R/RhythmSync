# RhythmSync

```
  ___ _        _   _          ___              
 | _ \ |_ _  _| |_| |_  _ __ / __|_  _ _ _  __ 
 |   / ' \ || |  _| ' \| '  \\__ \ || | ' \/ _|
 |_|_\_||_\_, |\__|_||_|_|_|_|___/\_, |_||_\__|
          |__/                    |__/         
```

CLI audio player that plays music while displaying synchronized lyrics (LRC).

---

## Features

- Play audio files in various modes (single file, directory, playlist)
- Display synchronized lyrics during playback
- Show song metadata tags
- Styled terminal music player UI
- Convert audio files to other formats using FFmpeg
- Embed `.lrc` files into audio files
- Create, load, repair, and delete `.mpl` playlists
- Player controls:
  - `SPACE` – Pause/Resume
  - `RIGHT Arrow` – Next track
  - `LEFT Arrow` – Previous track
  - `I` – Toggle main display between lyrics and info

---

## Requirements

- Python 3.8+
- FFmpeg (optional, required for conversion feature)

---

## Compatibility

RhythmSync is currently intended for UNIX-based systems (Linux/macOS).
Non-UNIX systems support is not currently available.

---

## Installation and Usage

**PyPI page:** [Click here](https://pypi.org/project/rhythmsync/)

1. Install the CLI application:
   ```
   pip install rhythmsync
   ```

2. Launch the CLI application:
   ```
   rhythmsync
   ```

---

## Supported Audio Formats

- MP3 (`.mp3`)
- FLAC (`.flac`)
- WAV (`.wav`)
- OGG (`.ogg`)

---

## Lyrics Sync

RhythmSync reads embedded lyric metadata from audio files.

### Supported LRC Tags

- `SYLT`, `SYLT::eng`
- `LYRICS`, `LYRICS:eng`
- `LYRICS-ENG`, `LYRICS_EN`
- `LYRICS_SYNCED`, `SYNCEDLYRICS`

### LRC Format

```
[00:12.34] First line
[00:15.67] Second line
[00:18.90] Third line
```

- Format: `[mm:ss.xx] Line`
- Timestamps are in minutes, seconds, and hundredths of a second.

> **Note:** If no lyrics are found, a placeholder message is shown instead.

---

## Commands

### Global Options

| Option | Description |
|--------|-------------|
| `--version`, `-v` | Show the version and exit |
| `--help` | Show help message and exit |

---

### `logo`

Display the Rhythmsync logo.

```
rhythmsync logo [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `-s` | Display the small logo |
| `-l` | Display the large logo |

> **Note:** Options `-s` and `-l` are mutually exclusive. Choose only one.

**Examples:**

```
rhythmsync logo          # Show logo (automatic based on terminal size)
rhythmsync logo -s       # Show small logo
rhythmsync logo -l       # Show large logo
```

---

### `play`

Play audio files, directories, or playlists.

```
rhythmsync play [OPTIONS] PATH
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `PATH` | Audio file, folder, or `.mpl` playlist |

**Options:**

| Option | Description |
|--------|-------------|
| `-d` | Play all audio files in directory (non‑recursive) |
| `-r` | Play all audio files in directory (recursive) |
| `-p` | Play `.mpl` playlist |

> **Note:** Options `-d`, `-r`, and `-p` are mutually exclusive. Choose only one.

**Examples:**

```
rhythmsync play song.mp3                 # Play a single file
rhythmsync play -d ~/Music/              # Play all audio files in directory
rhythmsync play -r ~/Music/              # Play all audio files in directory recursively
rhythmsync play -p playlist.mpl          # Play a playlist
```

---

### `info`

Display metadata from an audio file.

```
rhythmsync info [OPTIONS] FILE [TAGS]...
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `FILE` | Audio file to inspect |
| `TAGS` | (Optional) Specific tags to display |

**Examples:**

```
rhythmsync info song.mp3                 # Display all metadata
rhythmsync info song.mp3 artist title    # Display only artist and title
```

---

### `convert`

Convert an audio file to another format.

```
rhythmsync convert INPUT OUTPUT
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `INPUT` | Input file path |
| `OUTPUT` | Output file path |

**Example:**

```
rhythmsync convert input.flac output.ogg
```

---

### `embed`

Embed `.lrc` (lyrics) files into audio files.

```
rhythmsync embed [OPTIONS] PATH
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `PATH` | Audio file or directory |

**Options:**

| Option | Description |
|--------|-------------|
| `-d` | Embed LRC into all audio files in directory |

**Examples:**

```
rhythmsync embed song.mp3                 # Embed LRC for single file
rhythmsync embed -d ~/Music/              # Embed LRC for all files in directory
```

---

### `playlist`

Manage `.mpl` playlists.

#### `playlist create`

Create a new playlist from audio files.

```
rhythmsync playlist create OUTPUT_PATH FILES... [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `OUTPUT_PATH` | Output `.mpl` file path |
| `FILES` | Audio files to include (can specify multiple) |

**Options:**

| Option | Description |
|--------|-------------|
| `--name, -n` | Playlist name (default: filename stem) |

**Example:**

```
rhythmsync playlist create my_playlist.mpl song1.mp3 song2.flac -n "My Playlist"
```

---

#### `playlist load`

Load and display the tracks from a playlist.

```
rhythmsync playlist load PATH
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `PATH` | `.mpl` file to load |

**Example:**

```
rhythmsync playlist load my_playlist.mpl
```

---

#### `playlist repair`

Repair missing or moved tracks in a playlist.

```
rhythmsync playlist repair PATH SEARCH_DIRS...
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `PATH` | `.mpl` file to repair |
| `SEARCH_DIRS` | Directories to search for missing files (can specify multiple) |

**Example:**

```
rhythmsync playlist repair my_playlist.mpl ~/Music/ ~/Downloads/
```

---

#### `playlist delete`

Delete a playlist.

```
rhythmsync playlist delete [OPTIONS] PATH
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `PATH` | `.mpl` file to delete |

**Options:**

| Option | Description |
|--------|-------------|
| `-f` | Skip confirmation prompt |

**Examples:**

```
rhythmsync playlist delete my_playlist.mpl      # Prompts for confirmation
rhythmsync playlist delete -f my_playlist.mpl   # Deletes without confirmation
```

---

## Notes

- **Paths with spaces:** Must be wrapped in quotes or escaped with backslashes:
  ```
  rhythmsync play "My Music/song.mp3"
  rhythmsync play My\ Music/song.mp3
  ```

- **FFmpeg dependency:** The `convert` command uses FFmpeg and may alter or corrupt metadata.

- **Stopping playback:** Use `Ctrl+C` to stop playback.