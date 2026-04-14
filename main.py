import time
import mutagen
from mutagen import File
import pygame
from rich.console import Console
from rich.progress import Progress
import os
from re import match


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def format_lrc(lrc_data):
    timestamp = r"^\[\d{2}:\d{2}\.\d{2}\]"
    lrc_lines = lrc_data.split("\n")
    print([line for line in lrc_lines if match(timestamp, line)])


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

    with Progress() as progress:
        playback = progress.add_task(f"[green]Playing '{file_path}'", total=total_length)

        try:
            while pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos() / 1000
                progress.update(playback, advance=0.1)

                

                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            clear_screen()
            console.print("[yellow]Playback interrupted.[/yellow]")


if __name__ == "__main__":
    main()