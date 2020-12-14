import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy, QWidget, QFrame
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QCoreApplication, Qt, QRect
from MIDIMozartClasses import Composition, NOTES_AND_NAMES_is, NOTE_NUMBERS_AND_OCTAVES, NoteButton
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
        self.setWindowTitle('MIDIMozart')

        self.current_duration = 1
        self.current_chanel = 1
        self.current_tempo = 120

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
        self.chanel_buttons = [[] for _ in range(16)]
        for i in range(16):
            eval(f'self.chanel_layouts[{i}].setGeometry(QRect(161, 0, 3840, 80))')
            eval(f'self.chanel_layouts[{i}].setSpacing(0)')
            eval(f'self.chanel_layouts[{i}].setAlignment(Qt.AlignLeft)')
            eval(f'self.chanel_layouts[{i}].setContentsMargins(0, 0, 0, 0)')

        for i in range(16):
            eval(f'self.chanel{i + 1}instrument_input.valueChanged.connect(self.instrument_change)')

        # Привязка кнопок к обработчикам
        self.create_button.clicked.connect(self.create_midi)
        self.chanel_input.valueChanged.connect(self.current_chanel_change)
        self.tempo_input.valueChanged.connect(self.current_tempo_change)
        # self.instrument_input.valueChanged.connect(self.instrument_change)

        self.channelsAreaWidget.setGeometry(0, 0, 16777216, 1280)

    # Обработчик нажатия клавиши фортепиано
    def key_clicked(self):
        MyComposition[int(self.chanel_input.value()) - 1].add_note(pitch=int(self.sender().text().split('\n')[1]),
                                                                   duration=float(self.current_duration))
        self.make_button(note_name=self.sender().text().split('\n')[0], size=int(self.current_duration * 100),
                         chanel_number=int(self.chanel_input.value()))

    # Отрисовывает графическое изображение ноты в канале
    def make_button(self, size, note_name, chanel_number, note_number=None):
        self.chanel_buttons[chanel_number - 1].append(
            NoteButton(note_number=len(MyComposition[chanel_number - 1].notes) if not note_number else
            note_number, ch_number=chanel_number, note_name=note_name))

        self.chanel_buttons[chanel_number - 1][-1].setText(
            str(self.chanel_buttons[chanel_number - 1][-1].note_name) + '\n' +
            str(self.chanel_buttons[chanel_number - 1][-1].note_number))
        self.chanel_buttons[chanel_number - 1][-1].setMaximumWidth(size)
        self.chanel_buttons[chanel_number - 1][-1].setMinimumWidth(size)
        self.chanel_buttons[chanel_number - 1][-1].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.chanel_buttons[chanel_number - 1][-1].clicked.connect(self.delete_note)
        self.chanel_layouts[chanel_number - 1].addWidget(self.chanel_buttons[chanel_number - 1][-1])

    # Удаляет ноту с канала
    def delete_note(self):
        ch_n = self.sender().ch_number
        note_n = self.chanel_buttons[ch_n - 1].index(self.sender()) + 1
        print(f'delete_note executed for {ch_n, note_n}')
        MyComposition[ch_n - 1].remove_note(note_n - 1)
        self.chanel_layouts[ch_n - 1].removeWidget(self.sender())
        self.chanel_buttons[ch_n - 1].remove(self.chanel_buttons[ch_n - 1][note_n - 1])

        # for i in range(self.chanel_layouts[ch_n].count()):
        #     self.chanel_layouts[ch_n].itemAt(i).note_number = i + 1

        # for i in reversed(range(self.chanel_layouts[ch_n - 1].count())):
        #     widgetToRemove = self.chanel_layouts[ch_n - 1].itemAt(i).widget()
        #     self.chanel_layouts[ch_n - 1].removeWidget(widgetToRemove)
        #     widgetToRemove.setParent(None)
        #
        # for i, note in enumerate(MyComposition[ch_n - 1]):
        #     self.make_button(note_name=note.name, size=int(note.duration * 100), note_number=i + 1,
        #                      chanel_number=ch_n)

    # Обработчик смены длительности
    def duration_button_clicked(self):
        temp = {"1": 4, "2": 2, "2.": 3, "4": 1, "4.": 1.5, "8": 0.5, "8.": 0.75, "16": 0.25, "16.": 0.375}
        self.current_duration = temp.get(self.sender().text())
        self.duration_label.setText(f'Current duration: {self.current_duration} beats')

    def current_chanel_change(self):
        self.current_chanel = int(self.chanel_input.value())

    def current_tempo_change(self):
        MyComposition.set_tempo(self.tempo_input.value())
        self.current_tempo = int(self.tempo_input.value())

    # Обработчик клавиатуры
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

    # Обработчик смены инструмента
    def instrument_change(self):
        MyComposition[int(self.sender().objectName()[6]) - 1].set_instrument(int(self.sender().value()))

    # Создаёт MIDI-файл
    def create_midi(self):
        print(MyComposition)
        MyComposition.export_as_midi('test4.mid')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
