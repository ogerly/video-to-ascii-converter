# Video to ASCII Converter

Convert videos to ASCII art with a Streamlit web application.

## Description

This project provides a Streamlit web application to convert video files into ASCII art videos. Users can upload a video file, adjust settings like the number of columns, scale, color, and frame rate, and then convert the video. The resulting ASCII video can be previewed and downloaded.

## Features

- Upload video files (MP4, MOV, AVI)
- Convert videos to ASCII art
- Adjust settings for number of columns, scale, color, and frame rate
- Preview and download the converted ASCII video
- Progress bar for video processing
- FFmpeg integration for video creation

## Technical Details

### Requirements

- Python 3.x
- Streamlit
- OpenCV
- NumPy
- Pillow
- FFmpeg (installed on the system)

### Installation

1. Clone the repository:

```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/video-to-ascii-converter.git
cd video-to-ascii-converter
```

2. Install the dependencies:
```sh
pip install -r requirements.txt
```

3. Ensure FFmpeg is installed on your system. For installation instructions, visit FFmpeg Download.
Running the Application
Run the Streamlit application:

```sh
streamlit run app.py
```

### Code Explanation
- app.py: Main application file that contains the Streamlit web app code.
- frame_to_ascii: Function to convert a video frame to ASCII art.
- ascii_to_image: Function to convert ASCII art to an image.
- create_video_with_ffmpeg: Function to create a video from ASCII images using FFmpeg.
- process_video: Cached function to process the video and generate ASCII images.

## Demo
You can try the demo [here](https://video-to-ascii-converter-hrs78zjvi3shprhejcygrt.streamlit.app/).

## License
This project is licensed under the MIT License.




