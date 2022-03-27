#!/usr/bin/env python
"""
Nota bene: questo esempio è stato copiato, incollato e tradotto dalla repo originale del package "pygame":
https://github.com/pygame/pygame/blob/main/examples/aliens.py

Può essere avviato:
- eseguendo questo "main.py"
- creando un nuovo modulo ed eseguendo:

    from pygame.examples import aliens
    aliens.main()

"""

""" pygame.examples.aliens
Un clone di Space Invaders, un semplice progetto ideale per testare alcune funzionalità di base della libreria PyGame:

* `pg.sprite`, e la differenza tra `Sprite` e `Group`.
* dirty rectangle optimization per migliorare la velocità di processamento.
* musica di sottofondo con `pg.mixer.music`, incluso fadeout
* effetti sonori con `pg.Sound`
* processamento di eventi, gestione della tastiera, gestione del QUIT.
* un `main loop frame` legato ad un clock di gioco con `pg.time.Clock`
* passaggio a schermo pieno (fullscreen).

Controlli
--------
* <- e -> per muoversi
* Barra Spaziatrice per sparare
* `f` per il toggle con il fullscreen
"""

import random
import os

# import dei moduli base di PyGame (d'ora in poi sarà chiamato `pg`)
import pygame as pg

# check per vedere se si è limitati all'uso di BMP (bitmap)
if not pg.image.get_extended():
    # altrimenti, quit forzato
    raise SystemExit("Sorry, extended image module required")


# costanti di gioco
MAX_SHOTS = 2  # numero massimo consentito di proiettili player su schermo
ALIEN_ODDS = 22  # probabilità di comparsa di un nuovo alieno
BOMB_ODDS = 60  # probabilità di comparsa di una bomba
ALIEN_RELOAD = 12  # frame di attesa per la comparsa di un nuovo alieno
SCREENRECT = pg.Rect(0, 0, 640, 480) # Rettangolo di gioco
SCORE = 0 # punteggio

main_dir = os.path.split(os.path.abspath(__file__))[0] # utilizza la prima cartella più esterna come riferimento
# N.B. ogni file sarà preso come join di main_dir, "data", e nome_file

def load_image(file):
    """carica un file immagine, lo prepara per l'uso"""
    file = os.path.join(main_dir, "data", file) # carica dalla cartella "data"
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()


def load_sound(file):
    """carica un suono da utilizzare, lo prepara per l'uso"""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


# GAME OBJECTS : Ogni oggetto del gioco è rappresentato da una classe custom!

# Ogni oggetto possiede una funzione "init" e una "update"
# La funzione "update" viene chiamata ogni frame per modificare stato e posizione dell'oggetto
#
# L'oggetto Player possiede una funzione "move" anziché "update", essendo comandato direttamente.

# Nota aggiuntiva: ogni oggetto estende la classe "pg.sprite.Sprite", e ne chiama l'init in fase iniziale
# inizializza usando "self" e "self.containers", un parametro statico della classe settato successivamente

class Player(pg.sprite.Sprite):
    """La macchina che rappresenta il player"""

    speed = 10
    bounce = 24
    gun_offset = -11
    images = [] # array che conterrà le immagini del Player

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0] # immagine, la prima di quelle fornite
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom) # rettangolo di collisione
        self.reloading = 0 # ricarica proiettile
        self.origtop = self.rect.top
        self.facing = -1 # direzione

    def move(self, direction):
        if direction:
            self.facing = direction # setta la direzione, se non è nulla
        self.rect.move_ip(direction * self.speed, 0) # sposta il rettangolo, "ip" sta per "in place", ovvero non ritorna nulla
        self.rect = self.rect.clamp(SCREENRECT) # limita la posizione dentro il rettangolo di gioco
        # cambia l'immagine (left-right) in base alla direzione puntata
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        #self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx # calcola la X della posizione del cannone, rispetto al centro del rect
        return pos, self.rect.top


class Alien(pg.sprite.Sprite):
    """Un'astronave aliena che si sposta lentamente verso il basso"""

    speed = 13
    animcycle = 12
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Alien.speed # scelta random
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right # decide da che lato fare comparire l'UFO

    def update(self):
        self.rect.move_ip(self.facing, 0) # sposta avanti di "facing" pixels
        if not SCREENRECT.contains(self.rect): # se esce fuori
            self.facing = -self.facing # inverte la direzione
            self.rect.top = self.rect.bottom + 1 # sposta giù di una riga
            self.rect = self.rect.clamp(SCREENRECT) # rientra nello schermo
        self.frame = self.frame + 1 # aumenta il frame
        self.image = self.images[self.frame // self.animcycle % 3] # animazione


class Explosion(pg.sprite.Sprite):
    """Una singola esplosione"""

    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor): # dipende da "actor", l'elemento che esplode!
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        """
        Serve ad assicurarsi che dopo un'animazione completa, l'oggetto scompaia da solo
        """
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Shot(pg.sprite.Sprite):
    """Un proiettile del Player"""

    speed = -11
    images = []

    def __init__(self, pos): # utilizza una posizione rispetto al cannone del player
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        """
        Si assicura di scomparire in automatico se esce fuori dallo schermo
        """
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pg.sprite.Sprite):
    """Una bomba sganciata dall'alieno"""

    speed = 9
    images = []

    def __init__(self, alien):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=alien.rect.move(0, 5).midbottom)

    def update(self):
        """
        Si assicura di aggiungere un'Esplosione e scomparire se raggiunge la fine dello schermo cadendo
        """
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self)
            self.kill()


class Score(pg.sprite.Sprite):
    """Tiene traccia del punteggio"""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.font = pg.font.Font(None, 20) # setup del font
        self.font.set_italic(1) # corsivo
        self.color = "white"
        self.lastscore = -1 # tiene traccia dell'ultimo score
        self.update() # chiamato una volta in init
        self.rect = self.image.get_rect().move(10, 450) # fissa la posizione sullo schermo

    def update(self):
        """Si aggiorna solo se si è aggiornata la variabile SCORE"""
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)


def main(winstyle=0):
    # Inizializza PyGame
    if pg.get_sdl_version()[0] == 2: # usa SDL 2
        pg.mixer.pre_init(44100, 32, 2, 1024) # parametri tecnici del mixer audio: frequenza e bit di campionamento, canali, dimensione buffer
    pg.init()
    if pg.mixer and not pg.mixer.get_init(): # si assicura che il mixer sia inizializzato
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Setta la modalità display
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Carica le immagini e le assegna alle classi
    img = load_image("player1.gif")
    Player.images = [img, pg.transform.flip(img, 1, 0) ] # stessa img, flippata SX-DX
    img = load_image("explosion1.gif")
    Explosion.images = [img, pg.transform.flip(img, 1, 1)] # stessa img, flippata sotto sopra
    Alien.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    Bomb.images = [load_image("bomb.gif")]
    Shot.images = [load_image("shot.gif")]

    # Decora la finestra di sistema del gioco
    icon = pg.transform.scale(Alien.images[0], (32, 32)) # icona 32x32 per la finestra
    pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Aliens")
    pg.mouse.set_visible(0) # mouse invisibile

    # crea lo sfondo con logica tileset (ripeti per tutta la finestra)
    bgdtile = load_image("background.gif")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()): # il tile si ripete da 0 a width, a incrementi di tile_width
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0)) # applica allo schermo
    pg.display.flip() # applica a tutto il display

    # carica gli effetti sonori
    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    if pg.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav") # carica la musica
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    # inizializza i Groups di gioco
    aliens = pg.sprite.Group()
    shots = pg.sprite.Group()
    bombs = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    lastalien = pg.sprite.GroupSingle()

    # assegna come "containers" i rispettivi gruppi da gestire
    Player.containers = all
    Alien.containers = aliens, all, lastalien
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all

    # Crea dei valori di default
    global score
    alienreload = ALIEN_RELOAD
    clock = pg.time.Clock()

    # inizializza gli sprite di default
    global SCORE
    player = Player()
    Alien()  # Nota: questa scrittura senza assegnazione è valida SOLO perché abbiamo definito un Group per questi oggetti
    if pg.font:
        all.add(Score()) # stampa lo Score e aggiungilo al Group "all" solo se è caricato "pg.font"

    # MAIN LOOP
    while player.alive():

        # ottieni input da tastiera
        for event in pg.event.get():
            if event.type == pg.QUIT: # esci dal gioco
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: # ESC, esci dal gioco
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f: # F, gestione fullscreen
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    pg.display.flip() # aggiorna lo schermo
                    fullscreen = not fullscreen # toggle della modalità

        keystate = pg.key.get_pressed() # ottiene tutte le key premute

        # cancella e aggiorna tutti gli sprite
        all.clear(screen, background)
        all.update()

        # gestisci l'input del player
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT] # "direction" in base alla pressione di LEFT o RIGHT, 0 se entrambi
        player.move(direction) # sposta il player
        firing = keystate[pg.K_SPACE] # firing=True se si preme barra spaziatrice
        if not player.reloading and firing and len(shots) < MAX_SHOTS: # controlla che non si sia in RELOAD, o in MAX_SHOTS a schermo
            Shot(player.gunpos()) # nuovo proiettile
            if pg.mixer:
                shoot_sound.play() # suono proiettile
        player.reloading = firing # gestione reload

        # Creazione alieni
        if alienreload:
            alienreload = alienreload - 1 # abbassa il contatore di reload se diverso da 0
        elif not int(random.random() * ALIEN_ODDS): # crea un alieno con chance 1 su ALIEN_ODDS
            Alien()
            alienreload = ALIEN_RELOAD

        # Bombe
        if lastalien and not int(random.random() * BOMB_ODDS): # crea una bomba con chance 1 su BOMB_ODDS
            Bomb(lastalien.sprite)

        # Controllo collisioni alieni con Player
        for alien in pg.sprite.spritecollide(player, aliens, 1): # c'è un metodo dedicato!
            if pg.mixer:
                boom_sound.play() # esplosione
            Explosion(alien)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill() # termina il Player

        # Controllo collisioni proiettili con alieni
        for alien in pg.sprite.groupcollide(aliens, shots, 1, 1).keys():
            if pg.mixer:
                boom_sound.play()
            Explosion(alien)
            SCORE = SCORE + 1

        # Controllo collisioni bombe con player
        for bomb in pg.sprite.spritecollide(player, bombs, 1):
            if pg.mixer:
                boom_sound.play()
            Explosion(player)
            Explosion(bomb)
            player.kill()

        # Ridisegna la scena
        dirty = all.draw(screen)
        pg.display.update(dirty) # aggiorna

        #  cap a 40 fps / 40 Hz
        clock.tick(40)

    # se termina il loop:
    if pg.mixer:
        pg.mixer.music.fadeout(1000) # fadeout della musica di 1 sec
    pg.time.wait(1000) # attendi 1 sec


# chiama la funzione main, esci dal gioco appena termina
if __name__ == "__main__":
    main()
    pg.quit()