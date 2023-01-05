import pygame, sys, random
from koronis import *

# Constants
FRAMERATE = 60  # FPS
GAME_SPEEDUP_RATE = 5 # Every 5 seconds, the game speeds up 

MAX_ENEMIES = 8 # Max number of enemies on screen
PLANET_SPAWN_RATE = 10 # Every 10 seconds, a planet spawns
STAR_SPAWN_RATE = 15 # Every 15 seconds, a star spawns
POWERUP_SPAWN_RATE = 3 # Every 3 seconds, a powerup spawns

RELOAD_TIME = 2 # Time to reload
SHIELD_DURATION = 1.5 # Time the invencibility lasts

# Debug options
ENABLE_HITBOX = False


def check_enemies_collision(player, enemies):
    for enemy in enemies:
        if player.hitbox.colliderect(enemy.hitbox):
            return True
    return False

def check_projectile_collision(projectiles, enemies, player, explosions):
    for projectile in projectiles:
        for enemy in enemies:
            if projectile.hitbox.colliderect(enemy.hitbox) and enemy.isDestructible:
                projectiles.remove(projectile)
                enemies.remove(enemy)      
                player.score = player.score + enemy.size
                
                random.choice(explosions).play()
                break


def main():
    screen_w = 900
    screen_h = 900

    speed = 3

    # Pygame setup
    pygame.init()
    pygame.display.set_caption("Koronis")
    screen = pygame.display.set_mode([screen_w, screen_h], pygame.DOUBLEBUF)

    hit = pygame.mixer.Sound('data/sfx/hit.wav')

    explosions = [
        pygame.mixer.Sound('data/sfx/explosion1.wav'),
        pygame.mixer.Sound('data/sfx/explosion2.wav'),
        pygame.mixer.Sound('data/sfx/explosion3.wav')
    ]

    font_small = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 18)
    font_normal = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 27)
    font_big = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 32)
    font_large = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 81)
    


    # Background setup
    stars = []
    for i in range(50):
        stars.append(BackgroundStar(screen_w, screen_h))

    # UI setup
    key_size = 50
    key_sprites = {
        'up': pygame.transform.scale(
            pygame.image.load('data/gfx/key_up.png'), 
            (key_size, key_size)),
        
        'down': pygame.transform.scale(
            pygame.image.load('data/gfx/key_down.png'),
            (key_size, key_size)),
        
        'left': pygame.transform.scale(
            pygame.image.load('data/gfx/key_left.png'),
            (key_size, key_size)),
        
        'right': pygame.transform.scale(
            pygame.image.load('data/gfx/key_right.png'),
            (key_size, key_size))
    }
    

    # Player setup
    player = Player(100, screen_w, screen_h)
    projectiles = []
    dead = False
    reloading = False

    # Enemy setup
    enemies = []
    for i in range(MAX_ENEMIES):
        enemies.append(Asteroid((50, 75), speed, screen_w))

    # Text objects setup
    text = {
        'title': font_large.render("KORONIS", False, [255, 255, 255]),
        'space': font_big.render("[   SPACE  ]", False, [255, 255, 255]),
        'shoot': font_small.render("SHOOT", False, [255, 255, 255]),
        'move': font_small.render("MOVE", False, [255, 255, 255]),
        'begin': font_small.render("PRESS SPACE TO START", False, [255, 255, 255]),
        'game_over': font_large.render("GAME OVER", False, [255, 255, 255]),
        'restart': font_normal.render("[ SPACE ]    RESTART", False, [255, 255, 255]),
        'quit': font_normal.render("[ ESC ]    QUIT", False, [255, 255, 255])
    }

    clock = pygame.time.Clock()
    ready = False

    # Start menu
    while not ready:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    ready = True

        # Update background
        for star in stars:
            star.update()
            if star.out_of_bounds(screen_h):
                stars.remove(star)
                stars.append(BackgroundStar(screen_w, screen_h, y = -10))
        
        # Draw background
        screen.fill([0, 0, 0])
        for star in stars:
            star.draw(screen)
        
        screen.blit(player.sprite, player.position)

        # Draw UI
        screen.blit(
            text['title'], 
            [screen_w/2 - (text['title'].get_width()/2), screen_h/4])
        
        screen.blit(
            text['begin'], 
            [screen_w / 2 - (text['begin'].get_width() / 2), screen_h / 2 + (key_size*5)])

        clock.tick(FRAMERATE * 4)
        pygame.display.update()
    
    duration = 0
    frame = 0
    frame_shield = 10

    time_limit = 2.5 * FRAMERATE
    time_passed = 0

    # Tutorial loop
    while time_passed < time_limit:
        time_passed = time_passed + 1

        # Update background
        for star in stars:
            star.update()
            if star.out_of_bounds(screen_h):
                stars.remove(star)
                stars.append(BackgroundStar(screen_w, screen_h, y = -10))
        
        # Draw background
        screen.fill([0, 0, 0])
        for star in stars:
            star.draw(screen)

        # Draw player
        screen.blit(player.sprite, player.position)

        screen.blit(
            key_sprites['up'], 
            [screen_w/4 - (key_size/2), screen_h/2 - (key_size) - 3])
        
        screen.blit(
            key_sprites['left'], 
            [screen_w/4 - (key_size*1.5) - 3, screen_h/2])
        
        screen.blit(
            key_sprites['right'], 
            [screen_w/4 + (key_size*0.5) + 3, screen_h/2])
        
        screen.blit(
            key_sprites['down'], 
            [screen_w/4 - (key_size/2), screen_h/2])
        
        screen.blit(
            text['space'], 
            [screen_w - (screen_w/4) - (text['space'].get_width()/2), screen_h/2 + (key_size/8)])
        
        screen.blit(
            text['shoot'], 
            [screen_w - (screen_w/4) - (text['shoot'].get_width()/2), screen_h/2 + (key_size/2) + (text['space'].get_height())])
        
        screen.blit(
            text['move'], 
            [screen_w/4 - (text['move'].get_width()/2), screen_h/2 + (key_size/2) + (text['space'].get_height())])
        
        clock.tick(FRAMERATE)
        pygame.display.update()

    # Main loop
    while True:
        # Calculate time passed
        if frame == 0:
            duration = duration + 1
            player.score = player.score + 1
        
            if duration % GAME_SPEEDUP_RATE == 0:
                speed = speed + 0.1

        # Update invencibility
        if player.invencible:
            if duration > shield_time + SHIELD_DURATION:
                player.invencible = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                
                # Spacebar pressed
                if event.key == pygame.K_SPACE:
                    if not reloading:
                        projectiles.append(Nuke(player))
                        reloading = True
                        reload_cooldown = RELOAD_TIME * FRAMERATE
                
                # Escape pressed
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    while paused:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    paused = False

        # Update background
        for star in stars:
            star.update()
            if star.out_of_bounds(screen_h):
                stars.remove(star)
                stars.append(BackgroundStar(screen_w, screen_h, y = -10))

        # Update player
        keys = pygame.key.get_pressed()
        player.update_position(keys, (screen_w, screen_w))
        player.update_orientation()

        if reloading:
            reload_cooldown -= 1
            if reload_cooldown == 0:
                reloading = False

        # Update enemies
        if frame == 0 and duration % PLANET_SPAWN_RATE == 0:
            enemies.append(Planet((125, 150), speed, screen_w))

        if len(enemies) < MAX_ENEMIES:
                newAsteroid = Asteroid((50, 75), speed, screen_w)
                enemies.append(newAsteroid)

        for enemy in enemies:
            enemy.update_position()
            enemy.update_hitbox()

            if enemy.out_of_bounds(screen_h):
                enemies.remove(enemy)
                enemies.append(Asteroid((50, 75), speed, screen_w))

        # Update projectiles
        for projectile in projectiles:
            projectile.update_position()
            projectile.update_hitbox()

            if projectile.out_of_bounds():
                projectiles.remove(projectile)
        
        # Check collisions
        check_projectile_collision(projectiles, enemies, player, explosions)
        if not player.invencible and check_enemies_collision(player, enemies):
            frame_shield = frame_shield - 1
        
        if frame_shield < 0:
            frame_shield = 10
            
            player.hit()
            hit.play()

            shield_time = duration
            if player.lives == 0:
                dead = True

        # Draw background
        screen.fill([0, 0, 0])
        for star in stars:
            star.draw(screen)
        
        # Draw player
        if frame % 5 == 0:
            player.change_thrust()
        player.draw(screen)

        # Draw projectiles
        for projectile in projectiles:
            screen.blit(projectile.sprite, projectile.position)

        # Draw enemies
        for enemy in enemies:
            screen.blit(enemy.sprite, enemy.position)

        # Draw hitbox
        if ENABLE_HITBOX:
            pygame.draw.rect(screen, [255, 255, 255], player.hitbox, 1)
            for enemy in enemies:
                pygame.draw.rect(screen, [255, 255, 255], enemy.hitbox, 1)
            for projectile in projectiles:
                pygame.draw.rect(screen, [255, 255, 255], projectile.hitbox, 1)

        # Draw UI
        if reloading:
            progress = (RELOAD_TIME * FRAMERATE) - reload_cooldown
            progress = (progress / (RELOAD_TIME * FRAMERATE)) * (player.sprite.get_width() / 3)

            reloadbar = pygame.Rect(
                player.position.x + (player.sprite.get_width() / 3), 
                player.position.y - 20, 
                progress, 5)
            pygame.draw.rect(screen, [60, 60, 70], reloadbar)

        for i in range(player.lives):
            screen.blit(player.heart, [screen_w - (player.heart.get_width() * (i + 1) + 15), 15])
        
        score = font_normal.render("{:08d}".format(player.score), False, [255, 255, 255])
        screen.blit(score, [15, 15])

        # End of loop
        frame = (frame + 1) % FRAMERATE
        clock.tick(FRAMERATE)
        pygame.display.update()

        if dead:
            text_score = font_small.render("SCORE:  " + str(player.score),  False, [255, 255, 255])
            while dead:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_SPACE:
                            player = Player(100, screen_w, screen_h)
                            projectiles = []
                            enemies = []
                            for i in range(MAX_ENEMIES):
                                newAsteroid = Asteroid((50, 75), speed, screen_w)
                                enemies.append(newAsteroid)
                            duration = 0
                            frame = 0
                            dead = False
                            reloading = False
                            speed = 5
                
                screen.fill([0, 0, 0])
                
                screen.blit(
                    text['game_over'], 
                    [screen_w / 2 - (text['game_over'].get_width() / 2), 
                    screen_h / 4])
                
                screen.blit(
                    text_score, 
                    [screen_w / 2 - (text_score.get_width() / 2), 
                    screen_h / 4 + (2 * text['game_over'].get_height())])
                
                screen.blit(
                    text['restart'], 
                    [screen_w / 2 - (text['restart'].get_width() / 2), 
                    screen_h / 2])
                
                screen.blit(
                    text['quit'], 
                    [screen_w / 2 - (text['restart'].get_width() / 2), 
                    screen_h / 2 + text['restart'].get_height() * 2])
                
                pygame.display.update()

if __name__ == "__main__":
    main()