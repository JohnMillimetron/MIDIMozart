import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy, QWidget, QFrame, \
    QLineEdit, QRadioButton, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QCoreApplication, Qt, QRect
from MIDIMozartClasses import *
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
        self.setWindowTitle('MIDIMozart - untitled')

        self.current_duration = 1
        self.current_chanel = 1
        self.current_tempo = 120

        self.glissando_first_note = []
        self.manual_chord_notes = []

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
            eval(f'self.chanel{i + 1}notes_frame.setGeometry(QRect(160, 0, 1920, 81))')
            self.chanel_layouts[i].setGeometry(QRect(161, 0, 1920, 80))
            self.chanel_layouts[i].setSpacing(0)
            self.chanel_layouts[i].setAlignment(Qt.AlignLeft)
            self.chanel_layouts[i].setContentsMargins(0, 0, 0, 0)

        for i in range(16):
            eval(f'self.chanel{i + 1}instrument_input.valueChanged.connect(self.instrument_change)')
        for i in range(3):
            eval(f'self.chanel{i + 1}volume_input.valueChanged.connect(self.volume_change)')

        # Привязка кнопок к обработчикам
        self.create_button.clicked.connect(self.create_midi)
        self.chanel_input.valueChanged.connect(self.current_chanel_change)
        self.tempo_input.valueChanged.connect(self.current_tempo_change)
        self.chord_ready_button.clicked.connect(self.manual_chord_paste)
        self.manual_chord_clear_button.clicked.connect(self.manual_chord_clear)
        self.rest_button.clicked.connect(self.add_rest)
        self.interval_width_input.valueChanged.connect(self.interval_name_change)

        self.load_file_button.clicked.connect(self.open_file)

        self.channelsAreaWidget.setGeometry(0, 0, 1920, 1280)

    # Обработчик нажатия клавиши фортепиано
    def key_clicked(self):
        self.read_type_of_note(int(self.sender().text().split('\n')[1]))

    # Отрисовывает графическое изображение ноты в канале
    def make_button(self, size, note_name, chanel_number, note_number=None):
        self.chanel_buttons[chanel_number - 1].append(
            NoteButton(note_number=len(MyComposition[chanel_number - 1].notes) if not note_number else
            note_number, ch_number=chanel_number, note_name=note_name))

        print(self.chanel_layouts[self.current_chanel - 1].geometry().width())

        if sum(map(lambda x: x.width(), self.chanel_buttons[self.current_chanel - 1])) + size > self.chanel_layouts[
            self.current_chanel - 1].geometry().width():
            curr_w = self.chanel_layouts[self.current_chanel - 1].geometry().width()
            self.channelsAreaWidget.setGeometry(
                QRect(0, 0, max(map(lambda x: x.geometry().width(), self.chanel_layouts)) + size, 1280))
            eval(f'self.chanel{self.current_chanel}.setGeometry('
                 f'QRect(0, 80 * (self.current_chanel - 1), curr_w + size, 81))')
            eval(f'self.chanel{self.current_chanel}notes_frame.setGeometry(QRect(160, 0, curr_w + size, 81))')
            self.chanel_layouts[self.current_chanel - 1].setGeometry(QRect(2, 2, curr_w + size, 77))

        eval(f'print(self.chanel{self.current_chanel}notes_frame.geometry().width())')
        print(self.chanel_layouts[self.current_chanel - 1].geometry().width(), end='\n\n')

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

    def interval_name_change(self):
        names = {
            1: 'Малая секунда',
            2: 'Большая секунда',
            3: 'Малая терция',
            4: 'Большая секунда',
            5: 'Чистая кварта',
            6: 'Тритон',
            7: 'Чистая квинта',
            8: 'Малая секста',
            9: 'Большая секста',
            10: 'Малая септима',
            11: 'Большая секунда',
            12: 'Октава'
        }
        width = self.interval_width_input.value()
        self.interval_name.setText(names.get(width))

    def read_type_of_note(self, pitch):
        # Вызывается при нажатии клавиши на фо-но, считывает параметры того, что нужно добавить на канал
        # Если ожидается нажатие дополнительных клавиш для завершения действия, возвращает pitch
        if self.glissando_first_note:
            MyComposition[self.current_chanel - 1].add_note(self.glissando_first_note, pitch,
                                                            duration=float(self.current_duration), type='gliss')
            self.make_button(note_name=f'{pitch_to_name(self.glissando_first_note)}-{pitch_to_name(pitch)}\nGliss',
                             size=int(self.current_duration * 100),
                             chanel_number=self.current_chanel)
            self.glissando_first_note = None

        if self.note_radio_button.isChecked():
            if self.default_note_button.isChecked():
                MyComposition[self.current_chanel - 1].add_note(pitch, duration=float(self.current_duration))
                self.make_button(note_name=pitch_to_name(pitch), size=int(self.current_duration * 100),
                                 chanel_number=self.current_chanel)
            elif self.trem_note_button.isChecked():
                MyComposition[self.current_chanel - 1].add_note(pitch, duration=float(self.current_duration),
                                                                type='tremolo')
                self.make_button(note_name=f'{pitch_to_name(pitch)}\ntremolo', size=int(self.current_duration * 100),
                                 chanel_number=self.current_chanel)
            elif self.trill_note_button.isChecked():
                MyComposition[self.current_chanel - 1].add_note(pitch, duration=float(self.current_duration),
                                                                type='trill')
                self.make_button(note_name=f'{pitch_to_name(pitch)}\ntrill', size=int(self.current_duration * 100),
                                 chanel_number=self.current_chanel)

        elif self.chord_radio_button.isChecked():

            if self.manual_chord_button.isChecked():
                if len(self.manual_chord_notes) <= 10:
                    self.manual_chord_line.setText(pitch_to_name(pitch)
                                                   if self.manual_chord_line.text() == 'Notes will appear here...'
                                                   else self.manual_chord_line.text() + ' ' + pitch_to_name(pitch))

                    self.manual_chord_notes.append(pitch)
            elif self.auto_chord_button.isChecked():
                arpeggiato = self.chord_arpeggiato_button.isChecked()
                MyComposition[self.current_chanel - 1].add_chord(pitch,
                                                                 self.chord_structure_input.currentText().lower(),
                                                                 duration=self.current_duration,
                                                                 arpeggiato=arpeggiato)
                a = " ".join(list(map(lambda x: x.name, MyComposition[self.current_chanel - 1][-1].notes)))
                self.make_button(note_name=f'Chord\n{a}\n{"arpeggiato" if arpeggiato else ""}',
                                 size=int(self.current_duration * 100), chanel_number=self.current_chanel)

        elif self.gliss_radio_button.isChecked():
            self.glissando_first_note = pitch

        elif self.interval_radio_button.isChecked():
            width = self.interval_width_input.value()
            MyComposition[self.current_chanel - 1].add_chord((pitch, pitch + width),
                                                             duration=float(self.current_duration))
            self.make_button(
                note_name=f'{pitch_to_name(pitch)} {pitch_to_name(pitch + width)}\n{self.interval_name.text()}',
                size=int(self.current_duration * 100), chanel_number=self.current_chanel)

    def add_rest(self):
        MyComposition[self.current_chanel - 1].add_note(duration=self.current_duration, type='rest')
        self.make_button(note_name='Rest', size=int(self.current_duration * 100),
                         chanel_number=self.current_chanel)

    def manual_chord_paste(self):
        if self.manual_chord_line.text() != 'Notes will appear here...' \
                and len(self.manual_chord_line.text().split()) > 1:
            pitches = tuple(map(lambda x: name_to_pitch(x), self.manual_chord_line.text().split()))
            arpeggiato = self.chord_arpeggiato_button.isChecked()
            MyComposition[self.current_chanel - 1].add_chord(pitches, duration=self.current_duration,
                                                             arpeggiato=arpeggiato)
            self.make_button(note_name=f'Chord\n{self.manual_chord_line.text()}\n{"arpeggiato" if arpeggiato else ""}',
                             size=int(self.current_duration * 100), chanel_number=self.current_chanel)

    def manual_chord_clear(self):
        self.manual_chord_line.setText('Notes will appear here...')

    # Обработчик клавиатуры
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Z:
            self.C4.click()
        elif key == Qt.Key_S:
            self.Cis4.click()
        elif key == Qt.Key_X:
            self.D4.click()
        elif key == Qt.Key_D:
            self.Dis4.click()
        elif key == Qt.Key_C:
            self.E4.click()
        elif key == Qt.Key_V:
            self.F4.click()
        elif key == Qt.Key_G:
            self.Fis4.click()
        elif key == Qt.Key_B:
            self.G4.click()
        elif key == Qt.Key_H:
            self.Gis4.click()
        elif key == Qt.Key_N:
            self.A4.click()
        elif key == Qt.Key_J:
            self.B4.click()
        elif key == Qt.Key_M:
            self.H4.click()
        elif key == Qt.Key_Q or key == Qt.Key_Comma:
            self.C5.click()
        elif key == Qt.Key_2 or key == Qt.Key_L:
            self.Cis5.click()
        elif key == Qt.Key_W or key == Qt.Key_Period:
            self.D5.click()
        elif key == Qt.Key_3 or key == Qt.Key_Semicolon:
            self.Dis5.click()
        elif key == Qt.Key_E or key == Qt.Key_Slash:
            self.E5.click()
        elif key == Qt.Key_R:
            self.F5.click()
        elif key == Qt.Key_5:
            self.Fis5.click()
        elif key == Qt.Key_T:
            self.G5.click()
        elif key == Qt.Key_6:
            self.Gis5.click()
        elif key == Qt.Key_Y:
            self.A5.click()
        elif key == Qt.Key_7:
            self.B5.click()
        elif key == Qt.Key_U:
            self.H5.click()
        elif key == Qt.Key_I:
            self.C6.click()
        elif key == Qt.Key_Space:
            self.rest_button.click()
        elif key == Qt.Key_Backspace:
            if self.chanel_buttons[self.current_chanel - 1]:
                self.chanel_layouts[self.current_chanel - 1].itemAt(
                    len(self.chanel_buttons[self.current_chanel - 1]) - 1).widget().click()

    def instrument_change(self):
        MyComposition[int(self.sender().objectName()[6]) - 1].set_instrument(int(self.sender().value()) - 1)

    def volume_change(self):
        MyComposition[int(self.sender().objectName()[6]) - 1].set_volume(int(self.sender().value()))

    # Создаёт MIDI-файл
    def create_midi(self):
        print(MyComposition)
        MyComposition.export_as_midi(f'{self.output_file_name_input.text()}.mid')

    def open_file(self):
        # Name
        # tempo
        # chanel_count
        # ChanelName instrument
        # notes_count
        # type, pitches, time, length, volume
        # type, pitches, time, length, volume

        file_name = QFileDialog.getOpenFileName(
            self, 'Выбрать файл', '',
            'MIDIMozart file (*.mdmz);;Все файлы (*)')[0]

        if not file_name:
            return

        with open(file_name, mode='r', encoding='utf-8') as file:
            self.composition_name = file.readline().strip()
            print(self.composition_name)
            self.setWindowTitle('MIDIMozart - ' + self.composition_name)

            self.current_tempo = int(file.readline())
            print(self.current_tempo)

            chanel_count = int(file.readline())
            print(chanel_count)

            for i in range(chanel_count):
                name, instrument = file.readline().strip().split()
                print(name, instrument)
                MyComposition[i].set_name(name)
                MyComposition[i].set_instrument(int(instrument))
                eval(f'self.chanel{i + 1}name.setText(name)')
                eval(f'self.chanel{i + 1}instrument_input.setValue(int(instrument) + 1)')
                notes_count = int(file.readline())
                print(notes_count)
                for j in range(notes_count):
                    print(file.readline().split())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
