import subprocess
from pathlib import Path
from rich.console import Console
from typing import Dict, List
console = Console()


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
        console.print(f"[bold red]Conversion Error:[/bold red] Input file not found at '{input_file}'")
        return False

    suffix = output_file.suffix.lower()
    codec_args = CODEC_CONFIG.get(suffix)

    if codec_args is None:
        console.print(f"[bold red]Conversion Error:[/bold red] Unsupported output format '{suffix}'.")
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

        console.print(f"[blue]Starting conversion...[/blue]")

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
            console.print(f"\n[bold red]Conversion Error:[/bold red] Conversion failed (Exit Code {process.returncode}).")
            return False

        console.print(f"[green bold]Converted successfully:[/green bold]")
        console.print(f"{input_file.name} -> {output_file.name}")
        return True

    except FileNotFoundError:
        console.print("\n[bold red]System Error:[/bold red] FFmpeg command not found.")
        console.print("[yellow]Please ensure FFmpeg is installed and accessible in your system's PATH.[/yellow]")
        return False

    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]Conversion Error:[/bold red] FFmpeg failed unexpectedly.")
        console.print(f"Details: {e}")
        return False

    except Exception as e:
        console.print(f"\n[bold red]Conversion Error:[/bold red] {e}")
        return False