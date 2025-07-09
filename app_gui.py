import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import vision_controller

class FitVisionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FitVision")
        self.setGeometry(100, 100, 350, 300)

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        """Configura os widgets da interface."""
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # --- Título ---
        title_label = QLabel("FitVision")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("TitleLabel")
        layout.addWidget(title_label)

        # --- Seleção de Exercício ---
        self.exercise_label = QLabel("Escolha o Exercício:")
        layout.addWidget(self.exercise_label)

        self.exercise_combo = QComboBox()
        self.exercise_combo.addItems(["squat", "bicep_curl", "jumping_jack"])
        layout.addWidget(self.exercise_combo)

        # --- Seleção de Nível ---
        self.level_label = QLabel("Escolha o Nível:")
        layout.addWidget(self.level_label)

        self.level_combo = QComboBox()
        # Nomes mais descritivos para os níveis
        self.level_combo.addItems(["beginner", "medium", "advanced"])
        layout.addWidget(self.level_combo)

        # Espaçador
        layout.addStretch()
        
        # --- Layout para os botões ---
        button_layout = QHBoxLayout()
        
        self.quit_button = QPushButton("Sair")
        self.quit_button.clicked.connect(self.close) # Conecta ao fechamento da app
        button_layout.addWidget(self.quit_button)

        self.start_button = QPushButton("Iniciar Sessão")
        self.start_button.clicked.connect(self.start_session)
        button_layout.addWidget(self.start_button)

        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def apply_stylesheet(self):
        """Aplica uma folha de estilos (QSS) para um visual moderno."""
        stylesheet = """
            QWidget {
                background-color: #2E3440; /* Nord Polar Night */
                color: #D8DEE9; /* Nord Snow Storm */
                font-family: Arial;
                font-size: 11pt;
            }
            #TitleLabel {
                color: #88C0D0; /* Nord Frost */
                padding-bottom: 10px;
            }
            QLabel {
                color: #E5E9F0;
            }
            QComboBox {
                border: 1px solid #4C566A;
                border-radius: 5px;
                padding: 8px;
                background-color: #3B4252;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                selection-background-color: #81A1C1; /* Nord Frost */
                color: #ECEFF4;
            }
            QPushButton {
                background-color: #5E81AC; /* Nord Frost */
                color: #ECEFF4;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81A1C1; /* Nord Frost, mais claro */
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
            #QuitButton { /* Estilo específico para o botão de sair, se necessário */
                 background-color: #BF616A; /* Nord Aurora Red */
            }
        """
        self.setStyleSheet(stylesheet)
        # Aplica um ID ao botão de sair para estilização opcional
        self.quit_button.setObjectName("QuitButton")


    def start_session(self):
        """Obtém os valores selecionados, esconde a GUI e inicia a câmera."""
        selected_exercise = self.exercise_combo.currentText()
        selected_level = self.level_combo.currentText()
        
        print(f"Configuração selecionada: Exercício={selected_exercise}, Nível={selected_level}")
        
        self.hide()
        vision_controller.start_exercise_session(selected_exercise, selected_level)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FitVisionApp()
    window.show()
    sys.exit(app.exec())
