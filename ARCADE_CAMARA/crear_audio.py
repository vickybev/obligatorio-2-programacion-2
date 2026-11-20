"""Compone música y efectos originales; ejecutar solo para regenerar WAV."""
from pathlib import Path
import wave
import numpy as np

SR = 44100
DESTINO = Path(__file__).parent / 'assets' / 'audio'
RNG = np.random.default_rng(24)


def frecuencia(nota):
    return 440 * 2 ** ((nota-69)/12)


def nota(midi, duracion, tipo='campana'):
    t = np.arange(round(SR*duracion))/SR
    f = frecuencia(midi)
    if tipo == 'cuerda':
        onda = np.sin(2*np.pi*f*t) + .25*np.sin(2*np.pi*f*2*t)
        envolvente = np.minimum(t/.04,1)*np.exp(-t/1.1)
    elif tipo == 'aire':
        onda = np.sin(2*np.pi*f*t+0.02*np.sin(2*np.pi*4*t))
        envolvente = np.minimum(t/.16,1)*np.minimum((duracion-t)/.35,1)
    else:
        onda = np.sin(2*np.pi*f*t)+.28*np.sin(2*np.pi*f*2*t)+.08*np.sin(2*np.pi*f*3*t)
        envolvente = np.minimum(t/.006,1)*np.exp(-t/.48)
    return onda*envolvente*np.minimum((duracion-t)/.025,1)


def guardar(nombre, muestras):
    muestras = np.asarray(muestras)
    if muestras.ndim == 1:
        muestras = np.column_stack((muestras,muestras))
    pico = np.max(np.abs(muestras))
    if pico > .94:
        muestras = muestras*.94/pico
    pcm = (np.clip(muestras,-1,1)*32767).astype('<i2')
    with wave.open(str(DESTINO / f'{nombre}.wav'),'wb') as archivo:
        archivo.setnchannels(2);archivo.setsampwidth(2);archivo.setframerate(SR)
        archivo.writeframes(pcm.tobytes())


def crear_musica():
    pulso = 60/84
    largo = round(16*4*pulso*SR)
    mezcla = np.zeros((largo,2))
    acordes = [(45,52,57,60),(41,48,53,57),(48,55,60,64),(43,50,55,59),
               (45,52,57,60),(41,48,53,57),(38,45,50,53),(40,47,56,59)]
    melodias = [(76,79,81,79),(77,76,72,69),(76,79,84,83),(79,74,71,74),
                (76,81,79,76),(77,76,72,69),(74,77,76,74),(71,68,71,76)]

    def sumar(sonido, inicio, nivel, pan=0):
        indices=(np.arange(len(sonido))+round(inicio*SR))%largo
        mezcla[indices,0] += sonido*nivel*(1-pan*.35)
        mezcla[indices,1] += sonido*nivel*(1+pan*.35)

    for compas in range(16):
        inicio=compas*4*pulso
        acorde=acordes[compas%8]
        sumar(nota(acorde[0],2.8,'cuerda'),inicio,.13)
        for paso in range(8):
            midi=acorde[(paso%3)+1]+12
            sumar(nota(midi,1.3,'cuerda'),inicio+paso*pulso/2,.075,(-1)**paso*.65)
        for paso,midi in enumerate(melodias[compas%8]):
            sumar(nota(midi,1.7),inicio+paso*pulso,.10,.15)
        if compas>=8:
            sumar(nota(melodias[compas%8][0]-12,2.6,'aire'),inicio,.07,-.3)
    # Reverberación circular: las colas continúan al repetirse el archivo.
    mezcla += .17*np.roll(mezcla,round(SR*.23),axis=0)
    mezcla += .09*np.roll(mezcla[:,::-1],round(SR*.41),axis=0)
    guardar('jardin-nocturno',mezcla)


def arpegio(nombre, notas, paso=.08, nivel=.28):
    mezcla=np.zeros(round(SR*(len(notas)*paso+.8)))
    for i,midi in enumerate(notas):
        sonido=nota(midi,.7)*nivel
        a=round(i*paso*SR);mezcla[a:a+len(sonido)] += sonido
    guardar(nombre,mezcla)


def crear_efectos():
    arpegio('elegir',[81,88],.045,.20)
    arpegio('inicio',[69,72,76,81],.10,.23)
    arpegio('atrapar',[81,88,93],.035,.22)
    arpegio('entrega',[72,76,79,84],.065,.27)
    arpegio('victoria',[72,76,79,84,79,84,88],.15,.27)
    arpegio('final',[76,72,69,64],.17,.22)
    t=np.arange(round(.48*SR))/SR
    frecuencia_instantanea=170+190*np.exp(-t*12)
    fase=2*np.pi*np.cumsum(frecuencia_instantanea)/SR
    electrico=np.sin(fase)+.25*np.sin(fase*3)
    ruido=RNG.normal(0,1,len(t))
    ruido=np.convolve(ruido,np.ones(5)/5,mode='same')
    envolvente=np.minimum(t/.006,1)*np.exp(-t*9)*np.minimum((.48-t)/.025,1)
    guardar('picadura',(.24*electrico+.17*ruido)*envolvente)
    arpegio('escapa',[79,74,69],.07,.13)


if __name__ == '__main__':
    DESTINO.mkdir(parents=True,exist_ok=True)
    crear_musica();crear_efectos()
    print('Música original y ocho efectos creados en',DESTINO)
