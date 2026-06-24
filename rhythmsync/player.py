import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from rich.live import Live
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from mutagen import File
import sys
import termios
import tty
import select
from random import shuffle

import rhythmsync.metadata as metadata
import rhythmsync.terminal_disp as terminal_disp


# creates rich layout
def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="main", ratio=1),
        Layout(name="player", size=1),
        Layout(name="footer", size=1)
    )
    return layout


# header section
def make_header(title, artist, header_info):
    content = Group(Align.center(f"[bold]{title}"), Align.center(f"[#5900ab]{artist}"))
    
    now, total, s_icon, r_icon = header_info

    header_title = f"{s_icon}{r_icon}Playing {now} of {total}"

    return Panel(content, title=header_title, title_align="right", style="white")


# lyrics section
def make_lyrics(lyrics, index, window=2):
    # no lyrics msg
    if lyrics == None:
        return Align.center("No lyrics to display", vertical="middle")

    # get lyric lines list
    lyrics_lines = []

    for offset in range(-window, window + 1):
        idx = index + offset

        if 0 <= idx < len(lyrics):
            lyrics_lines.append(lyrics[idx][1])
        else:
            lyrics_lines.append("")

    # styles
    LYRIC_STYLES = {
        "prev2": "[#1f1f1f][not bold]{}[/not bold][/#1f1f1f]",
        "prev1": "[#2f2f2f][not bold]{}[/not bold][/#2f2f2f]",
        "current": "[#00d0ff][bold]{}[/bold][/#00d0ff]",
        "next1": "[#ffffff][not bold]{}[/not bold][/#ffffff]",
        "next2": "[#afafaf][not bold]{}[/not bold][/#afafaf]"
    }

    # format lyric lines list
    middle_idx = len(lyrics_lines) // 2
    styled_lines = []
    
    for i, line in enumerate(lyrics_lines):
        if not line:
            styled_lines.append(Align.center(" "))
            continue
            
        distance = i - middle_idx
        
        if distance == 0:
            style = LYRIC_STYLES["current"]
        elif distance == -1:
            style = LYRIC_STYLES["prev1"]
        elif distance == -2:
            style = LYRIC_STYLES["prev2"]
        elif distance == 1:
            style = LYRIC_STYLES["next1"]
        elif distance == 2:
            style = LYRIC_STYLES["next2"]

        styled_lines.append(Align.center(style.format(line)))
    
    return Align.center(Group(*styled_lines), vertical="middle")


# file info section
def make_file_info(info):
    return Align.center(Group(
            Align.center(f"[#00d0ff][bold]File Info:\n"),
            Align.center(f"[white][bold]Title: [not bold]{info['title']}"),
            Align.center(f"[white][bold]Artist: [not bold]{info['artist']}"),
            Align.center(f"[white][bold]Album: [not bold]{info['album']}"),
            Align.center(f"[white][bold]Genre: [not bold]{info['genre']}"),
            Align.center(f"[white][bold]Date: [not bold]{info['date']}"),
            Align.center(f"[white][bold]Sample Rate: [not bold]{info['sample_rate']}")
        ),
        vertical="middle"
    )


# player section
def make_player():
    return Progress(
        TextColumn("{task.description}[/]", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.fields[suffix]}", justify="right"),
    )


# footer section
def make_footer(file_path: str):
    prefix = "[bold][#5900ab]R[#4f17b4]h[#452ebd]y[#3b45c7]t[#315cd0]h[#2773d9]m[#1d8ae3]S[#13a1ec]y[#09b8f5]n[#00d0ff]c[white][not bold] | "

    length = len(file_path)
    width = os.get_terminal_size()[0]

    if length > width - 13:
        new_length = max(0, width - 13 - 3)
        displayed_path = "..." + file_path[length - new_length:]
    else:
        displayed_path = file_path

    return Align.center(f"{prefix}{displayed_path}")


# gets the total length of the audio file
def get_duration(file_path):
    audio = File(file_path)

    return int(audio.info.length * 1000) 


# formats milliseconds -> mm:ss.xx
def format_time(milliseconds):
    min = int((milliseconds // 1000) // 60)
    sec = (milliseconds // 1000) % 60
    mil = milliseconds % 1000
    hund = int(mil // 10)

    return f"{min:02}:{sec:02}.{hund:02}"


# formats mm:ss.xx -> milliseconds
def unformat_time(time_str):
    min, sec = time_str.split(":")
    sec, hund = sec.split(".")
    milliseconds = (
        int(min) * 60 * 1000 + int(sec) * 1000 + int(hund) * 10)
    
    return milliseconds


# creates random order for shuffle
def shuffled_indices(n, x = None):   
    if x != None: 
        numbers = [i for i in range(n) if i != x]
        shuffle(numbers)
        numbers.insert(x, x)
    else:
        numbers = [i for i in range(n)]
        shuffle(numbers)

    return numbers


# music player
def run_player(audio_files):
    player_loop = True
    
    repeat = False

    shuffled = False

    index = 0

    # initialize pygame
    pygame.init()
    clock = pygame.time.Clock()
    pygame.mixer.init()

    while player_loop:
        try:
            running = True
            
            file_path = audio_files[index]

            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            tty.setcbreak(fd)

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            total_length = get_duration(file_path)

            title, artist = metadata.get_ti_ar(file_path)

            lyrics = metadata.get_lrc(file_path)

            lyrics_exist = True if lyrics != None else False

            lyric_index = 0

            main_status = "lyrics" if lyrics_exist else "info"

            paused = False

            # prepare layout
            terminal_disp.clear_screen()

            layout = make_layout()

                # header
            if not repeat:
                r_icon = ""
            elif repeat == "all":
                r_icon = "🗘 "
            elif repeat == "single":
                r_icon = "⟲ "

            if shuffled:
                s_icon = "🔀︎"
            else:
                s_icon = ""

            layout["header"].update(make_header(title, artist, (index + 1, len(audio_files), s_icon, r_icon)))

                # main
            if main_status == "lyrics":
                layout["main"].update(make_lyrics(lyrics, lyric_index))
            elif main_status == "info":
                layout["main"].update(make_file_info(metadata.get_info(file_path)))

                # player
            progress = make_player()
            layout["player"].update(progress)

                # footer
            layout["footer"].update(make_footer(str(file_path)))

            # start player
            with Live(layout, refresh_per_second=100):

                playback = progress.add_task(
                    f"[red]<[/red]",
                    total=total_length,
                    suffix="[red]>[/red]"
                )

                while running:

                    current_time = pygame.mixer.music.get_pos()

                    # keyboard input
                    ready, _, _ = select.select([sys.stdin], [], [], 0)

                    if ready:
                        key = sys.stdin.read(1)

                        if key == " ":
                            if paused:
                                pygame.mixer.music.unpause()
                                paused = False

                            else:
                                progress.update(
                                    playback,
                                    completed=current_time,
                                    description=f"[red]<[/red] ▸ [#00d0ff]{format_time(current_time)}",
                                    suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>[/red]"
                                )
                                pygame.mixer.music.pause()
                                paused = True

                        #ESC seq
                        elif key == "\x1b":
                            seq = sys.stdin.read(2)

                            # LEFT arrow
                            if seq == "[D":
                                if shuffled:
                                    if i > 0:
                                        i -= 1
                                    else:
                                        i = len(audio_files) - 1

                                    index = shuffled_order[i]

                                elif index > 0:
                                    index -= 1
                                else:
                                    index = len(audio_files) - 1
                                running = False

                            #RIGHT arrow
                            elif seq == "[C":
                                if shuffled:
                                    if i < len(audio_files) - 1:
                                        i += 1

                                    else:
                                        if repeat == "all":
                                            shuffled_order = shuffled_indices(len(audio_files))
                                            i = 0
    
                                        else:
                                            i = 0

                                    index = shuffled_order[i]
    
                                elif index < len(audio_files) - 1:
                                    index += 1

                                else:
                                    index = 0
                                running = False

                        elif key in "Ii":
                            if main_status == "lyrics":
                                main_status = "info"

                                layout["main"].update(make_file_info(metadata.get_info(file_path)))

                            elif main_status == "info":
                                main_status = "lyrics"

                                layout["main"].update(make_lyrics(lyrics, lyric_index))

                        elif key in "Rr":
                            if not repeat:
                                repeat = "all"
                                r_icon = "🗘 "

                            elif repeat == "all":
                                repeat = "single"
                                r_icon = "⟲ "

                            elif repeat == "single":
                                repeat = False
                                r_icon = ""

                        elif key in "Ss":
                            if shuffled:
                                shuffled_order = None
                                i = None
                                shuffled = False
                                s_icon = ""

                            else:
                                shuffled_order = shuffled_indices(len(audio_files), index)
                                i = index
                                shuffled = True
                                s_icon = "🔀︎"


                    if not paused:
                        if lyrics_exist and lyric_index < len(lyrics) - 1 and main_status == "lyrics" and unformat_time(lyrics[lyric_index + 1][0]) <= current_time:
                            lyric_index += 1

                            layout["main"].update(make_lyrics(lyrics, lyric_index))

                        progress.update(
                            playback,
                            completed=current_time,
                            description=f"[red]<[/red] ⏸ [#00d0ff]{format_time(current_time)}",
                            suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>[/red]"
                        )
                        

                    if not(pygame.mixer.music.get_busy() or paused):

                        if repeat == "single":
                            pass

                        elif shuffled:
                            if i < len(audio_files) - 1:
                                i += 1

                            else:
                                if repeat == "all":
                                    shuffled_order = shuffled_indices(len(audio_files))
                                    i = 0
                                else:
                                    raise KeyboardInterrupt

                            index = shuffled_order[i]
                            
                        elif index < len(audio_files) - 1:
                            index += 1

                        else:
                            if repeat == "all":
                                index = 0
                            else:
                                raise KeyboardInterrupt
                            
                        running = False


                    layout["header"].update(make_header(title, artist, (index + 1, len(audio_files), s_icon, r_icon)))

                    layout["footer"].update(make_footer(str(file_path)))

                    clock.tick(100)

        except KeyboardInterrupt:
            print("Exiting...")
            player_loop = False
            pygame.mixer.music.stop()

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
            terminal_disp.clear_screen()

    # quit pygame
    pygame.mixer.quit()
    pygame.quit()