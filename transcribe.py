import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(api_subscription_key=os.environ["API_KEY"])

audio_dir = "clips"
output_dir = "transcripts"
os.makedirs(output_dir, exist_ok=True)

# Collect all audio clips
files = [
    os.path.join(audio_dir, f)
    for f in os.listdir(audio_dir)
    if f.endswith((".wav", ".mp3", ".mpeg"))
]

if not files:
    print("No audio files found in clips/")
else:
    job = client.speech_to_text_job.create_job(
        model="saaras:v3",
        mode="transcribe",
        language_code="hi-IN",
    )
    job.upload_files(file_paths=files)
    job.start()
    print("Job started, waiting for completion...")
    job.wait_until_complete()
    job.download_outputs(output_dir=output_dir)
    print(f"Done. Transcripts saved in {output_dir}/")