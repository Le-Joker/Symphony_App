import pygame
import numpy as np
import sounddevice as sd
import time
# --- paramètres audio et visuels ---
SAMPLE_RATE = 44100  # Échantillons par seconde
DURATION = 0.3       # Durée de la note en secondes
VOLUME = 0.5         # Volume (0.0 à 1.0)

# frequencies des notes du balafon
NOTES_FREQUENCIES = {
    "Do": 261.63,  # C4
    "Ré": 293.66,  # D4
    "Mi": 329.63,  # E4
    "Fa": 349.23,  # F4
    "Sol": 392.00, # G4
    "La": 440.00,  # A4
    "Si": 493.88,  # B4
    "Do_Octave": 523.25, # C5
}

#fenetre Pygame
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balafon Virtuel")

# Couleurs
COLOR_BACKGROUND = (30, 30, 60) #bleu foncé
COLOR_LAME_NORMAL = (150, 100, 50) # couleur bois
COLOR_LAME_ACTIVE = (255, 200, 100) # jaune clair quand la touche est pressée
COLOR_TEXT = (255, 255, 255) # blanc


# On va simuler cela en changeant la largeur de chaque lame
LAME_HEIGHT = 80
LAME_SPACING = 10 # space entre les lames

# clef Pygame -> (Nom de la note, Largeur de la lame, Couleurs)
BALAFON_LAMES = {
    pygame.K_a: {"note": "Do", "width": 120, "color": COLOR_LAME_NORMAL},
    pygame.K_z: {"note": "Ré", "width": 115, "color": COLOR_LAME_NORMAL},
    pygame.K_e: {"note": "Mi", "width": 110, "color": COLOR_LAME_NORMAL},
    pygame.K_r: {"note": "Fa", "width": 105, "color": COLOR_LAME_NORMAL},
    pygame.K_t: {"note": "Sol", "width": 100, "color": COLOR_LAME_NORMAL},
    pygame.K_y: {"note": "La", "width": 95, "color": COLOR_LAME_NORMAL},
    pygame.K_u: {"note": "Si", "width": 90, "color": COLOR_LAME_NORMAL},
    pygame.K_i: {"note": "Do_Octave", "width": 85, "color": COLOR_LAME_NORMAL},
}

# pour centrer les lames, nous calculons la largeur totale
total_width = sum(data["width"] for data in BALAFON_LAMES.values()) + \
              (len(BALAFON_LAMES) - 1) * LAME_SPACING

start_x = (SCREEN_WIDTH - total_width) // 2
current_x = start_x
lame_rects = {} # pour stocker les objets Rect de Pygame

for key, data in BALAFON_LAMES.items():
    rect = pygame.Rect(current_x, (SCREEN_HEIGHT - LAME_HEIGHT) // 2, data["width"], LAME_HEIGHT)
    lame_rects[key] = rect
    data["rect"] = rect # add le rect au dictionnaire de données
    current_x += data["width"] + LAME_SPACING

# fonction de son pour générer une onde sinusoïdale

def generate_sin_wave(frequency, duration, sample_rate, volume):
    num_samples = int(sample_rate * duration)
    time_array = np.linspace(0., duration, num_samples, endpoint=False)
    wave = volume * np.sin(2. * np.pi * frequency * time_array).astype(np.float32)
    
    # ajout d'une enveloppe de decay pour un son percussif
    decay = np.exp(-np.arange(num_samples) / (sample_rate * 0.15)) # 0.15s de decay
    wave = wave * decay
    
  
    # l'onde sinusoïdale seule est très pure, un balafon a des harmoniques.
    # harmonic_wave = (volume * 0.3) * np.sin(2. * np.pi * (frequency * 2) * time_array).astype(np.float32)
   
    
    return wave

def play_note(note_name):
    frequency = NOTES_FREQUENCIES.get(note_name)
    if frequency is None:
        print(f"Erreur : Fréquence non trouvée pour la note {note_name}")
        return

    audio_data = generate_sin_wave(frequency, DURATION, SAMPLE_RATE, VOLUME)
    sd.play(audio_data, samplerate=SAMPLE_RATE, blocking=False)
    print(f"Note jouée : {note_name} ({frequency:.2f} Hz)")

#boucle principale

running = True
font = pygame.font.Font(None, 28) # Police pour les noms des notes/touches

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key in BALAFON_LAMES:
                # changer la couleur de la lame active
                BALAFON_LAMES[event.key]["color"] = COLOR_LAME_ACTIVE
                # jouer la note
                play_note(BALAFON_LAMES[event.key]["note"])
            
            if event.key == pygame.K_ESCAPE:
                running = False
        
        if event.type == pygame.KEYUP:
            if event.key in BALAFON_LAMES:
                # revenir à la couleur normale quand la touche est relâchée
                BALAFON_LAMES[event.key]["color"] = COLOR_LAME_NORMAL

    #grqphisq,ne
    screen.fill(COLOR_BACKGROUND)  # nettoyer l'écran avec la couleur de fond

    # dessiner chaque lame du balafon
    for key, data in BALAFON_LAMES.items():
        pygame.draw.rect(screen, data["color"], data["rect"], border_radius=5) # dessiner la lame

        # afficher le nom de la note et la touche associée sur la lame
        note_text = font.render(data["note"], True, COLOR_TEXT)
        key_text = font.render(pygame.key.name(key).upper(), True, COLOR_TEXT)

        #centrer le texte sur la lame
        screen.blit(note_text, (data["rect"].centerx - note_text.get_width() // 2,
                                data["rect"].centery - note_text.get_height() // 2 - 10))
        screen.blit(key_text, (data["rect"].centerx - key_text.get_width() // 2,
                               data["rect"].centery + note_text.get_height() // 2 + 5))

    # afficher les instructions
    instruction_text = font.render("Pressez les touches indiquées. ESC pour quitter.", True, COLOR_TEXT)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT - 40))

    pygame.display.flip() # Mettre à jour l'écran

# nettoyer et quitter
sd.stop()
pygame.quit()