from midiutil import MIDIFile
from PyQt5 import QtWidgets

NOTES_AND_NAMES = {
    12: 'C',
    13: 'C#',
    14: 'D',
    15: 'D#',
    16: 'E',
    17: 'F',
    18: 'F#',
    19: 'G',
    20: 'G#',
    21: 'A',
    22: 'B',
    23: 'H'
}

NOTES_AND_NAMES_is = {
    12: 'C',
    13: 'Cis',
    14: 'D',
    15: 'Dis',
    16: 'E',
    17: 'F',
    18: 'Fis',
    19: 'G',
    20: 'Gis',
    21: 'A',
    22: 'B',
    23: 'H'
}

NOTE_NUMBERS_AND_OCTAVES = {
    range(21, 24): '0',
    range(24, 36): '1',
    range(36, 48): '2',
    range(48, 60): '3',
    range(60, 72): '4',
    range(72, 84): '5',
    range(84, 96): '6',
    range(96, 108): '7',
    range(108, 120): '8'
}


class Composition:
    """
    Class Composition
    Класс представляет собой музыкальное произведение, состоящее из одной или нескольких дорожек Chanel.
    Есть функция для конвертации в MIDI файл с помощью библиотеки midiutil.
    """

    def __init__(self):
        self.channels = [Chanel() for _ in range(16)]

    def __getitem__(self, channel):
        return self.channels[channel]

    def __str__(self):
        return f"\tClass Composition, {len(self.channels)} channel(s).\n" + \
               '\n'.join([str(self.channels.index(ch)) + '. ' + str(ch) for ch in self.channels])

    def add_chanel(self, tempo=120, instrument=0):  # Добавить пустую дорожку к произведению.
        if len(self.channels) >= 16:
            print('Невозможно добавить канал. Количесвто каналов не может быть больше 16.')
        else:
            self.channels.append(Chanel(tempo, instrument))

    def set_tempo(self, tempo):
        for chanel in self.channels:
            chanel.tempo = tempo

    def export_as_midi(self, file_name):
        midi_file = MIDIFile(1)
        # Перебираем каналы
        for chanel in self.channels:
            midi_file.addTempo(self.channels.index(chanel), 0, chanel.tempo)
            midi_file.addProgramChange(
                tracknum=0, channel=self.channels.index(chanel), program=chanel.instrument, time=0)

            # Перебираем ноты
            for note in chanel.notes:
                if type(note) == Note:
                    midi_file.addNote(0, self.channels.index(chanel), note.pitch, note.time, note.length, note.volume)
                elif type(note) == TremoloNote:
                    for i in note:
                        midi_file.addNote(0, self.channels.index(chanel), i.pitch, i.time, i.length,
                                          i.volume)
                elif type(note) == TrillNote:
                    for i in note:
                        midi_file.addNote(0, self.channels.index(chanel), i.pitch, i.time, i.length,
                                          i.volume)
                elif type(note) == Glissando:
                    for i in note:
                        midi_file.addNote(0, self.channels.index(chanel), i.pitch, i.time, i.length,
                                          i.volume)
                elif type(note) == Chord:
                    for i in note:
                        midi_file.addNote(0, self.channels.index(chanel), i.pitch, i.time, i.length,
                                          i.volume)

        try:
            with open(file_name, "wb") as output_file:
                midi_file.writeFile(output_file)
        except PermissionError:
            print('Ошибка записи\nФайл используется другим приложением. Заакройте и повторите попытку.')


class Chanel:
    """
    Class Chanel
    В классе содержится информация об одной дорожке произведения.
    Главный элемент класса - список нот notes.
    Несколько классов Chanel могут быть объединены в классе Composition
    """

    def __init__(self, tempo=120, instrument=0):
        self.tempo = tempo
        self.instrument = instrument
        self.last_note_time = 0
        self.length = 0
        self.notes = []

    def __str__(self):
        return f"Instrument: {self.instrument}, tempo: {self.tempo}, " \
               f"length: {self.calculate_length()} (in beats), {len(self.notes)} notes.\n" \
               f"{' '.join(map(lambda x: str(x), self.notes)) if self.notes else 'Empty'}"

    def __getitem__(self, item):
        return self.notes[item]

    def calculate_last_note_time(self, return_int=True):  # Вычисляет время последней ноты дорожки
        self.last_note_time = max(self.notes, key=lambda note: note.time).time if self.notes else 0
        if return_int:
            return self.last_note_time
        return max(self.notes, key=lambda note: note.time) if self.notes else None

    def calculate_length(self):  # Вычисляет длительность дорожки
        self.length = self.calculate_last_note_time(return_int=False).time + \
                      self.calculate_last_note_time(return_int=False).length if \
            self.calculate_last_note_time(return_int=False) else 0
        return self.length

    def set_tempo(self, tempo):  # Устанавливает темп дорожки (в bpm)
        if type(tempo) != int:
            raise ValueError
        self.tempo = tempo

    def set_instrument(self, instrument):  # Устанавливает инструмент дорожки
        if type(instrument) != int or instrument not in range(128):
            raise ValueError
        self.instrument = instrument

    def add_note(self, *pitch, type='default', time='auto', length=1, volume=100,
                 duration=1):  # Добавляет ноту к дорожке
        if time == 'auto':
            time = self.calculate_length()
        if type == 'default':
            self.notes.append(Note(*pitch, time, length, volume, duration))
        elif type == 'tremolo':
            self.notes.append(TremoloNote(*pitch, time, length, volume, duration))
        elif type == 'trill':
            self.notes.append(TrillNote(*pitch, time, length, volume, duration))
        elif type == 'gliss':
            self.notes.append(Glissando(*pitch, time, length, volume, duration))

    def add_chord(self, *args, arpeggiato=False, time='auto', length=1, volume=100, duration=1):
        # add_chord(60, 'maj', length=1)    | args == [60, 'maj']
        # add_chord((60, 64, 67), length=1) | args == [(60, 64, 67)]
        if time == 'auto':
            time = self.calculate_length()
        self.notes.append(
            Chord(*args, time=time, length=duration, duration=duration, volume=volume, arpeggiato=arpeggiato))

    def remove_note(self, note, autoshift=True):  # Удаляет ноту с дорожки
        rm_t, rm_d = self.notes[note].time, self.notes[note].length,
        self.notes.remove(self.notes[note])
        if autoshift:
            self.autoshift(rm_d, note)

    def autoshift(self, removed_note_duration,
                  shift_begin_number):  # Заполняет пустоту, сдвигая ноты друг к другу
        after_deleted = self.notes[shift_begin_number:]
        before_deleted = self.notes[:shift_begin_number]
        for note in after_deleted:
            note.time -= removed_note_duration
        self.notes = before_deleted + after_deleted
        # self.notes = self.notes[:shift_begin_number] + list(map(
        #     lambda note: Note(note.pitch, note.time - removed_note_duration, note.length, note.volume),
        #     self.notes[shift_begin_number:]))


class Note:
    """
    Class Note
    Класс представляет собой одиночную ноту произведения,
    которая должна быть прикреплена к определённой дорожке Chanel.
    """

    def __init__(self, pitch, time=1, length=1, volume=100, duration=1):
        self.pitch, self.time, self.length, self.volume, self.duration = pitch, time, duration, volume, length
        for diapason, octave in NOTE_NUMBERS_AND_OCTAVES.items():
            if self.pitch in diapason:
                self.octave = NOTE_NUMBERS_AND_OCTAVES.get(diapason)
                break
        self.name = NOTES_AND_NAMES.get(self.pitch - 12 * int(self.octave)) + self.octave

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self.name) + '-' + str(self.length) + 'b;'


class TremoloNote(Note):
    def __init__(self, pitch, time=1, length=1, volume=100, duration=1):
        super().__init__(pitch, time, length, volume, duration)
        self.count_of_notes = int(self.length // 0.125)
        self.notes = []
        self.name = f'trem.\n{self.name}'
        for i in range(self.count_of_notes):
            self.notes.append(Note(self.pitch, self.time + i * 0.125, 0.125, self.volume, 0.125))

    def __getitem__(self, item):
        return self.notes[item]

    def __repr__(self):
        return super().__repr__() + 'trem'


class TrillNote(Note):
    def __init__(self, pitch, time=1, length=1, volume=100, duration=1):
        super().__init__(pitch, time, length, volume, duration)
        self.count_of_notes = int(self.length // 0.125)
        self.notes = []
        self.name = f'trill\n{self.name}'
        for i in range(self.count_of_notes):
            self.notes.append(
                Note(self.pitch, self.time + i * 0.125, 0.125, self.volume, 0.125) if i % 2 == 0 else
                Note(self.pitch + 2, self.time + i * 0.125, 0.125, self.volume, 0.125))

    def __getitem__(self, item):
        return self.notes[item]

    def __repr__(self):
        return super().__repr__() + 'trill'


class Glissando(Note):
    def __init__(self, pitch, pitch2, time=1, length=1, volume=100, duration=1):
        super().__init__(pitch, time, length, volume, duration)
        # self.count_of_notes = int(self.length // 0.125)
        self.difference = abs(pitch2 - pitch) + 1
        self.notes = []
        if pitch2 > pitch:
            for i in range(self.difference):
                self.notes.append(Note(self.pitch + i, self.time + (self.length / self.difference) * i,
                                       self.length / self.difference, self.volume, self.length / self.difference))
        else:
            for i in range(self.difference):
                self.notes.append(Note(self.pitch - i, self.time + (self.length / self.difference) * i,
                                       self.length / self.difference, self.volume, self.length / self.difference))
        self.name = f'gliss\n{self.notes[0].name}-{self.notes[-1].name}'

    def __getitem__(self, item):
        return self.notes[item]

    def __repr__(self):
        return f'{self.notes[0].__repr__().split("-")[0]}/' \
               f'{self.notes[-1].__repr__().split("-")[0]}-{self.length}b;gliss'


class Chord(Note):
    def __init__(self, *args, time=1, length=1, volume=100, duration=1, arpeggiato=False):
        self.pitches = []
        if len(args) == 1:
            self.pitches = args[0]
            super().__init__(self.pitches[0], time, length, volume, duration)
        else:
            self.root_pitch = args[0]
            self.structure = args[1]
            super().__init__(self.root_pitch, time, length, volume, duration)
            self.notes = []

            if self.structure == 'major':
                self.pitches.extend((self.root_pitch, self.root_pitch + 4, self.root_pitch + 7))
            elif self.structure == 'minor':
                self.pitches.extend((self.root_pitch, self.root_pitch + 3, self.root_pitch + 7))
            elif self.structure == 'aug':
                self.pitches.extend((self.root_pitch, self.root_pitch + 4, self.root_pitch + 8))
            elif self.structure == 'dim':
                self.pitches.extend((self.root_pitch, self.root_pitch + 3, self.root_pitch + 6))
            elif self.structure == '7':  # Малый мажорный
                self.pitches.extend((self.root_pitch, self.root_pitch + 4, self.root_pitch + 7, self.root_pitch + 10))
            elif self.structure == 'sus2':
                self.pitches.extend((self.root_pitch, self.root_pitch + 2, self.root_pitch + 7))
            elif self.structure == 'sus4':
                self.pitches.extend((self.root_pitch, self.root_pitch + 5, self.root_pitch + 7))

        self.notes = []
        # self.name = f'chord\n{" ".join(map(lambda x: x.name, self.notes))}'
        if not arpeggiato or self.length < len(self.pitches) * 0.125:
            for i in self.pitches:
                self.notes.append(Note(i, self.time, self.length, self.volume, self.length))
        else:
            for j, i in enumerate(self.pitches):
                self.notes.append(Note(i, self.time + (0.125 * j), self.length - (0.125 * j),
                                       self.volume, self.length - (0.125 * j)))

    def __getitem__(self, item):
        return self.notes[item]

    def __repr__(self):
        return f'{self.notes}-{self.length}b;chord'


class NoteButton(QtWidgets.QPushButton):
    def __init__(self, note_number, ch_number, note_name):
        super().__init__()
        self.note_number, self.ch_number, self.note_name \
            = note_number, ch_number, note_name


def name_to_pitch(name):
    names_and_notes = {name: pitch for pitch, name in NOTES_AND_NAMES.items()}
    pitch = names_and_notes.get(name[:-1]) + 12 * int(name[-1])
    return pitch


def pitch_to_name(pitch):
    for diapason, octave in NOTE_NUMBERS_AND_OCTAVES.items():
        if pitch in diapason:
            octave = NOTE_NUMBERS_AND_OCTAVES.get(diapason)
            break
    name = NOTES_AND_NAMES.get(pitch - 12 * int(octave)) + octave
    return name


if __name__ == '__main__':
    MyComposition = Composition()
    print(MyComposition[0])
    print()
    MyComposition[0].set_tempo(480)
    MyComposition[0].set_instrument(26)

    # MyComposition[0].add_note(67, length=0.5)
    # MyComposition[0].add_note(72, length=1)
    # MyComposition[0].add_note(67, length=0.75)
    # MyComposition[0].add_note(69, length=0.25)
    # MyComposition[0].add_note(71, length=1)
    # MyComposition[0].add_note(64, length=0.5)
    # MyComposition[0].add_note(64, length=0.5)
    # MyComposition[0].add_note(69, length=1)
    # MyComposition[0].add_note(67, length=0.75)
    # MyComposition[0].add_note(65, length=0.25)
    # MyComposition[0].add_note(67, length=1)
    # MyComposition[0].add_note(60, length=0.5)
    # MyComposition[0].add_note(60, length=0.5)
    # MyComposition[0].add_note(62, length=1)
    # MyComposition[0].add_note(62, length=0.75)
    # MyComposition[0].add_note(64, length=0.25)
    # MyComposition[0].add_note(65, length=1)
    # MyComposition[0].add_note(65, length=0.75)
    # MyComposition[0].add_note(67, length=0.25)
    # MyComposition[0].add_note(69, length=1)
    # MyComposition[0].add_note(71, length=0.75)
    # MyComposition[0].add_note(72, length=0.25)
    # MyComposition[0].add_note(74, length=1.5)
    # MyComposition[0].add_note(67, length=0.5)
    # MyComposition[0].add_note(77, length=1)
    # MyComposition[0].add_note(76, length=0.75)
    # MyComposition[0].add_note(74, length=0.25)
    # MyComposition[0].add_note(76, length=1)
    # MyComposition[0].add_note(71, length=0.5)
    # MyComposition[0].add_note(67, length=0.5)
    # MyComposition[0].add_note(72, length=1)
    # MyComposition[0].add_note(71, length=0.75)
    # MyComposition[0].add_note(69, length=0.25)
    # MyComposition[0].add_note(71, length=1)
    # MyComposition[0].add_note(64, length=0.5)
    # MyComposition[0].add_note(64, length=0.5)
    # MyComposition[0].add_note(69, length=1)
    # MyComposition[0].add_note(67, length=0.75)
    # MyComposition[0].add_note(65, length=0.25)
    # MyComposition[0].add_note(67, length=1)
    # MyComposition[0].add_note(60, length=0.75)
    # MyComposition[0].add_note(60, length=0.25)
    # MyComposition[0].add_note(72, length=1)
    # MyComposition[0].add_note(71, length=0.75)
    # MyComposition[0].add_note(69, length=0.25)
    # MyComposition[0].add_note(67, length=2)

    # MyComposition[0].add_note(60, duration=1, type='tremolo')
    # MyComposition[0].add_note(62, duration=1, type='tremolo')
    # MyComposition[0].add_note(64, duration=1, type='tremolo')
    # MyComposition[0].add_note(60, duration=1, type='tremolo')
    # MyComposition[0].add_note(62, duration=2, type='trill')
    # MyComposition[0].add_note(60, duration=4, type='default')

    # MyComposition[0].add_note(60, 72, duration=2, type='gliss')
    # MyComposition[0].add_note(72, 60, duration=2, type='gliss')

    MyComposition[0].add_chord((60, 64, 67), duration=1, arpeggiato=True)
    MyComposition[0].add_chord((65, 69, 72), duration=1, arpeggiato=True)
    MyComposition[0].add_chord((67, 71, 74), duration=1, arpeggiato=True)
    MyComposition[0].add_chord((60, 64, 67), duration=4, arpeggiato=True)

    MyComposition[0].add_chord((60, 64, 67), duration=1)
    MyComposition[0].add_chord((65, 69, 72), duration=1)
    MyComposition[0].add_chord((67, 71, 74), duration=1)
    MyComposition[0].add_chord((60, 64, 67), duration=4)

    MyComposition[0].add_chord(60, 'major', duration=1)
    MyComposition[0].add_chord(60, 'sus2', duration=1)
    MyComposition[0].add_chord(60, 'sus4', duration=1)
    MyComposition[0].add_chord(60, 'sus2', duration=1)
    MyComposition[0].add_chord(60, 'major', duration=4, arpeggiato=True)

    # MyComposition[0].add_chord(60, 'dim', duration=0.25)
    # MyComposition[0].add_chord(60, 'aug', duration=0.25)

    print(MyComposition[0])
    print(MyComposition[0].notes)
    MyComposition.export_as_midi('test3.mid')
