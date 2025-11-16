"""Interface utilisateur moderne - Style React avec PyQt5.

Design moderne, responsive et élégant avec visualisations professionnelles.
Optimisé: Oscilloscope supprimé, Spectre conservé, Onglet Paramètres ajouté.
"""

import sys
import os
import json
import numpy as np
from typing import Optional
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QDialog, QFrame, QGridLayout, QSlider,
    QComboBox, QScrollArea, QListWidget, QListWidgetItem, QCheckBox,
    QSpinBox, QTabWidget, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QBrush, QLinearGradient,
    QKeySequence
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from core import audio_core, Note
from database import Database

# ============================================================================
# PALETTES MODERNES
# ============================================================================

COLORS = {
    "dark": {
        "bg": "#0f1419",
        "surface": "#1a1f2e",
        "surface_light": "#242b3d",
        "text": "#f1f5f9",
        "text_muted": "#94a3b8",
        "accent": "#6366f1",
        "accent_light": "#818cf8",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#334155",
        "wood": "#8B6F47",
    },
    "light": {
        "bg": "#f8fafc",
        "surface": "#ffffff",
        "surface_light": "#f1f5f9",
        "text": "#1e293b",
        "text_muted": "#64748b",
        "accent": "#6366f1",
        "accent_light": "#818cf8",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#e2e8f0",
        "wood": "#8B6F47",
    }
}


def get_stylesheet(theme: dict) -> str:
    """Génère le stylesheet moderne avec police optimisée."""
    return f"""
    QWidget {{
        background-color: {theme['bg']};
        color: {theme['text']};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
    }}
    
    QFrame#card {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    
    QLabel#title {{
        font-size: 18pt;
        font-weight: 700;
        color: {theme['text']};
    }}
    
    QLabel#subtitle {{
        font-size: 12pt;
        color: {theme['text_muted']};
    }}
    
    QLineEdit {{
        background-color: {theme['surface_light']};
        color: {theme['text']};
        border: 2px solid {theme['border']};
        border-radius: 8px;
        padding: 10px;
        selection-background-color: {theme['accent']};
    }}
    
    QLineEdit:focus {{
        border: 2px solid {theme['accent']};
        background-color: {theme['surface']};
    }}
    
    QPushButton {{
        background-color: {theme['accent']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 11pt;
    }}
    
    QPushButton:hover {{
        background-color: {theme['accent_light']};
    }}
    
    QPushButton:pressed {{
        background-color: {theme['accent']};
        padding: 11px 19px;
    }}
    
    QPushButton#danger {{
        background-color: {theme['danger']};
    }}
    
    QPushButton#danger:hover {{
        background-color: #dc2626;
    }}
    
    QComboBox {{
        background-color: {theme['surface_light']};
        color: {theme['text']};
        border: 2px solid {theme['border']};
        border-radius: 8px;
        padding: 8px;
    }}
    
    QComboBox:focus {{
        border: 2px solid {theme['accent']};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {theme['surface']};
        color: {theme['text']};
        selection-background-color: {theme['accent']};
    }}
    
    QTabWidget::pane {{
        border: 1px solid {theme['border']};
    }}
    
    QTabBar::tab {{
        background-color: {theme['surface_light']};
        color: {theme['text_muted']};
        padding: 8px 16px;
        margin-right: 2px;
        border: none;
        border-bottom: 2px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        color: {theme['text']};
        border-bottom: 2px solid {theme['accent']};
    }}
    
    QCheckBox {{
        color: {theme['text']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {theme['border']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {theme['accent']};
        border: 2px solid {theme['accent']};
    }}
    
    QSlider::groove:horizontal {{
        border: 1px solid {theme['border']};
        height: 6px;
        background: {theme['surface_light']};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {theme['accent']};
        border: 2px solid {theme['accent']};
        width: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {theme['accent_light']};
    }}
    
    QSpinBox {{
        background-color: {theme['surface_light']};
        color: {theme['text']};
        border: 2px solid {theme['border']};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QSpinBox:focus {{
        border: 2px solid {theme['accent']};
    }}
    """


# ============================================================================
# COMPOSANTS RÉUTILISABLES
# ============================================================================

class ModernKey(QPushButton):
    """Lame du balafon avec dimensions réalistes."""

    key_pressed = pyqtSignal(float)

    def __init__(self, note: Note, key_width: int = 45):
        super().__init__()
        self.note = note
        self.key_width = key_width
        self.is_active = False
        self.setFixedSize(key_width, 180)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._on_click)
        
        # Style initial
        self.update_style(False)

    def _on_click(self):
        """Déclenche la note et le signal."""
        audio_core.play_async(self.note.frequency)
        self.key_pressed.emit(self.note.frequency)
        self.activate()

    def activate(self):
        """Active la lame (subrillance)."""
        if not self.is_active:
            self.is_active = True
            self.update_style(True)
            QTimer.singleShot(150, self.deactivate)

    def deactivate(self):
        """Désactive la lame."""
        if self.is_active:
            self.is_active = False
            self.update_style(False)

    def update_style(self, active: bool):
        """Met à jour le style visuel."""
        theme = COLORS["dark"]
        color = theme['accent_light'] if active else "#8B6F47"
        glow = f"box-shadow: 0 0 16px {theme['accent']};" if active else ""
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #2e1f14;
                border-radius: 6px;
                {glow}
            }}
            QPushButton:hover {{
                background-color: #9d7f52;
            }}
        """)


class SpectrumWidget(FigureCanvas):
    """Analyseur de spectre FFT moderne et optimisé."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 3), dpi=100, facecolor='#0f1419')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumHeight(250)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a1f2e')
        self.ax.set_title('Spectre Fréquentiel', color='#f1f5f9', fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Fréquence (Hz)', color='#94a3b8')
        self.ax.set_ylabel('Magnitude', color='#94a3b8')
        self.ax.grid(True, color='#334155', alpha=0.3, linestyle='--')
        self.ax.set_xlim(0, 2000)
        self.ax.set_ylim(0, 1.2)
        
        for spine in self.ax.spines.values():
            spine.set_color('#334155')
        self.ax.tick_params(colors='#94a3b8')

    def update_spectrum(self, frequency: float):
        """Met à jour le spectre en temps réel."""
        try:
            self.ax.clear()
            self.ax.set_facecolor('#1a1f2e')
            
            sample = audio_core.get_cached_sample(frequency)
            freqs, mags = audio_core.analyze_spectrum(sample)
            
            self.ax.bar(freqs, mags, width=10, color='#10b981', alpha=0.8, edgecolor='#059669')
            
            self.ax.set_xlim(0, 2000)
            self.ax.set_ylim(0, 1.2)
            self.ax.set_title('Spectre Fréquentiel', color='#f1f5f9')
            self.ax.set_xlabel('Fréquence (Hz)', color='#94a3b8')
            self.ax.set_ylabel('Magnitude', color='#94a3b8')
            self.ax.grid(True, color='#334155', alpha=0.3)
            self.ax.tick_params(colors='#94a3b8')
            
            for spine in self.ax.spines.values():
                spine.set_color('#334155')
            
            self.fig.tight_layout()
            self.draw()
        except Exception as e:
            print(f"Erreur spectrum: {e}")
    
    def set_theme(self, theme: dict):
        """Change le thème du spectre."""
        self.fig.patch.set_facecolor(theme['bg'])
        self.ax.set_facecolor(theme['surface'])
        self.ax.set_title('Spectre Fréquentiel', color=theme['text'])
        self.ax.tick_params(colors=theme['text_muted'])
        self.draw()


# ============================================================================
# FENÊTRES
# ============================================================================

class LoginWindow(QWidget):
    """Fenêtre de connexion moderne."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.theme = COLORS["dark"]
        
        self.setWindowTitle("Symphony — Connexion")
        self.setGeometry(300, 150, 500, 600)
        self.setMinimumSize(400, 500)
        
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        """Construit l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # En-tête
        title = QLabel("Symphony")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Application musicale interactive")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Formulaire
        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")
        self.username.setMinimumHeight(40)
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(40)
        layout.addWidget(self.password)

        layout.addSpacing(10)

        # Boutons
        btn_layout = QHBoxLayout()
        
        btn_login = QPushButton("Connexion")
        btn_login.clicked.connect(self.login)
        btn_layout.addWidget(btn_login)

        btn_signup = QPushButton("Créer")
        btn_signup.setObjectName("secondary")
        btn_signup.clicked.connect(self.signup)
        btn_layout.addWidget(btn_signup)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def apply_theme(self):
        """Applique le thème."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.theme['bg']))
        palette.setColor(QPalette.WindowText, QColor(self.theme['text']))
        self.setPalette(palette)
        self.setStyleSheet(get_stylesheet(self.theme))

    def login(self):
        """Connexion utilisateur."""
        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Remplissez tous les champs")
            return

        user_id = self.db.verify_user(username, password)
        if user_id:
            self.main_window = MainWindow(self.db, user_id, username)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Erreur", "Identifiants invalides")

    def signup(self):
        """Inscription utilisateur."""
        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Remplissez tous les champs")
            return

        if self.db.create_user(username, password):
            QMessageBox.information(self, "Succès", f"Compte '{username}' créé")
            self.username.clear()
            self.password.clear()
        else:
            QMessageBox.warning(self, "Erreur", "Utilisateur déjà existant")


class MainWindow(QWidget):
    """Fenêtre principale du balafon - Interface React-like."""

    def __init__(self, db: Database, user_id: int, username: str):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.username = username
        self.theme = "dark"  # String pour le thème actuel
        
        self.recording = False
        self.record_buffer = np.zeros((0,))
        self.balafon_notes = audio_core.build_balafon_scale("pentatonic")
        self.key_buttons = []
        
        self.setWindowTitle(f"Symphony — Balafon ({username})")
        self.setGeometry(50, 50, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        """Construit l'interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Top bar
        top_bar = self.create_topbar()
        main_layout.addLayout(top_bar)

        # Contenu principal
        content = QHBoxLayout()
        content.setSpacing(12)

        # Balafon (gauche)
        balafon_section = self.create_balafon()
        content.addLayout(balafon_section, 1)

        # Visualiseurs (droite)
        viz_section = self.create_visualizers()
        content.addLayout(viz_section, 1)

        main_layout.addLayout(content, 1)
        self.setLayout(main_layout)

    def create_topbar(self) -> QHBoxLayout:
        """Crée la barre supérieure."""
        layout = QHBoxLayout()

        title = QLabel(f"🎵 Balafon — {self.username}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))

        scale_combo = QComboBox()
        scale_combo.addItems(["Pentatonique", "Majeure", "Chromatique"])
        scale_combo.currentTextChanged.connect(self.on_scale_change)
        self.scale_combo = scale_combo

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(QLabel("Mode :"))
        layout.addWidget(scale_combo)

        # Boutons
        self.record_btn = QPushButton("Enregistrer")
        self.record_btn.clicked.connect(self.start_record)
        layout.addWidget(self.record_btn)

        self.stop_btn = QPushButton("Arreter")
        self.stop_btn.clicked.connect(self.stop_record)
        layout.addWidget(self.stop_btn)

        save_btn = QPushButton("Exporter")
        save_btn.clicked.connect(self.save_recording)
        layout.addWidget(save_btn)

        logout_btn = QPushButton("Deconnexion")
        logout_btn.setObjectName("secondary")
        logout_btn.clicked.connect(self.close)
        layout.addWidget(logout_btn)

        return layout

    def create_balafon(self) -> QVBoxLayout:
        """Crée la section du balafon."""
        layout = QVBoxLayout()

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Balafon - 22 lames")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        card_layout.addWidget(title)

        # Grille des lames
        keys_grid = QGridLayout()
        keys_grid.setSpacing(2)

        self.key_buttons = []
        for i, note in enumerate(self.balafon_notes):
            # Varier la largeur selon la position
            distance = abs(i - 11)
            key_width = max(30, 50 - distance)
            
            btn = ModernKey(note, key_width)
            btn.key_pressed.connect(self.on_key_pressed)
            self.key_buttons.append(btn)

            row = i // 11
            col = i % 11
            keys_grid.addWidget(btn, row, col)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setLayout(keys_grid)
        scroll.setWidget(scroll_widget)

        card_layout.addWidget(scroll)
        layout.addWidget(card)

        return layout

    def create_visualizers(self) -> QVBoxLayout:
        """Crée le panneau des visualiseurs (Spectre + Paramètres)."""
        layout = QVBoxLayout()

        # Spectre
        spec_card = QFrame()
        spec_card.setObjectName("card")
        spec_layout = QVBoxLayout(spec_card)

        spec_label = QLabel("Spectre Frequentiel")
        spec_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        spec_layout.addWidget(spec_label)

        self.spectrum = SpectrumWidget()
        spec_layout.addWidget(self.spectrum)

        layout.addWidget(spec_card, 1)
        
        # Paramètres
        settings_card = QFrame()
        settings_card.setObjectName("card")
        settings_layout = QVBoxLayout(settings_card)
        
        settings_label = QLabel("Parametres")
        settings_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        settings_layout.addWidget(settings_label)
        
        # Onglets de paramètres
        tabs = QTabWidget()
        
        # Onglet Duree (sans volume)
        duration_widget = QWidget()
        duration_layout = QVBoxLayout()
        
        duration_label = QLabel("Duree du son (secondes):")
        duration_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.duration_spinbox = QDoubleSpinBox()
        self.duration_spinbox.setMinimum(0.1)
        self.duration_spinbox.setMaximum(2.0)
        self.duration_spinbox.setValue(0.45)
        self.duration_spinbox.setSingleStep(0.1)
        self.duration_spinbox.setMinimumHeight(40)
        self.duration_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                font-size: 12pt;
            }
        """)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spinbox)
        
        duration_layout.addSpacing(20)
        
        duration_info = QLabel("Ajustez la duree de chaque note")
        duration_info.setStyleSheet("color: #94a3b8; font-size: 10pt;")
        duration_layout.addWidget(duration_info)
        
        duration_layout.addStretch()
        duration_widget.setLayout(duration_layout)
        tabs.addTab(duration_widget, "Duree")
        
        # Onglet Apparence
        appearance_widget = QWidget()
        appearance_layout = QVBoxLayout()
        
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sombre", "Clair"])
        self.theme_combo.currentTextChanged.connect(self.switch_theme)
        appearance_layout.addWidget(theme_label)
        appearance_layout.addWidget(self.theme_combo)
        
        appearance_layout.addSpacing(15)
        
        self.fullscreen_check = QCheckBox("Mode plein ecran")
        self.fullscreen_check.setFont(QFont("Segoe UI", 10))
        self.fullscreen_check.stateChanged.connect(self.toggle_fullscreen)
        appearance_layout.addWidget(self.fullscreen_check)
        
        appearance_layout.addStretch()
        appearance_widget.setLayout(appearance_layout)
        tabs.addTab(appearance_widget, "Apparence")
        
        settings_layout.addWidget(tabs)
        layout.addWidget(settings_card, 1)

        return layout

    def apply_theme(self):
        """Applique le thème actuel."""
        theme_colors = COLORS[self.theme]
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(theme_colors['bg']))
        palette.setColor(QPalette.WindowText, QColor(theme_colors['text']))
        self.setPalette(palette)
        self.setStyleSheet(get_stylesheet(theme_colors))

    def on_scale_change(self, text: str):
        """Change l'échelle."""
        style_map = {
            "Pentatonique": "pentatonic",
            "Majeure": "major",
            "Chromatique": "chromatic",
        }
        self.balafon_notes = audio_core.build_balafon_scale(style_map[text])
        
        # Mettre à jour les boutons
        for btn, note in zip(self.key_buttons, self.balafon_notes):
            btn.note = note

    def on_key_pressed(self, frequency: float):
        """Gère la pression d'une touche."""
        sample = audio_core.get_cached_sample(frequency)
        self.spectrum.update_spectrum(frequency)

        if self.recording:
            self.record_buffer = np.concatenate((self.record_buffer, sample))

    def start_record(self):
        """Démarre l'enregistrement."""
        self.recording = True
        self.record_buffer = np.zeros((0,))
        self.record_btn.setStyleSheet("background-color: #ef4444;")

    def stop_record(self):
        """Arrête l'enregistrement."""
        self.recording = False
        self.record_btn.setStyleSheet("")

    def save_recording(self):
        """Sauvegarde l'enregistrement."""
        if self.record_buffer.size == 0:
            QMessageBox.warning(self, "Erreur", "Rien à enregistrer")
            return

        os.makedirs("recordings", exist_ok=True)
        filename = f"rec_{self.user_id}_{int(__import__('time').time())}.wav"
        filepath = os.path.join("recordings", filename)

        if audio_core.save_recording(self.record_buffer, filepath):
            QMessageBox.information(self, "Succès", f"Sauvegardé: {filepath}")
            self.record_buffer = np.zeros((0,))
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de sauvegarder")
    
    def set_volume(self, value: int):
        """Ajuste le volume (0-100)."""
        # La valeur sera utilisée lors du prochain rendu audio
        pass
    
    def switch_theme(self, theme_name: str):
        """Bascule entre les thèmes sombre et clair."""
        self.theme = "dark" if theme_name == "Sombre" else "light"
        self.apply_theme()
        
        # Mettre à jour les touches du balafon
        for key in self.key_buttons:
            key.update_style(key.is_active)
        
        # Mettre à jour le spectre
        if hasattr(self, 'spectrum'):
            self.spectrum.set_theme(COLORS[self.theme])
    
    def toggle_fullscreen(self, state: int):
        """Active/désactive le mode plein écran."""
        if state == Qt.Checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def keyPressEvent(self, event):
        """Gère les touches clavier."""
        if event.isAutoRepeat():
            return

        key_char = event.text().upper()
        key_map = {
            'A': 0, 'Z': 1, 'E': 2, 'R': 3, 'T': 4, 'Y': 5, 'U': 6, 'I': 7, 'O': 8, 'P': 9,
            'Q': 10, 'S': 11, 'D': 12, 'F': 13, 'G': 14, 'H': 15, 'J': 16, 'K': 17, 'L': 18,
            'M': 19, 'W': 20, 'X': 21,
        }

        if key_char in key_map:
            idx = key_map[key_char]
            if idx < len(self.key_buttons):
                self.key_buttons[idx].activate()
                audio_core.play_async(self.balafon_notes[idx].frequency)
                self.on_key_pressed(self.balafon_notes[idx].frequency)


def main():
    """Point d'entrée de l'application."""
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
