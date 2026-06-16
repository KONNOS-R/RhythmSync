import os
from rich.console import Console
console = Console()
from pathlib import Path
from random import shuffle
import shlex

import rhythmsync.player as player
import rhythmsync.metadata as metadata
import rhythmsync.converter as converter
import rhythmsync.terminal_disp as terminal_disp
import playlists.mpl.core as mpl


# resets the cli
def reset_cli():
    terminal_disp.clear_screen()
    terminal_disp.logo()


# supported extensions
def is_audio_file(file_path: Path):
    return file_path.is_file() and file_path.suffix.lower() in (".mp3", ".flac", ".wav", ".ogg")


# returns audio files in dir
def get_audio_files(file_path: Path, recursive: bool = False):
    if recursive:
        files = file_path.rglob("*")
    else:
        files = file_path.iterdir()

    return sorted([f for f in files if is_audio_file(f)])


# command parser
def parse_command(raw_command):
    if not raw_command.strip():
        return

    command = shlex.split(raw_command)
    cmd = command[0]
    command_parts = len(command)


    # help command
    if cmd == "help" and command_parts == 1:
        terminal_disp.help_msg()


    # list command
    elif cmd == "ls":

        if command_parts == 1:
            console.print(f"[blue]{'   '.join(sorted(os.listdir()))}", highlight=False)

        elif command_parts == 2:
            directory = Path(command[1]).expanduser().resolve()

            if directory.exists():
                console.print(f"[blue]{'   '.join(sorted(os.listdir(directory)))}", highlight=False)
            else:
                print("Please enter a valid path.")

        else:
            print("Please enter valid parameters.")


    # change directory command
    elif cmd == "cd" and command_parts == 2:
        directory = Path(command[1]).expanduser().resolve()

        if directory.exists():
            os.chdir(directory)
        else:
            print("Please enter a valid path.")


    # clear command
    elif cmd == "clear" and command_parts == 1:
        reset_cli()


    # play command
    elif cmd == "play":

        if command_parts == 2:
            # file mode
            file_path = Path(command[1]).expanduser().resolve()

            if not file_path.exists() and not is_audio_file(file_path):
                print("Please enter a valid file path.")
                return

            player.run_player([file_path])
            reset_cli()


        elif command_parts == 3:

            par = command[1]
            file_path = Path(command[2]).expanduser().resolve()

            if not file_path.exists():
                print("Please enter a valid file path.")
                return

            # directory mode (non-recursive)
            elif par == "-d" and file_path.is_dir():
                audio_files = get_audio_files(file_path, recursive=False)

                if not audio_files:
                    print("No valid audio files.")
                    return

                player.run_player(audio_files)
                reset_cli()


            # directory mode (recursive)
            elif par == "-D" and file_path.is_dir():
                audio_files = get_audio_files(file_path, recursive=True)

                if not audio_files:
                    print("No valid audio files.")
                    return

                player.run_player(audio_files)
                reset_cli()


            # playlist mode
            elif par == "-p" and file_path.suffix == ".mpl":
                audio_files = mpl.load_playlist(str(file_path))

                if not audio_files:
                    print("No valid audio files.")
                    return

                player.run_player(audio_files)
                reset_cli()


            # invalid parameters
            else:
                print("Please enter valid parameters.")

        else:
            print("Please enter a valid file path and parameters.")


    # info command
    elif cmd == "info":

        if command_parts >= 2:
            file_path = Path(command[1]).expanduser().resolve()
            tags = tuple(command[2:]) or None

            if file_path.exists():
                file_info =  metadata.get_metadata(file_path, tags)

                if file_info:
                    console.print(file_info, highlight=False)

            else:
                print("Please enter a valid file path.")

        else:
            print("Please enter a valid file path and parameters.")


    # playlist command
    elif cmd == "playlist" and command_parts == 3:

        par = command[1]
        path = command[2]

        # create playlist
        if par == "-c":
            pass

        # edit playlist
        elif par == "-e":
            pass

        # delete playlist
        elif par == "-d":
            pass


    # convert command
    elif cmd == "convert" and command_parts == 3:

        input_path = Path(command[1]).expanduser().resolve()
        output_path = Path(command[2]).expanduser().resolve()
        output_dir = output_path.parent

        if input_path.exists() and output_dir.exists():
            converter.convert(input_path, output_path)
        else:
            print("Please enter valid file paths.")


    # invalid command           
    else:
        print("Invalid command! Enter 'help' to display command list.")