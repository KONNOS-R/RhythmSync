import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from rich.live import Live
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
import sys
import termios
import tty
import select

import rhythmsync.metadata as metadata
import rhythmsync.terminal_disp as terminal_disp


# create rich layout
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
def make_header(title, artist, mode):
    content = Group(Align.center(f"[bold]{title}"), Align.center(f"[#5900ab]{artist}"))
    icons = {"repeat": "⭮ ", "shuffle": "🔀︎"}
    
    header_title = None

    if mode[0] == "repeat":
        header_title = icons["repeat"]

    elif mode[0] == "directory":
        now, total = mode[2:4]
        icon = icons.get(mode[1], "")
        header_title = f"{icon}Playing {now} of {total}".strip()

    return Panel(content, title=header_title, title_align="right", style="white")


# lyrics section
def make_lyrics(lyrics):
    line1, line2, line3, line4, line5 = lyrics
    return Align.center(Group(
            Align.center(f"[#1f1f1f][not bold]{line1}"),
            Align.center(f"[#2f2f2f][not bold]{line2}"),
            Align.center(f"[#00d0ff][bold]{line3}"),
            Align.center(f"[white][not bold]{line4}"),
            Align.center(f"[#afafaf][not bold]{line5}")
            ),
        vertical="middle"
    )


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
def make_footer(file_path):
    return Align.center(f"[bold][#5900ab]Rhythm[#00d0ff]Sync[white][not bold] | {file_path}")


# format time in mm:ss.xx format
def format_time(milliseconds):
    min = int((milliseconds // 1000) // 60)
    sec = (milliseconds // 1000) % 60
    mil = milliseconds % 1000
    hund = int(mil // 10)
    return f"{min:02}:{sec:02}.{hund:02}"


# format time to milliseconds
def unformat_time(time_str):
    min, sec = time_str.split(":")
    sec, hund = sec.split(".")
    milliseconds = (
        int(min) * 60 * 1000 + int(sec) * 1000 + int(hund) * 10)
    return milliseconds


# music player
def run_player(file_path, mode):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        layout = make_layout()

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        total_length = int(pygame.mixer.Sound(file_path).get_length() * 1000)

        title, artist = metadata.get_ti_ar(file_path)

        lyrics_exist = False

        raw_lrc = metadata.get_lrc(file_path)

        if raw_lrc is not None:
            lyrics = metadata.format_lrc(raw_lrc)
            lyrics_exist = True

        lyric_index = 0

        paused = False

        if lyrics_exist:
            main_status = "lyrics"
        else:
            main_status = "info"

        # prepare layout
        terminal_disp.clear_screen()

        layout["header"].update(make_header(title, artist, mode))

        if main_status == "lyrics":
            layout["main"].update(make_lyrics((
                    lyrics[lyric_index - 2][1] if lyric_index > 1 else "",
                    lyrics[lyric_index - 1][1] if lyric_index > 0 else "",
                    lyrics[lyric_index][1],
                    lyrics[lyric_index + 1][1] if lyric_index < len(lyrics) - 1 else "",
                    lyrics[lyric_index + 2][1] if lyric_index < len(lyrics) - 2 else ""
                )))
        elif main_status == "info":
            layout["main"].update(make_file_info(metadata.get_info(file_path)))

        progress = make_player()
        layout["player"].update(progress)

        layout["footer"].update(make_footer(file_path))

        # start player
        with Live(layout, refresh_per_second=100):
            playback = progress.add_task(
                f"[red]< [#00d0ff]",
                total=total_length,
                suffix="[#00d0ff] [red]>"
            )
                
            while pygame.mixer.music.get_busy() or paused:
                current_time = pygame.mixer.music.get_pos()

                # keyboard input
                ready, _, _ = select.select([sys.stdin], [], [], 0)

                if ready:
                    key = sys.stdin.read(1)

                    #SPACE
                    if key == " ":
                        if paused:
                            pygame.mixer.music.unpause()
                            paused = False

                        else:
                            progress.update(
                                playback,
                                completed=current_time,
                                description=f"[red]< [/red]▶ [#00d0ff]{format_time(current_time)}",
                                suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                            )
                            pygame.mixer.music.pause()
                            paused = True

                    #ESC seq
                    elif key == "\x1b":
                            seq = sys.stdin.read(2)

                            # LEFT arrow
                            if seq == "[D":
                                if mode[0] == "single":
                                    pygame.mixer.music.stop()
                                    return (True, 0)
                                
                                elif mode[0] == "repeat":
                                    pygame.mixer.music.stop()
                                    return (True, 0)
                                
                                elif mode[0] == "directory":
                                    pygame.mixer.music.stop()
                                    return (True, int(mode[2])-1)
                                
                            #RIGHT arrow
                            elif seq == "[C":
                                if mode[0] == "single":
                                    pygame.mixer.music.stop()
                                    return (False, 0)
                                elif mode[0] == "repeat":
                                    pygame.mixer.music.stop()
                                    return (True, 0)
                                elif mode[0] == "directory":
                                    pygame.mixer.music.stop()
                                    return (True, int(mode[2])+1)
                                
                    elif key in "Ii":
                        if main_status == "lyrics":
                            main_status = "info"

                            layout["main"].update(make_file_info(metadata.get_info(file_path)))
                            
                        elif main_status == "info":
                            main_status = "lyrics"

                            if lyrics_exist and main_status == "lyrics":
                                layout["main"].update(make_lyrics((
                                    lyrics[lyric_index - 2][1] if lyric_index > 1 else "",
                                    lyrics[lyric_index - 1][1] if lyric_index > 0 else "",
                                    lyrics[lyric_index][1],
                                    lyrics[lyric_index + 1][1] if lyric_index < len(lyrics) - 1 else "",
                                    lyrics[lyric_index + 2][1] if lyric_index < len(lyrics) - 2 else ""
                                )))
                            else:
                                layout["main"].update(Align.center("No lyrics to display", vertical="middle"))
                            
                if not paused:
                    if lyrics_exist and lyric_index < len(lyrics) - 1 and main_status == "lyrics" and unformat_time(lyrics[lyric_index + 1][0]) <= current_time:
                        lyric_index += 1

                        layout["main"].update(make_lyrics((
                            lyrics[lyric_index - 2][1] if lyric_index > 1 else "",
                            lyrics[lyric_index - 1][1] if lyric_index > 0 else "",
                            lyrics[lyric_index][1],
                            lyrics[lyric_index + 1][1] if lyric_index < len(lyrics) - 1 else "",
                            lyrics[lyric_index + 2][1] if lyric_index < len(lyrics) - 2 else ""
                        )))

                    progress.update(
                        playback,
                        completed=current_time,
                        description=f"[red]< [/red]⏸ [#00d0ff]{format_time(current_time)}",
                        suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                    )

            if mode[0] == "single":
                return (False, 0)
            if mode[0] == "repeat":
                return (True, 0)
            elif mode[0] == "directory":
                return (True, int(mode[2])+1)
            
    except KeyboardInterrupt:
        print("Exiting...")
        pygame.mixer.music.stop()
        return (False, 0)
    
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        terminal_disp.clear_screen()