# gradient function
# should go from color a to color b in set increments

'''
def hex_gradient(hex_a, hex_b, increment):
    HEX_A = [x for x in hex_a if x != "#"]
    print(HEX_A)

    red_a = (HEX_A[0] + HEX_A[1])
    green_a = (HEX_A[2] + HEX_A[3])
    blue_a = (HEX_A[4] + HEX_A[5])
    print(red_a, green_a, blue_a)


    HEX_B = [x for x in hex_b if x != "#"]
    print(HEX_B)

    #tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))




hex_gradient("#ffffff", "#000000", 4)
'''



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

print(hex_gradient("#ffffff", "#000000", 10))

a = hex_gradient("#ff0000", "#0099FF", 20)


from rich.console import Console
console = Console()

for i in range(20):
    console.print(f"[{a[i]}]test")