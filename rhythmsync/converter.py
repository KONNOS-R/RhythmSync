import subprocess
from pathlib import Path
from typing import Dict, List
from rich.console import Console
console = Console()

import rhythmsync.terminal_disp as terminal_disp


# converts audio file to another format
def convert(input_file: Path, output_file: Path) -> bool:
    CODEC_CONFIG: Dict[str, List[str]] = {
        ".mp3": [
            "-c:a", "libmp3lame",
            "-b:a", "320k",
            "-id3v2_version", "3"
        ],
        ".ogg": [
            "-c:a", "libvorbis",
            "-q:a", "6"
        ],
        ".flac": [
            "-c:a", "flac"
        ],
        ".wav": [
            "-c:a", "pcm_s16le"
        ]
    }

    if not input_file.exists():
        terminal_disp.error_msg(f"Input file not found at '{input_file}'", "Conversion")
        return False

    suffix = output_file.suffix.lower()
    codec_args = CODEC_CONFIG.get(suffix)

    if codec_args is None:
        terminal_disp.error_msg(f"Unsupported output format '{suffix}'", "Conversion")
        return False

    try:
        command = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-map_metadata", "0",
            "-map", "0:a",
            *codec_args,
            str(output_file)
        ]

        console.print("[blue]Starting conversion...[/blue]")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )

        output = []
        while True:
            line = process.stdout.readline()
            if not line:
                break
            output.append(line)

        process.wait()

        if process.returncode != 0:
            error_log = "\n".join(output[-15:])
            terminal_disp.error_msg(f"Conversion failed (Exit Code {process.returncode})", "Conversion")
            return False

        console.print(f"[green bold]Converted successfully:[/green bold]")
        console.print(f"{input_file.name} -> {output_file.name}")
        return True

    except FileNotFoundError:
        terminal_disp.error_msg(f"FFmpeg not found.\n[yellow]Please ensure FFmpeg is installed and accessible in your system's PATH.[/yellow]", "Conversion")
        return False

    except subprocess.CalledProcessError as e:
        terminal_disp.error_msg(f"FFmpeg failed unexpectedly.\nDetails: {e}", "Conversion")
        return False

    except Exception as e:
        terminal_disp.error_msg(e, "Conversion")
        return False