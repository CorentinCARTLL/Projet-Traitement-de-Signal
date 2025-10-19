import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import os

# Paramètres de modulation
fs = 44100  # Fréquence d'échantillonnage (Hz)
bit_rate = 100  # Débit binaire (bits/sec)
f0 = 1000  # Fréquence pour un '0' (Hz)
f1 = 2000  # Fréquence pour un '1' (Hz)
bit_duration = 1 / bit_rate  # Durée d'un bit en secondes

# Définition du chemin du fichier
output_dir = r"C:\Users\CORENTIN CARTALLIER\Desktop\CPI A1\PROJET 3\Avec importation basse fréquence"
filename = os.path.join(output_dir, "fsk_transmission.wav")

def text_to_bits(text):
    """ Convertit un texte en suite de bits """
    return ''.join(format(ord(c), '08b') for c in text)

def fsk_modulation(bits):
    """ Génère un signal FSK à partir d'une suite de bits """
    t = np.arange(0, bit_duration, 1/fs)  # Échelle de temps pour un bit
    signal = np.array([])  # Initialisation du signal final
    
    for bit in bits:
        freq = f1 if bit == '1' else f0
        wave = np.sin(2 * np.pi * freq * t)
        signal = np.concatenate((signal, wave))  # Ajout du signal modulé

    return signal

# Vérification si le dossier existe, sinon le créer
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Saisie utilisateur
message = input("Entrez un message à transmettre : ")
bits = text_to_bits(message)
print(f"Message en bits : {bits}")

# Modulation FSK
signal = fsk_modulation(bits)

# Normalisation du signal pour l'enregistrement
signal_int16 = np.int16(signal * 32767)

# Sauvegarde dans un fichier WAV
wav.write(filename, fs, signal_int16)
print(f"✅ Signal FSK enregistré dans {filename}")

# Lecture du signal audio
sd.play(signal, samplerate=fs)
sd.wait()
print("🔊 Lecture terminée.")
