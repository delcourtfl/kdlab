import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QFont, QKeyEvent
from PyQt6.QtCore import Qt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class KeyPressApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.key_char = ""  # Store the pressed key
        self.font = QFont("Arial", 300)  # Cache the font for reuse

    def init_ui(self):
        self.setWindowTitle("Keypress Display")
        self.setGeometry(0, 0, 400, 400)

    def keyPressEvent(self, event: QKeyEvent):
        """Update only when the key changes."""
        self.key_char = event.text()
        self.update()

    def paintEvent(self, event):
        """Efficiently repaint the widget."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)  # Set background color
        if self.key_char:
            painter.setFont(self.font)
            painter.setPen(Qt.GlobalColor.black)
            # text_width = painter.fontMetrics().horizontalAdvance(self.key_char)
            # text_height = painter.fontMetrics().height()
            # x = (400 - text_width) // 2
            # y = (200 + text_height) // 2
            # print("x: ", x, "y: ", y)
            painter.drawText(100, 323, self.key_char)


def main():
    app = QApplication(sys.argv)
    window = KeyPressApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
