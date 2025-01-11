import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class KeyPressApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Keypress Display")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: white;")

        # Create a label to display the pressed key
        self.label = QLabel(self)
        self.label.setText("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: black; font: 300px Arial;")
        self.label.setGeometry(0, 0, 400, 400)

    def keyPressEvent(self, event: QKeyEvent):
        """Handles key press events and updates the label."""
        self.label.setText(event.text())


def main():
    app = QApplication(sys.argv)
    window = KeyPressApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
