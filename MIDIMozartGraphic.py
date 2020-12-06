import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy, QWidget, QFrame
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QCoreApplication, Qt, QRect
from MIDIMozartClasses import Composition, NOTES_AND_NAMES_is, NOTE_NUMBERS_AND_OCTAVES
from MIDIMozartDesign import Ui_MIDIMozart

# pyuic5 MIDIMozartDesign.ui -o MIDIMozartDesign.py
QCoreApplication.addLibraryPath(
    r"C:\Users\Андрей\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\PyQt5\Qt\plugins")

MyComposition = Composition()


class MainWindow(QMainWindow):
    def __init__(self):
        # super().__init__()
        # self.setupUi(self)

        super().__init__()
        uic.loadUi('MIDIMozartDesign.ui', self)  # Загружаем дизайн

        self.current_duration = 1

        # Привязка клавиш к обработчику
        for i in range(21, 109):
            for diapason in NOTE_NUMBERS_AND_OCTAVES.keys():
                if i in diapason:
                    octave = NOTE_NUMBERS_AND_OCTAVES.get(diapason)
                    name = NOTES_AND_NAMES_is.get(i - 12 * int(octave)) + octave
                    eval(f'self.{name}.clicked.connect(self.key_clicked)')
                    break

        # Привязка кнопок длительностей
        temp = ['1', '2', '2p', '4', '4p', '8', '8p', '16', '16p']
        while temp:
            eval(f'self.duration_button_{temp.pop()}.clicked.connect(self.duration_button_clicked)')

        # Создание лэйаутов
        self.chanel_layouts = [QHBoxLayout(self.chanel1notes_frame), QHBoxLayout(self.chanel2notes_frame),
                               QHBoxLayout(self.chanel3notes_frame), QHBoxLayout(self.chanel4notes_frame),
                               QHBoxLayout(self.chanel5notes_frame), QHBoxLayout(self.chanel6notes_frame),
                               QHBoxLayout(self.chanel7notes_frame), QHBoxLayout(self.chanel8notes_frame),
                               QHBoxLayout(self.chanel9notes_frame), QHBoxLayout(self.chanel10notes_frame),
                               QHBoxLayout(self.chanel11notes_frame), QHBoxLayout(self.chanel12notes_frame),
                               QHBoxLayout(self.chanel13notes_frame), QHBoxLayout(self.chanel14notes_frame),
                               QHBoxLayout(self.chanel15notes_frame), QHBoxLayout(self.chanel16notes_frame)]
        for i in range(16):
            eval(f'self.chanel_layouts[{i}].setGeometry(QRect(161, 0, 3840, 80))')
            eval(f'self.chanel_layouts[{i}].setSpacing(0)')
            eval(f'self.chanel_layouts[{i}].setAlignment(Qt.AlignLeft)')
            eval(f'self.chanel_layouts[{i}].setContentsMargins(0, 0, 0, 0)')
            # self.chanel_layouts[i].addWidget(QPushButton())

        # Привязка кнопок к обработчикам
        self.create_button.clicked.connect(self.create_midi)
        self.instrument_input.valueChanged.connect(self.instrument_change)

    def key_clicked(self):
        MyComposition[int(self.chanel_input.value()) - 1].add_note(pitch=int(self.sender().text().split('\n')[1]),
                                                                   duration=float(self.current_duration))
        self.make_button(text=self.sender().text().split('\n')[0], x=int(self.current_duration * 100),
                         ch_n=int(self.chanel_input.value()))

    def make_button(self, x, text, ch_n):
        btn = QPushButton(text=f'{ch_n}\n{len(MyComposition[ch_n - 1].notes)}\n{text}')
        btn.setMaximumWidth(x)
        btn.setMinimumWidth(x)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        btn.clicked.connect(self.delete_note)
        eval(f'self.chanel_layouts[{ch_n - 1}].addWidget(btn)')

    def duration_button_clicked(self):
        temp = {"1": 4, "2": 2, "2.": 3, "4": 1, "4.": 1.5, "8": 0.5, "8.": 0.75, "16": 0.25, "16.": 0.375}
        self.current_duration = temp.get(self.sender().text())
        self.duration_label.setText(f'Current duration: {self.current_duration} beats')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z:
            self.C4.click()
        elif event.key() == Qt.Key_S:
            self.Cis4.click()
        elif event.key() == Qt.Key_X:
            self.D4.click()
        elif event.key() == Qt.Key_D:
            self.Dis4.click()
        elif event.key() == Qt.Key_C:
            self.E4.click()
        elif event.key() == Qt.Key_V:
            self.F4.click()
        elif event.key() == Qt.Key_G:
            self.Fis4.click()
        elif event.key() == Qt.Key_B:
            self.G4.click()
        elif event.key() == Qt.Key_H:
            self.Gis4.click()
        elif event.key() == Qt.Key_N:
            self.A4.click()
        elif event.key() == Qt.Key_J:
            self.B4.click()
        elif event.key() == Qt.Key_M:
            self.H4.click()

    def instrument_change(self, instr_num):
        MyComposition[int(self.chanel_input.value()) - 1].set_instrument(int(instr_num) - 1)

    def create_midi(self):
        print(MyComposition)
        MyComposition.export_as_midi('test4.mid')

    def delete_note(self):
        ch_n, note_n, _ = self.sender().text().split('\n')
        MyComposition[int(ch_n) - 1].remove_note(int(note_n) - 1)
        self.chanel_layouts[ch_n - 1].removeWidget(self.sender())

    # def refresh(self):
    #     for i, chanel in enumerate(MyComposition):
    #         for note in chanel:
    #             btn = QPushButton(text=str(note), parent=self.channelsAreaWidget)
    #             btn.resize(100, 50)
    #             btn.move(0, 0)
    #             # btn = QPushButton(text=str(note), parent=self.channelsAreaWidget)
    #             # self.graphic_notes[i].append(btn)
    #             # btn.move(10, 10)
    #             # btn.resize(10, 10)
    #             # print(self.graphic_notes)
    #             self.channelsAreaWidget.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
