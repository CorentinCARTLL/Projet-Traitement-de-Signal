import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import os

# Paramètres de modulation
fs = 44100  # Fréquence d'échantillonnage (Hz)
bit_rate = 100  # Débit binaire (bits/sec)
f0 = 17000  # Fréquence pour un '0' (Hz)
f1 = 19000  # Fréquence pour un '1' (Hz)
bit_duration = 1 / bit_rate  # Durée d'un bit en secondes

# Définition du chemin du fichier
output_dir = r"C:\Users\CORENTIN CARTALLIER\Desktop\CPI A1\PROJET 3\Avec importation haute fréquence"
filename = os.path.join(output_dir, "fsk_transmission.wav")

def text_to_bits(text):
    """ Convertit un texte en suite de bits """
    return ''.join(format(ord(c), '08b') for c in text)

def hamming_encode(bits):
    """ Encode les bits avec un code de Hamming (7,4) """
    n = len(bits)
    encoded = []

    # Parcourir les bits 4 par 4
    for i in range(0, n, 4):
        # Prendre 4 bits de données
        data = bits[i:i+4]
        # Ajouter 3 bits de parité
        p1 = int(data[0]) ^ int(data[1]) ^ int(data[2])
        p2 = int(data[0]) ^ int(data[1]) ^ int(data[3])
        p3 = int(data[1]) ^ int(data[2]) ^ int(data[3])
        # Construire le mot de code de 7 bits
        code = f"{p1}{p2}{data[0]}{p3}{data[1]}{data[2]}{data[3]}"
        encoded.append(code)

    return ''.join(encoded)

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

# Encodage avec le code de Hamming
encoded_bits = hamming_encode(bits)
print(f"Message encodé avec Hamming : {encoded_bits}")

# Modulation FSK
signal = fsk_modulation(encoded_bits)

# Normalisation du signal pour l'enregistrement
signal = signal / np.max(np.abs(signal))  # Normalisation pour éviter la saturation
signal_int16 = np.int16(signal * 32767)

# Sauvegarde dans un fichier WAV
try:
    wav.write(filename, fs, signal_int16)
    print(f"✅ Signal FSK enregistré dans {filename}")
except Exception as e:
    print(f"Erreur lors de l'enregistrement du fichier WAV : {e}")

# Lecture du signal audio
try:
    sd.play(signal, samplerate=fs)
    sd.wait()
    print("🔊 Lecture terminée.")
except Exception as e:
    print(f"Erreur lors de la lecture audio : {e}")
