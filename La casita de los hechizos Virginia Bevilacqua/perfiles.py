"""Pantalla inicial y almacenamiento local de las partidas de cada jugador."""
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import pygame

from interfaz import boton, escribir, papel, texto_renderizado, MUSGO, TINTA, PAPEL


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
    BORRAR = pygame.Rect(352, 554, 256, 42)
    CANCELAR_BORRADO = pygame.Rect(180, 432, 278, 52)
    CONFIRMAR_BORRADO = pygame.Rect(502, 432, 278, 52)
    CAMPO_NOMBRE = pygame.Rect(210, 254, 540, 66)

    def __init__(self, ruta_anterior):
        """Recupera perfiles válidos e identifica un diario de versiones anteriores."""
        ruta_anterior = Path(ruta_anterior)
        self.carpeta = ruta_anterior.parent / 'jugadores'
        self.perfiles = []
        self.indice = 0
        self.editando = False
        self.enfocado = False
        self.inicio_cursor = 0
        self.nombre = ''
        self.error = ''
        self.pendiente_borrar = None
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
        self.enfocar(True)

    def enfocar(self, activo):
        """Muestra el foco del campo y controla la entrada de texto de SDL."""
        self.enfocado = activo
        self.inicio_cursor = pygame.time.get_ticks()
        if activo:
            pygame.key.start_text_input()
        else:
            pygame.key.stop_text_input()

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
        self.enfocar(False)
        return perfil

    def pedir_borrado(self):
        self.pendiente_borrar = self.perfiles[self.indice]
        self.error = ''

    def cancelar_borrado(self):
        self.pendiente_borrar = None
        self.error = ''

    def borrar(self):
        """Quita la partida del selector y conserva los archivos en borradas."""
        perfil = self.pendiente_borrar
        destino = self.carpeta / '.borradas' / uuid4().hex
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            if perfil.archivo is not None:
                perfil.archivo.parent.rename(destino)
            else:
                destino.mkdir()
                perfil.ruta_diario.rename(destino / perfil.ruta_diario.name)
                mascota = perfil.ruta_diario.with_name('mascota.json')
                try:
                    if mascota.is_file():
                        mascota.rename(destino / mascota.name)
                except OSError:
                    (destino / perfil.ruta_diario.name).rename(perfil.ruta_diario)
                    raise
        except OSError:
            self.error = 'No se pudo borrar la partida. Podés volver a intentar.'
            return
        self.perfiles.remove(perfil)
        self.indice = min(self.indice, max(0, len(self.perfiles) - 1))
        self.cancelar_borrado()
        if not self.perfiles:
            self.nuevo()

    def dibujar_confirmacion(self, pantalla, puntero, activar):
        perfil = self.pendiente_borrar
        escribir(pantalla, '¿Borrar esta partida?', (480, 220), 32, negrita=True)
        escribir(pantalla, perfil.nombre, (480, 290), 30, ancho=610, titulo=True)
        escribir(pantalla, 'Se quitarán sus niveles, premios y compañero del selector.',
                 (480, 352), 22, ancho=660)
        boton(pantalla, self.CANCELAR_BORRADO, 'Cancelar',
              puntero is not None and self.CANCELAR_BORRADO.collidepoint(puntero))
        borrar = self.CONFIRMAR_BORRADO
        pygame.draw.rect(pantalla, (137, 64, 63), borrar, border_radius=7)
        if puntero is not None and borrar.collidepoint(puntero):
            pygame.draw.rect(pantalla, (213, 152, 119), borrar, 3, border_radius=7)
        escribir(pantalla, 'Sí, borrar partida', borrar.center, 25, PAPEL, negrita=True)
        escribir(pantalla, self.error, (480, 548), 22, ancho=650)
        if activar and puntero is not None:
            if self.CANCELAR_BORRADO.collidepoint(puntero):
                self.cancelar_borrado()
            elif borrar.collidepoint(puntero):
                self.borrar()

    def evento(self, evento):
        """Procesa teclado y devuelve un perfil al confirmar."""
        if self.pendiente_borrar is not None:
            return None
        if self.editando and self.enfocado and evento.type == pygame.TEXTINPUT:
            self.nombre = (self.nombre + ''.join(c for c in evento.text if c.isprintable()))[:32]
            self.inicio_cursor = pygame.time.get_ticks()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                return self.confirmar()
            if self.editando and evento.key == pygame.K_TAB:
                self.enfocar(True)
            elif self.editando and self.enfocado and evento.key == pygame.K_BACKSPACE:
                self.nombre = self.nombre[:-1]
                self.inicio_cursor = pygame.time.get_ticks()
            elif not self.editando and self.perfiles and evento.key == pygame.K_DELETE:
                self.pedir_borrado()
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
        if self.pendiente_borrar is not None:
            self.dibujar_confirmacion(pantalla, puntero, activar)
            return None
        hay_perfiles = bool(self.perfiles)
        if self.editando:
            escribir(pantalla, 'Nueva partida', (480, 210), 26, negrita=True)
            campo = self.CAMPO_NOMBRE
            if activar and puntero is not None:
                if campo.collidepoint(puntero):
                    self.enfocar(True)
                elif not self.NUEVA.collidepoint(puntero):
                    self.enfocar(False)
            papel(pantalla, campo)
            izquierda = campo.left + 22
            if self.nombre:
                texto = texto_renderizado(self.nombre, 27, TINTA, False, 484, False)
                pantalla.blit(texto, texto.get_rect(midleft=(izquierda, campo.centery)))
                izquierda += texto.get_width() + 3
            elif not self.enfocado:
                escribir(pantalla, 'Tu nombre', campo.center, 24, MUSGO)
            if self.enfocado:
                pygame.draw.rect(pantalla, MUSGO, campo, 3, border_radius=9)
                if (pygame.time.get_ticks() - self.inicio_cursor) % 1000 < 550:
                    pygame.draw.line(pantalla, TINTA, (izquierda, campo.centery - 15),
                                     (izquierda, campo.centery + 15), 2)
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
            pygame.draw.rect(pantalla, (170, 109, 94), self.BORRAR, 1, border_radius=7)
            if puntero is not None and self.BORRAR.collidepoint(puntero):
                pygame.draw.rect(pantalla, (239, 216, 195), self.BORRAR, border_radius=7)
            escribir(pantalla, 'Borrar partida…', self.BORRAR.center, 21, (128, 62, 58))
        escribir(pantalla, self.error or ('Elegí con ↑ y ↓' if len(self.perfiles) > 4 and not self.editando else ''), (480, 470), 20, MUSGO)
        if activar and puntero is not None:
            if not self.editando and hay_perfiles and self.BORRAR.collidepoint(puntero):
                self.pedir_borrado()
            elif self.NUEVA.collidepoint(puntero):
                if self.editando:
                    return self.confirmar()
                self.nuevo()
            elif self.CONTINUAR.collidepoint(puntero):
                if self.editando and hay_perfiles:
                    self.editando = False
                    self.error = ''
                    self.enfocar(False)
                elif not self.editando:
                    return self.confirmar()
        return None
