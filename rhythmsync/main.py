import typer
from pathlib import Path
from typing import List
from rich.console import Console
console = Console()

import mpl

import rhythmsync.player as player
import rhythmsync.metadata as metadata
import rhythmsync.converter as converter
import rhythmsync.terminal_disp as terminal_disp


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

    options = [small, large]

    if sum(options) > 1:
        terminal_disp.error_msg("Multiple options (-s, -l) selected. Choose only one!")
        raise typer.Exit(1)

    try:
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

    if not path.exists():
        terminal_disp.error_msg(f"Path does not exist: {path}")
        raise typer.Exit(1)
    
    modes = [dir_mode, dir_rec_mode, playlist_mode]

    if sum(modes) > 1:
        terminal_disp.error_msg("Multiple modes (-d, -D, -p) selected. Choose only one!")
        raise typer.Exit(1)

    audio_files = []

    try:
        if playlist_mode:
            if path.suffix.lower() != ".mpl":
                terminal_disp.error_msg("Playlist must have a .mpl extension.")
                raise typer.Exit(1)
            try:
                audio_files = mpl.load_playlist(str(path))
            except Exception as e:
                terminal_disp.error_msg(f"Failed to load playlist: {e}")
                raise typer.Exit(1)

        elif dir_mode or dir_rec_mode:
            if not path.is_dir():
                terminal_disp.error_msg("Path must be a directory when using directory modes (-d, -D).")
                raise typer.Exit(1)
            audio_files = get_audio_files(path, recursive=dir_rec_mode)

        else:
            # Single file mode
            if not is_audio_file(path):
                terminal_disp.error_msg(f"Unsupported or invalid file.")
                raise typer.Exit(1)
            
            audio_files = [path]

        if not audio_files:
            terminal_disp.error_msg("No supported audio files found.")
            raise typer.Exit(1)

        try:
            player.run_player(audio_files)
            console.print("Exiting player...", highlight=False)

        except Exception as e:
            terminal_disp.error_msg(e, "Playback")
            raise typer.Exit(1)

    except typer.Exit:
        raise

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

    if not file.exists():
        terminal_disp.error_msg(f"File does not exist.")
        raise typer.Exit(1)

    try:
        file_info = metadata.get_metadata(file, tags)

    except Exception as e:
        terminal_disp.error_msg(f"Failed to read metadata: {e}")
        raise typer.Exit(1)

    if file_info:
        console.print(file_info, highlight=False)
    else:
        console.print("[yellow]No metadata found for this file.[/yellow]")


# convert command
@app.command()
def convert(
    input: Path = typer.Argument(..., resolve_path=True, help="Input audio file"),
    output: Path = typer.Argument(..., resolve_path=True, help="Output file")
):
    """Convert an audio file."""

    if not input.exists():
        terminal_disp.error_msg(f"Input file does not exist: {input}")
        raise typer.Exit(1)

    output_dir = output.parent

    if not output_dir.exists():
        terminal_disp.error_msg("Output directory does not exist.")
        raise typer.Exit(1)

    try:
        converter.convert(input, output)
        console.print("[green]Conversion complete.[/green]")

    except typer.Exit:
        raise
    
    except Exception as e:
        terminal_disp.error_msg(f"Conversion failed: {e}")
        raise typer.Exit(1)


# playlist subcommands
playlist_app = typer.Typer(help="Manage .mpl playlists")
app.add_typer(playlist_app, name="playlist")


# create playlist command
@playlist_app.command("create")
def playlist_create(name: str):
    """Create a new playlist."""

    try:
        pass
    except Exception as e:
        terminal_disp.error_msg(f"Failed to create playlist: {e}")
        raise typer.Exit(1)


# edit playlist command
@playlist_app.command("edit")
def playlist_edit(name: str):
    """Edit an existing playlist."""

    try:
        pass
    except Exception as e:
        terminal_disp.error_msg(f"Failed to edit playlist: {e}")
        raise typer.Exit(1)


# delete playlist command
@playlist_app.command("delete")
def playlist_delete(name: str):
    """Delete a playlist."""

    try:
        pass
    except Exception as e:
        terminal_disp.error_msg(f"Failed to delete playlist: {e}")
        raise typer.Exit(1)


# main
def main():
    app()


# entry point
if __name__ == "__main__":
    main()