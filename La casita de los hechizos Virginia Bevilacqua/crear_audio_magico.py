"""Timbres originales de cristal, aire y humo para los eventos mágicos."""
import numpy as np
from crear_audio import SR, guardar, frecuencia


def cristal(nombre,notas,paso,duracion):
    salida=np.zeros(round(SR*duracion))
    for i,midi in enumerate(notas):
        inicio=round(i*paso*SR)
        t=np.arange(len(salida)-inicio)/SR
        f=frecuencia(midi)
        fase=2*np.pi*f*t+.8*np.sin(2*np.pi*f*1.5*t)*np.exp(-t*8)
        onda=(np.sin(fase)+.2*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*4)
        onda*=np.minimum(t/.025,1)*np.minimum((duracion-i*paso-t)/.04,1)
        salida[inicio:]+=onda*.16
    eco=np.zeros_like(salida);retardo=round(SR*.13)
    eco[retardo:]=salida[:-retardo]*.28
    guardar(nombre,salida+eco)


if __name__=='__main__':
    cristal('runa_inicio',[69,81,88],.15,1.2)
    cristal('runa_trazo',[93,100],.045,.35)
    cristal('runa_sello',[69,76,81,88,93],.09,1.3)
    cristal('runa_victoria',[69,76,81,88,93,100],.17,2.0)
    cristal('runa_final',[81,76,69],.2,1.3)
    cristal('magia',[81,88,93,100],.07,1.0)
    cristal('combo',[84,88,91],.055,.65)
    rng=np.random.default_rng(18);t=np.arange(round(SR*.65))/SR
    ruido=rng.normal(0,1,len(t))
    ruido=np.convolve(ruido,np.ones(31)/31,mode='same')
    env=np.minimum(t/.008,1)*np.exp(-t*7)*np.minimum((.65-t)/.04,1)
    guardar('explosion',(ruido*.9+np.sin(2*np.pi*(95*t-40*t*t))*.22)*env)
    print('Ocho nuevos efectos mágicos originales creados')
