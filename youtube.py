import yt_dlp
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QFileDialog, QRadioButton, QButtonGroup,
                           QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# FFmpeg yolunu kontrol et
def check_ffmpeg():
    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
    if not os.path.exists(ffmpeg_path):
        os.makedirs(ffmpeg_path)
    return ffmpeg_path

class IndirmeThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, format_type, save_path, is_playlist):
        super().__init__()
        self.url = url
        self.format_type = format_type
        self.save_path = os.path.abspath(save_path)
        self.is_playlist = is_playlist
        self.ffmpeg_path = check_ffmpeg()

    def playlist_bilgilerini_al(self, url):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                return [(entry['title'], entry['url']) for entry in result['entries']]
            return []

    def run(self):
        try:
            if self.is_playlist:
                videolar = self.playlist_bilgilerini_al(self.url)
                playlist_file = os.path.join(self.save_path, 'playlist_videolari.txt')
                with open(playlist_file, 'w', encoding='utf-8') as f:
                    for i, (title, _) in enumerate(videolar, 1):
                        f.write(f"{i}. {title}\n")
                self.progress.emit("Playlist içeriği kaydedildi.")

            format_opts = {
                'MP3': {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'postprocessor_args': [
                        '-ar', '44100',
                        '-ac', '2',
                        '-b:a', '192k',
                    ],
                },
                'MP4': {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                },
                'Video': {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mkv',
                }
            }

            ydl_opts = {
                **format_opts[self.format_type],
                'ffmpeg_location': self.ffmpeg_path,
                'paths': {'home': self.save_path},
                'outtmpl': {
                    'default': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                },
                'progress_hooks': [lambda d: self.progress.emit(f"İndiriliyor: {d['filename']} - %{d.get('downloaded_bytes', 0) / (d.get('total_bytes', 1) or 1) * 100:.1f}")],
                'verbose': True,
                'no_warnings': False,
                'ignoreerrors': True,
                'windowsfilenames': True,
                'restrictfilenames': True,
                'writethumbnail': True,
                'keepvideo': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error = ydl.download([self.url])
                if error:
                    raise Exception(f"İndirme hatası: {error}")
            
            self.finished.emit(True, "İndirme başarıyla tamamlandı!")
        except Exception as e:
            self.finished.emit(False, f"Hata oluştu: {str(e)}")

    def update_progress(self, message):
        self.progress_label.setText(message)
        if "%" in message:
            try:
                percentage = float(message.split("%")[1].strip())
                self.progress_bar.setValue(int(percentage))
            except:
                pass

    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.progress_label.setText(message)
        if success:
            QMessageBox.information(self, 'Başarılı', f"{message}\nKonum: {self.path_input.text()}")
        else:
            QMessageBox.warning(self, 'Hata', message)

class YoutubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube İndirici')
        self.setFixedSize(600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # URL girişi
        url_layout = QHBoxLayout()
        url_label = QLabel('URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # İndirme türü seçimi
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup()
        self.radio_normal = QRadioButton('Tekli Video')
        self.radio_playlist = QRadioButton('Playlist')
        self.radio_normal.setChecked(True)
        self.type_group.addButton(self.radio_normal)
        self.type_group.addButton(self.radio_playlist)
        type_layout.addWidget(self.radio_normal)
        type_layout.addWidget(self.radio_playlist)
        layout.addLayout(type_layout)

        # Format seçimi
        format_layout = QHBoxLayout()
        format_label = QLabel('Format:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP3', 'MP4', 'Video'])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Kayıt konumu
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser("~/Downloads"))
        path_button = QPushButton('Konum Seç')
        path_button.clicked.connect(self.select_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_button)
        layout.addLayout(path_layout)

        # İndirme butonu
        self.download_button = QPushButton('İndir')
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # İlerleme çubuğu
        self.progress_label = QLabel('Hazır')
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        main_widget.setLayout(layout)

    def select_path(self):
        folder = QFileDialog.getExistingDirectory(self, 'Kayıt Konumu Seç')
        if folder:
            self.path_input.setText(folder)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Hata', 'Lütfen bir URL girin!')
            return

        if not os.path.exists(self.path_input.text()):
            try:
                os.makedirs(self.path_input.text())
            except Exception as e:
                QMessageBox.warning(self, 'Hata', f'Kayıt konumu oluşturulamadı: {str(e)}')
                return

        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.thread = IndirmeThread(
            url=url,
            format_type=self.format_combo.currentText(),
            save_path=self.path_input.text(),
            is_playlist=self.radio_playlist.isChecked()
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_finished)
        self.thread.start()

    def update_progress(self, message):
        self.progress_label.setText(message)
        if "%" in message:
            try:
                percentage = float(message.split("%")[1].strip())
                self.progress_bar.setValue(int(percentage))
            except:
                pass

    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.progress_label.setText(message)
        if success:
            QMessageBox.information(self, 'Başarılı', f"{message}\nKonum: {self.path_input.text()}")
        else:
            QMessageBox.warning(self, 'Hata', message)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ex = YoutubeDownloader()
    ex.show()
    sys.exit(app.exec_())
