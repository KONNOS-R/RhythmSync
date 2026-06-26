from pathlib import Path
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import eyed3
from rich.console import Console
console = Console()

from . import terminal_disp


# embeds lyrics (.lrc) into audio file (.flac, .mp3, .ogg)
def embed_file(audio_path: Path) -> bool:
    lrc_path = audio_path.with_suffix('.lrc')
    if not lrc_path.exists():
        return False

    try:
        with open(lrc_path, 'r', encoding='utf-8') as f:
            lyrics = f.read()

        suffix = audio_path.suffix.lower()
        if suffix == '.flac':
            audio = FLAC(audio_path)
            audio['LYRICS'] = lyrics
            audio.save()

        elif suffix == '.mp3':
            audio = eyed3.load(audio_path)
            if audio.tag is None:
                audio.init_tag()
            audio.tag.lyrics.set(lyrics)
            audio.tag.save(version=eyed3.id3.ID3_V2_3)

        elif suffix == '.ogg':
            audio = OggVorbis(audio_path)
            audio.tags['LYRICS'] = lyrics
            audio.save()

        else:
            return False

        return True

    except Exception as e:
        terminal_disp.error_msg(f"{audio_path.name}: {e}", "LRC Embedding")
        return False


# orchestretes lyrics embedding 
def embed_lrc(path: Path, dir_mode: bool = False):
    path = Path(path)
    embedded_count = 0
    failed_files = []

    AUDIO_EXTENSIONS = ('.flac', '.mp3', '.ogg')

    if not dir_mode:
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            audio_files = [path]
        else:
            terminal_disp.error_msg(f"'{path}' is not a valid audio file.")
            return
        
    else:
        if path.is_dir():
            audio_files = [p for p in path.rglob('*') if p.suffix.lower() in AUDIO_EXTENSIONS]
        else:
            terminal_disp.error_msg(f"'{path}' is not a directory.")
            return

    console.print("[blue]Embedding lyrics...[/blue]")

    for audio_path in audio_files:
        if embed_file(audio_path):
            embedded_count += 1
        else:
            failed_files.append(str(audio_path))

    total = len(audio_files)
    console.print(f"[green]Embedded lyrics in {embedded_count} out of {total} audio files.[/green]")

    if failed_files:
        console.print("[red]Failed to embed LRC for:[/red]")
        for f in failed_files:
            console.print(f"    {f}")