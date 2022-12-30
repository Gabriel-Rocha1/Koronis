import pygame
import random


class Player:
    def __init__(self, size, screen_width, screen_height):
        self.size = size

        self.sprite = pygame.transform.scale(
            pygame.image.load('data/gfx/player.png'), 
            (self.size, self.size))
        
        self.invencible_sprite = pygame.transform.scale(
            pygame.image.load('data/gfx/invencible.png'), 
            (self.size, self.size))

        self.thrust = pygame.transform.scale(
            pygame.image.load('data/gfx/thrust' + str(1) + '.png'), 
            (self.size, self.size))

        self.thrustCount = 1

        heart = pygame.image.load('data/gfx/heart.png')
        self.heart = pygame.transform.scale(heart, (32, 32))

        self.position = pygame.Vector2()
        self.position.xy = (screen_width / 2) - self.sprite.get_width(), screen_height - self.sprite.get_height() - 10
        self.speed = 3

        self.default_hitbox = pygame.Rect(
            self.position.x, 
            self.position.y, 
            self.sprite.get_width() - (self.sprite.get_width() / 2), 
            self.sprite.get_height())

        self.hitbox = self.default_hitbox

        self.reloadBar = pygame.Rect(
            self.position.x + (self.sprite.get_width() / 4),
            self.position.y - 20,
            self.sprite.get_width() - (self.sprite.get_width() / 2),
            6)
        
        self.lives = 3
        self.invencible = False
        self.score = 0

    def update_hitbox(self):
        self.hitbox.left = self.position.x + (self.sprite.get_width() / 4)
        self.hitbox.top  = self.position.y
    
    def update_reloadBar(self):
        self.reloadBar.left = self.position.x + (self.sprite.get_width() / 4)
        self.reloadBar.top  = self.position.y - 20

    def tilt(self, sprite, direction):
        if sprite == self.sprite or self.invencible_sprite:
            self.tilt_hitbox(direction)
        if direction == 'right':
            return pygame.transform.rotozoom(sprite, -45, 1)
        if direction == 'left':
            return pygame.transform.rotozoom(sprite,  45, 1)
        
    def tilt_hitbox(self, direction):
        self.hitbox = self.sprite.get_rect()
        if direction == 'right':
            self.hitbox.left = self.position.x + (self.sprite.get_width()  / 4)
            self.hitbox.top  = self.position.y + (self.sprite.get_height() / 4)
        if direction == 'left':
            self.hitbox.left = self.position.x + (self.sprite.get_width()  / 4)
            self.hitbox.top  = self.position.y + (self.sprite.get_height() / 4)

    def change_thrust(self):
        if self.thrustCount == 8:
            self.thrustCount = 0
        self.thrust = pygame.image.load('data/gfx/thrust' + str(self.thrustCount + 1) + '.png')
        self.thrust = pygame.transform.scale(self.thrust, (self.size, self.size))
        self.thrustCount += 1


class Nuke:
    def __init__(self, player):
        self.size = 50
        self.sprite_offset = self.size / 5
        self.sprite = pygame.transform.scale(
            pygame.image.load('data/gfx/nuke.png'), 
            (self.size, self.size))

        self.position = pygame.Vector2()
        self.position.x = player.position.x + 30
        self.position.y = player.position.y
        self.speed = 15
        self.hitbox = pygame.Rect(
            self.position.x + self.sprite_offset, 
            self.position.y, 
            self.size - (2 * self.sprite_offset), 
            self.size)

    def update_position(self):
        self.position.y -= self.speed

    def update_hitbox(self):
        self.hitbox.top = self.position.y

    def offBounds(self):
        if self.position.y < 0:
            return True
        return False


class Astro:
    def __init__ (self, name, size, game_speed, screen_width):
        # Sprite
        self.size = random.randint(size[0], size[1])
        self.sprite = pygame.transform.scale(
            pygame.image.load('data/gfx/' + str(name) + str(random.randint(1,3)) + '.png'), 
            (self.size, self.size))

        # Physics
        self.position = pygame.Vector2()
        self.position.y = random.randint(-200, -100)
        self.position.x = random.randint(0, screen_width - self.size)
        self.speed = random.uniform(game_speed[0], game_speed[1])
        self.hitbox = pygame.Rect(self.position.x, self.position.y, self.sprite.get_width(), self.sprite.get_height())

        # Propreties:
        self.isDestructible = True
    
    def update_position(self):
        self.position.y += self.speed

    def update_hitbox(self):
        self.hitbox.left = self.position.x
        self.hitbox.top  = self.position.y

    def offBounds(self, screen_height):
        if self.position.y > screen_height:
            return True
        return False


class Asteroid (Astro):
    def __init__ (self, size, game_speed, screen_width):
        super().__init__('asteroid', size, game_speed, screen_width)


class Planet (Astro):
    def __init__(self, size, game_speed, screen_width):
        super().__init__('planet', size, game_speed, screen_width)


class BackgroundStar:
    colors = [[255,255,255], [166,168,255], [168,123,255]]

    def __init__ (self, screen_width):
        self.position = pygame.Vector2()
        self.position.xy = [random.randint(0, screen_width), -2]
        self.color = random.choice(self.colors)
        self.size = 1
