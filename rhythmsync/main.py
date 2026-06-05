import os
import sys
import termios
import tty
import signal
import re

import rhythmsync.terminal_disp as terminal_disp
import rhythmsync.command_parser as command_parser


# capture key strokes
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    return ch


# history redraw logic
def redraw_input(prompt, buffer):
    global last_rendered_lines

    cols = os.get_terminal_size().columns
    full = prompt + buffer

    lines = max(1, (len(full) // cols) + 1)

    for _ in range(last_rendered_lines - 1):
        sys.stdout.write("\x1b[F")

    for i in range(last_rendered_lines):
        sys.stdout.write("\r\x1b[2K")

        if i < last_rendered_lines - 1:
            sys.stdout.write("\x1b[E")

    for _ in range(last_rendered_lines - 1):
        sys.stdout.write("\x1b[F")

    sys.stdout.write("\r" + full)
    sys.stdout.flush()

    last_rendered_lines = lines


# path autocompletion
def complete_path(text: str) -> str:
    if not text:
        return text

    escape_chars_re = re.compile(r'([ \t\n\r\f\v\\\'\"&|()<>!*?~])')

    def escape_path(path: str) -> str:
        return escape_chars_re.sub(r'\\\1', path)

    def unescape_path(path: str) -> str:
        return path.replace('\\', '')

    def complete_fragment(fragment):
        raw_path = unescape_path(fragment)
        expanded_path = os.path.expanduser(raw_path)

        breakslash = False
        
        dir_name, prefix = os.path.split(expanded_path)
        if not dir_name:
            dir_name = "."

        try:
            entries = list(os.scandir(dir_name))
        except OSError:
            return None

        matches = [e.name for e in entries if e.name.startswith(prefix)]
        if not matches:
            return None

        if len(matches) == 1:
            chosen_name = matches[0]
        else:
            common = os.path.commonprefix(matches)
            if not common or common == prefix:
                return None
            chosen_name = common
            breakslash = True

        completed = os.path.join(dir_name, chosen_name)
        
        if os.path.isdir(completed) and not breakslash:
            completed += os.sep

        return escape_path(completed)

    parts = re.split(r'(?<!\\) ', text)
    
    if parts:
        last_part = parts[-1]
        completed = complete_fragment(last_part)
        
        if completed:
            base = " ".join(parts[:-1])
            return f"{base} {completed}".strip()

    return text


# cli input
def input_cli(prompt="> "):
    global history_index

    buffer = ""
    history_index = len(history)
    redraw_input(prompt, buffer)

    while True:
        ch = getch()

        # CTRL+C
        if ch == "\x03":
            print()
            raise KeyboardInterrupt

        # CTRL+Z
        elif ch == "\x1a":
            print("\n[Suspended]")
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))

            os.kill(os.getpid(), signal.SIGTSTP)

        # ENTER
        elif ch == "\r" or ch == "\n":
            print()
            if buffer.strip():
                history.append(buffer)
            return buffer

        # BACKSPACE
        elif ch == "\x7f":
            if buffer:
                buffer = buffer[:-1]
                redraw_input(prompt, buffer)

        # TAB
        elif ch == "\t":
            buffer = complete_path(buffer)
            redraw_input(prompt, buffer)

        # ESC Sequences
        elif ch == "\x1b":
            try:
                next1 = getch()
                next2 = getch()
            except Exception:
                continue

            # UP
            if next2 == "A":
                if history:
                    history_index = max(0, history_index - 1)
                    buffer = history[history_index]
                    redraw_input(prompt, buffer)

            # DOWN
            elif next2 == "B":
                if history:
                    history_index = min(len(history) - 1, history_index + 1)
                    buffer = history[history_index]
                    redraw_input(prompt, buffer)

        else:
            buffer += ch
            redraw_input(prompt, buffer)


# main program
def main():
    terminal_disp.clear_screen()

    global history, history_index, last_rendered_lines

    history = []
    history_index = -1
    last_rendered_lines = 1

    terminal_disp.logo()

    while True:
        try:
            command_parser.parse_command(input_cli("> "))
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            terminal_disp.error_msg(e)
            break


# entry point
if __name__ == "__main__":
    main()