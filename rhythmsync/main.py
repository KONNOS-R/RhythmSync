import os
import typer
from pathlib import Path
from typing import List
from rich.console import Console
from typing import Optional
console = Console()

from mpl import core as mpl

import rhythmsync.player as player
import rhythmsync.metadata as metadata
import rhythmsync.converter as converter
import rhythmsync.terminal_disp as terminal_disp
import rhythmsync.lrc_embedder as lrc_embedder


# Helper functions
def is_audio_file(file_path: Path) -> bool:
    return file_path.is_file() and file_path.suffix.lower() in (".mp3", ".flac", ".wav", ".ogg")


def get_audio_files(file_path: Path, recursive: bool = False) -> List[Path]:
    try:
        files = file_path.rglob("*") if recursive else file_path.iterdir()

    except PermissionError:
        terminal_disp.error_msg("Permission denied when reading directory.")
        return []
    return sorted([f for f in files if is_audio_file(f)])


def mpl_msg_handler(level: str, msg: str) -> None:
    if level == "warning":
        console.print(f"[yellow]{msg}[/yellow]")
    elif level == "info":
        console.print(f"[green]{msg}[/green]")
    elif level == "error":
        terminal_disp.error_msg(msg, "Playlist")
    else:
        console.print(msg)


# main app
app = typer.Typer()


# --version flag
def version_callback(value: bool):
    if value:
        version = "1.2.0"
        console.print(f"Rhythmsync version: [green]{version}[/green]")
        raise typer.Exit()


# rhythmsync callback
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        is_flag=True,
        help="Show the version and exit.",
    ),
):
    """
    Rhythmsync: CLI Music Player
    """

    if ctx.invoked_subcommand is None:
        terminal_disp.logo()


# Commands

# logo command
@app.command()
def logo(
    small: bool = typer.Option(False, "-s", help="Small logo"),
    large: bool = typer.Option(False, "-l", help="Large logo")
):
    """Display the rhythmsync logo."""

    try:
        options = [small, large]

        if sum(options) > 1:
            raise ValueError("Multiple options (-s, -l) selected. Choose only one!")
    
        if small:
            terminal_disp.logo("small")
        elif large:
            terminal_disp.logo("large")
        else:
            terminal_disp.logo()

    except Exception as e:
        terminal_disp.error_msg(f"Failed to display logo: {e}")
        raise typer.Exit(1)


# play command
@app.command()
def play(
    path: Path = typer.Argument(..., resolve_path=True, help="Audio file, folder, or .mpl playlist"),
    dir_mode: bool = typer.Option(False, "-d", help="Play all audio files in directory (non-recursive)"),
    dir_rec_mode: bool = typer.Option(False, "-D", help="Play all audio files in directory (recursive)"),
    playlist_mode: bool = typer.Option(False, "-p", help="Play .mpl playlist"),
):
    """Play an audio file, a directory of files, or a .mpl playlist."""

    try:
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        modes = [dir_mode, dir_rec_mode, playlist_mode]

        if sum(modes) > 1:
            raise ValueError("Multiple modes (-d, -D, -p) selected. Choose only one!")

        audio_files = []

        if playlist_mode:
            if path.suffix.lower() != ".mpl":
                raise ValueError("Playlist must have a .mpl extension.")
        
            audio_files = mpl.load_playlist(str(path), msg_callback=mpl_msg_handler)

        elif dir_mode or dir_rec_mode:
            if not path.is_dir():
                raise ValueError("Path must be a directory when using directory modes (-d, -D).")
            
            audio_files = get_audio_files(path, recursive=dir_rec_mode)

        else:
            # single file mode
            if not is_audio_file(path):
                raise ValueError("Unsupported or invalid file.")
            
            audio_files = [path]

        if not audio_files:
            raise ValueError("No supported audio files found.")

        try:
            player.run_player(audio_files)
            console.print("Exiting player...", highlight=False)

        except Exception as e:
            terminal_disp.error_msg(e, "Playback")

    except Exception as e:
        terminal_disp.error_msg(e)
        raise typer.Exit(1)


# info command
@app.command()
def info(
    file: Path = typer.Argument(..., resolve_path=True, help="Audio file to inspect"),
    tags: List[str] = typer.Argument(None, help="Specific tags to display (optional)")
):
    """Display metadata for an audio file."""

    try:
        if not file.exists():
            raise FileNotFoundError(f"File does not exist: {file}")

        file_info = metadata.get_metadata(file, tags)

        if file_info:
            console.print(file_info, highlight=False)
        else:
            console.print("[yellow]No metadata found for this file.[/yellow]")

    except Exception as e:
        terminal_disp.error_msg(f"Failed to read metadata: {e}")
        raise typer.Exit(1)


# convert command
@app.command()
def convert(
    input: Path = typer.Argument(..., resolve_path=True, help="Input audio file"),
    output: Path = typer.Argument(..., resolve_path=True, help="Output file")
):
    """Convert an audio file."""

    try:
        if not input.exists():
            raise FileNotFoundError(f"Input file does not exist: {input}")

        output_dir = output.parent

        if not output_dir.exists():
            raise FileNotFoundError("Output directory does not exist.")

        converter.convert(input, output)
        console.print("[green]Conversion complete.[/green]")

    except typer.Exit:
        raise
    
    except Exception as e:
        terminal_disp.error_msg(f"Conversion failed: {e}")
        raise typer.Exit(1)


@app.command("embed")
def embed_lrc(
    path: Path = typer.Argument(..., resolve_path=True, help="Input audio file"),
    dir_mode: bool = typer.Option(False, "-d", help="Embed lrc to all audio files in directory")
):
    """Embed .lrc files into audio files."""

    try:
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if dir_mode:
            lrc_embedder.embed_lrc(path, True)
        else:
            lrc_embedder.embed_lrc(path, False)

    except Exception as e:
        terminal_disp.error_msg(e)
        raise typer.Exit(1)


# playlist subcommands
playlist_app = typer.Typer(help="Manage .mpl playlists")
app.add_typer(playlist_app, name="playlist")


# playlist create command
@playlist_app.command("create")
def playlist_create(
    output_path: Path = typer.Argument(..., resolve_path=True, help="Output .mpl file path"),
    files: List[Path] = typer.Argument(..., help="Audio files to include"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Playlist name (default: filename stem)"),
):
    """Create a new playlist from the given audio files."""

    try:
        console.print("[blue]Creating playlist...[/blue]")

        file_paths = [f.resolve() for f in files]
        created = mpl.create_playlist(
            output_path,
            file_paths,
            playlist_name=name,
            msg_callback=mpl_msg_handler,
        )

        console.print(f"[bold green]Playlist created:[/bold green] {created}", highlight=False)

    except Exception as e:
        terminal_disp.error_msg(e)
        raise typer.Exit(1)


#playlist repair command
@playlist_app.command("repair")
def playlist_repair(
    path: Path = typer.Argument(..., resolve_path=True, help=".mpl file to repair"),
    search_dirs: List[Path] = typer.Argument(
        ..., help="Directories to search for missing files (can give multiple)"
    ),
):
    """Repair missing or moved tracks path."""

    try:
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        console.print("[blue]Starting playlist repair...[/blue]")

        dir_strings = [str(d.resolve()) for d in search_dirs]

        repaired = mpl.repair_playlist(
            path,
            dir_strings,
            msg_callback=mpl_msg_handler,
        )

        console.print(f"[bold green]Repair completed:[/bold green] {repaired} track(s) fixed", highlight=False)

    except Exception as e:
        terminal_disp.error_msg(e)
        raise typer.Exit(1)


# playlist load command
@playlist_app.command("load")
def playlist_load(
    path: Path = typer.Argument(..., resolve_path=True, help=".mpl file to load"),
):
    """Load and display the tracks from a playlist."""

    try:
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        track_paths = mpl.load_playlist(path, msg_callback=mpl_msg_handler)

        if not track_paths:
            return

        console.print(f"[bold cyan]Playlist contains {len(track_paths)} track(s):[/bold cyan]")
        for idx, track in enumerate(track_paths, start=1):
            console.print(f"  [bold]{idx}.[/bold] {track}", highlight=False)
    
    except Exception as e:
        terminal_disp.error_msg(e)
        raise typer.Exit(1)



# playlist delete command
@playlist_app.command("delete")
def playlist_delete(
    path: Path = typer.Argument(..., resolve_path=True, help=".mpl file to delete"),
    force: bool = typer.Option(False, "-f", help="Skip confirmation"),
):
    """Delete a playlist."""

    try:
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete '{path}'?")
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return

        os.remove(path)

        console.print(f"[bold green]Deleted:[/bold green] {path}", highlight=False)

    except Exception as e:
        terminal_disp.error_msg(e)
        raise typer.Exit(1)


# main
def main():
    app()


# entry point
if __name__ == "__main__":
    main() 