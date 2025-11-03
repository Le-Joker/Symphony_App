
import sys
import os
from PyQt5.QtWidgets import QApplication

from db_manager import create_db
from ui_controller import LoginWindow


def main():
	"""Point d'entrée de l'application.

	- Crée le dossier `data/` et la base SQLite si nécessaire.
	- Lance la fenêtre de connexion (LoginWindow).
	"""
	base_dir = os.path.dirname(__file__)
	data_dir = os.path.join(base_dir, 'data')
	os.makedirs(data_dir, exist_ok=True)
	db_path = os.path.join(data_dir, 'symphony.db')
	# création de la base et des tables si nécessaire
	create_db(db_path)

	app = QApplication(sys.argv)
	# ouvrir l'écran de connexion
	win = LoginWindow(db_path)
	win.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()

