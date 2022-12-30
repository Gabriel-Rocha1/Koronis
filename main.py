import pygame, sys, random, time
from koronis import *

#---------------------------------------------- GLOBALS ---------------------------------------------#
SCREEN_W = 900
SCREEN_H = 900
FRAMERATE = 60
ENABLE_HITBOX = False
MAX_ENEMIES = 5
GAME_SPEEDUP_RATE = 5
PLANET_SPAWN_RATE = 10
STAR_SPAWN_RATE = 15
POWERUP_SPAWN_RATE = 3
RELOAD_TIME = 2
SHIELD_DURATION = 1.5

game_speed = [3, 7]

#--------------------------------------------- FUNCTIONS ----------------------------------------------#
def check_wall_collision(player):
    if player.position.x  > SCREEN_W - player.sprite.get_width():
        player.position.x = SCREEN_W - player.sprite.get_width()
    if player.position.x  < 0:
        player.position.x = 0
    if player.position.y  > SCREEN_H - player.sprite.get_height():
        player.position.y = SCREEN_H - player.sprite.get_height()
    if player.position.y  < 0:
        player.position.y = 0

def check_enemies_collision(player, enemies):
    for enemy in enemies:
        if player.hitbox.colliderect(enemy.hitbox):
            return True
    return False

def check_projectile_collision(projectiles, enemies, player):
    for projectile in projectiles:
        for enemy in enemies:
            if enemy.isDestructible and projectile.hitbox.colliderect(enemy.hitbox):
                enemies.remove(enemy)
                player.score += enemy.size
                projectiles.remove(projectile)
                explosion = pygame.mixer.Sound('data/sfx/explosion' + str(random.randint(1, 3)) + '.wav')
                explosion.play()
                break


def main():
    # PYGAME AND CLOCK
    pygame.init()
    pygame.display.set_caption("Koronis")
    hit = pygame.mixer.Sound('data/sfx/hit.wav')
    font = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 27)
    clock  = pygame.time.Clock()
    screen = pygame.display.set_mode([SCREEN_W, SCREEN_H])

    # BACKGROUND
    background_stars = []
    for i in range(50):
        background_stars.append(BackgroundStar(SCREEN_W))
        background_stars[i].position.y = random.randint(0, SCREEN_H)

    # PLAYER
    player = Player(100, SCREEN_W, SCREEN_H)
    projectiles = []
    dead = False

    # UTILS
    oneSecond = 1
    frameLives = 10
    currFrame = 1
    reloading = False
    planet_spawn = PLANET_SPAWN_RATE
    game_speedup = GAME_SPEEDUP_RATE

    # ENEMIES
    enemies = []
    for i in range(MAX_ENEMIES):
        newAsteroid = Asteroid((50, 75), game_speed, SCREEN_W)
        enemies.append(newAsteroid)


    # TITLE SCREEN
    ready = False
    titleFont = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 81)

    gameTitle = titleFont.render("KORONIS", False, [255, 255, 255])
    gameBegin = font.render("[ SPACE ]    START", False, [255, 255, 255])
    

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

        # UPDATE BACKGROUND
        for star in background_stars:
            star.position.y += 0.5
            if star.position.y > SCREEN_H:
                background_stars.remove(star)
                background_stars.append(BackgroundStar(SCREEN_W))
        
        # DRAW BACKGROUND
        screen.fill([0, 0, 0])
        for star in background_stars:
            pygame.draw.circle(screen, star.color, star.position, star.size)
        
        screen.blit(player.sprite, player.position)

        screen.blit(gameTitle, [SCREEN_W / 2 - (gameTitle.get_width() / 2), SCREEN_H / 4])
        screen.blit(gameBegin, [SCREEN_W / 2 - (gameBegin.get_width() / 2), SCREEN_H / 2])

        clock.tick(FRAMERATE * 4)
        pygame.display.flip()
    start  = time.time()

#------------------------------------------ MAIN GAME LOOP ------------------------------------------#
    while not dead:
        
        # CALCULATE TIME
        curr = time.time()
        timePassed = curr - start
        if currFrame == 61:
            currFrame = 1
            if not check_enemies_collision(player, enemies):
                frameLives = 10
        
        if timePassed > game_speedup:
            game_speedup += GAME_SPEEDUP_RATE
            game_speed[0] += 0.1
            game_speed[1] += 0.1
        
        if timePassed > oneSecond:
            oneSecond += 1
            player.score += 1
        
        if player.invencible:
            if timePassed > shieldTime + SHIELD_DURATION:
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
                        reloadProgress = timePassed

        # UPDATE BACKGROUND
        for star in background_stars:
            star.position.y += 0.5
            if star.position.y > SCREEN_H:
                background_stars.remove(star)
                background_stars.append(BackgroundStar(SCREEN_W))

        # UPDATE PLAYER
        player.hitbox = player.default_hitbox
        keys = pygame.key.get_pressed()
        player.position.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])  * player.speed
        player.position.x -= (keys[pygame.K_LEFT]  - keys[pygame.K_RIGHT]) * player.speed
        player.position.y += (keys[pygame.K_DOWN]  - keys[pygame.K_UP])    * player.speed
        player.position.y -= (keys[pygame.K_UP]    - keys[pygame.K_DOWN])  * player.speed
        player.sprite_rect = player.sprite.get_rect(center = [player.position.x, player.position.y])
        player.update_hitbox()

        if reloading:
            if timePassed >= reloadProgress + RELOAD_TIME:
                reloading = False

        # UPDATE ENEMIES
        if timePassed > planet_spawn:
            planet_spawn += PLANET_SPAWN_RATE
            newPlanet = Planet((125, 150), game_speed, SCREEN_W)
            enemies.append(newPlanet)

        if len(enemies) < MAX_ENEMIES:
                newAsteroid = Asteroid((50, 75), game_speed, SCREEN_W)
                enemies.append(newAsteroid)

        for enemy in enemies:
            enemy.update_position()
            enemy.update_hitbox()

            if enemy.offBounds(SCREEN_H):
                enemies.remove(enemy)
                newAsteroid = Asteroid((50, 75), game_speed, SCREEN_W)
                enemies.append(newAsteroid)

        # UPDATE PROJECTILES
        for projectile in projectiles:
            projectile.update_position()
            projectile.update_hitbox()

            if projectile.offBounds():
                projectiles.remove(projectile)

        # DRAW BACKGROUND
        screen.fill([0, 0, 0])
        for star in background_stars:
            pygame.draw.circle(screen, star.color, star.position, star.size)
        
        # DRAW PROJECTILES
        for projectile in projectiles:
            screen.blit(projectile.sprite, projectile.position)

        # RELOADING ANIMATION
        if reloading:
            stage = (reloadProgress + RELOAD_TIME - timePassed) * (RELOAD_TIME * 10)
            
            reloadBar = pygame.Rect(player.position.x + (player.sprite.get_width() / 3), player.position.y - 20, stage, 5)
            pygame.draw.rect(screen, [60, 60, 70], reloadBar)

        # DRAW PLAYER
        if currFrame % 5 == 0:
            player.change_thrust()
        
        if player.invencible:
            rocket = player.invencible_sprite
        else:
            rocket = player.sprite

        thrust = player.thrust

        if (keys[pygame.K_UP]    and not keys[pygame.K_DOWN])  or \
           (keys[pygame.K_LEFT]  and not keys[pygame.K_RIGHT]) or \
           (keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]):
            thrust_pos = [player.position.x, player.position.y + rocket.get_height()]

            if   (keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]):
                rocket     = player.tilt(rocket, 'left')
                thrust     = player.tilt(player.thrust, 'left')
                thrust_pos = [player.position.x + (rocket.get_width() / 2), player.position.y + (rocket.get_height() / 2)]

            elif (keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]):
                rocket     = player.tilt(rocket, 'right')
                thrust     = player.tilt(player.thrust, 'right')
                thrust_pos = [player.position.x - (rocket.get_width() / 2), player.position.y + (rocket.get_height() / 2)]
            
            screen.blit(thrust, thrust_pos)   
        screen.blit(rocket, player.position)

        # DRAW ENEMIES
        for enemy in enemies:
            screen.blit(enemy.sprite, enemy.position)

        # DRAW UI
        if reloading:
            player.update_reloadBar()
        
        for i in range(player.lives):
            screen.blit(player.heart, [player.heart.get_width()  * i, SCREEN_H - player.heart.get_height()])

        # DRAW HITBOX
        if ENABLE_HITBOX:
            pygame.draw.rect(screen, [255, 255, 255], player.hitbox, 1)
            for enemy in enemies:
                pygame.draw.rect(screen, [255, 255, 255], enemy.hitbox, 1)
            for projectile in projectiles:
                pygame.draw.rect(screen, [255, 255, 255], projectile.hitbox, 1)

        # DRAW SCORE
        scoreTxt = "{:08d}".format(player.score)
        score = font.render(scoreTxt, False, [255, 255, 255])
        screen.blit(score, [SCREEN_W - score.get_width(), SCREEN_H - score.get_height()])

        # CHECK COLLISION
        check_wall_collision(player)
        check_projectile_collision(projectiles, enemies, player)
        if not player.invencible and check_enemies_collision(player, enemies):
            frameLives -= 1

        # END OF LOOP
        currFrame += 1
        clock.tick(FRAMERATE)
        pygame.display.update()

        if frameLives <= 0:
            hit.play()
            frameLives        = 10
            player.lives     -= 1
            player.invencible = True
            shieldTime        = timePassed
            if player.lives  == 0:
                dead = True

        if dead:
            scoreFont = pygame.font.Font('data/font/8-BIT_WONDER.TTF', 18)
            scoreTxt = scoreFont.render("score " + str(player.score),  False, [255, 255, 255])
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
                            player      = Player()
                            projectiles = []
                            enemies     = []
                            for i in range(MAX_ENEMIES):
                                newAsteroid = Asteroid((50, 75), game_speed, SCREEN_W)
                                enemies.append(newAsteroid)
                            start = time.time()
                            dead  = False
                            reloading = False
                            game_speed[0] = 3
                            game_speed[1] = 7
                
                screen.fill([0, 0, 0])
                screen.blit(deadText, [SCREEN_W / 2 - (deadText.get_width() / 2), SCREEN_H / 4])
                screen.blit(scoreTxt, [SCREEN_W / 2 - (scoreTxt.get_width() / 2), SCREEN_H / 4 + (2 * deadText.get_height())])
                screen.blit(deadCont, [SCREEN_W / 2 - (deadCont.get_width() / 2), SCREEN_H / 2])
                screen.blit(deadQuit, [SCREEN_W / 2 - (deadCont.get_width() / 2), SCREEN_H / 2 + deadCont.get_height() * 2])
                pygame.display.update()

if __name__ == "__main__":
    main()