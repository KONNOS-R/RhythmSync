import subprocess
from rich.console import Console
console = Console()


#converts audio file to other formats
def convert(input_file, output_file):
    try:
        subprocess.run([
            "ffmpeg",

            "-y",

            "-i", str(input_file),

            "-map_metadata", "0",

            str(output_file)

        ],

        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,

        check=True
        )

        console.print("[green]Converted successfully:")
        print(f"{input_file} -> {output_file}")

    except FileNotFoundError:
        print("Conversion error: FFmpeg is not installed.")

    except subprocess.CalledProcessError:
        print("Conversion error: Conversion failed.")

    except Exception as e:
        print(f"Conversion error: {e}")