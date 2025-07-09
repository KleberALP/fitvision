import numpy as np

def calculate_angle(a, b, c):
    """
    Calcula o ângulo entre três pontos (em graus) usando atan2.
    Este método é o original do repositório, mais robusto para a detecção de pose em 2D.
    O ponto 'b' é o vértice do ângulo.
    """
    a = np.array(a)  # Primeiro ponto
    b = np.array(b)  # Vértice
    c = np.array(c)  # Terceiro ponto

    # Calcula o ângulo em radianos e converte para graus
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    # Garante que o ângulo não seja maior que 180 graus
    if angle > 180.0:
        angle = 360 - angle

    return angle
