import os
from rich.console import Console
console = Console()
from rich.align import Align


# gradient
def hex_gradient(color1, color2, steps):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(rgb):
        return  f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    steps_r = (rgb2[0] - rgb1[0]) / (steps - 1)
    steps_g = (rgb2[1] - rgb1[1]) / (steps - 1)
    steps_b = (rgb2[2] - rgb1[2]) / (steps - 1)

    gradient = []
    for i in range(steps):
        r = int(rgb1[0] + steps_r * i)
        g = int(rgb1[1] + steps_g * i)
        b = int(rgb1[2] + steps_b * i)
        gradient.append(rgb_to_hex((r, g, b)))
    
    return gradient


# clear the terminal
def clear_screen():
    os.system('clear')


# print logo
def logo(option = None):
    small_logo = r'''
 _____  _           _   _                _____                  
|  __ \| |         | | | |              / ____|                 
| |__) | |__  _   _| |_| |__  _ __ ___ | (___  _   _ _ __   ___ 
|  _  /| '_ \| | | | __| '_ \| '_ ` _ \ \___ \| | | | '_ \ / __|
| | \ \| | | | |_| | |_| | | | | | | | |____) | |_| | | | | (__ 
|_|  \_\_| |_|\__, |\__|_| |_|_| |_| |_|_____/ \__, |_| |_|\___|
               __/ |                            __/ |           
              |___/                            |___/            
'''
        
    large_logo = r'''
 /███████  /██                   /██     /██                      /██████                               
| ██__ '██| ██                  | ██    | ██                     /██__ '██                              
| ██  \ ██| ███████  /██   /██ /██████  | ███████  /██████/████ | ██  \__/ /██   /██ /███████   /███████
| ███████/| ██__ '██| ██  | ██|_ '██_/  | ██__ '██| ██_ '██_ '██|  ██████ | ██  | ██| ██__ '██ /██_____/
| ██__ '██| ██  \ ██| ██  | ██  | ██    | ██  \ ██| ██ \ ██ \ ██ \____ '██| ██  | ██| ██  \ ██| ██      
| ██  \ ██| ██  | ██| ██  | ██  | ██ /██| ██  | ██| ██ | ██ | ██ /██  \ ██| ██  | ██| ██  | ██| ██      
| ██  | ██| ██  | ██|  ███████  | '████/| ██  | ██| ██ | ██ | ██| '██████/|  ███████| ██  | ██| '███████
|__/  |__/|__/  |__/ \____ '██   \___/  |__/  |__/|__/ |__/ |__/ \______/  \____ '██|__/  |__/ \_______/
                     /██  | ██                                             /██  | ██                    
                    | '██████/                                            | '██████/                    
                     \______/                                              \______/                     
'''

    if option == "small":
        displayed_logo = small_logo
    elif option == "large":
        displayed_logo = large_logo
    else:
        if os.get_terminal_size()[0] < 128:
            displayed_logo = small_logo
        else:
            displayed_logo = large_logo

    lines = displayed_logo.splitlines()
    length = len(lines[1])
    gradient = hex_gradient("#5900ab", "#00d0ff", length)

    colored_logo = "[bold]\n"
    for i in range(1, len(lines)):
        for j in range(length):
            colored_logo += f"[{gradient[j]}]{lines[i][j] if lines[i][j] != "\\" else "\\\\"}"
        colored_logo += "\n"

    console.print(Align.center(colored_logo))


# print help message
def help_msg():
    console.print('''COMMAND LIST:
[green]help[/green]  lists all available commands

[green]ls[/green]  lists all files and directories in the current working directory
[green]ls[/green] [cyan]{dir}[/cyan]  lists all files and directories in the specified directory
                                          
[green]cd[/green] [cyan]{dir}[/cyan]  changes the current working directory to the specified directory

[green]clear[/green]  clears the terminal
                   
[green]play[/green] [cyan]{path}[/cyan]  the given audio file plays once
[green]play[/green] [cyan]{option} {path}[/cyan]
    [cyan]-r[/cyan]   the given audio file plays in repeat until stopped
[green]play[/green] [cyan]{option} {dir}[/cyan]
    [cyan]-d[/cyan]   the audio files of given directory play in alphabetical order
    [cyan]-dr[/cyan]  the audio files of given directory play in alphabetical order and loop around until stopped
    [cyan]-ds[/cyan]  the audio files of given directory play in shuffled order and loop around until stopped
    [cyan]-D[/cyan]   the audio files of given directory and its subdirectories play in alphabetical order
    [cyan]-Dr[/cyan]  the audio files of given directory and its subdirectories play in alphabetical order and loop around until stopped
    [cyan]-Ds[/cyan]  the audio files of given directory and its subdirectories play in shuffled order and loop around until stopped
   
[green]info[/green] [cyan]{path}[/cyan]  shows all available tags and their respective values for the given audio file.
[green]info[/green] [cyan]{path} {tags}[/cyan]  hows only the provided tags (separate tags with space for multiple ones) and their respective values
                  
[green]convert[/green] [cyan]{input path} {output path}[/cyan] Converts an audio file to another format (FFmpeg required)
''')


# format and print error messages
def error_msg(content, title = None):
    if title != None:
        console.print(f"[bold red]{title} Error:[/bold red] {content}")
    else:
        console.print(f"[bold red]Error:[/bold red] {content}")