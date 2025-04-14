# UniDownlaod

A modern, user-friendly YouTube video downloader with a sleek interface and powerful features. Download videos in various qualities with just a few clicks.

![UniDownlaod](screenshots/preview.png)

## Features

- 🎥 Download YouTube videos in multiple qualities
- 📱 Responsive and modern user interface
- 🎨 Beautiful gradient design with animations
- 🔄 Real-time video information fetching
- 🎯 Easy-to-use quality selection
- 💾 Fast and reliable downloads
- 🌐 Cross-platform compatibility

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pramanshav-downloader.git
cd pramanshav-downloader
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd backend
python app.py
```

4. Open `frontend/index.html` in your web browser

## Requirements

- Python 3.8 or higher
- Flask
- yt-dlp
- Modern web browser
- Internet connection

## Usage

1. Enter a YouTube URL in the input field
2. Click the fetch button to get video information
3. Select your preferred quality from the dropdown
4. Click Download to start downloading

## Project Structure

```
pramanshav-downloader/
├── backend/
│   ├── app.py
│   └── youtube_downloader.py
├── frontend/
│   ├── index.html
│   └── style/
│       ├── style.css
│       └── script.js
└── requirements.txt
```

## Dependencies

- Flask==3.0.0
- flask-cors==4.0.0
- yt-dlp==2024.3.10

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Pramanshav** - [GitHub Profile](https://github.com/yourusername)

## Acknowledgments

- Thanks to the yt-dlp team for their amazing tool
- Icons provided by Font Awesome
- Fonts from Google Fonts

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/pramanshav-downloader/issues).