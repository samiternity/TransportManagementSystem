import sys
from PyQt5.QtWidgets import QApplication, QDialog
from config import THEME_FILE
from views.login_window import LoginWindow
from views.main_window import MainWindow


def load_theme(app: QApplication):
    try:
        with open(THEME_FILE, 'r', encoding='utf-8') as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        pass


def main():
    app = QApplication(sys.argv)
    load_theme(app)

    while True:
        login = LoginWindow()
        if login.exec_() != QDialog.Accepted:
            break

        user_data = login.user_data or {}
        window = MainWindow(user_data)
        window.show()
        
        # This blocks until the main window is closed
        app.exec_()
        
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

