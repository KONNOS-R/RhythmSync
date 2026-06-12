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


# single file modes logic
def player_file(file_path, mode):
    repeat = True

    while repeat:
        result = player.run_player(str(file_path), [mode])
        repeat = result[0]
        
    reset_cli()


# directory and playlist modes logic
def player_directory(files, mode):
    if not files:
        print("No audio files found.")
        return
    
    repeat = True
    i = 1

    if mode in("repeat", "shuffle"):
        while repeat:
            for j in range(i-1, len(files)):
                repeat, i = player.run_player(files[j], ["directory", mode, i, len(files)])
                if i < 1:
                    i = len(files)
                elif i > len(files):
                    i = 1
                break

    else:
        while i-1 < len(files) and i >= 1 and repeat:
            for j in range(i-1, len(files)):
                repeat, i = player.run_player(files[j], ["directory", mode, i, len(files)])
                if i < 1:
                    i = 1
                break
        terminal_disp.clear_screen()
        terminal_disp.logo() 
    
    reset_cli()


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
            file_path = Path(command[1]).expanduser().resolve()

            # single mode
            if is_audio_file(file_path):
                player_file(file_path, "single")
            else:
                print("Please enter a valid file path.")

        elif command_parts == 3:

            par = command[1]
            file_path = Path(command[2]).expanduser().resolve()

            if not file_path.exists():
                print("Please enter a valid file path.")
                return

            # single repeat mode
            elif par == "-r" and is_audio_file(file_path):
                player_file(file_path, "repeat")

            # directory modes
            elif par in ("-d", "-dr", "-ds") and file_path.is_dir():

                directory = file_path
                audio_files = get_audio_files(directory, recursive=False)

                if par == "-d":
                    audio_files.sort()
                    player_directory(audio_files, "single")

                elif par == "-dr":
                    audio_files.sort()
                    player_directory(audio_files, "repeat")

                elif par == "-ds":
                    shuffle(audio_files)
                    player_directory(audio_files, "shuffle")

            # recursive directory modes
            elif par in ("-D", "-Dr", "-Ds") and file_path.is_dir():

                directory = file_path
                audio_files = get_audio_files(directory, recursive=True)

                if par == "-D":
                    audio_files.sort()
                    player_directory(audio_files, "single")

                elif par == "-Dr":
                    audio_files.sort()
                    player_directory(audio_files, "repeat")

                elif par == "-Ds":
                    shuffle(audio_files)
                    player_directory(audio_files, "shuffle")

            # playlist modes
            elif par in ("-p", "-pr", "-ps") and file_path.suffix == ".mpl":

                audio_files = mpl.load_playlist(str(file_path))

                if par == "-p":
                    player_directory(audio_files, "single")

                elif par == "-pr":
                    player_directory(audio_files, "repeat")

                elif par == "-ps":
                    shuffle(audio_files)
                    player_directory(audio_files, "shuffle")

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