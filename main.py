import time
import mutagen
from mutagen import File
import pygame
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
import os
from re import match


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(milliseconds):
    min = int((milliseconds // 1000) // 60)
    sec = (milliseconds // 1000) % 60
    mil = milliseconds % 1000
    hund = int(mil // 10)
    return f"{min:02}:{sec:02}.{hund:02}"


def format_lrc(lrc_data):
    timestamp = r"^\[\d{2}:\d{2}\.\d{2}\]"
    lrc_lines = lrc_data.split("\n")
    return [line for line in lrc_lines if match(timestamp, line)]


def display_lrc(formatted_lrc):
    pass


def get_lrc_from_audio(file_path):
    try:
        audio = File(file_path)

        if audio is None:
            print(f"Error: Could not open file {file_path}")
            return None

        lrc_tag_names = ['LYRICS', 'UNSYNCEDLYRICS', 'LRC', 'USLT::eng']

        for tag_name in lrc_tag_names:
            if tag_name in audio:
                return audio[tag_name][0]

        return None

    except Exception as e:
        print(f"Error extracting LRC data: {e}")
        return None


#main programme
def main():
    clear_screen()
    console = Console()
    pygame.mixer.init()

    file_path = input("Path to audio file: ")

    try:
        lrc_data = get_lrc_from_audio(file_path)

        if lrc_data:
            lyrics = format_lrc(lrc_data)
        else:
            console.print("[red]No lyrics found in audio file.[/red]")
            lyrics = []

    except Exception as e:
        print(f"Error loading metadata: {e}")
        return None

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Error playing audio file: {e}")
        return None

    total_length = pygame.mixer.Sound(file_path).get_length()

    with Progress(
        TextColumn("{task.description}[/]", justify="right"),
        BarColumn(),
        TextColumn("{task.fields[suffix]}", justify="right")
    ) as progress:

        console.print(lyrics[0])

        playback = progress.add_task(
            f"[green]Playing: [white]'{file_path}' [blue]()",
            total=total_length, 
            suffix="[blue]()")

        try:
            while pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos()
                progress.update(
                    playback, 
                    advance=0.01, 
                    description=f"[green]Playing: [white]'{file_path}' [blue]({format_time(current_time)})",
                    suffix=f"([blue]{format_time(total_length)})")

                

                time.sleep(0.01)

        except KeyboardInterrupt:
            pass
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            clear_screen()
            console.print("[yellow]Playback interrupted.[/yellow]")


if __name__ == "__main__":
    main()