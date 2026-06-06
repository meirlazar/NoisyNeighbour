import os, argparse, logging, time
from pathlib import Path

from src.audio_downloader import AudioDownloader
from src.audio_splitter import AudioSplitter
from src.processing import extract_audio_from_video, combine_audio_video, preprocess_audio_for_demucs

parser = argparse.ArgumentParser(description="Download, split, and process audio pipelines via Demucs.")
parser.add_argument("--url", type=str, help="The URL of the video to download and process.")
parser.add_argument("--media-dir", type=str, default="./data", help="Local directory for recursive processing if no URL is specified.")
parser.add_argument("--download_path", type=str, default="./data", help="Path to save downloaded assets.")
parser.add_argument("--audio-only", action="store_true", default=False, help="Skip video stream extraction/recombination.")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose step-by-step logging.")

def process_pipeline(media_path, is_video, audio_splitter, log):
    log.info(f"--- Starting: {media_path.name} ---")
    t_start = time.time()

    if is_video:
        log.debug(f"[{media_path.name}] Extracting audio stream from video...")
        t_step = time.time()
        extracted_audio_path = extract_audio_from_video(media_path)
        log.debug(f"[{media_path.name}] Audio extraction completed in {time.time() - t_step:.2f}s")
    else:
        extracted_audio_path = media_path

    log.debug(f"[{media_path.name}] Normalizing audio levels and format for Demucs...")
    normalized_audio_path = str(extracted_audio_path).rsplit('.', 1)[0] + "_normalized.wav"
    processed_audio = preprocess_audio_for_demucs(extracted_audio_path, normalized_audio_path)

    log.info(f"[{media_path.name}] Handing off to Demucs (this takes time)...")
    t_step = time.time()
    instrumental_path, vocal_path = audio_splitter.split_audio(processed_audio)
    log.debug(f"[{media_path.name}] Demucs split finished in {time.time() - t_step:.2f}s")

    if is_video:
        log.debug(f"[{media_path.name}] Recombining video with instrumental track...")
        final_video_path = combine_audio_video(media_path, instrumental_path)
        log.info(f"[{media_path.name}] Success: Final video -> {final_video_path}")
    else:
        log.info(f"[{media_path.name}] Success: Audio outputs -> {instrumental_path} | {vocal_path}")
    
    log.info(f"--- Finished: {media_path.name} in {time.time() - t_start:.2f}s ---\n")

def main():
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
    log = logging.getLogger(__name__)

    log.info("Initializing Demucs AudioSplitter...")
    audio_splitter = AudioSplitter()
    video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.webm'}

    if args.url:
        log.info(f"Execution Mode: Single URL Download -> {args.url}")
        downloader = AudioDownloader(download_path=args.download_path, audio_only=args.audio_only)
        media_path = downloader.download_audio(args.url)
        if not media_path: log.critical("Download failed. Exiting."); return
        
        media_path = Path(media_path)
        is_video = not args.audio_only and media_path.suffix.lower() in video_exts
        process_pipeline(media_path, is_video, audio_splitter, log)
    else:
        media_dir = Path(args.media_dir)
        if not media_dir.is_dir(): log.critical(f"Directory '{media_dir}' does not exist."); return
        log.info(f"Execution Mode: Recursive Directory Scan -> {media_dir.resolve()}")

        for media_path in media_dir.rglob('*'):
            if not media_path.is_file(): continue
            # Prevent infinite loops processing its own intermediate normalized outputs
            if media_path.name.endswith("_normalized.wav"): continue 
            
            is_video = not args.audio_only and media_path.suffix.lower() in video_exts
            process_pipeline(media_path, is_video, audio_splitter, log)

if __name__ == "__main__":
    main()
