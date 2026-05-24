import subprocess
from rich.console import Console
console = Console()


# converts audio file to other formats
def convert(input_file, output_file):
    try:
        suffix = output_file.suffix.lower()

        codec_args = []

        if suffix == ".mp3":
            codec_args = [
                "-c:a", "libmp3lame",
                "-b:a", "320k",

                # better compatibility
                "-id3v2_version", "3"
            ]

        elif suffix == ".ogg":
            codec_args = [
                "-c:a", "libvorbis",
                "-q:a", "6"
            ]

        elif suffix == ".flac":
            codec_args = [
                "-c:a", "flac"
            ]

        elif suffix == ".wav":
            codec_args = [
                "-c:a", "pcm_s16le"
            ]

        command = [
            "ffmpeg",

            "-y",

            "-i", str(input_file),

            "-map_metadata", "0",

            "-map", "0:a",

            *codec_args,

            str(output_file)
        ]

        result = subprocess.run(
            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True,

            check=True
        )

        console.print("[green]Converted successfully:")
        console.print(f"{input_file} -> {output_file}")

        return True

    except FileNotFoundError:
        console.print("Conversion error: FFmpeg is not installed.")
        return False

    except subprocess.CalledProcessError as e:
        console.print("Conversion error: Conversion failed.")

        if e.stderr:
            console.print(f"Conversion error: {e.stderr.strip()}")
        return False

    except Exception as e:
        console.print(f"Conversion error: {e}")
        return False