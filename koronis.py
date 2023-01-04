import pygame
import random


class Player:
    def __init__(self, size, screen_width, screen_height):
        self.size = size

        normal_sprite = pygame.transform.scale(
            pygame.image.load('data/gfx/player.png'), 
            (self.size, self.size))
        
        invencible_sprite = pygame.transform.scale(
            pygame.image.load('data/gfx/invencible.png'), 
            (self.size, self.size))

        self.sprites = {
            'normal': normal_sprite,
            'tilt_right': pygame.transform.rotozoom(normal_sprite, -45, 1),
            'tilt_left': pygame.transform.rotozoom(normal_sprite, 45, 1),
            
            'invencible': invencible_sprite,
            'inv_tilt_right': pygame.transform.rotozoom(invencible_sprite, -45, 1),
            'inv_tilt_left': pygame.transform.rotozoom(invencible_sprite, 45, 1)
        }

        self.thrust_sprites = [
            pygame.transform.scale(
                pygame.image.load('data/gfx/thrust' + str(i) + '.png'), 
                (self.size, self.size)) 
            for i in range(8)
            ]

        self.right_tilted_thrust = [
            pygame.transform.rotozoom(self.thrust_sprites[i], -45, 1)
            for i in range(8)
        ]

        self.left_tilted_thrust = [
            pygame.transform.rotozoom(self.thrust_sprites[i], 45, 1)
            for i in range(8)
        ]

        self.direction = 'straight'
        self.stopped = True

        self.sprite = self.sprites['normal']        
        self.thrust = self.thrust_sprites[0]

        self.thrust_count = 0

        heart = pygame.image.load('data/gfx/heart.png')
        self.heart = pygame.transform.scale(heart, (32, 32))

        self.position = pygame.Vector2()
        self.position.x = (screen_width / 2) - (self.sprite.get_width() / 2)
        self.position.y = screen_height - self.sprite.get_height() - 10
        
        self.speed = 3

        self.default_hitbox = pygame.Rect(
            self.position.x, 
            self.position.y, 
            self.sprite.get_width() - (self.sprite.get_width() / 2), 
            self.sprite.get_height())

        self.hitbox = self.default_hitbox

        self.reloadbar = pygame.Rect(
            self.position.x + (self.sprite.get_width() / 4),
            self.position.y - 20,
            self.sprite.get_width() - (self.sprite.get_width() / 2),
            6)
        
        self.lives = 3
        self.invencible = False
        self.score = 0

    def update_position(self, keys, screen_size):
        self.position.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.position.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed

        width, height = screen_size

        if self.position.x  > width - self.sprite.get_width():
            self.position.x = width - self.sprite.get_width()
        if self.position.x  < 0:
            self.position.x = 0
        
        if self.position.y  > height - self.sprite.get_height():
            self.position.y = height - self.sprite.get_height()
        if self.position.y  < 0:
            self.position.y = 0

        if (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) > 0:
            self.direction = 'right'
        
        if (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) < 0:
            self.direction = 'left'
        
        if (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) == 0:
            self.direction = 'straight'

        if (keys[pygame.K_DOWN] + keys[pygame.K_UP] + 
            keys[pygame.K_RIGHT] + keys[pygame.K_LEFT]) == 0:
             self.stopped = True
        else:
             self.stopped = False


        self.sprite_rect = self.sprite.get_rect(
            center = [self.position.x, self.position.y])
        
        self.hitbox.left = self.position.x + (self.sprite.get_width() / 4)
        self.hitbox.top  = self.position.y

    def hit(self):
        self.lives = self.lives - 1
        self.invencible = True

        if self.direction == 'straight':
            self.sprite = self.sprites['invencible']
        elif self.direction == 'right':
            self.sprite = self.sprites['inv_tilt_right']
        elif self.direction == 'left':
            self.sprite = self.sprites['inv_tilt_left']

    def update_orientation(self):
        if self.direction == 'straight':
            self.sprite = self.sprites['invencible'] if self.invencible else self.sprites['normal']
            self.thrust = self.thrust_sprites[self.thrust_count]

            self.hitbox = self.default_hitbox
                
        elif self.direction == 'right':
            self.sprite = self.sprites['inv_tilt_right'] if self.invencible else self.sprites['tilt_right']
            self.thrust = self.right_tilted_thrust[self.thrust_count]
           
            # TODO: fix hitbox
            self.hitbox.left = self.position.x + (self.sprite.get_width() / 4)
            self.hitbox.top = self.position.y + (self.sprite.get_height() / 4)

        elif self.direction == 'left':
            self.sprite = self.sprites['inv_tilt_left'] if self.invencible else self.sprites['tilt_left']
            self.thrust = self.left_tilted_thrust[self.thrust_count]

            self.hitbox.left = self.position.x + (self.sprite.get_width() / 4)
            self.hitbox.top = self.position.y + (self.sprite.get_height() / 4)

    def change_thrust(self):        
        if self.direction == 'straight':
            self.thrust = self.thrust_sprites[self.thrust_count]
        elif self.direction == 'right':
            self.thrust = self.right_tilted_thrust[self.thrust_count]
        elif self.direction == 'left':
            self.thrust = self.left_tilted_thrust[self.thrust_count]
        
        self.thrust_count = (self.thrust_count + 1) % 8
    
    def draw(self, screen):
        if not self.stopped:
            if self.direction == 'straight':
                thrust_position = [
                    self.position.x, 
                    self.position.y + self.sprite.get_height()]
            
            elif self.direction == 'right':
                thrust_position = [
                    self.position.x - (self.sprite.get_width() / 2), 
                    self.position.y + (self.sprite.get_height() / 2)]
            
            elif self.direction == 'left':
                thrust_position = [
                    self.position.x + (self.sprite.get_width() / 2), 
                    self.position.y + (self.sprite.get_height() / 2)]

            screen.blit(self.thrust, thrust_position)
        
        screen.blit(self.sprite, self.position)


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

    def out_of_bounds(self):
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
        self.speed = random.uniform(game_speed - 2, game_speed + 2)
        self.hitbox = pygame.Rect(self.position.x, self.position.y, self.sprite.get_width(), self.sprite.get_height())

        # Propreties:
        self.isDestructible = True
    
    def update_position(self):
        self.position.y += self.speed

    def update_hitbox(self):
        self.hitbox.left = self.position.x
        self.hitbox.top  = self.position.y

    def out_of_bounds(self, screen_height):
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

    def __init__ (self, screen_width, screen_height, y = None):
        self.size = 1
        self.speed = random.uniform(0.5, 1.5)

        self.position = pygame.Vector2()
        self.position.x = random.randint(0, screen_width)
        self.position.y = random.randint(0, screen_height) if y is None else y
        self.color = random.choice(self.colors)
    
    def update(self):
        self.position.y += self.speed

    def out_of_bounds(self, screen_height):
        return self.position.y > screen_height

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.size)
