"""Música en bucle y efectos por evento, con canales independientes."""
from pathlib import Path
import pygame

CARPETA = Path(__file__).parent / 'assets' / 'audio'


class Sonido:
    def __init__(self):
        self.activo = False
        self.silenciado = False
        self.anterior = None
        self.juego = 1
        self.error = ''
        self.efectos = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100,-16,2,512)
            pygame.mixer.set_num_channels(8)
            for nombre in ('elegir','inicio','atrapar','entrega','picadura','victoria','final','escapa','runa_inicio','runa_trazo','runa_sello','runa_victoria','runa_final','magia','combo','explosion'):
                self.efectos[nombre] = pygame.mixer.Sound(str(CARPETA / f'{nombre}.wav'))
            pygame.mixer.music.load(str(CARPETA / 'jardin-nocturno.wav'))
            pygame.mixer.music.play(-1,fade_ms=900)
            self.activo = True
        except (pygame.error,FileNotFoundError) as error:
            self.error = str(error)

    def tocar(self, nombre):
        if not self.activo or self.silenciado:
            return
        canal = {'elegir':0,'inicio':0,'atrapar':1,'entrega':2,
                 'picadura':3,'victoria':4,'final':4,'escapa':1,'runa_inicio':0,
                 'runa_trazo':5,'runa_sello':2,'runa_victoria':4,'runa_final':4,
                 'magia':6,'combo':6,'explosion':3}[nombre]
        pygame.mixer.Channel(canal).set_volume(.62 if nombre=='picadura' else .75)
        pygame.mixer.Channel(canal).play(self.efectos[nombre])

    def recibir(self, eventos):
        mapa={'captura':'atrapar','entrega':'entrega','picadura':'picadura',
              'escape':'escapa','magia':'magia','combo':'combo',
              'explosion':'explosion','veneno':'picadura'}
        if self.juego==4:
            mapa.update(captura='runa_trazo',entrega='runa_sello')
        for tipo, _pos, _numero in eventos:
            if tipo in mapa:
                self.tocar(mapa[tipo])

    def alternar(self):
        self.silenciado = not self.silenciado
        if self.activo and self.silenciado:
            pygame.mixer.stop()
            pygame.mixer.music.set_volume(0)

    def actualizar(self, estado, pausa=False, gano=False):
        if not self.activo:
            return
        if estado != self.anterior:
            if estado == 'instrucciones':
                self.tocar('elegir')
            elif estado == 'juego':
                self.tocar('runa_inicio' if self.juego==4 else 'inicio')
            elif estado == 'resultado':
                self.tocar(('runa_victoria' if gano else 'runa_final') if self.juego==4 else ('victoria' if gano else 'final'))
            self.anterior = estado
        volumen = .23 if estado=='juego' else .16
        if pausa or pygame.mixer.Channel(3).get_busy() or estado=='resultado':
            volumen = .085
        pygame.mixer.music.set_volume(0 if self.silenciado else volumen)

    def cerrar(self):
        if self.activo:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
