from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
)
from PyQt5.QtCore import pyqtSignal, Qt
from models.user_model import UserModel

class LoginWindow(QDialog):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Transport Management System - Sign In')
        self.setFixedSize(900, 650)
        self.user_model = UserModel()
        self.user_data = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Center the login card
        container = QWidget()
        container_layout = QHBoxLayout(container)
        
        card = QFrame()
        card.setObjectName('LoginCard')
        card.setFixedWidth(700)
        card.setGraphicsEffect(self._create_shadow())
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 50, 40, 50)
        card_layout.setSpacing(20)

        # Branding
        title = QLabel('Transport Management System')
        title.setObjectName('LoginTitle')
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel('Sign in to manage your transport network')
        subtitle.setStyleSheet('color: #636E72; font-size: 10pt;')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setMinimumHeight(45)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)

        self.login_button = QPushButton('Sign In')
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_button)
        card_layout.addStretch()

        container_layout.addWidget(card)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _create_shadow(self):
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        from PyQt5.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        return shadow

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        user = self.user_model.authenticate(username, password)
        if user:
            self.user_data = user
            self.login_success.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, 'Access Denied', 'Invalid username or password.')
