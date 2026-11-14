
import sys
import threading
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from jarvis import main


PROJECT_ROOT = Path(__file__).resolve().parent
GIF_PATH = PROJECT_ROOT / "cbe227_fb70e39e9dd94e30bbe30c48b2367dd8~mv2.gif"


class MujibUI(QWidget):

    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.is_listening = False
        self.process_thread = None
        self.movie = None
        self.drag_position = None
        self.stop_event = threading.Event()

        self.init_ui()
        self.status_changed.connect(self.update_status)

    def init_ui(self):

        self.setWindowTitle("MUJIB AI")
        self.setFixedSize(280, 280)

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        self.mic_label = QLabel(self)
        self.mic_label.setGeometry(10, 10, 260, 260)
        self.mic_label.setAlignment(Qt.AlignCenter)

        self.mic_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        self.mic_label.setAttribute(
            Qt.WA_TranslucentBackground, True
        )

        if GIF_PATH.is_file():

            self.movie = QMovie(str(GIF_PATH))
            self.movie.setScaledSize(QSize(260, 260))
            self.mic_label.setMovie(self.movie)
            self.movie.start()

        else:
            self.mic_label.setText("MUJIB")
            self.mic_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    color: #00d9ff;
                    font-size: 35px;
                    font-weight: bold;
                }
            """)

        self.mic_label.installEventFilter(self)

        self.setToolTip(
            "Left click: Start | Right click: Stop and Exit | Drag: Move"
        )

    def update_status(self, message):
        print("MUJIB STATUS:", message)
        self.setToolTip(message)

    def start_listening(self):

        if self.is_listening:
            return

        self.is_listening = True
        self.stop_event.clear()

        self.status_changed.emit("MUJIB is starting...")

        self.process_thread = threading.Thread(
            target=self.run_mujib,
            daemon=True
        )

        self.process_thread.start()

    def run_mujib(self):

        try:
            main(self.stop_event)

        except Exception as error:
            print("MUJIB Startup Error:", error)
            self.status_changed.emit("Startup error. Check terminal.")

        finally:
            self.is_listening = False
            self.status_changed.emit("MUJIB stopped.")

    def stop_mujib(self):

        if not self.is_listening:
            self.close()
            return

        self.status_changed.emit("Stopping MUJIB...")
        self.stop_event.set()

        if self.movie:
            self.movie.stop()

        self.close()

    def eventFilter(self, watched, event):

        if watched is self.mic_label:

            if event.type() == event.MouseButtonPress:

                if event.button() == Qt.RightButton:
                    self.stop_mujib()
                    return True

                if event.button() == Qt.LeftButton:

                    self.drag_position = (
                        event.globalPos()
                        - self.frameGeometry().topLeft()
                    )

                    if not self.is_listening:
                        self.start_listening()

                    return True

            elif event.type() == event.MouseMove:

                if (
                    event.buttons() == Qt.LeftButton
                    and self.drag_position is not None
                ):
                    self.move(
                        event.globalPos() - self.drag_position
                    )
                    return True

            elif event.type() == event.MouseButtonRelease:
                self.drag_position = None
                return True

        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.stop_mujib()
            return

        super().keyPressEvent(event)

    def closeEvent(self, event):

        self.stop_event.set()

        if self.movie:
            self.movie.stop()

        event.accept()


def UI():

    app = QApplication(sys.argv)

    window = MujibUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    UI()
