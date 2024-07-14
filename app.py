import subprocess
import sys
import tempfile
import os

# Funktion zur Installation von Paketen
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Versuchen Sie, die erforderlichen Pakete zu importieren, und installieren Sie sie bei Bedarf
try:
    import streamlit as st
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    install('streamlit')
    install('opencv-python-headless')
    install('numpy')
    install('Pillow')
    import streamlit as st
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

# Überprüfen, ob FFmpeg installiert ist
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

if not check_ffmpeg():
    st.error("FFmpeg ist nicht installiert. Bitte installieren Sie FFmpeg, um Videos zu erstellen.")

# Funktion zur Umwandlung eines Frames in ASCII
def frame_to_ascii(frame, num_cols, scale, color=True):
    grayscale_values = '@%#*+=-:. '
    height, width = frame.shape[:2]
    cell_width = width / num_cols
    cell_height = scale * cell_width
    num_rows = int(height / cell_height)
    ascii_frame = ''

    for i in range(num_rows):
        for j in range(num_cols):
            x1, y1 = int(j * cell_width), int(i * cell_height)
            x2, y2 = int((j + 1) * cell_width), int((i + 1) * cell_height)
            block = frame[y1:y2, x1:x2]
            avg_color = block.mean(axis=0).mean(axis=0)

            if color:
                avg_gray = int((avg_color[0] + avg_color[1] + avg_color[2]) / 3)
                color_code = '\x1b[38;2;{};{};{}m'.format(int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))
            else:
                avg_gray = int((0.2989 * avg_color[2] + 0.5870 * avg_color[1] + 0.1140 * avg_color[0]))

            ascii_char = grayscale_values[int((avg_gray / 255) * (len(grayscale_values) - 1))]
            ascii_frame += color_code + ascii_char if color else ascii_char

        ascii_frame += '\n'
    return ascii_frame

# Funktion zur Erstellung eines ASCII-Bildes als Bild
def ascii_to_image(ascii_str, num_cols, scale, frame_width, frame_height):
    font = ImageFont.load_default()
    image = Image.new('RGB', (frame_width, frame_height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    y_offset = 0
    for line in ascii_str.split('\n'):
        draw.text((0, y_offset), line, font=font, fill=(0, 0, 0))
        y_offset += int(scale * (frame_width / num_cols))
    return image

# Funktion zum Erstellen des Videos mit ffmpeg
def create_video_with_ffmpeg(frames, output_path, frame_rate):
    temp_dir = tempfile.mkdtemp()
    for i, frame in enumerate(frames):
        frame_path = os.path.join(temp_dir, f'frame_{i:04d}.png')
        frame.save(frame_path)

    ffmpeg_cmd = [
        'ffmpeg', '-y', '-r', str(frame_rate), '-i', os.path.join(temp_dir, 'frame_%04d.png'),
        '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', output_path
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Fehler beim Erstellen des Videos: {e}")
        return

    # Temporären Ordner aufräumen
    for file_name in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file_name))
    os.rmdir(temp_dir)

# Streamlit App
st.title('Video to ASCII Converter')

st.markdown("""
Diese Anwendung ermöglicht es Ihnen, ein Video in ASCII-Kunst umzuwandeln. Laden Sie ein Video hoch und passen Sie die Einstellungen an, um das gewünschte ASCII-Ergebnis zu erhalten.

**Einstellungen:**
- **Number of Columns:** Bestimmt die Anzahl der ASCII-Zeichen in der Breite des Bildes. Höhere Werte ergeben detailliertere Bilder.
- **Scale:** Verhältnis von Breite zu Höhe der ASCII-Zeichen. Kleinere Werte führen zu einer höheren Auflösung.
- **Color:** Ob die ASCII-Ausgabe farbig sein soll oder nicht.
- **Frame Rate:** Bestimmt, wie oft ein Frame aus dem Video zur Umwandlung in ASCII ausgewählt wird.
""")

uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    allowed_types = ["video/mp4", "video/quicktime", "video/x-msvideo"]
    if uploaded_file.type not in allowed_types:
        st.error("Bitte laden Sie ein gültiges Videoformat hoch (MP4, MOV oder AVI).")
    elif uploaded_file.size > 200 * 1024 * 1024:
        st.error("Die Datei ist zu groß. Bitte laden Sie ein Video kleiner als 200 MB hoch.")
    else:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        video_path = tfile.name
        cap = cv2.VideoCapture(video_path)

        success, frame = cap.read()
        if success:
            st.text('Original Video Frame')
            st.image(frame, channels="BGR")

        cap.release()

        num_cols = st.slider('Number of Columns', min_value=50, max_value=200, value=100)
        scale = st.slider('Scale', min_value=0.1, max_value=1.0, value=0.5)
        color = st.checkbox('Color', value=True)

        frame_rate = st.slider('Frame Rate', min_value=1, max_value=30, value=5)

        if st.button('Convert to ASCII'):
            progress_bar = st.progress(0)
            frames = []
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            for count in range(total_frames):
                success, frame = cap.read()
                if not success:
                    break
                if count % frame_rate == 0:
                    ascii_frame = frame_to_ascii(frame, num_cols, scale, color)
                    frames.append(ascii_to_image(ascii_frame, num_cols, scale, frame.shape[1], frame.shape[0]))
                progress_bar.progress((count + 1) / total_frames)
            
            cap.release()

            # Video speichern
            output_path = os.path.join(tempfile.gettempdir(), f'{os.path.splitext(uploaded_file.name)[0]}_ascii.mp4')
            create_video_with_ffmpeg(frames, output_path, frame_rate)

            st.success(f'ASCII Video saved as {output_path}')
            st.video(output_path)

            if os.path.exists(output_path):
                with open(output_path, "rb") as file:
                    btn = st.download_button(
                        label="Download ASCII Video",
                        data=file,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_ascii.mp4",
                        mime="video/mp4"
                    )
