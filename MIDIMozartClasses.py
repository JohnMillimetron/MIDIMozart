from midiutil import MIDIFile

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

    def export_as_midi(self, file_name):
        midi_file = MIDIFile(1)
        for chanel in self.channels:
            midi_file.addTempo(self.channels.index(chanel), 0, chanel.tempo)
            midi_file.addProgramChange(
                tracknum=0, channel=self.channels.index(chanel), program=chanel.instrument, time=0)
            for note in chanel.notes:
                midi_file.addNote(0, self.channels.index(chanel), note.pitch, note.time, note.length, note.volume)
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

    def add_note(self, pitch, time='auto', length=1, volume=100, duration=1):  # Добавляет ноту к дорожке
        if time == 'auto':
            time = self.calculate_length()
        self.notes.append(Note(pitch, time, length, volume, duration))

    def remove_note(self, note, autoshift=True):  # Удаляет ноту с дорожки
        rm_t, rm_d = self.notes[note].time, self.notes[note].duration,
        self.notes.remove(self.notes[note])
        if autoshift:
            self.autoshift_left(rm_d, note)

    def autoshift_left(self, removed_note_duration,
                       shift_begin_number):  # Заполняет пустоту, сдвигая ноты друг к другу
        self.notes = self.notes[:shift_begin_number] + list(map(
            lambda note: Note(note.pitch, note.time - removed_note_duration, note.length, note.volume),
            self.notes[shift_begin_number:]))


class Note:
    """
    Class Note
    Класс представляет собой одиночную ноту произведения,
    которая должна быть прикреплена к определённой дорожке Chanel.
    """

    def __init__(self, pitch, time=1, length=1, volume=100, duration=1):
        # duration - программная длина, length - слышимая длина.
        self.pitch, self.time, self.length, self.volume, self.duration = pitch, time, duration, volume, length
        for diapason, octave in NOTE_NUMBERS_AND_OCTAVES.items():
            if self.pitch in diapason:
                self.octave = NOTE_NUMBERS_AND_OCTAVES.get(diapason)
                break
        self.name = NOTES_AND_NAMES.get(self.pitch - 12 * int(self.octave)) + self.octave

    def __str__(self):
        return self.name


if __name__ == '__main__':
    MyComposition = Composition()
    MyComposition.add_chanel()
    print(MyComposition)
    print()
    MyComposition[0].set_tempo(120)
    MyComposition[0].set_instrument(127)
    MyComposition[0].add_note(67, length=0.5)
    MyComposition[0].add_note(72, length=1)
    MyComposition[0].add_note(67, length=0.75)
    MyComposition[0].add_note(69, length=0.25)
    MyComposition[0].add_note(71, length=1)
    MyComposition[0].add_note(64, length=0.5)
    MyComposition[0].add_note(64, length=0.5)
    MyComposition[0].add_note(69, length=1)
    MyComposition[0].add_note(67, length=0.75)
    MyComposition[0].add_note(65, length=0.25)
    MyComposition[0].add_note(67, length=1)
    MyComposition[0].add_note(60, length=0.5)
    MyComposition[0].add_note(60, length=0.5)
    MyComposition[0].add_note(62, length=1)
    MyComposition[0].add_note(62, length=0.75)
    MyComposition[0].add_note(64, length=0.25)
    MyComposition[0].add_note(65, length=1)
    MyComposition[0].add_note(65, length=0.75)
    MyComposition[0].add_note(67, length=0.25)
    MyComposition[0].add_note(69, length=1)
    MyComposition[0].add_note(71, length=0.75)
    MyComposition[0].add_note(72, length=0.25)
    MyComposition[0].add_note(74, length=1.5)
    MyComposition[0].add_note(67, length=0.5)
    MyComposition[0].add_note(77, length=1)
    MyComposition[0].add_note(76, length=0.75)
    MyComposition[0].add_note(74, length=0.25)
    MyComposition[0].add_note(76, length=1)
    MyComposition[0].add_note(71, length=0.5)
    MyComposition[0].add_note(67, length=0.5)
    MyComposition[0].add_note(72, length=1)
    MyComposition[0].add_note(71, length=0.75)
    MyComposition[0].add_note(69, length=0.25)
    MyComposition[0].add_note(71, length=1)
    MyComposition[0].add_note(64, length=0.5)
    MyComposition[0].add_note(64, length=0.5)
    MyComposition[0].add_note(69, length=1)
    MyComposition[0].add_note(67, length=0.75)
    MyComposition[0].add_note(65, length=0.25)
    MyComposition[0].add_note(67, length=1)
    MyComposition[0].add_note(60, length=0.75)
    MyComposition[0].add_note(60, length=0.25)
    MyComposition[0].add_note(72, length=1)
    MyComposition[0].add_note(71, length=0.75)
    MyComposition[0].add_note(69, length=0.25)
    MyComposition[0].add_note(67, length=2)
    print(MyComposition)
    print()
    MyComposition.export_as_midi('test3.mid')
