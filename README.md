# 🎙️ NoisyNeighbour
**AI-Powered Karaoke Generator & Stem Extractor**

NoisyNeighbour is an automated pipeline that downloads media from YouTube, utilizes Meta's Demucs neural network to isolate vocals from instrumentals, and creates custom karaoke tracks. 

Whether you are pulling single URLs from YouTube or recursively batch-processing a local directory of media files, NoisyNeighbour handles the extraction, normalization, AI-splitting, and video recombination automatically.

## ✨ Features
* **Smart Downloading:** Pull full video or audio-only streams from YouTube.
* **Batch Processing (New):** Recursively scan and process local directories without needing to download anything.
* **AI Vocal Separation:** Powered by Meta's Demucs to mathematically split audio into isolated stems.
* **Automated Muxing:** Automatically recombines the isolated instrumental track with the original video stream.
* **Detailed Telemetry:** Integrated verbose logging to track execution timers and pipeline bottlenecks.

*Note: CPU processing is supported but GPU (CUDA) is highly recommended. A web dashboard (via Node.js) is planned for a future release.*

---

## 🛠️ Prerequisites

Before you begin, ensure your system has the following installed:
1. **Python 3.8+**
2. **FFmpeg** (Required for all audio/video multiplexing)
3. **Node.js** (Required for future dashboard UI and package management)



## 🚀 Installation & Setup

Follow these exact steps to ensure an isolated and clean deployment.

### 1. Clone the Repository
```
git clone [https://github.com/yourusername/NoisyNeighbour.git](https://github.com/yourusername/NoisyNeighbour.git)
cd NoisyNeighbour
```

### 2. Install System Dependencies FFmpeg:
Ubuntu/Debian:
``` sudo apt-get update && sudo apt-get install ffmpeg ```

macOS (Homebrew):
``` brew install ffmpeg ```

RHEL/CentOS:
``` sudo dnf install ffmpeg ffmpeg-devel ```
Node.js (For future dashboard integration):
Ubuntu/Debian (Using NodeSource):
```
curl -fsSL [https://deb.nodesource.com/setup_20.x](https://deb.nodesource.com/setup_20.x) | sudo -E bash -
sudo apt-get install -y nodejs
```

macOS:
``` brew install node ```

# 3. Initialize the Virtual Environment
Never install Python ML dependencies globally. 
Create and activate a virtual environment:

Create the venv
``` python3 -m venv venv ```

Activate it (Linux/macOS)
``` source venv/bin/activate ```

Activate it (Windows)
``` .\venv\Scripts\activate ```
### 4. Install Python Requirements

#### Note: Your requirements.txt should include yt-dlp[default]>=2023.10.0 to pull in necessary cryptography and websocket libraries that prevent YouTube from throttling or blocking your download requests.

Upgrade pip first
``` python3 -m pip install --upgrade pip ```

Install the pipeline requirements
``` pip install -r requirements.txt ```


## 📖 Command Line Options
Command ```venv/bin/python3 -m main``` 

Flags
```--url (String, Default: None)```
The exact YouTube URL you want to download and process. If this option is omitted, the script automatically defaults to local directory batch processing.

```--media-dir (Path, Default: ./data)```
The root directory to recursively scan for local media files. This parameter is active only when --url is NOT provided.

```--download_path (Path, Default: ./data)```
The destination directory where yt-dlp will save downloaded YouTube videos.

```--audio-only (Flag, Default: False)```
Skips video extraction and recombination. Outputs only the isolated .wav stems.

```-v, --verbose (Flag, Default: False)```
Enables step-by-step debug logging, outputting exact timestamps and execution metrics.

```-h, --help (Command, Default: N/A)```
Shows the help menu and parameter definitions.

## 💻 Usage Examples

Make sure your virtual environment is active (source venv/bin/activate) before running these commands.

Local Recursive Batch Processing (No Downloading)
Scans the default directory (./data) and all its subdirectories, automatically processing every video and audio file it finds without downloading anything new.
```
venv/bin/python3 -m main.py
```

Local Batch Processing with Custom Directory
Recursively crawls a specific local folder and its subfolders to process all media files, enabling verbose logging to track performance.
```
venv/bin/python3 -m main.py --media-dir "/path/to/your/media/folder" -v
```

Local Audio-Only Batch Processing
Recursively scans the local directory, processes both video and audio files, but forces the script to treat everything as audio-only (skipping video stream recombination and outputting only the vocal/instrumental stems).
```
venv/bin/python3 -m main.py --media-dir "./data" --audio-only
```
Single URL Download and Recombine Video
Downloads a fresh YouTube video, splits the audio, and outputs a final video with the vocals removed.
```
venv/bin/python3 -m main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```


## 🔧 Troubleshooting

Script skips certain local files during recursive run.
Check the filenames. The script is explicitly programmed to skip files ending in "_normalized.wav" to prevent infinite loops where it continuously re-processes its own intermediate outputs.

yt-dlp throws an HTTP 403 or "Sign in to confirm you're not a bot" error.
YouTube aggressively updates its bot-detection algorithms. Ensure you installed yt-dlp[default] via your requirements, and run pip install -U yt-dlp to pull the absolute latest version, as their patching cycle is frequent.

CUDA Out of Memory (OOM) / Script crashes during Demucs processing.
Audio splitting is highly VRAM intensive. If you are using an 8GB GPU (like a GTX 1070) and process a massive audio file, PyTorch may fragment the memory and crash. Ensure no other AI models (like local Ollama instances) are hogging VRAM while NoisyNeighbour runs.

"Command 'ffmpeg' not found"
The python ffmpeg-python library is just a wrapper. You must have the actual FFmpeg binary installed on your host OS. Verify it is in your system path by running ffmpeg -version in your terminal.

Script hangs silently for a long time.
Demucs takes time to mathematically separate tracks. Run your command with the -v flag. If it hangs after [Filename] Handing off to Demucs (this takes time)..., the script is working properly; your GPU/CPU is just crunching the tensors.
