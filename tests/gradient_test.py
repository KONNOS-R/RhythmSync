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





from rich.console import Console
console = Console()


#logos
if False:
    logo = r'''
 _____  _           _   _                _____                  
|  __ \| |         | | | |              / ____|                 
| |__) | |__  _   _| |_| |__  _ __ ___ | (___  _   _ _ __   ___ 
|  _  /| '_ \| | | | __| '_ \| '_ ` _ \ \___ \| | | | '_ \ / __|
| | \ \| | | | |_| | |_| | | | | | | | |____) | |_| | | | | (__ 
|_|  \_\_| |_|\__, |\__|_| |_|_| |_| |_|_____/ \__, |_| |_|\___|
               __/ |                            __/ |           
              |___/                            |___/            
'''
elif False:
    logo = r'''
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
else:
    logo = r'''
RhythmSync
'''



lines = logo.splitlines()

length = len(lines[1])
gradient = hex_gradient("#5900ab", "#00d0ff", length)


colored_logo = "[bold]\n"
for i in range(1, len(lines)):
    for j in range(length):
        colored_logo += f"[{gradient[j]}]{lines[i][j] if lines[i][j] != "\\" else "\\\\"}"
    colored_logo += "\n"

console.print(colored_logo)
print(colored_logo)
