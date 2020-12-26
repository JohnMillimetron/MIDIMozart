import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QSizePolicy, QFileDialog
from PyQt5 import uic, QtMultimedia
from PyQt5.QtCore import QCoreApplication, Qt, QRect, QUrl
from PyQt5.QtSql import *
from MIDIMozartClasses import *

QCoreApplication.addLibraryPath(
    r"C:\Users\Андрей\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\PyQt5\Qt\plugins")

MyComposition = Composition()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('MIDIMozartDesign.ui', self)  # Загружаем дизайн
        self.setWindowTitle('MIDIMozart - untitled')

        self.current_duration = 1
        self.current_chanel = 1
        self.current_tempo = 120

        self.saved = True
        self.output_midi_name = 'untitled.mid'
        self.output_mdmz_name = 'untitled.mdmz'
        self.composition_name = 'untitled'

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
        temp = ['1', '2', '2p', '4', '4p', '8', '8p', '16', '16p', '32']
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
        for i in range(16):
            eval(f'self.chanel{i + 1}volume_input.valueChanged.connect(self.volume_change)')

        # Привязка кнопок к обработчикам
        self.create_button.clicked.connect(self.create_midi)
        self.chanel_input.valueChanged.connect(self.current_chanel_change)
        self.tempo_input.valueChanged.connect(self.current_tempo_change)
        self.chord_ready_button.clicked.connect(self.manual_chord_paste)
        self.manual_chord_clear_button.clicked.connect(self.manual_chord_clear)
        self.rest_button.clicked.connect(self.add_rest)
        self.interval_width_input.valueChanged.connect(self.interval_name_change)
        self.duration_manual_button.clicked.connect(self.duration_button_clicked)
        self.play_button.clicked.connect(self.play)
        self.stop_button.clicked.connect(self.stop)

        self.load_file_button.clicked.connect(self.open_file)
        self.save_as_button.clicked.connect(self.write_file)

        self.channelsAreaWidget.setGeometry(0, 0, 1920, 1280)

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('MIDIMozartDatabase.sqlite')
        db.open()
        model = QSqlTableModel(self, db)
        model.setTable('ProgramNames')
        model.select()

        self.program_names_table.setModel(model)

    # Заполняет каналы из файла с сохранением .mdmz
    def open_file(self):
        # Name
        # tempo
        # chanel_count
        # ChanelName instrument volume
        # notes_count
        # type pitches time length mod
        # type duration

        file_name = QFileDialog.getOpenFileName(
            self, 'Выбрать файл', '',
            'MIDIMozart file (*.mdmz);;Все файлы (*)')[0]

        if not file_name:
            return

        try:
            with open(file_name, mode='r', encoding='utf-8') as file:
                self.clear_all()

                self.output_mdmz_name = file_name
                self.output_midi_name = file_name

                self.composition_name = file.readline().strip()

                self.current_tempo = int(file.readline())

                chanel_count = int(file.readline())

                for i in range(chanel_count):
                    name, instrument, volume = file.readline().strip().split()
                    MyComposition[i].set_name(name)
                    MyComposition[i].set_instrument(int(instrument))
                    MyComposition[i].set_volume(int(volume))
                    eval(f'self.chanel{i + 1}name.setText(name)')
                    eval(f'self.chanel{i + 1}instrument_input.setValue(int(instrument) + 1)')
                    notes_count = int(file.readline())
                    for j in range(notes_count):
                        line = file.readline().split()

                        if line[0] == 'n':
                            duration, mod = float(line[2]), line[3]
                            pitch = int(line[1])
                            MyComposition[i].add_note(pitch, duration=duration, type=mod, length=duration)
                            mod_name = '\ntrem' if mod == 'tremolo' else '\ntrill' if mod == 'trill' else ''
                            self.make_button(note_name=pitch_to_name(pitch) + mod_name, size=int(duration * 100),
                                             chanel_number=i + 1)

                        elif line[0] == 'c':
                            duration, mod = float(line[2]), line[3]
                            pitches = eval(line[1])
                            MyComposition[i].add_chord(
                                pitches, duration=duration, length=duration, arpeggiato=bool(int(mod)))
                            a = " ".join(list(map(lambda x: pitch_to_name(x), pitches)))
                            self.make_button(note_name=f'Chord\n{a}\n{"arpeggiato" if eval(mod) else ""}',
                                             size=int(duration * 100), chanel_number=i + 1)

                        elif line[0] == 'r':
                            duration = float(line[1])
                            MyComposition[i].add_note(type='rest', duration=duration)
                            self.make_button(note_name='Rest', size=int(duration * 100), chanel_number=i + 1)

                        elif line[0] == 'g':
                            duration, pitches = float(line[2]), eval(line[1])
                            MyComposition[i].add_note(*pitches, type='gliss', duration=duration)
                            self.make_button(
                                note_name=f'Gliss\n{pitch_to_name(pitches[0])}-{pitch_to_name(pitches[1])}',
                                size=int(duration * 100), chanel_number=i + 1)

        except Exception:
            print('Файл некорректен. Произошла ошибка.')
            return

    # Записывает набранные ноты в файл .mdmz
    def write_file(self):
        file_name = QFileDialog.getSaveFileName(
            self, 'Выбрать файл', '',
            'MIDIMozart file (*.mdmz);;Все файлы (*)')[0]

        if not file_name:
            return

        try:
            with open(file_name, mode='w', encoding='utf-8') as file:
                self.output_mdmz_name = file_name
                self.output_midi_name = file_name
                # self.setWindowTitle('MIDIMozart - ' + self.composition_name)

                file.writelines(self.composition_name + '\n')
                file.writelines(str(MyComposition.tempo) + '\n')
                file.writelines('16\n')

                for i in MyComposition.channels:
                    file.writelines(f'{i.name} {i.instrument} {i.volume}\n')
                    file.writelines(str(len(i.notes)) + '\n')
                    for j in i.notes:
                        if type(j) == Note:
                            file.writelines(f'n {j.pitch} {j.length} default\n')
                        elif type(j) == TremoloNote:
                            file.writelines(f'n {j.pitch} {j.length} tremolo\n')
                        elif type(j) == TrillNote:
                            file.writelines(f'n {j.pitch} {j.length} trill\n')
                        elif type(j) == Rest:
                            file.writelines(f'r {j.duration}\n')
                        elif type(j) == Chord:
                            file.writelines(f'c ({",".join(list(map(str, j.pitches)))}) '
                                            f'{j.length} {1 if j.arpeggiato else 0}\n')
                        elif type(j) == Glissando:
                            file.writelines(f'g ({j.pitch},{j.pitch2}) {j.length}\n')
        except Exception:
            print('Произошла ошибка при записи.')
            return

    # Отрисовывает графическое изображение ноты в канале
    def make_button(self, size, note_name, chanel_number, note_number=None):
        self.chanel_buttons[chanel_number - 1].append(NoteButton(
            note_number=len(MyComposition[chanel_number - 1].notes), ch_number=chanel_number, note_name=note_name))

        self.notes_area_resize(size)

        self.chanel_buttons[chanel_number - 1][-1].setText(
            str(self.chanel_buttons[chanel_number - 1][-1].note_name) + '\n' +
            str(self.chanel_buttons[chanel_number - 1][-1].note_number))
        self.chanel_buttons[chanel_number - 1][-1].setMaximumWidth(size)
        self.chanel_buttons[chanel_number - 1][-1].setMinimumWidth(size)
        self.chanel_buttons[chanel_number - 1][-1].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.chanel_buttons[chanel_number - 1][-1].clicked.connect(self.delete_note)
        self.chanel_layouts[chanel_number - 1].addWidget(self.chanel_buttons[chanel_number - 1][-1])

    # Изменяет размер виджета с каналами
    def notes_area_resize(self, size):
        self.channelsAreaWidget.setGeometry(
            QRect(0, 0, self.channelsAreaWidget.geometry().width() + size, 1280))
        for i in range(16):
            eval(f'self.chanel{i + 1}.setGeometry('
                 f'QRect(0, 80 * i, self.chanel{i + 1}.geometry().width() + size, 81))')
            eval(f'self.chanel{i + 1}notes_frame.setGeometry('
                 f'QRect(160, 0, self.chanel{i + 1}notes_frame.geometry().width() + size, 81))')
            self.chanel_layouts[i].setGeometry(
                QRect(2, 2, self.chanel_layouts[i].geometry().width() + size, 77))

    # Очищает все каналы
    def clear_all(self):
        MyComposition.clear()
        for i in self.chanel_buttons:
            i.clear()
        for layout in self.chanel_layouts:
            for i in reversed(range(layout.count())):
                widgetToRemove = layout.itemAt(i).widget()
                # remove it from the layout list
                layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

    # Обработчик нажатия клавиши фортепиано
    def key_clicked(self):
        self.read_type_of_note(int(self.sender().text().split('\n')[1]))

    # Удаляет ноту с канала
    def delete_note(self):
        ch_n = self.sender().ch_number
        size = self.sender().size().width()
        note_n = self.chanel_buttons[ch_n - 1].index(self.sender()) + 1
        MyComposition[ch_n - 1].remove_note(note_n - 1)
        self.chanel_layouts[ch_n - 1].removeWidget(self.sender())
        self.chanel_buttons[ch_n - 1].remove(self.chanel_buttons[ch_n - 1][note_n - 1])
        self.notes_area_resize(size * -1)

    # Обработчик смены длительности
    def duration_button_clicked(self):
        if self.sender().text() != '-->':
            temp = {"1": 4, "2": 2, "2.": 3, "4": 1, "4.": 1.5, "8": 0.5, "8.": 0.75, "16": 0.25, "16.": 0.375,
                    '32': 0.125}
            self.current_duration = temp.get(self.sender().text())
        else:
            self.current_duration = float(self.duration_input.value())
        self.duration_label.setText(f'Длительность: {self.current_duration} beat(s)')

    # Изменяет канал, с которым сейчас работаем
    def current_chanel_change(self):
        self.current_chanel = int(self.chanel_input.value())

    # Изменяет темп композиции
    def current_tempo_change(self):
        MyComposition.set_tempo(self.tempo_input.value())
        self.current_tempo = int(self.tempo_input.value())

    # Обновляет окошко с названием интервала
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

    # Вызывается при нажатии клавиши на фо-но, считывает параметры того, что нужно добавить на канал
    def read_type_of_note(self, pitch):
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

    # Добавляет паузу на канал
    def add_rest(self):
        MyComposition[self.current_chanel - 1].add_note(duration=self.current_duration, type='rest')
        self.make_button(note_name='Rest', size=int(self.current_duration * 100),
                         chanel_number=self.current_chanel)

    # Вставляет набранный вручную аккорд на канал
    def manual_chord_paste(self):
        if self.manual_chord_line.text() != 'Notes will appear here...' \
                and len(self.manual_chord_line.text().split()) > 1:
            pitches = tuple(map(lambda x: name_to_pitch(x), self.manual_chord_line.text().split()))
            arpeggiato = self.chord_arpeggiato_button.isChecked()
            MyComposition[self.current_chanel - 1].add_chord(pitches, duration=self.current_duration,
                                                             arpeggiato=arpeggiato)
            self.make_button(note_name=f'Chord\n{self.manual_chord_line.text()}\n{"arpeggiato" if arpeggiato else ""}',
                             size=int(self.current_duration * 100), chanel_number=self.current_chanel)

    # Очищает окно ручного набора аккорда
    def manual_chord_clear(self):
        self.manual_chord_line.setText('Notes will appear here...')

    # Обработчик клавиатуры
    def keyPressEvent(self, event):
        key = event.key()
        a = self.keyboard_octave_input.value()
        if key == Qt.Key_Z:
            eval(f'self.C{a}.click()')
        elif key == Qt.Key_S:
            eval(f'self.Cis{a}.click()')
        elif key == Qt.Key_X:
            eval(f'self.D{a}.click()')
        elif key == Qt.Key_D:
            eval(f'self.Dis{a}.click()')
        elif key == Qt.Key_C:
            eval(f'self.E{a}.click()')
        elif key == Qt.Key_V:
            eval(f'self.F{a}.click()')
        elif key == Qt.Key_G:
            eval(f'self.Fis{a}.click()')
        elif key == Qt.Key_B:
            eval(f'self.G{a}.click()')
        elif key == Qt.Key_H:
            eval(f'self.Gis{a}.click()')
        elif key == Qt.Key_N:
            eval(f'self.A{a}.click()')
        elif key == Qt.Key_J:
            eval(f'self.B{a}.click()')
        elif key == Qt.Key_M:
            eval(f'self.H{a}.click()')
        elif key == Qt.Key_Q or key == Qt.Key_Comma:
            eval(f'self.C{a + 1}.click()')
        elif key == Qt.Key_2 or key == Qt.Key_L:
            eval(f'self.Cis{a + 1}.click()')
        elif key == Qt.Key_W or key == Qt.Key_Period:
            eval(f'self.D{a + 1}.click()')
        elif key == Qt.Key_3 or key == Qt.Key_Semicolon:
            eval(f'self.Dis{a + 1}.click()')
        elif key == Qt.Key_E or key == Qt.Key_Slash:
            eval(f'self.E{a + 1}.click()')
        elif key == Qt.Key_R:
            eval(f'self.F{a + 1}.click()')
        elif key == Qt.Key_5:
            eval(f'self.Fis{a + 1}.click()')
        elif key == Qt.Key_T:
            eval(f'self.G{a + 1}.click()')
        elif key == Qt.Key_6:
            eval(f'self.Gis{a + 1}.click()')
        elif key == Qt.Key_Y:
            eval(f'self.A{a + 1}.click()')
        elif key == Qt.Key_7:
            eval(f'self.B{a + 1}.click()')
        elif key == Qt.Key_U:
            eval(f'self.H{a + 1}.click()')
        elif key == Qt.Key_I:
            eval(f'self.C{a + 2}.click()')
        elif key == Qt.Key_Space:
            eval(f'self.rest_button.click()')
        elif key == Qt.Key_Backspace:
            if self.chanel_buttons[self.current_chanel - 1]:
                self.chanel_layouts[self.current_chanel - 1].itemAt(
                    len(self.chanel_buttons[self.current_chanel - 1]) - 1).widget().click()

    # Изменяет инструмент канала
    def instrument_change(self):
        MyComposition[int(self.sender().objectName()[6]) - 1].set_instrument(int(self.sender().value()) - 1)

    # Изменяет громкость канала
    def volume_change(self):
        MyComposition[int(self.sender().objectName()[6]) - 1].set_volume(int(self.sender().value()))

    # Проигрывает набранную композицию
    def play(self):
        self.create_midi(temp=True)
        media = QUrl.fromLocalFile('temp.mid')
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)
        self.player.play()

    # Останавливает проигрывание
    def stop(self):
        self.player.stop()

    # Задаёт путь для экспорта midi файла
    def set_output_path(self):
        self.output_midi_name = QFileDialog.getSaveFileName(
            self, 'Выбрать файл', '',
            'MIDI sequence (*.midi);;Все файлы (*)')[0]

    # Создаёт MIDI-файл
    def create_midi(self, temp=False):
        if not temp:
            print(MyComposition)
            self.set_output_path()
            MyComposition.export_as_midi(self.output_midi_name)
        else:
            MyComposition.export_as_midi('temp.mid')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
