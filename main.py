import pygame
import os

# sprite link https://pixelfrog-assets.itch.io/pixel-adventure-1?download#google_vignette

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bunny Invasion')

#set framerate
clock  = pygame.time.Clock()
FPS = 60

# Game Variables
GRAVITY = 0.75
TILE_SIZE = 40

## action variables
moving_left = False
moving_right = False
shoot = False

# load images
# bullet
bullet_img = pygame.image.load('Sprites/Fire/fire_bullet.png').convert_alpha()


#items
health_box_img = pygame.image.load('Sprites/Fruits/Apple_Animation/0.png').convert_alpha()
ammo_box_img = pygame.image.load('Sprites/Fire/Fire_Ammo/0.png').convert_alpha()

item_boxes = {
  'Health': health_box_img,
  'Ammo': ammo_box_img
}


# define colors
BG= (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN =(0, 255, 0)
BLACK = (0, 0, 0)

# define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def draw_bg():
  screen.fill(BG)
  pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

#################################################################################################

class Soldier(pygame.sprite.Sprite):
  def __init__(self, char_type, x, y, scale, speed, ammo):
    pygame.sprite.Sprite.__init__(self)
    self.alive = True
    self.char_type = char_type 
    self.speed = speed
    self.ammo = ammo
    self.start_ammo = ammo
    self.shoot_cooldown = 0
    self.health = 100
    self.max_health = self.health
    self.direction = 1
    self.vel_y = 0
    self.jump = False
    self.in_air = True
    self.flip = False
    self.animation_list = []
    self.frame_index = 0
    self.action = 0
    self.update_time = pygame.time.get_ticks()

    # load all images for players
    animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Hit']
    for animation in animation_types:
      # reset temporary list of images
      temp_list = []
      num_of_frames = len(os.listdir(f'Sprites/Main_Characters/{self.char_type}/{animation}'))
      for i in range(num_of_frames):
        img = pygame.image.load(f'Sprites/Main_Characters/{self.char_type}/{animation}/{i}.png').convert_alpha()
        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        temp_list.append(img)
      self.animation_list.append(temp_list)

    self.img = self.animation_list[self.action][self.frame_index]
    self.rect = self.img.get_rect()
    self.rect.center = (x, y)

  def update(self):
    self.update_animation()
    self.check_alive()
    # update cooldown
    if self.shoot_cooldown > 0:
      self.shoot_cooldown -= 1

  def move(self, moving_left, moving_right):
    # reset movement
    dx = 0
    dy = 0

    #movement function
    if moving_left:
      dx = -self.speed
      self.flip = True
      self.direction = -1
    if moving_right:
      dx = self.speed
      self.flip = False
      self.direction = 1

    # jump
    if self.jump == True and self.in_air == False:
      self.vel_y = -11
      self.jump = False
      self.in_air = True
    
    #gravity  
    self.vel_y += GRAVITY
    if self.vel_y > 10:
      self.vel_y
    dy += self.vel_y  

    # check floor collision with floor
    if self.rect.bottom + dy > 300:
      dy = 300 - self.rect.bottom  
      self.in_air = False

    # update rectangle position
    self.rect.x += dx
    self.rect.y += dy

  def shoot(self):
      if self.shoot_cooldown == 0 and self.ammo > 0:
        self.shoot_cooldown = 20
        bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
        bullet_group.add(bullet)
        #reduce ammo
        self.ammo -= 1

  def update_animation(self):
    #update animation
    ANIMATION_COOLDOWN = 100
    # update image depending on current frame
    self.img = self.animation_list[self.action][self.frame_index]
    # check if enough time has passed since last update
    if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
      self.update_time = pygame.time.get_ticks()
      self.frame_index += 1
    # loop animation
    if self.frame_index >= len(self.animation_list[self.action]):
      if self.action == 3:
        self.frame_index = len(self.animation_list[self.action]) - 1
        self.rect.y += 50
      else:
        self.frame_index = 0

  def update_action(self, new_action):
    # check if the new action is different from the previous one
    if new_action != self.action:
      self.action = new_action
      # update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def check_alive(self):
    if self.health <= 0:
      self.health = 0
      self.speed = 0
      self.alive = False
      self.update_action(3)

  def draw(self):
    screen.blit(pygame.transform.flip(self.img, self.flip, False),  self.rect)

##################################################################################################

class Flame(pygame.sprite.Sprite):
  def __init__(self, x, y, scale):
    pygame.sprite.Sprite.__init__(self)
    self.images = []
    for num in range(1, 4):
      img = pygame.image.load(f'Sprites/Fire/Flame/{num}.png').convert_alpha()
      img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
      self.images.append(img)
    self.frame_index = 0
    self.image = self.images[self.frame_index]
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    FIRE_SPEED = 4
    #update fire animation
    self.counter += 1
    
    if self.counter >= FIRE_SPEED:
      self.counter = 0
      self.frame_index += 1
      #if the animation is complete then delete flame
      if self.frame_index >= len(self.images):
        self.kill()
      else:
        self.image = self.images[self.frame_index]

########################################################################################

class ItemBox(pygame.sprite.Sprite):
  def __init__(self, item_type, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.item_type = item_type
    self.image = item_boxes[self.item_type]
    self.rect = self.image.get_rect()
    self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

  def update(self):
    ## check for collision against the player
    if pygame.sprite.collide_rect(self, player):
      # check what kind of box it was
      if self.item_type == 'Health':
        player.health += 25
        if player.health > player.max_health:
          player.health = player.max_health
      elif self.item_type == 'Ammo':
        player.ammo += 15
      self.kill()

#################################################################################################

class HealthBar():
  def __init__(self, x, y, health, max_health):
    self.x = x
    self.y = y
    self.health = health
    self.max_health = max_health

  def draw(self, health):
    # update with new health
    self.health = health
    ratio = self.health / self.max_health

    pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
    pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
    pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20) )

#################################################################################################

class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y, direction):
    pygame.sprite.Sprite.__init__(self)
    self.speed = 10
    self.image = bullet_img
    self.timer = 100
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.direction = direction

  def update(self):
    #move bullet
    self.rect.x += (self.direction * self.speed)
    # check if bullet has gone off screen
    if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
      self.kill
    
    # check collision with enemy
    if pygame.sprite.spritecollide(player, bullet_group, False):
      if player.alive:
        player.health -= 5
        self.kill()

    for enemy in enemy_group:
      if pygame.sprite.spritecollide(enemy, bullet_group, False):
        if enemy.alive:
            enemy.health -= 25
            self.kill()

    # fire countdown
    self.timer -= 1
    if self.timer <= 0:
      fire = Flame(self.rect.x, self.rect.y, 0.5)
      flame_group.add(fire)

#################################################################################################

# create sprite groups
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
flame_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 300, 260)
item_box_group.add(item_box)


# character build
player = Soldier('Mask_Dude', 200, 200, 3, 5, 20)
health_bar = HealthBar(10, 10, player.health, player.health)
enemy = Soldier('Bunny', 600, 235, 3, 5, 20)
enemy2 = Soldier('Bunny', 300, 235, 3, 5, 20)

enemy_group.add(enemy)
enemy_group.add(enemy2)

#############################################################################################

run = True
while run:
  clock.tick(FPS)
  draw_bg()
  #health bar
  health_bar.draw(player.health)
  #show health
  draw_text(f'Health: {player.health}%', font, WHITE, 10, 70)
  #show ammo
  draw_text(f'AMMO: ', font, WHITE, 10, 35)
  for x in range(player.ammo):
    screen.blit(ammo_box_img, (135 + (x * 15), 50))


 # drawings
  player.draw()
  item_box_group.draw(screen)
  bullet_group.draw(screen)
  flame_group.draw(screen)

  for enemy in enemy_group:
    enemy.update()
    enemy.draw()


  # update and draw groups
  player.update()
  bullet_group.update()
  item_box_group.update()
  flame_group.update()
  
  
  # update player action
  if player.alive:
    # shoot bullets
    if shoot:
      player.shoot()
    if player.in_air:
      player.update_action(2)
    elif moving_left or moving_right:
      player.update_action(1) # 1 means run
    else:
      player.update_action(0)

  player.move(moving_left, moving_right)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

      
      
      
      #player movement
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_SPACE:
        shoot = True
      if event.key == pygame.K_w and player.alive:
        player.jump = True
      if event.key == pygame.K_ESCAPE:
        run = False

      #player stop movement
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_SPACE:
        shoot = False


  pygame.display.update()

pygame.quit()