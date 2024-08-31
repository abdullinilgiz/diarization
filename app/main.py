import os
import shutil
from pathlib import Path

import whisper
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pyannote.audio import Pipeline
from pydub import AudioSegment


BASE_DIR = Path(__file__).resolve().parent

model = whisper.load_model(os.path.join(BASE_DIR, 'whisper_model', 'base.pt'))
pipeline = Pipeline.from_pretrained(
    "pyannot_model/config.yaml")

app = FastAPI()

os.makedirs("temp_files", exist_ok=True)


def format_seconds_to_hhmmss(seconds) -> str:
    seconds = round(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"


def check_file_format(file_path: str):
    if file_path.endswith('.m4a'):
        file = AudioSegment.from_file(file_path)
        new_file_path = file_path.replace('.m4a', '.wav')
        file.export(new_file_path, format="wav")
        os.remove(file_path)
        file_path = new_file_path
    return file_path


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(
            status_code=400,
            detail="Wrong file extension. Allowed extensions: wav, mp3, m4a"
        )

    save_path = os.path.join('temp_files', file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    save_path = check_file_format(save_path)
    diarization = pipeline(save_path)

    response_content = {"dialogue": list()}
    audio = AudioSegment.from_file(save_path)
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if turn.end - turn.start < 0.1:
            continue
        start_ms = round(turn.start * 1000)
        end_ms = round(turn.end * 1000)
        audio_chunk = audio[start_ms: end_ms]
        temp_filename = f"temp_chunk_{start_ms}_{end_ms}.wav"
        audio_chunk.export(temp_filename, format="wav")
        result = model.transcribe(temp_filename)
        os.remove(temp_filename)
        response_content['dialogue'].append(
            {
                'speaker': speaker,
                'text': result['text'],
                'duration': format_seconds_to_hhmmss(turn.start) +
                '-' + format_seconds_to_hhmmss(turn.end),
            }
        )
    os.remove(save_path)
    return JSONResponse(content=response_content)
