import pygame
import sys
from random import randint
from time import sleep
from multiprocessing import Process

# Initialize Pygame
pygame.init()


scorefont = pygame.font.Font('static/font.ttf', 72)
youDied = pygame.font.Font('static/font.ttf', 72)

#  Load images
deathscreen = pygame.image.load("static/deathmsg.png")
pygame_icon = pygame.image.load('static/jpsonnosway1.png')
playagain = pygame.image.load("static/playagain.png")

pygame.display.set_icon(pygame_icon)

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

score = 0
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jetpack Sam")

# define astroids
class Astroid:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = randint(50,100)
        astroidType = randint(1,3)
        self.astroid = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(f"static/astroid{astroidType}.png"),(can_size, can_size)), randint(0,360))
        self.roll = 0
    def setup(self, WIDTH, HEIGHT):
        self.x = WIDTH + self.size * 5
        self.y = randint(100, 500)

        self.astroid = pygame.transform.scale(self.astroid,(self.size, self.size))
astroids = []
astroidFrameCheck = 0

# Jerry can setup
can_size = 50
can_x = randint(0, WIDTH - can_size - 50)
can_y = randint(0, HEIGHT - can_size)
CAN_SPEED = -4
can = pygame.transform.scale(pygame.image.load("static/jerrycan.png"),(can_size, can_size))
canhb = pygame.Rect(can_x, can_y, can_size, can_size)
can_rotate = 0


bg = pygame.image.load("static/background.png")
playagain = pygame.transform.scale(playagain, (70,70))
playagainrec = playagain.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))


# load sound
jetpackblast = pygame.mixer.Sound("static/jetpack3.wav")
powerup = pygame.mixer.Sound("static/powerup3.wav")
deathsound = pygame.mixer.Sound("static/death.wav")
bonk = pygame.mixer.Sound("static/bonk2.wav")
lowFuelBeep = pygame.mixer.Sound("static/low_fuel.wav")

#player setup
dead = False
fuel = 10
player_size = 60
player_x = 0
player_y = 0
playerhb = pygame.Rect(player_x, player_y, player_size, player_size)
player_speed = 5
player_v = 0
fall_speed = 0.1
flipped = True
on = "on"
sway = "nosway"
fire_frame = 1
jps = {"on":{
        "sway":{
            "1":pygame.transform.scale(pygame.image.load("static/jpsonsway1.png"), (player_size,player_size)),
            "2":pygame.transform.scale(pygame.image.load("static/jpsonsway2.png"), (player_size,player_size))
        },
        "nosway":{
            "1":pygame.transform.scale(pygame.image.load("static/jpsonnosway1.png"), (player_size,player_size)),
            "2":pygame.transform.scale(pygame.image.load("static/jpsonnosway2.png"), (player_size,player_size))
        }},
        "off":{
        "sway":{
            "1":pygame.transform.scale(pygame.image.load("static/jpsoffsway1.png"), (player_size,player_size))
        },
        "nosway":{
            "1":pygame.transform.scale(pygame.image.load("static/jpsoffnosway1.png"), (player_size,player_size))
        }
    }
}

# Main game loop
clock = pygame.time.Clock()

def astroidtoscore(points):
    points = 50 - points
    if points <= 15: points = 15
    return points

scorepersecond = round(1/FPS, 2)
lowFuelBeepTimer = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    if not dead: score = round(score + scorepersecond, 2)

    lowFuelBeepTimer += 1
    if lowFuelBeepTimer == FPS: 
        lowFuelBeepTimer = 0
        if fuel < 2: pygame.mixer.Sound.play(lowFuelBeep)

    def DrawBar(pos, size, borderC, barC, progress):

        pygame.draw.rect(screen, borderC, (*pos, *size), 1)
        innerPos  = (pos[0]+3, pos[1]+3)
        innerSize = ((size[0]-6) * progress, size[1]-6)
        pygame.draw.rect(screen, barC, (*innerPos, *innerSize))


    if dead and playagainrec.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        player_x = 0
        player_y = 0
        astroids.clear()
        score = 0
        dead = False
        fuel = 10
        pygame.mixer.Sound.play(powerup)
    
    # Spawn astroids every 15 frames
    astroidFrameCheck += 1
    if astroidFrameCheck == astroidtoscore(round(score)):
       
        if randint(1,2) == 1:
            astroid = Astroid()
            astroid.setup(HEIGHT,WIDTH)
            astroids.append(astroid)
        astroidFrameCheck = 0
    if astroidFrameCheck >= 100:
        astroidFrameCheck = 0


    canhb = pygame.Rect(can_x, can_y, can_size, can_size)
    playerhb = pygame.Rect(player_x, player_y, player_size, player_size)
            
    if fire_frame == 1:
        fire_frame = 2
    else: fire_frame = 1
    sway = "nosway"
    on = "off"
    if not dead:
        # Handle player input
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
            if flipped:
                
                flipped = False
            sway = "sway"
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
            if not flipped:
                flipped = True
            sway = "sway"


        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and player_y >= 0:
            
            pygame.mixer.Sound.play(jetpackblast)
            on = "on"
            if player_v > -5: 
                player_v += -1
                fuel -= 10/FPS
            else:fuel -= 2/FPS
        
    # Update game logic here
    falling = True

    if player_y >= 550 + 10 and not player_v < 0:
        falling = False
        player_v = 0

    if falling and player_y <= 600:
        player_y += player_v
        player_v += fall_speed
        if player_y <= 0:
            player_y -= player_v -1
            player_v = player_v/2 * -1

    if fuel < 0:
        dead = True
    
    if playerhb.colliderect(canhb):
        can_x, can_y = randint(100, 600), randint(100, 500)
        CAN_SPEED = randint(3,5) * -1
        pygame.mixer.Sound.play(powerup)
        score = round(score + 1, 2)
        fuel = 10
    
    # Draw everything

    screen.fill((94, 94, 94))
    #pygame.draw.rect(screen, (0,0,0), pygame.Rect(player_x, player_y, player_size, player_size))
    if fire_frame == 2 and on == "off": fire_frame = 1
    jpstf = jps[on][sway][str(fire_frame)]
    if flipped == True: jpstf = pygame.transform.flip(jpstf, True ,False)

    # blit all surfaces
    ratio = fuel / 10
    
    screen.blit(bg, (0, 0))
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH-150, 60, 100, 16))
    pygame.draw.rect(screen, (0, 255, 0), (WIDTH-150, 60, 100 * ratio, 16))
    screen.blit(scorefont.render(str(score), True, (255,255,255)), (60, 40))
    screen.blit(can, (can_x, can_y, can_size, can_size))
    screen.blit(jpstf, (player_x, player_y, player_size, player_size))
    

    for astroid in astroids:
        astroid.x += -4
        astroid.roll += 0.5
        if astroid.x + astroid.size < 0:
            astroids.remove(astroid)
        screen.blit(pygame.transform.rotate(astroid.astroid, astroid.roll), (astroid.x, astroid.y))
        if pygame.Rect.colliderect(pygame.Rect(player_x, player_y, player_size- 16, player_size- 13),pygame.Rect(astroid.x, astroid.y, astroid.size-20, astroid.size-20)):
            if not dead:
                pygame.mixer.Sound.play(deathsound)
            dead = True
    if dead:
        #screen.blit(pygame.transform.scale(deathscreen, (300, 300)), deathscreen.get_rect(center=(WIDTH/2 - 100, HEIGHT/2 - 100)))
        screen.blit(youDied.render("You died!", True, (255,255,255)), deathscreen.get_rect(center=(WIDTH/2 - 100, HEIGHT/2 )))
        screen.blit(playagain, playagainrec)
  
    
    # Update the display
    pygame.display.flip()
    pygame.display.update()
    

    # Cap the frame rate
    clock.tick(FPS)