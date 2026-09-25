"""
Instancia compartida de slowapi para rate limiting (Fase 11).

Se define en un modulo aparte para poder importarla tanto en main.py
(donde se registra en la app) como en los routers que aplican limites
especificos por endpoint, sin generar importaciones circulares.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
