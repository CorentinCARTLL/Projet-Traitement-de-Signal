import numpy as np
import scipy.io.wavfile as wav
import os

# Paramètres de démodulation (identiques à ceux de l'émetteur)
fs = 44100  # Fréquence d'échantillonnage (Hz)
bit_rate = 100  # Débit binaire (bits/sec)
f0 = 1000  # Fréquence du bit '0' (Hz)
f1 = 2000  # Fréquence du bit '1' (Hz)
bit_duration = 1 / bit_rate  # Durée d'un bit (s)

# Définition du chemin du fichier
input_dir = r"C:\Users\CORENTIN CARTALLIER\Desktop\CPI A1\PROJET 3\Avec importation basse fréquence"
filename = os.path.join(input_dir, "fsk_transmission.wav")

def demodulate_fsk(signal):
    """ Démodule le signal FSK pour extraire les bits """
    bits = ""
    samples_per_bit = int(bit_duration * fs)

    for i in range(0, len(signal), samples_per_bit):
        segment = signal[i:i + samples_per_bit]

        if len(segment) < samples_per_bit:
            continue

        # Calcul de la FFT pour détecter la fréquence dominante
        fft_result = np.fft.fft(segment)
        freqs = np.fft.fftfreq(len(segment), d=1/fs)
        magnitude = np.abs(fft_result)

        # Détection des fréquences présentes
        f0_energy = np.sum(magnitude[(freqs >= f0 - 50) & (freqs <= f0 + 50)])
        f1_energy = np.sum(magnitude[(freqs >= f1 - 50) & (freqs <= f1 + 50)])

        # Décision sur le bit reçu
        bit = '1' if f1_energy > f0_energy else '0'
        bits += bit

    return bits

def bits_to_text(bits):
    """ Convertit une suite de bits en texte ASCII """
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# Vérification de l'existence du fichier
if not os.path.exists(filename):
    print(f"❌ Erreur : le fichier {filename} n'existe pas !")
    exit()

# Étape 1 : Chargement du fichier audio
print(f"📂 Chargement du fichier : {filename}")
fs, signal = wav.read(filename)

# Étape 2 : Normalisation du signal
signal = signal.astype(np.float32) / 32767  # Conversion en float

# Étape 3 : Démodulation FSK
decoded_bits = demodulate_fsk(signal)
print(f"🔢 Bits reçus : {decoded_bits}")

# Étape 4 : Conversion en texte
decoded_message = bits_to_text(decoded_bits)
print(f"💬 Message reçu : {decoded_message}")
