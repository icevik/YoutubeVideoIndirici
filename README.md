İşte Windows için README.md içeriği:

```markdown
# YouTube Video İndirici

Bu uygulama, YouTube'dan video ve ses indirmenizi sağlayan basit bir grafik arayüz uygulamasıdır.

## Özellikler

- Tekli video veya playlist indirme
- MP3, MP4 ve Video (MKV) formatlarında indirme
- İlerleme çubuğu
- Özelleştirilebilir indirme konumu

## Gereksinimler

```bash
pip install -r requirements.txt
```

requirements.txt içeriği:
```
yt-dlp
PyQt5
```

## Kurulum

1. FFmpeg'i indirin:
   - [FFmpeg Windows Builds](https://github.com/BtbN/FFmpeg-Builds/releases) sayfasından en son ffmpeg-master-latest-win64-gpl.zip dosyasını indirin
   - Zip dosyasını açın
   - ffmpeg.exe, ffplay.exe ve ffprobe.exe dosyalarını projenin /bin klasörüne kopyalayın

2. Python bağımlılıklarını yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python youtube.py
```

## Kullanım

1. YouTube video/playlist URL'sini girin
2. İndirme türünü seçin (Tekli Video/Playlist)
3. İstediğiniz formatı seçin (MP3/MP4/Video)
4. Kayıt konumunu seçin
5. 'İndir' butonuna tıklayın

## Not

- Windows 10/11'de test edilmiştir
- İndirilen dosyalar varsayılan olarak Downloads klasörüne kaydedilir
- Playlist indirirken, video başlıkları playlist_videolari.txt dosyasına kaydedilir
```
