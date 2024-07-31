import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont
import json
from collections import Counter
from datetime import datetime


class SpotifyAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.start()


    #Initializes UI ising PyQt5
    def start(self):
        self.setWindowTitle('Full Spotify Stats')
        self.setGeometry(400, 200, 1200, 800)

        default_font = QFont('Helvetica', 12)
        title_font = QFont('Helvetica', 16)

        layout = QVBoxLayout()

        self.label = QLabel('Select JSON files with listening history (multiple files allowed):')
        self.label.setFont(default_font)
        layout.addWidget(self.label)

        self.load_button = QPushButton('Load JSON Files')
        self.load_button.setFont(title_font)
        self.load_button.clicked.connect(self.load_files)
        layout.addWidget(self.load_button)

        self.result_text = QTextEdit()
        self.result_text.setFont(default_font)
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def load_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Open JSON Files", "", "JSON Files (*.json);;All Files (*)",
                                                options=options)
        if not files:
            return

        try:
            combined_data = []
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    combined_data.extend(data)

            self.parse(combined_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def parse(self, data):
        artists = []
        songs = []
        albums = []
        year_artist_counter = {}

        for entry in data:
            artist = entry.get("master_metadata_album_artist_name")
            song = entry.get("master_metadata_track_name")
            album = entry.get("master_metadata_album_album_name")
            timestamp = entry.get("ts")

            if artist:
                if "feat." not in artist and "ft." not in artist:
                    artists.append(artist)
                    year = self.year(timestamp)
                    if year:
                        if year not in year_artist_counter:
                            year_artist_counter[year] = Counter()
                        year_artist_counter[year][artist] += 1

            if song:
                songs.append(song)
            if album:
                albums.append(album)

        artist_counter = Counter(artists)
        song_counter = Counter(songs)
        album_counter = Counter(albums)

        top_artists = artist_counter.most_common(25)
        top_songs = song_counter.most_common(25)
        top_albums = album_counter.most_common(25)

        self.result_text.clear()

        self.result_text.append("\nTop 25 Artists:\n")
        for i, (artist, count) in enumerate(top_artists, 1):
            self.result_text.append(f"{i}. {artist} ({count} plays)")

        self.result_text.append("\nTop 25 Songs:\n")
        for i, (song, count) in enumerate(top_songs, 1):
            self.result_text.append(f"{i}. {song} ({count} plays)")

        self.result_text.append("\nTop 25 Albums:\n")
        for i, (album, count) in enumerate(top_albums, 1):
            self.result_text.append(f"{i}. {album} ({count} plays)")

        self.result_text.append("\nTop 5 Artists Per Year:\n")
        for year, counter in sorted(year_artist_counter.items()):
            self.result_text.append(f"\nYear {year}:\n")
            top_artists_per_year = counter.most_common(5)
            for i, (artist, count) in enumerate(top_artists_per_year, 1):
                self.result_text.append(f"{i}. {artist} ({count} plays)")


    #determines year for seperation
    def year(self, timestamp):
        try:
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return dt.year
        except ValueError:
            return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotifyAnalyzer()
    ex.show()
    sys.exit(app.exec_())