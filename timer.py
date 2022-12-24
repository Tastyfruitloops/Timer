import os
from time import gmtime
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QLabel,
    QMainWindow,
    QApplication,
    QFileDialog,
)


def edit_time(time, limit):
    if len(time) > 2:
        time = time[-2:]
    if len(time) < 2:
        time = "0" * (2 - len(time)) + time
    if int(time) > limit:
        time = str(limit)
    return time


class TimerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        width = 550
        height = 200
        self.timer_setup(width, height)

    def timer_setup(self, width, height):
        self.active = False
        self.paused = False
        self.started = False


        self.setGeometry(0, 0, width, height)
        self.setup_ui()

        self.set_editing_finished_connections()
        self.set_clicked_connections()

        self.hours_button.setValidator(QtGui.QIntValidator())
        self.minutes_button.setValidator(QtGui.QIntValidator())
        self.seconds_button.setValidator(QtGui.QIntValidator())

        self.setup_media_player()

        self.time = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.setInterval(1000)

    def setup_media_player(self):
        self.default_alarm = "resources/alarm.mp3"
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(
            QUrl.fromLocalFile(self.default_alarm)
        )

    def setup_ui(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.center_app()
        self.setStyleSheet(
            "background-color: #1E1D1D;"
            "border-radius: 200px;"
        )

        self.label = QLabel("Timer", self)
        self.label.setGeometry(240, 10, 100, 50)
        self.label.setStyleSheet(
            "font-family: 'Inter';"
            "font-size: 32px;"
            "color: #ffffff"
        )

        self.hours_button = QLineEdit("00", self)
        self.hours_button.setGeometry(40, 70, 100, 90)
        self.hours_button.setStyleSheet(
            "background-color: #000000;"
            "color: #ffffff;"
            "border-style: outset;"
            "border-radius: 5px;"
            "font-size: 50px;"
            "font-family: 'Inter';"
        )
        self.hours_button.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.minutes_button = QLineEdit("00", self)
        self.minutes_button.setGeometry(165, 70, 100, 90)
        self.minutes_button.setStyleSheet(
            "background-color: #000000;"
            "color: #ffffff;"
            "border-style: outset;"
            "border-radius: 5px;"
            "font-size: 50px;"
            "font-family: 'Inter';"
        )
        self.minutes_button.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.seconds_button = QLineEdit("00", self)
        self.seconds_button.setGeometry(290, 70, 100, 90)
        self.seconds_button.setStyleSheet(
            "background-color: #000000;"
            "color: #ffffff;"
            "border-style: outset;"
            "border-radius: 5px;"
            "font-size: 50px;"
            "font-family: 'Inter';"
        )
        self.seconds_button.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.dots = [
            QLabel("", self),
            QLabel("", self),
            QLabel("", self),
            QLabel("", self),
        ]
        self.dots[0].setGeometry(150, 100, 5, 5)
        self.dots[1].setGeometry(150, 130, 5, 5)
        self.dots[2].setGeometry(275, 100, 5, 5)
        self.dots[3].setGeometry(275, 130, 5, 5)
        self.dots[0].setStyleSheet(
            "background-color: #ffffff"
        )
        self.dots[1].setStyleSheet(
            "background-color: #ffffff"
        )
        self.dots[2].setStyleSheet(
            "background-color: #ffffff"
        )
        self.dots[3].setStyleSheet(
            "background-color: #ffffff"
        )

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(410, 120, 100, 40)
        self.start_button.setStyleSheet(
            "background-color: #2CFF80;"
            "font-size: 14px;"
            "color: #000000;"
            "border-style: outset;"
            "border-radius: 5px;"
            "font-family: 'Inter';"
        )

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setGeometry(410, 70, 100, 40)
        self.reset_button.setStyleSheet(
            "background-color: #00CCF9;"
            "font-size: 14px;"
            "color: #000000;"
            "border-style: outset;"
            "border-radius: 5px;"
            "font-family: 'Inter';"
        )

        self.upload_button = QPushButton("", self)
        self.upload_button.setGeometry(470, 20, 25, 25)
        self.upload_button.setStyleSheet("")
        self.upload_button.setIcon(QtGui.QIcon("resources/update.png"))
        self.upload_button.setIconSize(QtCore.QSize(25, 25))

        self.close_button = QPushButton("", self)
        self.close_button.setGeometry(510, 20, 25, 25)
        self.close_button.setStyleSheet("")
        self.close_button.setIcon(QtGui.QIcon("resources/close.png"))
        self.close_button.setIconSize(QtCore.QSize(25, 25))

    def set_clicked_connections(self):
        self.start_button.clicked.connect(self.start_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        self.close_button.clicked.connect(self.shutdown)
        self.upload_button.clicked.connect(self.upload_new_alarm)

    def upload_new_alarm(self):
        if not self.started:
            qfileDialog = QFileDialog.getOpenFileName(
                parent=self,
                caption="Choose media file",
                directory=f"{os.getcwd()}/resources/",
            )
            filename = qfileDialog[0]
            self.media_player.setSource(
                QUrl.fromLocalFile(filename)
            )

    def set_editing_finished_connections(self):
        self.hours_button.editingFinished.connect(
            self.edit_hours
        )
        self.minutes_button.editingFinished.connect(
            self.edit_minutes
        )
        self.seconds_button.editingFinished.connect(
            self.edit_seconds
        )

    def edit_hours(self):
        self.hours_button.setText(
            edit_time(self.hours_button.text(), 99)
        )

    def edit_minutes(self):
        self.minutes_button.setText(
            edit_time(self.minutes_button.text(), 59)
        )

    def edit_seconds(self):
        self.seconds_button.setText(
            edit_time(self.seconds_button.text(), 59)
        )

    def shutdown(self):
        self.close()

    def get_self_time(self):
        h = int(self.hours_button.text())
        m = int(self.minutes_button.text())
        s = int(self.seconds_button.text())
        return s + 60 * m + 3600 * h

    def start_timer(self):
        if self.started:
            self.started = False
            self.paused = True
            self.timer.stop()
            self.start_button.setText("Continue")
            self.start_button.setStyleSheet(
                "background-color: #2CFF80;"
                "font-size: 14px;"
                "color: #000000;"
                "border-style: outset;"
                "border-radius: 5px;"
                "font-family: 'Inter';"
            )
            self.block_time_edit(False)
        else:
            if not self.active:
                self.media_player.stop()
            if not self.active or self.paused:
                self.active = True
                self.started = True
                self.paused = False
                self.time = self.get_self_time()
                self.timer.start()
                self.start_button.setText("Pause")
                self.start_button.setStyleSheet(
                    "background-color: #FF2C2C;"
                    "font-size: 14px;"
                    "color: #000000;"
                    "border-style: outset;"
                    "border-radius: 5px;"
                    "font-family: 'Inter';"
                )
                if self.started:
                    self.block_time_edit(True)
                self.update_display()

    def reset_timer(self):
        self.timer.stop()
        self.time = 0

        self.active = False
        self.paused = False
        self.started = False

        self.block_time_edit(False)

        self.start_button.setStyleSheet(
            "background-color: #2CFF80;"
            "font-size: 14px;"
            "color: #000000;"
            "border-style: outset;"
            "border-radius: 5px;"
            "font-family: 'Inter';"
        )
        self.start_button.setText("Start")
        self.update_display()

    def block_time_edit(self, flag):
        self.hours_button.setReadOnly(flag)
        self.minutes_button.setReadOnly(flag)
        self.seconds_button.setReadOnly(flag)

    def center_app(self):
        screen_centre = self.screen().availableGeometry().center()
        screen_centre.setX(screen_centre.x() - (self.width() // 2))
        screen_centre.setY(screen_centre.y() - (self.height() // 2))
        self.move(screen_centre)

    def update_time(self):
        if self.time:
            self.time -= 1
            self.update_display()
        else:
            self.media_player.play()
            self.reset_timer()

    def update_display(self):
        st = gmtime(self.time)
        self.hours_button.setText(str(st.tm_hour))
        self.edit_hours()
        self.minutes_button.setText(str(st.tm_min))
        self.edit_minutes()
        self.seconds_button.setText(str(st.tm_sec))
        self.edit_seconds()


if __name__ == "__main__":
    timer_app = QApplication([])
    window = TimerWindow()
    window.show()

    timer_app.exec()
