"""Dimensiones, paleta y parámetros compartidos del juego."""

ANCHO, ALTO = 960, 720
NIDO = (480, 485)
RADIO_NIDO = 74
FPS = 60
CAMARA_ANCHO, CAMARA_ALTO = 640, 480
CAMARA_FPS = 60
CONFIANZA_MANO = 0.6
RETENCION_DETECCION = 0.55

FONDO = (25, 19, 40)
CREMA = (247, 239, 210)
LIMA = (213, 210, 161)
CORAL = (242, 198, 134)
VIOLETA = (185, 140, 247)


# Umbrales relativos al tamaño de la palma y margen del cursor.
PINZA_CIERRE = 0.38
PINZA_APERTURA = 0.58
ANCLA_PINZA_ENTRADA = 0.85
ANCLA_PINZA_SALIDA = 0.95
MARGEN_MANO_NORMALIZADO = 0.08
MARGEN_CURSOR = 20
FACTOR_DEDO_EXTENDIDO = 1.12

# Duración (segundos) y objetivo de cada aventura.
TIEMPO_BICHOS, META_BICHOS = 60.0, 8
TIEMPO_FAROLES, META_FAROLES = 75.0, 4
TIEMPO_BANQUETE, META_BANQUETE = 60.0, 40
TIEMPO_SELLOS, META_SELLOS = 90.0, 4


# Cada par indica segundos y meta. Los índices corresponden a los niveles 1 a 3.
NIVELES_BICHOS = ((TIEMPO_BICHOS, META_BICHOS), (65, 10), (75, 13))
NIVELES_FAROLES = ((TIEMPO_FAROLES, META_FAROLES), (80, 5), (85, 6))
NIVELES_BANQUETE = ((TIEMPO_BANQUETE, META_BANQUETE), (65, 55), (70, 72))
NIVELES_SELLOS = ((TIEMPO_SELLOS, META_SELLOS), (105, 5), (120, 6))
NIVELES_AVENTURAS = (NIVELES_BICHOS, NIVELES_FAROLES, NIVELES_BANQUETE, NIVELES_SELLOS)


NOMBRES_BICHOS = ('La despensa del bosque', 'Claro de luciérnagas', 'Jardín lunar')
AYUDAS_BICHOS = ('Atrapá y soltá en la bolsa', 'Acercate despacio o atrapá la luciérnaga',
                 'Llevá cada bicho a su bolsa')
LUCIERNAGA_DURACION = 7.0
