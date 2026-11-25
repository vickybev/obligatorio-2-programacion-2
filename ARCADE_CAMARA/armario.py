"""Prendas del compañero, dibujadas sobre su propio plano de giro."""
import pygame

PRENDAS = (
    ('Pañuelo de musgo', 'Pañuelo de miel', 'Pañuelo de luna'),
    ('Gorro de bruma', 'Gorro de rocío', 'Gorro del crepúsculo'),
    ('Moño de menta', 'Moño de frutilla', 'Moño de caramelo'),
    ('Colgante de salvia', 'Colgante de amatista', 'Colgante lunar'),
)
TONOS = (
    ((110,145,93),(231,164,64),(162,144,210)),
    ((117,182,176),(147,178,206),(132,92,163)),
    ((128,201,161),(223,126,148),(217,154,103)),
    ((138,179,112),(181,133,209),(156,191,219)),
)


def dibujar_prenda(capa, prenda):
    """Superpone la prenda elegida antes de girar la imagen del compañero."""
    grupo, nivel = prenda
    color = TONOS[grupo][nivel]
    sombra = tuple(round(c*.61) for c in color)
    brillo = tuple(round(c*.65+255*.35) for c in color)
    if grupo == 0:
        pygame.draw.polygon(capa, sombra, ((43,92),(96,94),(88,111),(67,123),(47,110)))
        pygame.draw.polygon(capa, color, ((44,91),(96,93),(85,106),(67,117),(49,106)))
        pygame.draw.line(capa, brillo, (49,94),(83,100),2)
    elif grupo == 1:
        pygame.draw.polygon(capa, sombra, ((48,54),(68,20),(73,13),(92,52)))
        pygame.draw.polygon(capa, color, ((51,52),(73,15),(90,51)))
        pygame.draw.ellipse(capa, sombra, (41,46,60,12))
        pygame.draw.arc(capa, brillo, (42,44,58,10),0,3.14,2)
        pygame.draw.circle(capa, brillo, (73,17), 4)
    elif grupo == 2:
        pygame.draw.polygon(capa, sombra, ((42,91),(72,97),(100,91),(96,114),(72,104),(46,114)))
        pygame.draw.polygon(capa, color, ((44,92),(72,99),(98,92),(94,109),(72,102),(48,109)))
        pygame.draw.circle(capa, brillo, (72,100), 7)
    else:
        pygame.draw.arc(capa, (221,191,117), (48,80,48,28),3.14,6.28,3)
        pygame.draw.polygon(capa, sombra, ((72,99),(84,109),(72,123),(60,109)))
        pygame.draw.polygon(capa, color, ((72,101),(82,109),(72,120),(62,109)))
        pygame.draw.line(capa, brillo, (72,102),(63,109),2)
