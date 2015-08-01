from MidiFile3 import MIDIFile
from PianoUtilities import *
from random import *
from copy import *

class Song:

    def __init__(self, tempo, key, num_measures, instruments, singers, num_tracks):
        self.num_tracks = num_tracks
        self.num_measures = num_measures
        self.MyMIDI = MIDIFile(self.num_tracks + 1)
        self.instruments = instruments
        self.singers = singers
        self.key = key
        self.time = 0
        self.sections = []

        self.MyMIDI.addTempo(track=0, tempo=tempo, time=0)
        self.triads = self.create_triad_sequence(num_measures, key)
        self.notes_for_track = [[]]

        for x in range(self.num_tracks//3):
            for singer_index in range(len(self.singers[x])):
                if self.num_tracks//3*singer_index + x >= 9:
                    self.singers[x][singer_index].track = self.num_tracks//3*singer_index + x + 1
                    self.singers[x][singer_index].channel = self.num_tracks//3*singer_index + x + 1
                else:
                    self.singers[x][singer_index].track = self.num_tracks//3*singer_index + x
                    self.singers[x][singer_index].channel = self.num_tracks//3*singer_index + x

        for singer in [row[0] for row in self.singers]:
            self.add_track(singer)
        for singer in [row[1] for row in self.singers]:
            self.add_track(singer)
        for singer in [row[2] for row in self.singers]:
            self.add_track(singer)

        self.build_song()

    def add_track(self, singer):
        self.MyMIDI.addTrackName(singer.track, 0, singer.name + ', Volume:' + str(singer.volume))
        self.MyMIDI.addProgramChange(track=singer.track, channel=singer.channel, time=0, program=singer.instrument)
        self.notes_for_track.append([])

    def add_single_note(self, singer, pitch, duration):
        if pitch >= 0:
            self.MyMIDI.addNote(track=singer.track, channel=singer.track, pitch=pitch, time=self.time, duration=duration, volume=singer.volume)

    def create_triad_sequence(self, num_triads, key):
        triads = []
        for x in range(num_triads-1):
            start_note = key.notes_in_key[randint(0,7)]
            triads.append(triad(key, start_note))
        triads.append(triad(key, key.notes_in_key[0]))
        return triads

    def return_next_pitch(self, input_singer, input_triad):
        possible_notes = []
        for note in input_triad:
            note_choices = input_singer.octave_notes_in_range(note)
            for note in note_choices:
                possible_notes.append(note)
        if len(self.notes_for_track[input_singer.track]) > 0:
            previous = self.notes_for_track[input_singer.track][len(self.notes_for_track[input_singer.track])-1]
            jumps = []
            steps = []
            for note in possible_notes:
                difference = abs(note-previous)
                if difference < 5:
                    steps.append(note)
                elif difference <= 12:
                    jumps.append(note)
            jump_or_step = randint(0,9)
            if len(jumps) == 0:
                pick_step = randint(0,len(steps)-1)
                return steps[pick_step]
            if len(steps) == 0:
                pick_jump = randint(0,len(jumps)-1)
                return jumps[pick_jump]
            if jump_or_step <= 1:  #there is a 20% of choosing a jump
                pick_jump = randint(0,len(jumps)-1)
                return jumps[pick_jump]
            else:
                pick_step = randint(0,len(steps)-1)
                return steps[pick_step]
        else:
            pick_any = randint(0,len(possible_notes)-1)
            return possible_notes[pick_any]

    def build_song(self):
        section_length = 8
        # chorus:0,verse:1,bridge:2
        self.build_verse(section_length)
        self.sections.append(1)
        for x in range(self.num_measures//section_length-2):
            if x != self.num_measures//section_length-2:
                choices = [0,1,2]
                choices.pop(self.sections[len(self.sections)-1])
                section_type = choices[randint(0,1)]
                self.sections.append(section_type)

            else: # ensures that the second to last measure isn't a chorus
                choices = [0,1,2]
                if self.sections[len(self.sections)-1] != 0:
                    choices.pop(self.sections[len(self.sections)-1])
                choices.pop(0)

            if section_type == 0:
                self.build_chorus(section_length)
            elif section_type == 1:
                self.build_verse(section_length)
            elif section_type == 2:
                self.build_bridge(section_length)

        self.build_chorus(self.num_measures-(self.time//4)-1)
        for singer in [row[0] for row in self.singers]:
            self.build_measure(singer, triad(self.key, self.key.notes_in_key[0]), self.time, [[4],[4],[4],[4]])

    def build_chorus(self, length):
        duration_options = [[1,2],[1],[.5,1],[.25,.5]]
        for x in range(length-1):
            for singer in [row[0] for row in self.singers]:
                self.build_measure(singer, self.triads[0], self.time, duration_options)
            self.triads.pop(0)
            self.time += 4
        for singer in [row[0] for row in self.singers]:
            self.build_measure(singer, triad(self.key, self.key.notes_in_key[0]), self.time, duration_options)
        self.triads.pop()
        self.time+=4

    def build_verse(self, length):
        duration_options = [[1,2,4],[1,2],[.5,1],[.25,.5,1]]
        for x in range(length-1):
            for singer in [row[1] for row in self.singers]:
                self.build_measure(singer, self.triads[0], self.time, duration_options)
            self.triads.pop(0)
            self.time += 4
        for singer in [row[1] for row in self.singers]:
            self.build_measure(singer, triad(self.key, self.key.notes_in_key[0]), self.time, duration_options)
        self.triads.pop()
        self.time+=4

    def build_bridge(self, length):
        duration_options = [[2],[1],[.25,.5,1],[.25,.5,1]]
        for x in range(length-1):
            for singer in [row[2] for row in self.singers]:
                self.build_measure(singer, self.triads[0], self.time, duration_options)
            self.triads.pop(0)
            self.time += 4
        for singer in [row[2] for row in self.singers]:
            self.build_measure(singer, triad(self.key, self.key.notes_in_key[0]), self.time, duration_options)
        self.triads.pop()
        self.time+=4

    def build_measure(self, singer, input_triad, time, note_options):
        orig_time = deepcopy(time)

        if singer.name == 'Bass':
            duration_options = note_options[0]

        elif singer.name == 'Tenor':
            duration_options = note_options[1]

        elif singer.name == 'Alto':
            duration_options = note_options[2]

        elif singer.name == 'Soprano':
            duration_options = note_options[3]


        while time < orig_time + 4:
            temp_options = [duration for duration in duration_options if duration <= (orig_time+4)-time]
            duration = temp_options[randint(0,len(temp_options)-1)]
            if duration == .25:
                for x in range(4):
                    self.build_beat(input_triad, time, singer, duration)
                    time += .25
            else:
                self.build_beat(input_triad, time, singer, duration)
                time += duration

    def build_beat(self, input_triad, time, singer, duration=1):
        pitch = self.return_next_pitch(singer, input_triad)
        self.notes_for_track[singer.track].append(pitch)
        self.MyMIDI.addNote(singer.track, singer.track, pitch, time, duration, singer.volume)

    def build_x_sixteenths(self, num_sixteenths, input_triad, time, singer):
        for x in range(num_sixteenths):
            pitch = self.return_next_pitch(singer, input_triad)
            self.MyMIDI.addNote(singer.track, singer.track, pitch, time, .25, singer.volume)
            self.notes_for_track[singer.track].append(pitch)
            time += .25

    def set_instrument(self, track, channel, input_instrument):
        self.MyMIDI.addProgramChange(track, channel, 0, input_instrument)

    def write_to_disk(self, output_name):
        binfile = open(r'Songs/{}.mid'.format(output_name), 'wb')
        self.MyMIDI.writeFile(binfile)
        binfile.close()
        print("Written to file with name: '{}'!".format(output_name + '.mid'))
