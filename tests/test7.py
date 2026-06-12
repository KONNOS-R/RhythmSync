import pygame
import time

pygame.mixer.init()
pygame.mixer.music.load("/home/konnosr/Music/Internet/Mitski/Puberty 2/1.05 - Your Best American Girl.flac")
pygame.mixer.music.play()

#while pygame.mixer.music.get_busy():
 #   pass