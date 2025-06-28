import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.mp4', '.mov', '.avi', '.mkv')):
            logger.info(f"Nouvelle vidéo détectée: {event.src_path}")
            self.process_video(event.src_path)
    
    def process_video(self, input_path):
        try:
            # Extraire le nom du fichier sans extension
            video_name = Path(input_path).stem
            output_dir = "/videos/encoded/" + video_name
            
            # Créer le dossier de sortie s'il n'existe pas
            os.makedirs(output_dir, exist_ok=True)
            
            # Chemin de sortie pour la playlist HLS
            output_playlist = f"{output_dir}/playlist.m3u8"
            
            # Commande FFmpeg pour la conversion en HLS
            cmd = [
                'ffmpeg',
                '-i', input_path,  # Fichier d'entrée
                '-c:v', 'libx264',  # Codec vidéo
                '-hls_time', '10',  # Durée de chaque segment (secondes)
                '-hls_playlist_type', 'vod',  # Type de playlist VOD
                '-hls_segment_filename', f'{output_dir}/segment_%03d.ts',  # Format des segments
                '-hls_flags', 'independent_segments',
                '-hls_segment_type', 'mpegts',
                '-b:v', '2000k',  # Bitrate vidéo
                '-maxrate', '2148k',
                '-bufsize', '4296k',
                '-c:a', 'aac',  # Codec audio
                '-b:a', '128k',  # Bitrate audio
                '-start_number', '0',
                output_playlist
            ]
            
            logger.info(f"Début du traitement de la vidéo: {input_path}")
            
            # Exécuter la commande FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Afficher la sortie en temps réel
            for line in process.stdout:
                logger.debug(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"Vidéo traitée avec succès: {output_playlist}")
                
                # Créer une miniature
                self.create_thumbnail(input_path, f"/videos/thumbnails/{video_name}.jpg")
                
                # Déplacer le fichier source vers un dossier d'archivage
                os.makedirs("/videos/originals/processed", exist_ok=True)
                os.rename(input_path, f"/videos/originals/processed/{os.path.basename(input_path)}")
                
            else:
                logger.error(f"Erreur lors du traitement de la vidéo: {input_path}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la vidéo {input_path}: {str(e)}")
    
    def create_thumbnail(self, input_path, output_path):
        """Crée une miniature à partir d'une vidéo"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', '00:00:05',  # Prendre une image à 5 secondes
                '-vframes', '1',     # Une seule image
                '-q:v', '2',         # Qualité de l'image (2-31, 2 étant la meilleure)
                output_path
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Miniature créée: {output_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors de la création de la miniature: {str(e)}")

def main():
    # Vérifier que les dossiers existent
    for folder in ['/videos/originals', '/videos/encoded', '/videos/thumbnails']:
        os.makedirs(folder, exist_ok=True)
    
    # Créer l'observateur de fichiers
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, '/videos/originals', recursive=False)
    
    logger.info("Démarrage de l'observateur de fichiers...")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
