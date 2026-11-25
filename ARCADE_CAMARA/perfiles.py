"""Pantalla inicial y almacenamiento local de las partidas de cada jugador."""
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import pygame

from interfaz import boton, escribir, papel, MUSGO


@dataclass
class Perfil:
    """Identifica un jugador y la aventura en la que quedó."""
    nombre: str
    ruta_diario: Path
    ultimo_juego: int = 0
    archivo: Path | None = None

    def guardar(self):
        """Persiste el acceso a la última aventura sin modificar el diario."""
        if self.archivo is None:
            return
        temporal = self.archivo.with_suffix('.tmp')
        temporal.write_text(json.dumps({'nombre': self.nombre, 'juego': self.ultimo_juego},
                                       ensure_ascii=False), encoding='utf-8')
        temporal.replace(self.archivo)


class SelectorJugadores:
    """Crea y abre partidas individuales en el mismo equipo."""

    NUEVA = pygame.Rect(490, 490, 330, 54)
    CONTINUAR = pygame.Rect(140, 490, 330, 54)

    def __init__(self, ruta_anterior):
        """Recupera perfiles válidos e identifica un diario de versiones anteriores."""
        ruta_anterior = Path(ruta_anterior)
        self.carpeta = ruta_anterior.parent / 'jugadores'
        self.perfiles = []
        self.indice = 0
        self.editando = False
        self.nombre = ''
        self.error = ''
        if ruta_anterior.is_file():
            self.perfiles.append(Perfil('Partida anterior', ruta_anterior))
        for archivo in sorted(self.carpeta.glob('*/perfil.json'), key=lambda p: p.parent.name):
            try:
                datos = json.loads(archivo.read_text(encoding='utf-8'))
                nombre, juego = datos['nombre'], datos['juego']
                if isinstance(nombre,str) and nombre.strip() and juego in (0, 1, 2, 3, 4):
                    self.perfiles.append(Perfil(nombre[:32], archivo.with_name('diario.json'), juego, archivo))
            except (OSError, ValueError, TypeError, KeyError):
                continue
        self.perfiles.sort(key=lambda p: p.nombre.casefold())
        if not self.perfiles:
            self.nuevo()

    def nuevo(self):
        """Abre el campo de nombre para crear una partida."""
        self.editando = True
        self.nombre = ''
        self.error = ''
        pygame.key.start_text_input()

    def confirmar(self):
        """Abre el perfil elegido o crea el nuevo si su nombre es válido."""
        if not self.editando:
            return self.perfiles[self.indice] if self.perfiles else None
        nombre = self.nombre.strip()
        if not nombre:
            self.error = 'Escribí un nombre para empezar'
            return None
        if any(p.nombre.casefold() == nombre.casefold() for p in self.perfiles):
            self.error = 'Ese nombre ya tiene una partida'
            return None
        carpeta = self.carpeta / uuid4().hex
        perfil = Perfil(nombre, carpeta / 'diario.json', archivo=carpeta / 'perfil.json')
        try:
            carpeta.mkdir(parents=True)
            perfil.guardar()
        except OSError:
            self.error = 'No se pudo guardar el jugador'
            return None
        self.perfiles.append(perfil)
        self.indice = len(self.perfiles) - 1
        self.editando = False
        pygame.key.stop_text_input()
        return perfil

    def evento(self, evento):
        """Procesa teclado y devuelve un perfil al confirmar."""
        if self.editando and evento.type == pygame.TEXTINPUT:
            self.nombre = (self.nombre + ''.join(c for c in evento.text if c.isprintable()))[:32]
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                return self.confirmar()
            if self.editando and evento.key == pygame.K_BACKSPACE:
                self.nombre = self.nombre[:-1]
            elif not self.editando and evento.key == pygame.K_n:
                self.nuevo()
            elif not self.editando and self.perfiles and evento.key in (pygame.K_UP, pygame.K_DOWN):
                delta = 1 if evento.key == pygame.K_DOWN else -1
                self.indice = (self.indice + delta) % len(self.perfiles)
        return None

    def dibujar(self, pantalla, puntero, activar):
        """Dibuja la portada de jugadores y admite selección por clic o pinza."""
        papel(pantalla, (88, 62, 784, 555))
        escribir(pantalla, '¿Quién visita la casita?', (480, 130), 40, titulo=True)
        hay_perfiles = bool(self.perfiles)
        if self.editando:
            escribir(pantalla, 'Nueva partida', (480, 210), 26, negrita=True)
            papel(pantalla, (210, 254, 540, 66))
            escribir(pantalla, self.nombre + '│', (480, 287), 27, ancho=510)
            escribir(pantalla, 'Escribí tu nombre y presioná Enter', (480, 359), 22)
            boton(pantalla, self.NUEVA, 'Empezar')
            if hay_perfiles:
                boton(pantalla, self.CONTINUAR, 'Volver a jugadores')
        else:
            primero = max(0, self.indice - 3)
            for i, perfil in enumerate(self.perfiles[primero:primero + 4], primero):
                rect = pygame.Rect(190, 186 + (i-primero) * 66, 580, 53)
                papel(pantalla, rect, (215, 227, 196) if i == self.indice else (239, 226, 195))
                escribir(pantalla, perfil.nombre, rect.center, 25, negrita=i == self.indice, ancho=545)
                if activar and puntero is not None and rect.collidepoint(puntero):
                    self.indice = i
            boton(pantalla, self.CONTINUAR, 'Continuar · Enter')
            boton(pantalla, self.NUEVA, 'Nueva partida · N')
        escribir(pantalla, self.error or ('Elegí con ↑ y ↓' if len(self.perfiles) > 4 and not self.editando else ''), (480, 578), 20, MUSGO)
        if activar and puntero is not None:
            if self.NUEVA.collidepoint(puntero):
                if self.editando:
                    return self.confirmar()
                self.nuevo()
            elif self.CONTINUAR.collidepoint(puntero):
                if self.editando and hay_perfiles:
                    self.editando = False
                    self.error = ''
                    pygame.key.stop_text_input()
                elif not self.editando:
                    return self.confirmar()
        return None
