import pygame, sys, random
from koronis import *

# Constants
FRAMERATE = 60  # FPS
GAME_SPEEDUP_RATE = 5 # Every 5 seconds, the game speeds up

MAX_ENEMIES = 5 # Max number of enemies on screen
PLANET_SPAWN_RATE = 10 # Every 10 seconds, a planet spawns
STAR_SPAWN_RATE = 15 # Every 15 seconds, a star spawns
POWERUP_SPAWN_RATE = 3 # Every 3 seconds, a powerup spawns

RELOAD_TIME = 2 # Time to reload
SHIELD_DURATION = 1.5 # Time the invencibility lasts

# Debug options
ENABLE_HITBOX = True


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
                return


def main():
    screen_w = 900
    screen_h = 900

    speed = 5

    # Pygame setup
    pygame.init()
    pygame.display.set_caption("Koronis")
    screen = pygame.display.set_mode([screen_w, screen_h])

    hit = pygame.mixer.Sound('data/sfx/hit.wav')

    explosions = [
        pygame.mixer.Sound('data/sfx/explosion1.wav'),
        pygame.mixer.Sound('data/sfx/explosion2.wav'),
        pygame.mixer.Sound('data/sfx/explosion3.wav')
    ]

    font = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 27)
    clock = pygame.time.Clock()

    # Background setup
    stars = []
    for i in range(50):
        stars.append(BackgroundStar(screen_w, screen_h))

    # Player setup
    player = Player(100, screen_w, screen_h)
    projectiles = []
    dead = False
    reloading = False

    # Enemy setup
    enemies = []
    for i in range(MAX_ENEMIES):
        enemies.append(Asteroid((50, 75), speed, screen_w))

    # Start menu label
    title_font = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 81)
    txt_title = title_font.render("KORONIS", False, [255, 255, 255])
    txt_begin = font.render("[ SPACE ]    START", False, [255, 255, 255])
    
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

        screen.blit(txt_title, [screen_w / 2 - (txt_title.get_width() / 2), screen_h / 4])
        screen.blit(txt_begin, [screen_w / 2 - (txt_begin.get_width() / 2), screen_h / 2])

        clock.tick(FRAMERATE * 4)
        pygame.display.flip()
    
    duration = 0
    frame = 0
    frame_shield = 10

    # Main loop
    while not dead:
        # Calculate time passed
        if frame == 0:
            duration = duration + 1
            player.score = player.score + 1
        
            if duration % GAME_SPEEDUP_RATE == 0:
                speed = speed + 0.5

        if player.invencible:
            if duration > shield_time + SHIELD_DURATION:
                player.invencible = False

        # EVENT HANDLING
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

        # Update background
        for star in stars:
            star.update()
            if star.out_of_bounds(screen_h):
                stars.remove(star)
                stars.append(BackgroundStar(screen_w, screen_h, y = -10))

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
            screen.blit(player.heart, [player.heart.get_width()  * i, screen_h - player.heart.get_height()])
        
        score = font.render("{:08d}".format(player.score), False, [255, 255, 255])
        screen.blit(score, [screen_w - score.get_width(), screen_h - score.get_height()])

        # End of loop
        frame = (frame + 1) % FRAMERATE

        clock.tick(FRAMERATE)
        pygame.display.update()

        if dead:
            scoreFont = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 18)
            txt_score = scoreFont.render("score " + str(player.score),  False, [255, 255, 255])
            deadText = font.render("You died",     False, [255, 255, 255])
            deadCont = font.render("[ SPACE ]   Continue", False, [255, 255, 255])
            deadQuit = font.render("[ ESC ]       Exit",    False, [255, 255, 255])
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
                screen.blit(deadText, [screen_w / 2 - (deadText.get_width() / 2), screen_h / 4])
                screen.blit(txt_score, [screen_w / 2 - (txt_score.get_width() / 2), screen_h / 4 + (2 * deadText.get_height())])
                screen.blit(deadCont, [screen_w / 2 - (deadCont.get_width() / 2), screen_h / 2])
                screen.blit(deadQuit, [screen_w / 2 - (deadCont.get_width() / 2), screen_h / 2 + deadCont.get_height() * 2])
                pygame.display.update()

if __name__ == "__main__":
    main()