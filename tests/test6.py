import os


width, height = os.get_terminal_size()

print(f"width: {width}")
print(f"height: {height}")

for i in range(height):
    print("░▒▓▒"*(int(width/4)))


# test for new lyric system
lyric_index = int(input("lyric index:"))
lyrics = [
    [1, "[00:15.60]I don't smoke except for when I'm missing you"],
    [2, "[00:21.93]To remember your mouth, how it tasted true"],
    [3, "[00:28.81]And I don't smoke except for after I've held you, baby"],
    [4, "[00:36.41]Being with you makes the flame burn good"],
    [5, "[00:44.66]"],
    [6, "[00:47.78]So if you need to be mean, be mean to me"],
    [7, "[00:54.40]I can take it and put it inside of me"],
    [8, "[01:01.45]If your hands need to break"],
    [9, "[01:04.75]More than trinkets in your room"],
    [10, "[01:08.26]You can lean on my arm as you break my heart"],
    [11, "[01:22.35]I'm what's left of when we swam under the moon"],
    [12, "[01:28.28]Now the rest of my days are just waiting for when"],
    [13, '[01:35.12]You come down and tell me, "I was meant for you", baby'],
    [14, "[01:42.82]Being with you makes the flame burn good"],
    [15, "[01:48.13]If you need to be mean, be mean to me"],
    [16, "[01:54.58]I can take it and put it inside of me"],
    [17, "[02:01.33]If your hands need to break"],
    [18, "[02:05.40]More than trinkets in your room"],
    [19, "[02:08.32]You can lean on my arm as you break my heart"],
    [20, "[02:15.43]Just don't leave me alone wondering where you are"],
    [21, "[02:22.38]I am stronger than you give me credit for"],
    [22, "[02:29.17]If your hands need to break"],
    [23, "[02:32.65]More than trinkets in your room"],
    [24, "[02:36.49]You can lean on my arm as you break my heart"],
    [25, "[02:42.19]"],
]

header = 4
player = 1
footer = 1
padding = 2

lyric_lines = height - header - player - footer - padding*2
print(f"{lyric_lines} of {height}")

for i in range(header):
    print("▓"*width)

for i in range(padding):
    print(" "*width)



half = lyric_lines // 2
if lyric_lines % 2 == 0:
    start = max(1, lyric_index - half + 1)
    end = min(len(lyrics) + 1, lyric_index + half + (lyric_lines % 2) + 1)
else:
    start = max(1, lyric_index - half)
    end = min(len(lyrics) + 1, lyric_index + half + (lyric_lines % 2))

for i in lyrics:
    if start <= i[0] < end:
        print(i)



for i in range(padding):
    print(" "*width)

for i in range(player):
    print("▓"*width)