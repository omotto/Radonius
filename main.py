import pygame

try:
    import android
except ImportError:
    android = None
try:
    import pygame.mixer as mixer
except ImportError:
    import android.mixer as mixer

import os
import sys
import random
import math
import pygame.gfxdraw

# -----------
# Constantes
# -----------

ADJUST = False

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

TILE_SIZE = 32

IMG_DIR = "images"
SND_DIR = "sounds"
FNT_DIR = "fonts"
MAP_DIR = "maps"

EXPLOSION_GRANDE   = 0
EXPLOSION_MEDIANA  = 1
EXPLOSION_PEQUENYA = 2
IMPACTO            = 3

BONUS_ORANGE       = 0
BONUS_BLUE         = 1

MAX_LIFE           = 10
MAX_LASER_TYPE     = 9

ASTEROIDE_GRANDE   = 0
ASTEROIDE_MEDIANO  = 1
ASTEROIDE_PEQUENYO = 2

BACKGROUND_SPEED   = 1

SIMPLE             = 0

# ------------------------------
# Funciones globales al programa
# ------------------------------

def load_image(nombre, dir_imagen, adjust = ADJUST):
    # Encontramos la ruta completa de la imagen
    ruta = os.path.join(dir_imagen, nombre)
    try:
        image = pygame.image.load(ruta)
    except:
        print "Error, no se puede cargar la imagen: ", ruta
        sys.exit(1)
    # Comprobar si la imagen tiene "canal alpha" (como los png)
    image = image.convert_alpha()
    # Ajustar a tamanyo de pantalla
    if adjust == True: 
        image = pygame.transform.scale(image,((image.get_width() * width) / SCREEN_WIDTH, (image.get_height() * height) / SCREEN_HEIGHT) )
    return image

def load_sound(nombre, dir_sonido):
    ruta = os.path.join(dir_sonido, nombre)
    # Intentar cargar el sonido
    try:
        sonido = mixer.Sound(ruta)
    except pygame.error:
        print "No se pudo cargar el sonido:", ruta
        sonido = None
    return sonido

def load_text_font(nombre, dir_fuente, tamanyo):
    ruta = os.path.join(dir_fuente, nombre)
    # Intentar cargar el sonido
    try:
        fuente = pygame.font.Font(ruta, tamanyo)
    except:
        print "Error, no se puede cargar la fuente: ", ruta
        sys.exit(1)  
    return fuente

def load_text_file(nombre, dir_fichero):
    ruta = os.path.join(dir_fichero, nombre)
    # Intentar cargar el fichero
    try:
        archivo = open(ruta, 'rt')
        file = archivo.readlines()
        archivo.close()    
    except:     
        print "Fichero ", ruta, " no encontrado"
        sys.exit(1)  
    return file

def load_level(level):     
    file_map = 'nivel_%d.png' % level
    mapa = load_image(file_map,MAP_DIR, False)
    #mapa = load_text_file(file_map, MAP_DIR)
    if level == 1:
        mixer.music.load(os.path.join(SND_DIR,"od-endorfin.ogg"))
    elif level == 2:
        mixer.music.load(os.path.join(SND_DIR,"od-fs.ogg"))
    elif level == 3:
        mixer.music.load(os.path.join(SND_DIR,"od-green_groove.ogg"))
    elif level == 4:
        mixer.music.load(os.path.join(SND_DIR,"od-irony.ogg"))
    elif level == 5:
        mixer.music.load(os.path.join(SND_DIR,"od-nkpng.ogg"))
    elif level == 6:
        mixer.music.load(os.path.join(SND_DIR,"od-special_s.ogg"))       
    return mapa

def load_sprite_sheet(nombre, dir_fichero, size_x, size_y, adjust = ADJUST):
    images = []
    masks = []
    sprite_sheet = load_image(nombre,dir_fichero, False)
    for y in range(sprite_sheet.get_height()/size_y):
        for x in range(sprite_sheet.get_width()/size_x):
            temp_surface = pygame.Surface((size_x,size_y))
            temp_surface.fill((1, 48, 6))
            temp_surface.set_colorkey((1, 48, 6), pygame.RLEACCEL)
            temp_surface.blit(sprite_sheet, (-x*size_x, -y*size_y))
            image = pygame.transform.scale2x(temp_surface)
             # Ajustar a tamanyo de pantalla
            if adjust == True: 
                image = pygame.transform.scale(image,((image.get_width() * width) / SCREEN_WIDTH, (image.get_height() * height) / SCREEN_HEIGHT) )
            images.append(image)
            masks.append(pygame.mask.from_surface(image))
    return images, masks

def exit():
    pygame.quit()
    sys.exit()

def get_angle(x1, y1, x2, y2):
    angle = math.atan2((x1 - x2), (y1 - y2)) # get the angle in radians
    angle = angle * (180 / math.pi) # convert to degrees
    angle = (angle + 90) % 360 # adjust for a right-facing sprite
    # Tomamos el angulo mas cercano disponible
    angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]
    angle = angles[min(range(len(angles)), key=lambda i: abs(angles[i]-angle))]
    if angle == 360: angle = 0
    return angle

class StarEffect():
    def __init__(self, speed, x, y, size_x, size_y, num, color):    
        self.max = num
        self.speed = speed
        self.color = color
        self.stars = []
        self.x = x
        self.size_x = size_x
        for loop in range(0, self.max):
            self.stars.append([random.randrange(x, x + size_x - 1), random.randrange(y, y + size_y -1)])

    def draw(self, screen):
        for loop in range(0, self.max):
            screen.set_at((int(self.stars[loop][0]), int(self.stars[loop][1])), self.color)
            
    def update(self):
        for loop in range(0, self.max):
            self.stars[loop] = (self.stars[loop][0] - self.speed, self.stars[loop][1])
            if self.stars[loop][0] <= self.x:
                self.stars[loop] = (self.x + self.size_x, self.stars[loop][1])
            
class Background():  
    def __init__(self, nombre, dir_fichero, speed, x):
        self.image = load_image(nombre, dir_fichero)
        self.max_y_fondo = self.image.get_height()
        self.max_x_fondo = self.image.get_width()
        self.speed = speed
        self.x = x
           
    def set_speed(self, speed):
        self.speed = speed
        
    def update(self, screen):
        self.x = self.x + self.speed
        if self.x <= self.max_x_fondo - width:
            screen.blit(self.image, (0, 0), (self.x, 0, width, self.max_y_fondo))
        elif self.x <= self.max_x_fondo:
            screen.blit(self.image, (0, 0), (self.x, 0, self.max_x_fondo - self.x, self.max_y_fondo))
            screen.blit(self.image, (self.max_x_fondo - self.x, 0), (0, 0, self.x - self.max_x_fondo - width, self.max_y_fondo))
        else:
            self.x = 0

class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        self.images, self.masks = load_sprite_sheet("SpaceShip_SpriteSheet.png",IMG_DIR, 32, 16)
        self.index = 2
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = y 
        self.rect.centerx = x 
        self.death = False
        # -----------------------------------
        self.life = MAX_LIFE
        self.laser_try = 0
        self.laser_try_max = 10
        self.current_laser_type = 0
        # -----------------------------------
        self.laser_sound = load_sound("simplylaser.wav", SND_DIR)
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = load_sound("explosion.wav", SND_DIR)
        self.explosion_sound.set_volume(0.5)        
        self.impacto_sound = load_sound("impacto.wav", SND_DIR)
        self.impacto_sound.set_volume(0.1)      
        
    def update(self, dx, dy, touch):
        # Colision entre Laser Enemigo y Player
        if pygame.sprite.groupcollide(enemy_laser_sprites, player_sprite, True, False):
            self.life -= 1
            if self.life == 0:
                self.kill()
                explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, EXPLOSION_MEDIANA))
                self.explosion_sound.play()  
            else:
                explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, IMPACTO))
                self.impacto_sound.play()                 
        # Movement
        centery = self.rect.centery
        centerx = self.rect.centerx
        if android:
            # IMPLEMENTAR TECLADO ANDROID
            if touch == True:
                if dy > 10: dy = 10
                if dx > 10: dy = 10
                if dy < -10: dy = -10
                if dx < -10: dy = -10
                centery -= dy
                centerx -= dx
                if (dy < 0):
                    if (self.index < 4): self.index += 0.5
                    if (self.index > 4) and (self.index < 9): self.index += 0.5
                elif (dy > 0):
                    if (self.index > 0) and (self.index < 4): self.index -= 0.5
                    if (self.index > 5): self.index -= 0.5
                elif (dx != 0):
                    if (self.index < 5): self.index += 5
            else:
                if (self.index > 4):
                    self.index -= 5
                else:
                    if (self.index > 2): self.index -= 0.5
                    if (self.index < 2): self.index += 0.5
        else:
            key = pygame.key.get_pressed()
            # Calcula Image
            if key[pygame.K_UP]:
                centery -=  5
                if (self.index < 4): self.index += 0.5
                if (self.index > 4) and (self.index < 9): self.index += 0.5
            if key[pygame.K_DOWN]:
                centery +=  5
                if (self.index > 0) and (self.index < 4): self.index -= 0.5
                if (self.index > 5): self.index -= 0.5
            if key[pygame.K_RIGHT]:
                centerx += 5
                if (self.index < 5): self.index += 5
            if key[pygame.K_LEFT]:
                centerx -= 5
                if (self.index < 5): self.index += 5
            if not(key[pygame.K_LEFT]) and not(key[pygame.K_RIGHT]) and not(key[pygame.K_DOWN]) and not(key[pygame.K_UP]):
                if (self.index > 4):
                    self.index -= 5
                else:
                    if (self.index > 2): self.index -= 0.5
                    if (self.index < 2): self.index += 0.5
        self.image = self.images[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx
        # Restrictions
        self.rect.bottom = min(self.rect.bottom, height)
        self.rect.top = max(self.rect.top, 0)
        self.rect.right = min(self.rect.right, width)
        self.rect.left = max(self.rect.left, 0)
        # Shot
        if android or key[pygame.K_z]:
            self.laser_try = self.laser_try + 1
            if self.laser_try == self.laser_try_max:
                self.laser_try = 0
                if self.current_laser_type == 0:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo0.png", 0, 15))
                    self.laser_sound.play()   
                elif self.current_laser_type == 1:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo0.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    self.laser_sound.play()   
                elif self.current_laser_type == 2:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo45.png", 45, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo0.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo315.png", 315, 15))
                    self.laser_sound.play()   
                elif self.current_laser_type == 3:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo45.png", 45, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "DualLaser.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo315.png", 315, 15))
                    self.laser_sound.play()   
                elif self.current_laser_type == 4 or self.current_laser_type == 5:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo45.png", 45, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "DualLaser.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo315.png", 315, 15))
                    self.laser_sound.play()   
                elif self.current_laser_type == 6:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "DualLaser.png", 0, 15))
                    self.laser_sound.play()   
                    for shield in shield_sprites:
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "SimplyLaser.png", 0, 15))
                        self.laser_sound.play()   
                elif self.current_laser_type == 7:
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "laser_plus_plus_plus.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    self.laser_sound.play()   
                    for shield in shield_sprites:
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "laser_plus_plus.png", 0, 15))
                        self.laser_sound.play()           
                elif self.current_laser_type == 8:                    
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo45.png", 45, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "laser_plus_plus_plus_plus.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo315.png", 315, 15))                    
                    for shield in shield_sprites:
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "MisilAngulo45.png", 45, 15))
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "laser_plus_plus_plus.png", 0, 15))
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "MisilAngulo315.png", 315, 15))
                        self.laser_sound.play()                     
                elif self.current_laser_type == 9:                    
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo45.png", 45, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo30.png", 30, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "SuperLaser.png", 0, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo330.png", 330, 15))
                    laser_sprites.add(Laser((self.rect.right, self.rect.centery), "MisilAngulo315.png", 315, 15))                    
                    for shield in shield_sprites:
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "MisilAngulo45.png", 45, 15))
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "MisilAngulo30.png", 30, 15))
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "laser_plus_plus_plus.png", 0, 15))
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "MisilAngulo330.png", 330, 15))
                        laser_sprites.add(Laser((shield.rect.right, shield.rect.centery), "MisilAngulo315.png", 315, 15))
                        self.laser_sound.play()                       
                        
    def is_death(self):
        return self.death
    
    def set_bonus(self, bonus):
        if (bonus == BONUS_BLUE) and (self.life < MAX_LIFE): 
            self.life += 1
        if (bonus == BONUS_ORANGE) and (self.current_laser_type < MAX_LASER_TYPE):
            self.current_laser_type += 1
            if self.current_laser_type == 5:
                shield_sprites.add(Shield())                 
            
# Clase Laser:
# Se encarga de gestionar todos los lasers, balas, rayos gamma que se lanzan 
# durante la partida y admite los angulos de disparo siguientes: 0, 30, 45, 60,
# 90,... en los cuatro cuadrantes.
class Laser(pygame.sprite.Sprite):
    def __init__(self, position, image, angle, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale2x(load_image(image,IMG_DIR))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.angle = angle
        self.high_speed = speed
        self.low_speed = speed / 2
    
    def update(self):
        if self.angle == 0:
            if self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(self.high_speed, 0)    
        elif self.angle == 90:
            if self.rect.top < 0: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(0, -self.high_speed)    
        elif self.angle == 270:    
            if self.rect.bottom > height: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(0, +self.high_speed)    
        elif self.angle == 45:    
            if self.rect.top < 0 or self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(+self.low_speed, -self.low_speed)    
        elif self.angle == 30:    
            if self.rect.top < 0 or self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(+self.high_speed, -self.low_speed) 
        elif self.angle == 60:    
            if self.rect.top < 0 or self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(+self.low_speed, -self.high_speed)                 
        elif self.angle == 315:    
            if self.rect.bottom > height or self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(+self.low_speed, +self.low_speed)    
        elif self.angle == 330:    
            if self.rect.bottom > height or self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(+self.high_speed, +self.low_speed)    
        elif self.angle == 300:    
            if self.rect.bottom > height or self.rect.right > width: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(+self.low_speed, +self.high_speed)               
        # ------------------------------
        elif self.angle == 180:
            if self.rect.right < 0: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.high_speed, 0)    
        elif self.angle == 135:    
            if self.rect.left < 0 or self.rect.top < 0: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.low_speed, -self.low_speed)    
        elif self.angle == 225:    
            if self.rect.left < 0 or self.rect.bottom > height: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.low_speed, +self.low_speed)    
        elif self.angle == 120:    
            if self.rect.left < 0 or self.rect.top < 0: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.low_speed, -self.high_speed)    
        elif self.angle == 240:    
            if self.rect.left < 0 or self.rect.bottom > height: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.low_speed, +self.high_speed)   
        elif self.angle == 150:    
            if self.rect.left < 0 or self.rect.top < 0: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.high_speed, -self.low_speed)    
        elif self.angle == 210:    
            if self.rect.left < 0 or self.rect.bottom > height: # Si se sale de la pantalla, desaparece.
                self.kill()
            else:
                self.rect.move_ip(-self.high_speed, +self.low_speed)   
    
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        self.type = type
        if self.type == 0:
            self.images, self.masks = load_sprite_sheet("enemy_A.png",IMG_DIR, 16, 16)
            self.life = 4
        elif self.type == 1:
            self.images, self.masks = load_sprite_sheet("enemy_B.png",IMG_DIR, 16, 17)
            self.life = 4
        elif self.type == 2:
            self.images, self.masks = load_sprite_sheet("enemy_C.png",IMG_DIR, 14, 16)
            self.life = 4
        elif self.type == 3:
            self.images, self.masks = load_sprite_sheet("enemy_D.png",IMG_DIR, 18, 16)            
            self.life = 4
        elif self.type == 4:
            self.images, self.masks = load_sprite_sheet("enemy_DD.png",IMG_DIR, 18, 16)
            self.life = 4
        elif self.type == 5:
            self.images, self.masks = load_sprite_sheet("enemy_E.png",IMG_DIR, 16, 16)
            self.life = 4
        elif self.type == 6:
            self.images, self.masks = load_sprite_sheet("enemy_F.png",IMG_DIR, 96, 64)
            self.life = 10
        elif self.type == 7:
            self.images, self.masks = load_sprite_sheet("enemy_G.png",IMG_DIR, 32, 32)
            self.life = 4
        elif self.type == 8:
            self.images, self.masks = load_sprite_sheet("enemy_GG.png",IMG_DIR, 32, 32)
            self.life = 4
        elif self.type == 9:
            self.images, self.masks = load_sprite_sheet("enemy_H.png",IMG_DIR, 32, 30)
            self.life = 4
        elif self.type == 10:
            self.images, self.masks = load_sprite_sheet("enemy_HH.png",IMG_DIR, 32, 30)            
            self.life = 4
        elif self.type == 11:
            self.images, self.masks = load_sprite_sheet("enemy_I.png",IMG_DIR, 16, 17)            
            self.life = 4
        elif self.type == 12:
            self.images, self.masks = load_sprite_sheet("enemy_J.png",IMG_DIR, 18, 20)            
            self.life = 4            
        elif self.type == 13:
            self.images, self.masks = load_sprite_sheet("enemy_K.png",IMG_DIR, 14, 512)            
            self.life = 9999999999            
        elif self.type == 14:
            self.images, self.masks = load_sprite_sheet("enemy_L.png",IMG_DIR, 32, 31)            
            self.life = 4  
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = y + (self.image.get_height() / 2.0)
        self.rect.centerx = x + (self.image.get_width() / 2.0)
        self.angle = 90
        # depende del tipo de enemigo....
        self.laser_bool = True
        self.laser_try = 0
        self.laser_try_max = 100
        self.laser_sound = load_sound("simplylaser.wav", SND_DIR)
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = load_sound("explosion.wav", SND_DIR)
        self.explosion_sound.set_volume(0.5)
        self.impacto_sound = load_sound("impacto.wav", SND_DIR)
        self.impacto_sound.set_volume(0.1)           
                
    def update(self):
        # ----------------------------------------------------------------------
        # Comprobacion de si morimos
        # ----------------------------------------------------------------------
        #if self.rect.right < 0 or self.rect.left > width or self.rect.bottom < 0 or self.rect.top > height:
        #if self.rect.right < 0 or self.rect.bottom < 0 or self.rect.top > height:
        if self.rect.centerx <= 0 or self.rect.bottom < 0 or self.rect.top > height:
            self.kill()
        # Colision entre Player Laser y Enemigo OR Colision entre Player y Enemigo OR Colision entre Shield y Enemigo
        temporal = pygame.sprite.Group()
        temporal.add(self)        
        if pygame.sprite.groupcollide(temporal, laser_sprites, False, True) or pygame.sprite.groupcollide(temporal, shield_sprites, False, False):
            self.life -= 1
            if self.life == 0:
                self.kill()
                explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, EXPLOSION_MEDIANA))
                self.explosion_sound.play()   
                if (random.random() < 0.2):
                    bonus_sprites.add(Bonus(self.rect.centerx, self.rect.centery))
                # Es un caso especial donde el enemigo 13 depende de la existencia del 12
                if self.type == 12: 
                    for enemy in enemy_sprites:
                        if enemy.get_type() == 13:
                            enemy.kill()
            else:
                explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, IMPACTO))
                self.impacto_sound.play() 
        if pygame.sprite.groupcollide(temporal, player_sprite, True, True):
            explosion_sprites.add(Explosion(player.rect.centerx, player.rect.centery, EXPLOSION_MEDIANA))
            self.impacto_sound.play() 
        # ----------------------------------------------------------------------
        # Movement
        # ----------------------------------------------------------------------
        centery = self.rect.centery
        centerx = self.rect.centerx
        ship_angle = get_angle(centerx, centery, player.rect.centerx, player.rect.centery)
        if self.type == 0:
            self.angle += 5
            if (self.angle > 360): self.angle -=360
            centerx = centerx - 2
            centery = centery + round(4*math.sin(math.radians(self.angle)))
        elif self.type == 1:
            if centerx > width*7/8: 
                centerx -= 2
            else:
                self.angle += 2
                if (self.angle > 360): self.angle -=360
                centery = centery + round(6*math.sin(math.radians(self.angle)))
        elif self.type == 2:
            centerx -= 2
            if centerx < width:                
                self.angle += 2
                if (self.angle > 360): self.angle -=360
                centerx = centerx + round(5*math.cos(math.radians(self.angle)))
                centery = centery + round(5*math.sin(math.radians(self.angle)))
        elif self.type == 5 or self.type == 14:
            if ship_angle == 0:
                centerx = centerx + 2
            elif ship_angle == 30:   
                centerx = centerx + 2
                centery = centery - 1                
            elif ship_angle == 45:                    
                centerx = centerx + 1
                centery = centery - 1
            elif ship_angle == 60:   
                centerx = centerx + 1
                centery = centery - 2                
            elif ship_angle == 90:
                centery = centery - 2
            elif ship_angle == 120:  
                centerx = centerx - 1
                centery = centery - 2
            elif ship_angle == 135:    
                centerx = centerx - 1
                centery = centery - 1                
            elif ship_angle == 150:
                centerx = centerx - 2
                centery = centery - 1
            elif ship_angle == 180:
                centerx = centerx - 2
            elif ship_angle == 210:    
                centerx = centerx - 2
                centery = centery + 1                
            elif ship_angle == 225:                    
                centerx = centerx - 1
                centery = centery + 1                
            elif ship_angle == 240:                    
                centerx = centerx - 1
                centery = centery + 2                
            elif ship_angle == 270:    
                centery = centery + 2
            elif ship_angle == 300:                    
                centerx = centerx + 1
                centery = centery + 2                
            elif ship_angle == 315:    
                centerx = centerx + 1
                centery = centery + 1                
            elif ship_angle == 330:    
                centerx = centerx + 2
                centery = centery + 1   
        elif self.type == 6:
            if centerx > (width*3)/4:
                centerx = centerx - BACKGROUND_SPEED
            if centery > player.rect.centery and self.rect.top > 0:
                centery -= 1
            if centery < player.rect.centery and self.rect.bottom < height:
                centery += 1                
        elif self.type == 3 or self.type == 4 or self.type == 7 or self.type == 8 or self.type == 9 or self.type == 10 or self.type == 12 or self.type == 13:
            centerx = centerx - BACKGROUND_SPEED # Velocidad de movimiento del background
        elif self.type == 11:
            centerx = centerx - BACKGROUND_SPEED
            if centery > height/8 and centerx < (width*2)/3:
                centery = centery - BACKGROUND_SPEED/2.0
              
        # ----------------------------------------------------------------------            
        # Calcula Image
        # ----------------------------------------------------------------------
        if (self.type < 3) or (self.type == 11) or (self.type == 14):
            if self.index < len(self.images)-1: 
                self.index += 0.2 
            else: 
                self.index = 0
        elif self.type == 3:
            if ship_angle <= 180:
                self.index = [180,150,135,120,90,60,45,30,0].index(ship_angle)
        elif self.type == 4:
            if ship_angle >= 180 or ship_angle == 0:
                self.index = [180,210,225,240,270,300,315,330,0].index(ship_angle)
        elif self.type == 5:
            self.index = [180,150,135,120,90,60,45,30,0,330,315,300,270,240,225,210].index(ship_angle)
        elif self.type >= 7 and self.type <= 10:
            if centerx  < (width * 3) / 4:
                if self.index < len(self.images)-1: 
                    self.index += 0.2 
        elif (self.type == 13):
            if self.index < len(self.images)-1: 
                self.index += 0.5 
            else: 
                self.index = 0                    
        self.image = self.images[int(self.index)]                
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx
        # ----------------------------------------------------------------------
        # Enemy Shots
        # ----------------------------------------------------------------------
        self.laser_try = self.laser_try + 1
        if self.laser_try == self.laser_try_max:
            self.laser_try = 0
            shot_angle = get_angle(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
            if ((((self.type > 0 and self.type < 3) or self.type == 11) and (shot_angle >= 90) and (shot_angle <= 270)) or 
                ((self.type == 3) and (shot_angle >= 0) and (shot_angle <= 180)) or 
                ((self.type == 4) and (shot_angle >= 180) or (shot_angle == 0))):
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.centery),"bala_enemiga0.png", shot_angle, 5))
                self.laser_sound.play()   
            elif self.type == 7 and self.index >= len(self.images)-1:
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga1.png", 45, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga1.png", 60, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga1.png", 90, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga1.png", 120, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga1.png", 135, 5))
                self.laser_sound.play()                       
            elif self.type == 8 and self.index >= len(self.images)-1:                        
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga1.png", 225, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga1.png", 240, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga1.png", 270, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga1.png", 300, 5))
                enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga1.png", 315, 5))
                self.laser_sound.play()  
            elif self.type == 9 and self.index >= len(self.images)-1:
                enemy_sprites.add(Enemy(self.rect.centerx, self.rect.top, 5))
                self.laser_sound.play()                       
            elif self.type == 10 and self.index >= len(self.images)-1:                        
                enemy_sprites.add(Enemy(self.rect.centerx, self.rect.bottom, 5))
                self.laser_sound.play()                 
            elif self.type == 6:                                        
                if self.laser_bool == True:
                    enemy_laser_sprites.add(Laser((self.rect.left, self.rect.centery+10),"bala_enemiga3.png", 180, 5))
                    enemy_laser_sprites.add(Laser((self.rect.left, self.rect.centery-10),"bala_enemiga3.png", 180, 5))
                    self.laser_sound.play()                      
                    self.laser_bool = False
                else:
                    enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga3.png", 180, 5))
                    enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga3.png", 180, 5))
                    self.laser_sound.play()
                    self.laser_bool = True
            elif self.type == 12:
                if self.laser_bool == True:
                    enemy_sprites.add(Enemy(self.rect.centerx, self.rect.centery+100, 13))
                    self.laser_bool = False
                    
    def get_type(self):        
        return self.type
                
class FinalEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        self.type = type
        if self.type == 0:
            self.images, self.masks = load_sprite_sheet("final_enemy1.png",IMG_DIR, 135, 138)
            self.life = 100
        self.index = 0
        self.image = self.images[self.index]
        self.mask = self.masks[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        self.angle = 90
        # depende del tipo de enemigo....
        self.laser_cnt = 0
        self.laser_try = 0
        self.laser_try_max = 10
        self.laser_sound = load_sound("simplylaser.wav", SND_DIR)
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = load_sound("explosion.wav", SND_DIR)
        self.explosion_sound.set_volume(0.5)
        self.impacto_sound = load_sound("impacto.wav", SND_DIR)
        self.impacto_sound.set_volume(0.1)           
                
    def update(self):
        # ----------------------------------------------------------------------
        # Comprobacion de si morimos
        # ----------------------------------------------------------------------
        if self.rect.centerx <= 0 or self.rect.bottom < 0 or self.rect.top > height:
            self.kill()
        # Colision entre Player Laser y Enemigo OR Colision entre Player y Enemigo OR Colision entre Shield y Enemigo
        for laser in laser_sprites:
            if pygame.sprite.collide_mask(laser, self) != None:
                laser.kill()
                self.life -= 1
                if self.life == 0:
                    self.kill()
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.right, self.rect.centery, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.left, self.rect.centery, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.top, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.bottom, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.left, self.rect.top, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.right, self.rect.top, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.left, self.rect.bottom, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.right, self.rect.bottom, EXPLOSION_GRANDE))
                    self.explosion_sound.play()   
                else:
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, IMPACTO))
                    self.impacto_sound.play() 
        for laser in shield_sprites:                    
            if pygame.sprite.collide_mask(laser, self) != None:
                self.life -= 1
                if self.life == 0:
                    self.kill()
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.right, self.rect.centery, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.left, self.rect.centery, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.top, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.bottom, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.left, self.rect.top, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.right, self.rect.top, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.left, self.rect.bottom, EXPLOSION_GRANDE))
                    explosion_sprites.add(Explosion(self.rect.right, self.rect.bottom, EXPLOSION_GRANDE))
                    self.explosion_sound.play()   
                else:
                    explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, IMPACTO))
                    self.impacto_sound.play() 
        if pygame.sprite.collide_mask(player, self) != None:
            explosion_sprites.add(Explosion(player.rect.centerx, player.rect.centery, EXPLOSION_PEQUENYA))   
            self.explosion_sound.play()
            player.kill()
        # ----------------------------------------------------------------------
        # Movement
        # ----------------------------------------------------------------------
        centery = self.rect.centery
        centerx = self.rect.centerx
        if self.type == 0:
            if centerx > width*3/4:
                centerx -= 2
            else:
                self.angle += 2
                if (self.angle > 360): self.angle -=360
                centery = centery + round(5*math.sin(math.radians(self.angle)))
        # ----------------------------------------------------------------------            
        # Calcula Image
        # ----------------------------------------------------------------------
        if (self.type == 0):
            if centerx <= width*3/4:
                if self.index < len(self.images)-1 and self.laser_cnt < 100: 
                    self.index += 0.1 
                elif self.laser_cnt >= 100 and self.index > 0:
                    self.index -= 0.1 
        self.image = self.images[int(self.index)]                
        self.mask = self.masks[int(self.index)]                
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx
        # ----------------------------------------------------------------------
        # Enemy Shots
        # ----------------------------------------------------------------------
        if centerx <= width*3/4: 
            self.laser_try = self.laser_try + 1
            if self.laser_try == self.laser_try_max:
                self.laser_try = 0
                self.laser_cnt += 1
                if self.laser_cnt < 100:
                    enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.top),"bala_enemiga4.png", 180, 5))
                    enemy_laser_sprites.add(Laser((self.rect.centerx, self.rect.bottom),"bala_enemiga4.png", 180, 5))
                    self.laser_sound.play()                      
                elif self.laser_cnt < 200:
                    shot_angle = get_angle(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                    enemy_laser_sprites.add(Laser((self.rect.left, self.rect.centery),"bala_enemiga2.png", shot_angle, 5))
                    self.laser_sound.play()                       
                else:
                    self.laser_cnt = 0
                    
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, type):    
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        self.type = type
        if self.type == EXPLOSION_GRANDE:
            self.images, self.masks = load_sprite_sheet("explosion_grande.png",IMG_DIR, 118, 121)
        elif self.type == EXPLOSION_MEDIANA:
            self.images, self.masks = load_sprite_sheet("explosion_mediana.png",IMG_DIR, 33, 32)            
        elif self.type == EXPLOSION_PEQUENYA:
            self.images, self.masks = load_sprite_sheet("explosion_pequenya.png",IMG_DIR, 16, 16)            
        elif self.type == IMPACTO:
            self.images, self.masks = load_sprite_sheet("impacto.png",IMG_DIR, 16, 16)            
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        
    def update(self):
        if self.index < len(self.images)-1: 
            self.index += 0.2 
        else: 
            self.kill()
        centery = self.rect.centery
        centerx = self.rect.centerx
        self.image = self.images[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):    
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        if (random.random() < 0.5):
            self.type = BONUS_BLUE
            self.images, self.masks = load_sprite_sheet("bonus2_sprite_sheet.png",IMG_DIR, 16, 13)            
        else:
            self.type = BONUS_ORANGE
            self.images, self.masks = load_sprite_sheet("bonus_sprite_sheet.png",IMG_DIR, 16, 13)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        self.bonus_sound = load_sound("bonus.wav", SND_DIR)
        self.bonus_sound.set_volume(1) 
        
    def update(self):
        # Miramos si hemos de desaparecer
        #if self.rect.right < 0 or self.rect.bottom < 0 or self.rect.top > height:
        if self.rect.centerx <= 0 or self.rect.bottom < 0 or self.rect.top > height:
            self.kill()
        if pygame.sprite.collide_rect(self, player):
           self.bonus_sound.play()         
           player.set_bonus(self.type)
           self.kill()
        # Calcula imagen a mostrar
        if self.index < 3: 
            self.index += 0.2 
        else: 
            self.index = 0
        # Calcula movimiento
        centery = self.rect.centery
        centerx = self.rect.centerx
        self.image = self.images[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx - BACKGROUND_SPEED 

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, type, angulo):    
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        self.type = type
        if (self.type == ASTEROIDE_GRANDE):
            self.images, self.masks = load_sprite_sheet("asteroide1.png",IMG_DIR, 54, 54)            
        elif (self.type == ASTEROIDE_MEDIANO):
            self.images, self.masks = load_sprite_sheet("asteroide2.png",IMG_DIR, 27, 27)
        elif (self.type == ASTEROIDE_PEQUENYO):
            self.images, self.masks = load_sprite_sheet("asteroide3.png",IMG_DIR, 18, 18)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        self.angulo = angulo
        self.explosion_sound = load_sound("explosion.wav", SND_DIR)
        self.explosion_sound.set_volume(0.5)
        self.impacto_sound = load_sound("impacto.wav", SND_DIR)
        self.impacto_sound.set_volume(0.1)        
        self.life = 10
        
    def update(self):
        # Miramos si hemos de desaparecer
        #if self.rect.right < 0 or self.rect.bottom < 0 or self.rect.top > height:
        if self.rect.centerx <= 0 or self.rect.bottom < 0 or self.rect.top > height or self.rect.left > width*3/2:
            self.kill()
        # Colision entre Player Laser y Enemigo OR Colision entre Player y Enemigo OR Colision entre Shield y Enemigo
        temporal = pygame.sprite.Group()
        temporal.add(self)
        if pygame.sprite.groupcollide(temporal, laser_sprites, False, True) or pygame.sprite.groupcollide(temporal, shield_sprites, False, False):
            self.life -= 1
            if self.life == 0:
                self.kill()
                if (self.type == ASTEROIDE_GRANDE):
                    explosion = EXPLOSION_GRANDE
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 0))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 30))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 45))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 60))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 90))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 120))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 135))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 150))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 180))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 210))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 225))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 240))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 270))  
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 300))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 315))
                    asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_MEDIANO, 330))
                elif (self.type == ASTEROIDE_MEDIANO):    
                    explosion = EXPLOSION_MEDIANA
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 0))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 30))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 45))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 60))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 90))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 120))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 135))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 150))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 180))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 210))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 225))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 240))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 270))  
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 300))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 315))
#                   asteroids_sprites.add(Asteroid(self.rect.centerx, self.rect.centery, ASTEROIDE_PEQUENYO, 330))
#               else:
#                   explosion = EXPLOSION_PEQUENYA
                explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, explosion))
                self.explosion_sound.play()   
            else:
                explosion_sprites.add(Explosion(self.rect.centerx, self.rect.centery, IMPACTO))
                self.impacto_sound.play()   
        if pygame.sprite.groupcollide(temporal, player_sprite, True, True):
            explosion_sprites.add(Explosion(player.rect.centerx, player.rect.centery, EXPLOSION_MEDIANA))
            self.impacto_sound.play()                 
        # Calcula imagen a mostrar
        if self.index < 19: 
            self.index += 0.2 
        else: 
            self.index = 0
        # Calcula movimiento
        centery = self.rect.centery
        centerx = self.rect.centerx
        if self.angulo == 0:
            centerx = centerx + 2
        elif self.angulo == 30:   
            centerx = centerx + 2
            centery = centery - 1                
        elif self.angulo == 45:                    
            centerx = centerx + 1
            centery = centery - 1
        elif self.angulo == 60:   
            centerx = centerx + 1
            centery = centery - 2                
        elif self.angulo == 90:
            centery = centery - 2
        elif self.angulo == 120:  
            centerx = centerx - 1
            centery = centery - 2
        elif self.angulo == 135:    
            centerx = centerx - 1
            centery = centery - 1                
        elif self.angulo == 150:
            centerx = centerx - 2
            centery = centery - 1
        elif self.angulo == 180:
            if (self.type == ASTEROIDE_GRANDE):
                centerx = centerx - 1
            else:
                centerx = centerx - 2
        elif self.angulo == 210:    
            centerx = centerx - 2
            centery = centery + 1                
        elif self.angulo == 225:                    
            centerx = centerx - 1
            centery = centery + 1                
        elif self.angulo == 240:                    
            centerx = centerx - 1
            centery = centery + 2                
        elif self.angulo == 270:    
            centery = centery + 2
        elif self.angulo == 300:                    
            centerx = centerx + 1
            centery = centery + 2                
        elif self.angulo == 315:    
            centerx = centerx + 1
            centery = centery + 1                
        elif self.angulo == 330:    
            centerx = centerx + 2
            centery = centery + 1                
        self.image = self.images[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx    

class Shield(pygame.sprite.Sprite):
    def __init__(self):    
        pygame.sprite.Sprite.__init__(self)
        # Declaramos el listado de sprites del player
        self.images, self.masks = load_sprite_sheet("shield_sprite_sheet.png",IMG_DIR, 24, 25)            
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.centery = player.rect.centery
        self.rect.centerx = player.rect.left - self.rect.width
        self.angle = 90
    def update(self):
        # Calcula imagen a mostrar
        if self.index < 7: 
            self.index += 0.2 
        else: 
            self.index = 0
        # Calcula movimiento
        centery = self.rect.centery
        centerx = self.rect.centerx
        self.angle += 10
        if (self.angle > 360): self.angle -=360
        centerx = player.rect.centerx + 60 * math.cos(math.radians(self.angle))
        centery = player.rect.centery + 60 * math.sin(math.radians(self.angle))
        self.image = self.images[int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.centery = centery
        self.rect.centerx = centerx
        
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, name_tile, back_front, static_dynamic, movement_type, size_x, size_y):
        pygame.sprite.Sprite.__init__(self)
        self.back_front = back_front
        self.static_dynamic = static_dynamic
        self.movement_type = movement_type
        if static_dynamic == False:
            self.images, self.masks = load_sprite_sheet(name_tile, IMG_DIR, size_x, size_y)    
            self.index = 0
            self.image = self.images[self.index]
            self.mask = self.masks[self.index]
        else:
            self.image = load_image(name_tile, IMG_DIR)
            self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centery = y + (self.image.get_height() / 2.0)
        self.rect.centerx = x + (self.image.get_width() / 2.0)
        self.explosion_sound = load_sound("explosion.wav", SND_DIR)
        self.explosion_sound.set_volume(0.5)
        self.impacto_sound = load_sound("impacto.wav", SND_DIR)
        self.impacto_sound.set_volume(0.1)
        
    def update(self):
        # Miramos si hemos de desaparecer
        if self.rect.right <= 0 or self.rect.bottom < 0 or self.rect.top > height:
            self.kill()
        # Comprobar con mascaras si hay colision
        if self.back_front == False:
            # Colision entre Laser y Tile
            for laser in laser_sprites:
                if pygame.sprite.collide_mask(laser, self) != None:
                    explosion_sprites.add(Explosion(laser.rect.centerx, laser.rect.centery, IMPACTO))   
                    self.impacto_sound.play()
                    laser.kill()
            for laser in enemy_laser_sprites:                    
                if pygame.sprite.collide_mask(laser, self) != None:
                    explosion_sprites.add(Explosion(laser.rect.centerx, laser.rect.centery, IMPACTO))   
                    self.impacto_sound.play()
                    laser.kill()
            # Colision entre Player y Tile
            if pygame.sprite.collide_mask(player, self) != None:
                explosion_sprites.add(Explosion(player.rect.centerx, player.rect.centery, EXPLOSION_PEQUENYA))   
                self.explosion_sound.play()
                player.kill()
        if self.static_dynamic == False:
            if self.index < len(self.images)-1: 
                self.index += 0.1 
            else: 
                self.index = 0 
            centery = self.rect.centery
            centerx = self.rect.centerx
            self.image = self.images[int(self.index)]
            self.mask = self.masks[int(self.index)]
            self.rect = self.image.get_rect()
            self.rect.centery = centery
            self.rect.centerx = centerx            
        # Calcula movimiento
        if self.movement_type == SIMPLE:
            self.rect.centerx -= BACKGROUND_SPEED

def update_map(mapa, position, adjust = ADJUST):
    if (position % 32 == 0) and ((position / 32) < mapa.get_width()):
        xx = position / 32
        for yy in range(mapa.get_height()):
            color = mapa.get_at((xx, yy))
            y = yy * 32
            if adjust == True: y = (y * height) / SCREEN_HEIGHT
            if   color == (255,0,0):
                asteroids_sprites.add(Asteroid(width*9/8, y, ASTEROIDE_MEDIANO, 180))
            elif color == (0,200,0):
                asteroids_sprites.add(Asteroid(width*9/8, y, ASTEROIDE_GRANDE, 180))
            elif color == (0,0,255):
                enemy_sprites.add(Enemy(width*9/8, y, 0))
            elif color == (255,255,0):
                enemy_sprites.add(Enemy(width*9/8, y, 1))
            elif color == (255,0,255):
                enemy_sprites.add(Enemy(width*9/8, y, 2))
            elif color == (255,200,0):
                enemy_sprites.add(Enemy(width*9/8, y+16, 3))
            elif color == (63,72,204):
                enemy_sprites.add(Enemy(width*9/8, y-16, 4))
            elif color == 7:
                enemy_sprites.add(Enemy(width*9/8, y, 5))
            elif color == 8:
                enemy_sprites.add(Enemy(width*9/8, y, 6))
            elif color == 9:
                enemy_sprites.add(Enemy(width*9/8, y, 7))
            elif color == 10:
                enemy_sprites.add(Enemy(width*9/8, y, 8))
            elif color == 11:
                enemy_sprites.add(Enemy(width*9/8, y, 9))       
            elif color == 12:
                enemy_sprites.add(Enemy(width*9/8, y, 10))             
            elif color == (0,150,0):
                enemy_sprites.add(Enemy(width*9/8, y, 11))             
            elif color == 14:
                enemy_sprites.add(Enemy(width*9/8, y, 12))   
            elif color == 15:
                enemy_sprites.add(Enemy(width*9/8, y, 14))  
 
            elif color == (200,0,0):
                tiles_sprites.add(Tile(width*9/8, y, "tile100_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == (125,125,125):
                tiles_sprites.add(Tile(width*9/8, y, "tile101_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == (100,100,100):
                tiles_sprites.add(Tile(width*9/8, y, "tile102_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == (0,100,0):
                tiles_sprites.add(Tile(width*9/8, y, "tile103_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == 21:
                tiles_sprites.add(Tile(width*9/8, y, "tile104_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == (220,220,220):
                tiles_sprites.add(Tile(width*9/8, y, "tile105_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == 21:
                tiles_sprites.add(Tile(width*9/8, y, "tile106_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == 21:
                tiles_sprites.add(Tile(width*9/8, y, "tile107_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == 21:
                tiles_sprites.add(Tile(width*9/8, y, "tile108_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == 21:
                tiles_sprites.add(Tile(width*9/8, y, "tile109_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
            elif color == (150,150,150):
                tiles_sprites.add(Tile(width*9/8, y, "tile110_32_32_front_static.png", False, True, SIMPLE, 32, 32))                
                
                
#            elif color == 16:
#                tiles_sprites.add(Tile(width*3/2, y, "tile00_320_120_front_dynamic.png", False, False, SIMPLE, 320, 120))
#            elif color == 17:
#                tiles_sprites.add(Tile(width*3/2, y, "tile01_48_224_back_static.png", False, True, SIMPLE, 48, 224))
#            elif color == 18:
#                tiles_sprites.add(Tile(width*3/2, y, "tile02_229_224_back_static.png", False, True, SIMPLE, 229, 224))                

#            elif color == 20:
#                tiles_sprites.add(Tile(width*3/2, y, "tile03_228_75_back_static.png", True, True, SIMPLE, 228, 75))                
#            elif color == 21:
#                tiles_sprites.add(Tile(width*3/2, y, "tile04_58_36_back_static.png", True, True, SIMPLE, 58, 36))                

            elif color == (0,0,0):
                final_enemy_sprites.add(FinalEnemy(width*9/8, y, 0))             
                
# ------------------------------
# Funcion principal del juego
# ------------------------------
 
def main():
    pygame.init()
    if android: 
        android.init()	
        android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE) # La tecla de retorno del telefono mapeada como ESC
    
    # Nueva ventana
    global width
    global height
    if android:
        pygame.display.init()
        width = pygame.display.Info().current_w
        height = pygame.display.Info().current_h
    else:
        width = SCREEN_WIDTH
        height = SCREEN_HEIGHT

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("RADONIUS")
    
    # Cargamos los objetos de la clase FONDO PANTALLA
    fondo1 = Background("fondo_espacio4.jpg", IMG_DIR, 0.2, 0)
    fondo2 = Background("fondo_transp.png", IMG_DIR, 0, 0)
    
    estrellas_frente = StarEffect(1.5, 0, 0, width, height*2/3, 100, (255, 255, 255))
    estrellas_atras = StarEffect(0.5, 0, 0, width, height*2/3, 100, (128, 128, 128))
    
    global player
    player = SpaceShip(width/2, height/2)
    
    global player_sprite
    player_sprite = pygame.sprite.RenderPlain((player))
    
    global enemy_sprites
    enemy_sprites = pygame.sprite.RenderPlain()
    
    global final_enemy_sprites
    final_enemy_sprites = pygame.sprite.RenderPlain()
    
    global laser_sprites 
    laser_sprites = pygame.sprite.RenderPlain()

    global enemy_laser_sprites 
    enemy_laser_sprites = pygame.sprite.RenderPlain()

    global explosion_sprites
    explosion_sprites = pygame.sprite.RenderPlain()        

    global bonus_sprites 
    bonus_sprites = pygame.sprite.RenderPlain()        

    global shield_sprites 
    shield_sprites = pygame.sprite.RenderPlain()        
    
    global asteroids_sprites
    asteroids_sprites = pygame.sprite.RenderPlain()        
    
    global tiles_sprites
    tiles_sprites = pygame.sprite.RenderPlain()
      
      
    level = 1
    mapa = load_level(level)
    position = 0
    
    mixer.music.play(-1, 0)
    mixer.music.set_volume(1) 
    
    clock = pygame.time.Clock()

    touch = False
    dx = 0
    dy = 0

    # el bucle principal del juego
    while 1:
               
        move  = False
        
        clock.tick(100)
        
        if android:
            if android.check_pause():
                android.wait_for_resume()
        
        # Posibles entradas del teclado y mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                (x,y) = pygame.mouse.get_pos()
                touch = True
            elif event.type == pygame.MOUSEMOTION:
                if touch == True:
                    (xx,yy) = pygame.mouse.get_pos()
                    dx = x - xx
                    dy = y - yy
                    x = xx
                    y = yy
                    move = True
            elif event.type == pygame.MOUSEBUTTONUP:
                touch = False
        # Actualizamos el mapa
        update_map(mapa, position)
        position += BACKGROUND_SPEED
        
        # Actualizamos los fondos
        fondo1.update(screen)
        fondo2.update(screen)
        estrellas_frente.update()
        estrellas_atras.update()
                
        player.update(dx, dy, move)
        enemy_sprites.update()
        final_enemy_sprites.update()
        asteroids_sprites.update()
        laser_sprites.update()
        enemy_laser_sprites.update()
        explosion_sprites.update()
        bonus_sprites.update()
        shield_sprites.update()
        tiles_sprites.update()

        # -----------------------------
        
        estrellas_frente.draw(screen)
        estrellas_atras.draw(screen)

        tiles_sprites.draw(screen)
        player_sprite.draw(screen)
        enemy_sprites.draw(screen)
        final_enemy_sprites.draw(screen)
        asteroids_sprites.draw(screen)
        laser_sprites.draw(screen)
        enemy_laser_sprites.draw(screen)
        explosion_sprites.draw(screen)
        bonus_sprites.draw(screen)
        shield_sprites.draw(screen)
        
        # -----------------------------
        
        pygame.display.flip()
        
if __name__ == "__main__":
    main()
