import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as sp_signal
import os

# Paramètres de démodulation (identiques à ceux de l'émetteur)
fs = 44100  # Fréquence d'échantillonnage (Hz)
bit_rate = 100  # Débit binaire (bits/sec)
f0 = 17000  # Fréquence du bit '0' (Hz)
f1 = 19000  # Fréquence du bit '1' (Hz)
bit_duration = 1 / bit_rate  # Durée d'un bit (s)

# Définition du chemin du fichier
input_dir = r"C:\Users\CORENTIN CARTALLIER\Desktop\CPI A1\PROJET 3\Avec importation haute fréquence"
filename = os.path.join(input_dir, "fsk_transmission.wav")

def bandpass_filter(data, fs, lowcut=16500, highcut=19500, order=4):
    """Applique un filtre passe-bande Butterworth"""
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = sp_signal.butter(order, [low, high], btype='band')
    return sp_signal.filtfilt(b, a, data)

def demodulate_fsk(audio_signal):
    """ Démodule le signal FSK pour extraire les bits """
    bits = ""
    samples_per_bit = int(bit_duration * fs)

    for i in range(0, len(audio_signal), samples_per_bit):
        segment = audio_signal[i:i + samples_per_bit]

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

def hamming_decode(encoded):
    """ Décode les bits avec un code de Hamming (7,4) """
    n = len(encoded)
    decoded = []

    # Parcourir les bits 7 par 7
    for i in range(0, n, 7):
        # Prendre 7 bits de données
        code = encoded[i:i+7]
        # Extraire les bits de parité et de données
        p1, p2, d1, p3, d2, d3, d4 = code
        # Calculer les bits de parité
        new_p1 = int(d1) ^ int(d2) ^ int(d3)
        new_p2 = int(d1) ^ int(d2) ^ int(d4)
        new_p3 = int(d2) ^ int(d3) ^ int(d4)
        # Calculer le syndrome
        syndrome = f"{int(p1) ^ new_p1}{int(p2) ^ new_p2}{int(p3) ^ new_p3}"
        # Corriger l'erreur si nécessaire
        if syndrome != "000":
            error_pos = int(syndrome, 2) - 1
            code = code[:error_pos] + str(int(code[error_pos]) ^ 1) + code[error_pos+1:]
        # Extraire les bits de données
        decoded.append(f"{code[2]}{code[4]}{code[5]}{code[6]}")

    return ''.join(decoded)

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
fs, audio_signal = wav.read(filename)

# Étape 2 : Normalisation du signal
audio_signal = audio_signal.astype(np.float32) / 32767  # Conversion en float

# Étape 3 : Application du filtre passe-bande
audio_signal = bandpass_filter(audio_signal, fs)

# Étape 4 : Démodulation FSK
decoded_bits = demodulate_fsk(audio_signal)
print(f"🔢 Bits reçus : {decoded_bits}")

# Étape 5 : Décodage avec le code de Hamming
corrected_bits = hamming_decode(decoded_bits)
print(f"🔢 Bits corrigés : {corrected_bits}")

# Étape 6 : Conversion en texte
decoded_message = bits_to_text(corrected_bits)
print(f"💬 Message reçu : {decoded_message}")