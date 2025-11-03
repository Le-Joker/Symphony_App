import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QListWidget, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

from db_manager import DBManager
import numpy as np
import os
import time

try:
    import sounddevice as sd
    import soundfile as sf
except Exception:
    sd = None
    sf = None

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QComboBox, QScrollArea, QDialog, QFileDialog, QSlider



def theme_stylesheet(dark: bool) -> str:
    """Return a stylesheet string adapted to dark or light theme.

    The stylesheet uses colors so that text is black on light backgrounds and white on dark ones.
    """
    if dark:
        bg = '#1e1e1e'
        card = '#232323'
        input_bg = '#2b2b2b'
        text = '#ffffff'
        muted = '#bdbdbd'
        accent = '#5599ff'
        btn_bg = 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90e2, stop:1 #2f6fbf)'
    else:
        bg = '#f7f7f7'
        card = '#ffffff'
        input_bg = '#ffffff'
        text = '#0a0a0a'
        muted = '#666666'
        accent = '#1a73e8'
        btn_bg = 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #69a9ff, stop:1 #2f6fbf)'

    return f"""
    QWidget{{
        background: {bg};
        color: {text};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
    }}
    QFrame#card{{
        background: {card};
        border-radius: 12px;
        padding: 18px;
    }}
    QLabel#title{{
        font-size: 16pt;
        font-weight: 700;
        color: {text};
    }}
    QLineEdit{{
        background: {input_bg};
        color: {text};
        border: 1px solid rgba(0,0,0,0.15);
        border-radius: 8px;
        padding: 8px 10px;
    }}
    QLineEdit:focus{{
        border: 1px solid {accent};
    }}
    QPushButton{{
        color: white;
        background: {btn_bg};
        border: none;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 600;
    }}
    QPushButton#ghost{{
        background: transparent;
        color: {muted};
        border: 1px solid rgba(0,0,0,0.08);
        font-weight: 600;
    }}
    QPushButton:hover{{
        opacity: 0.95;
    }}
    QListWidget{{
        background: transparent;
        border: none;
        color: {text};
    }}
    """


class LoginWindow(QWidget):
    """Fenêtre de connexion / inscription / suppression.

    Gère l'affichage des utilisateurs existants et fournit les actions
    de création, connexion et suppression. Utilise `DBManager` pour
    persister les comptes dans la base SQLite.
    """
    def __init__(self, db_path):
        super().__init__()
        self.db = DBManager(db_path)
        # keep a persistent connection while UI open
        self.db.connect()
        self.setWindowTitle('Symphony App — Connexion')
        self.setGeometry(200, 200, 520, 360)
        self.is_dark = True
        self.init_ui()

    def init_ui(self):
        # Construction de l'interface graphique de la fenêtre de login
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        # card
        card = QFrame(self)
        card.setObjectName('card')
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        # header with title and theme toggle
        header = QHBoxLayout()
        title = QLabel('Connexion')
        title.setObjectName('title')
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        self.theme_btn = QPushButton('Mode clair')
        self.theme_btn.setObjectName('ghost')
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_btn)
        card_layout.addLayout(header)

        # form
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nom d'utilisateur")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Mot de passe')
        self.password_edit.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.username_edit)
        card_layout.addWidget(self.password_edit)

        # actions
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton('Créer')
        self.login_btn = QPushButton('Se connecter')
        self.delete_btn = QPushButton('Supprimer')
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.delete_btn)
        card_layout.addLayout(btn_layout)

        # user list
        card_layout.addWidget(QLabel('Utilisateurs existants :'))
        self.user_list = QListWidget()
        card_layout.addWidget(self.user_list)

        outer.addWidget(card)

        # signals
        self.create_btn.clicked.connect(self.on_create)
        self.login_btn.clicked.connect(self.on_login)
        self.delete_btn.clicked.connect(self.on_delete)

        self.refresh_user_list()
        self.apply_theme()

    def apply_theme(self):
        # Appliquer la palette et la feuille de style en fonction du thème choisi
        palette = QPalette()
        if self.is_dark:
            palette.setColor(QPalette.Window, QColor('#1e1e1e'))
            palette.setColor(QPalette.WindowText, QColor('#ffffff'))
        else:
            palette.setColor(QPalette.Window, QColor('#f7f7f7'))
            palette.setColor(QPalette.WindowText, QColor('#0a0a0a'))
        self.setPalette(palette)
        self.setStyleSheet(theme_stylesheet(self.is_dark))
        # update theme button label
        self.theme_btn.setText('Mode sombre' if not self.is_dark else 'Mode clair')

    def toggle_theme(self):
        # Basculer le thème sombre / clair
        self.is_dark = not self.is_dark
        self.apply_theme()

    def refresh_user_list(self):
        self.user_list.clear()
        users = self.db.list_users()
        for uid, username, created in users:
            self.user_list.addItem(f"{username}  —  {created}")

    def on_create(self):
        # Action : création d'un nouveau compte utilisateur
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        if not username or not password:
            QMessageBox.warning(self, 'Erreur', "Nom d'utilisateur et mot de passe requis")
            return
        ok = self.db.create_user(username, password)
        if ok:
            QMessageBox.information(self, 'Succès', f"Compte '{username}' créé")
            self.username_edit.clear()
            self.password_edit.clear()
            self.refresh_user_list()
        else:
            QMessageBox.warning(self, 'Erreur', "Nom d'utilisateur déjà utilisé")

    def on_login(self):
        # Action : tentative de connexion de l'utilisateur
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        if not username or not password:
            QMessageBox.warning(self, 'Erreur', "Nom d'utilisateur et mot de passe requis")
            return
        ok = self.db.verify_user(username, password)
        if ok:
            QMessageBox.information(self, 'Bienvenue', f'Connecté en tant que {username}')
            # Ouvrir la fenêtre principale de l'application et garder une référence
            # pour éviter que la fenêtre principale soit détruite par le ramasse-miettes.
            # On passe aussi la référence de la fenêtre de login pour permettre
            # un retour (déconnexion) vers l'écran de connexion.
            from PyQt5.QtWidgets import QApplication
            self.main_window = MainWindow(self.db, username, login_window=self)
            self.main_window.show()
            # Masquer la fenêtre de connexion (on pourra la réafficher au logout)
            self.hide()
        else:
            QMessageBox.critical(self, 'Erreur', "Nom d'utilisateur ou mot de passe invalide")

    def on_delete(self):
        # Action : suppression d'un compte utilisateur
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, 'Erreur', "Entrez le nom d'utilisateur à supprimer")
            return
        ret = QMessageBox.question(self, 'Confirmer', f"Supprimer le compte '{username}' ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            ok = self.db.delete_user(username)
            if ok:
                QMessageBox.information(self, 'Supprimé', 'Compte supprimé')
                self.refresh_user_list()
            else:
                QMessageBox.warning(self, 'Erreur', 'Compte introuvable')

    def closeEvent(self, event):
        # close DB connection
        self.db.close()
        super().closeEvent(event)


class MainWindow(QWidget):
    """Fenêtre principale : balafon, contrôle d'enregistrement, visualisation.

    Cette fenêtre représente l'espace instrument où l'utilisateur peut jouer
    le balafon, enregistrer et visualiser les formes d'onde. Elle peut
    également renvoyer l'utilisateur à l'écran de connexion via le bouton
    de déconnexion (logout).
    """
    def __init__(self, db_manager: DBManager, username: str, login_window: QWidget = None):
        super().__init__()
        self.db = db_manager
        self.username = username
        # Référence vers la fenêtre de login (pour permettre le logout)
        self.login_window = login_window
        self.user_id = self.db.get_user_id(username)
        self.setWindowTitle(f'Symphony App — Balafon ({username})')
        self.setGeometry(100, 100, 1200, 800)
        self.is_dark = True

        # audio settings
        self.sr = 44100
        self.waveform = 'sine'
        self.volume = 0.6

        # recording buffer (samples)
        self.recording = False
        self.record_buffer = np.zeros((0,))

        # default scale
        self.scale_type = 'Pentatonique'
        self.frequencies = self.build_frequencies(self.scale_type)

        # cache des samples pour chaque lame (réduit la latence)
        self.note_cache = {}

        self.init_ui()
        # construire les samples une fois l'UI initialisée
        self.build_note_cache()
        # s'assurer que la fenêtre capture les events clavier
        try:
            self.setFocusPolicy(Qt.StrongFocus)
            self.setFocus()
        except Exception:
            pass

    def init_ui(self):
        # Construction de l'interface principale (top bar, balafon, visualisation)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        # top bar
        top = QHBoxLayout()
        self.play_btn = QPushButton('Play (auto)')
        self.record_btn = QPushButton('Enregistrer')
        self.stop_record_btn = QPushButton('Stop')
        self.save_btn = QPushButton('Sauvegarder')
        self.list_btn = QPushButton('Enregistrements')
        top.addWidget(self.play_btn)
        top.addWidget(self.record_btn)
        top.addWidget(self.stop_record_btn)
        top.addWidget(self.save_btn)
        top.addWidget(self.list_btn)
        top.addStretch()

        # scale selector and settings
        top.addWidget(QLabel('Style de balafon :'))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(['Pentatonique', 'Heptatonique', 'Chromatique'])
        self.scale_combo.currentTextChanged.connect(self.on_scale_change)
        top.addWidget(self.scale_combo)

        # bouton de déconnexion (retour vers l'écran de connexion)
        self.logout_btn = QPushButton('Déconnexion')
        top.addWidget(self.logout_btn)

        self.settings_btn = QPushButton('Paramètres')
        top.addWidget(self.settings_btn)
        outer.addLayout(top)

        # balafon area
        balafon_card = QFrame(self)
        balafon_card.setObjectName('card')
        balafon_layout = QVBoxLayout(balafon_card)

        instr_label = QLabel('Balafon — 22 lames')
        instr_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        instr_label.setAlignment(Qt.AlignCenter)
        balafon_layout.addWidget(instr_label)

        keys_widget = QWidget()
        keys_layout = QHBoxLayout(keys_widget)
        # touches un peu collées
        keys_layout.setSpacing(1)
        keys_layout.setContentsMargins(8, 8, 8, 8)
        self.key_buttons = []
        # construire des largeurs variées pour ressembler à un balafon réel
        base_height = 160
        center = 11  # index central (0-based)
        for i in range(22):
            # largeur décroissante vers les bords
            distance = abs(i - center)
            width = max(36, 80 - distance * 3)
            btn = QPushButton('')
            btn.setFixedSize(width, base_height)
            btn.setProperty('key_index', i)
            btn.setCursor(Qt.PointingHandCursor)
            # couleur marron foncé pour les touches
            shade = 80 + int((1 - distance / (center + 1)) * 80)
            # RGB marron variant
            r = min(120 + distance, 140)
            g = max(40, 30 + int((center - distance) * 2))
            b = max(20, 10)
            color = f'rgb({r},{g},{b})'
            btn.setStyleSheet(f"background:{color}; border-radius:6px; border:2px solid #2e1f14;")
            btn.clicked.connect(self.on_key_click)
            self.key_buttons.append(btn)
            keys_layout.addWidget(btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(keys_widget)
        balafon_layout.addWidget(scroll)
        outer.addWidget(balafon_card, stretch=2)

        # matplotlib visualization
        fig = Figure(figsize=(8, 3))
        self.canvas = FigureCanvas(fig)
        self.ax = fig.add_subplot(111)
        self.ax.set_title('Visualisation temporelle')
        self.ax.set_xlabel('Samples')
        self.ax.set_ylabel('Amplitude')
        outer.addWidget(self.canvas, stretch=1)

        # connect top buttons
        self.record_btn.clicked.connect(self.start_record)
        self.stop_record_btn.clicked.connect(self.stop_record)
        self.save_btn.clicked.connect(self.save_recording)
        self.list_btn.clicked.connect(self.show_recordings)
        self.settings_btn.clicked.connect(self.open_settings)
        self.logout_btn.clicked.connect(self.logout)

        # apply theme
        self.apply_theme()

        # Mapping clavier -> index de lame (AZERTY-friendly)
        # On choisit 22 touches (lettres) adaptées pour un clavier FR :
        # A Z E R T Y U I O P Q S D F G H J K L M W X  (22 touches)
        keys = [
            'A','Z','E','R','T','Y','U','I','O','P',
            'Q','S','D','F','G','H','J','K','L','M',
            'W','X'
        ]
        self.key_map = {k: idx for idx, k in enumerate(keys)}
        # ensemble des touches actuellement appuyées (éviter les répétitions auto-repeat)
        self._pressed_keys = set()

    def keyPressEvent(self, event):
        # Ignorer si un QLineEdit a le focus (saisie de texte dans UI)
        fw = self.focusWidget()
        try:
            from PyQt5.QtWidgets import QLineEdit
        except Exception:
            QLineEdit = None
        if QLineEdit is not None and isinstance(fw, QLineEdit):
            super().keyPressEvent(event)
            return

        key_char = event.text().upper()
        if not key_char:
            super().keyPressEvent(event)
            return

        # si déjà en pressed (auto-repeat), ignorer
        if key_char in self._pressed_keys:
            return

        if key_char in self.key_map:
            idx = self.key_map[key_char]
            # safety check
            if 0 <= idx < len(self.frequencies):
                # visuel : mettre en état 'pressé'
                try:
                    btn = self.key_buttons[idx]
                    btn.setStyleSheet(btn.styleSheet() + "; box-shadow: none; opacity: 0.85; filter: brightness(1.25);")
                except Exception:
                    btn = None
                # jouer la note
                self.play_note(self.frequencies[idx])
                self._pressed_keys.add(key_char)
            return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        key_char = event.text().upper()
        if not key_char:
            super().keyReleaseEvent(event)
            return

        if key_char in self._pressed_keys:
            self._pressed_keys.remove(key_char)
            if key_char in self.key_map:
                idx = self.key_map[key_char]
                if 0 <= idx < len(self.key_buttons):
                    try:
                        btn = self.key_buttons[idx]
                        # retirer le style ajouté
                        btn.setStyleSheet(btn.styleSheet().replace('; box-shadow: none; opacity: 0.85; filter: brightness(1.25);', ''))
                    except Exception:
                        pass
            return

        super().keyReleaseEvent(event)

    def apply_theme(self):
        # Appliquer la feuille de style correspondant au thème
        self.setStyleSheet(theme_stylesheet(self.is_dark))

    def on_scale_change(self, text):
        # Mise à jour du type d'échelle et recalcul des fréquences
        self.scale_type = text
        self.frequencies = self.build_frequencies(self.scale_type)
        # reconstruire le cache pour que les nouvelles fréquences aient des samples prêts
        self.build_note_cache()

    def build_frequencies(self, style: str):
        # Génère 22 fréquences à partir du Do4 (C4 = 261.6256 Hz)
        f0 = 261.6256
        freqs = []
        if style == 'Chromatique':
            # semitone steps
            for n in range(22):
                freqs.append(f0 * (2 ** (n / 12)))
        elif style == 'Heptatonique':
            pattern = [0, 2, 4, 5, 7, 9, 11]
            n = 0
            while len(freqs) < 22:
                for step in pattern:
                    freqs.append(f0 * (2 ** ((n + step) / 12)))
                    if len(freqs) >= 22:
                        break
                n += 12
        else:  # Pentatonique
            pattern = [0, 2, 4, 7, 9]
            n = 0
            while len(freqs) < 22:
                for step in pattern:
                    freqs.append(f0 * (2 ** ((n + step) / 12)))
                    if len(freqs) >= 22:
                        break
                n += 12
        return freqs

    def build_note_cache(self, duration: float = 0.45):
        """Pré-génère un court sample pour chaque lame afin de réduire la latence.

        Chaque sample reçoit une enveloppe (attaque très courte + décroissance) pour
        éviter les clics et donner un rendu direct dès l'appui.
        """
        # si rate ou volume non initialisés, on ne fait rien
        try:
            sr = int(self.sr)
        except Exception:
            return

        self.note_cache = {}
        attack = 0.005  # très court
        for i, f in enumerate(self.frequencies):
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            wave = np.sin(2 * np.pi * f * t)
            # enveloppe simple : court attack linéaire puis décroissance exponentielle
            env = np.ones_like(t)
            a_samples = max(1, int(sr * attack))
            env[:a_samples] = np.linspace(0, 1, a_samples)
            env[a_samples:] = np.exp(-3 * (t[a_samples:] - t[a_samples]))
            sample = (wave * env * self.volume).astype(np.float32)
            self.note_cache[i] = sample

    def on_key_click(self):
        # Lorsqu'une lame est cliquée : jouer la note correspondante
        btn = self.sender()
        idx = btn.property('key_index')
        freq = self.frequencies[idx]
        # effet visuel : éclaircir la touche momentanément
        try:
            # obtenir la couleur actuelle et éclaircir
            btn.setStyleSheet(btn.styleSheet() + "; box-shadow: none; opacity: 0.9; filter: brightness(1.2);")
        except Exception:
            pass
        QTimer.singleShot(140, lambda b=btn: b.setStyleSheet(b.styleSheet().replace('; box-shadow: none; opacity: 0.9; filter: brightness(1.2);', '')))
        self.play_note(freq)

    def play_note(self, freq, duration=0.8):
        # Lecture immédiate via cache si disponible, sinon génération à la volée
        sr = int(self.sr)
        # trouver l'index de la fréquence la plus proche
        try:
            freqs_arr = np.array(self.frequencies)
            idx = int(np.argmin(np.abs(freqs_arr - freq)))
        except Exception:
            idx = None

        if idx is not None and idx in self.note_cache:
            wave = self.note_cache[idx]
        else:
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            if self.waveform == 'sine':
                wave = np.sin(2 * np.pi * freq * t)
            elif self.waveform == 'square':
                wave = np.sign(np.sin(2 * np.pi * freq * t))
            else:
                wave = np.sin(2 * np.pi * freq * t)
            wave = (wave * self.volume).astype(np.float32)

        # Visualisation style "Deezer": waveform rempli + barres spectrales colorées
        self.ax.clear()
        # waveform rempli
        x = np.arange(len(wave))
        self.ax.fill_between(x, wave, color='#d9c6a6', alpha=0.6)
        self.ax.plot(x, wave, color='#ffd9a6', linewidth=1.0, alpha=0.9)
        self.ax.set_ylim(-1.1, 1.1)

        # spectre
        spec = np.abs(np.fft.rfft(wave))
        nb = 60
        spec_bins = np.array_split(spec, nb)
        mags = np.array([b.mean() for b in spec_bins])
        if mags.max() > 0:
            mags = mags / mags.max()
        else:
            mags = np.zeros_like(mags)
        bar_x = np.linspace(0, len(wave), nb)
        width = max(1, len(wave) / nb * 0.8)
        # couleurs dégradées
        for xi, mi in zip(bar_x, mags):
            color = (0.9 * mi + 0.1, 0.3 * (1 - mi) + 0.1, 0.2 * mi + 0.2)
            self.ax.bar(xi, mi * 0.9, width=width, bottom=-1.02, color=color, alpha=0.95)

        # masquer axes
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()

        # append to record buffer if recording
        if self.recording:
            self.record_buffer = np.concatenate((self.record_buffer, wave))

        # playback non bloquant (thread) pour garder l'UI réactive
        if sd is not None:
            import threading

            def _play(w):
                try:
                    sd.play(w, sr)
                except Exception as e:
                    print('Playback error:', e)

            threading.Thread(target=_play, args=(wave,), daemon=True).start()

    def start_record(self):
        # Démarrer l'enregistrement : réinitialiser le buffer
        self.recording = True
        self.record_buffer = np.zeros((0,))
        QMessageBox.information(self, 'Enregistrement', 'Enregistrement démarré')

    def stop_record(self):
        # Arrêter l'enregistrement
        self.recording = False
        QMessageBox.information(self, 'Enregistrement', 'Enregistrement arrêté')

    def save_recording(self):
        # Sauvegarder le buffer courant au format WAV et insérer métadonnée en DB
        if self.record_buffer.size == 0:
            QMessageBox.warning(self, 'Erreur', 'Aucun enregistrement à sauvegarder')
            return
        os.makedirs('recordings', exist_ok=True)
        filename = f'rec_{int(time.time())}.wav'
        path = os.path.join('recordings', filename)
        if sf is not None:
            sf.write(path, self.record_buffer, self.sr)
            length = len(self.record_buffer) / self.sr
            # save metadata in DB
            if self.user_id is not None:
                self.db.add_recording(self.user_id, path, float(length))
            QMessageBox.information(self, 'Sauvegardé', f'Enregistrement sauvegardé: {path}')
            self.record_buffer = np.zeros((0,))
        else:
            QMessageBox.warning(self, 'Erreur', 'soundfile non disponible pour écrire le fichier')

    def show_recordings(self):
        # Afficher la liste des enregistrements de l'utilisateur
        recs = self.db.list_recordings(self.user_id)
        dlg = QDialog(self)
        dlg.setWindowTitle('Enregistrements')
        dlg.resize(600, 400)
        layout = QVBoxLayout(dlg)
        listw = QListWidget()
        for rid, aid, fname, length, created in recs:
            listw.addItem(f"{fname} — {length:.2f}s — {created}")
        layout.addWidget(listw)
        btn_play = QPushButton('Jouer')
        btn_open = QPushButton('Ouvrir dossier')
        hb = QHBoxLayout()
        hb.addWidget(btn_play)
        hb.addWidget(btn_open)
        layout.addLayout(hb)

        def play_selected():
            idx = listw.currentRow()
            if idx < 0:
                return
            row = recs[idx]
            path = row[2]
            if sf is not None and sd is not None:
                try:
                    data, sr = sf.read(path, dtype='float32')
                    sd.play(data, sr)
                except Exception as e:
                    QMessageBox.warning(self, 'Erreur', str(e))
            else:
                QMessageBox.warning(self, 'Erreur', 'Playback non disponible')

        def open_folder():
            idx = listw.currentRow()
            if idx < 0:
                return
            row = recs[idx]
            path = os.path.abspath(row[2])
            folder = os.path.dirname(path)
            QFileDialog.getExistingDirectory(self, 'Ouvrir dossier', folder)

        btn_play.clicked.connect(play_selected)
        btn_open.clicked.connect(open_folder)
        dlg.exec_()

    def logout(self):
        """Déconnecter l'utilisateur : afficher la fenêtre de login et fermer la fenêtre principale."""
        if self.login_window is not None:
            # ré-afficher la fenêtre de connexion
            self.login_window.show()
        # fermer la fenêtre principale
        self.close()

    def open_settings(self):
        # Boîte de dialogue pour ajuster les paramètres audio et le thème
        dlg = QDialog(self)
        dlg.setWindowTitle('Paramètres')
        layout = QVBoxLayout(dlg)

        # Choix du thème (sombre / clair)
        layout.addWidget(QLabel('Thème'))
        theme_combo = QComboBox()
        theme_combo.addItems(['Sombre', 'Clair'])
        theme_combo.setCurrentIndex(0 if self.is_dark else 1)
        layout.addWidget(theme_combo)

        # Réglage de l'échantillonnage
        layout.addWidget(QLabel('Échantillonnage (Hz)'))
        sr_slider = QSlider(Qt.Horizontal)
        sr_slider.setMinimum(8000)
        sr_slider.setMaximum(96000)
        sr_slider.setValue(self.sr)
        layout.addWidget(sr_slider)

        # Réglage du volume
        layout.addWidget(QLabel('Volume'))
        vol_slider = QSlider(Qt.Horizontal)
        vol_slider.setMinimum(0)
        vol_slider.setMaximum(100)
        vol_slider.setValue(int(self.volume * 100))
        layout.addWidget(vol_slider)

        def apply():
            # Appliquer les paramètres choisis
            self.sr = int(sr_slider.value())
            self.volume = vol_slider.value() / 100.0
            # appliquer le thème au MainWindow
            self.is_dark = True if theme_combo.currentText() == 'Sombre' else False
            self.apply_theme()
            # appliquer aussi à la fenêtre de login si présente
            if hasattr(self, 'login_window') and self.login_window is not None:
                self.login_window.is_dark = self.is_dark
                self.login_window.apply_theme()
            dlg.accept()

        btn_ok = QPushButton('Appliquer')
        btn_ok.clicked.connect(apply)
        layout.addWidget(btn_ok)
        dlg.exec_()
