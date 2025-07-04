import os
import sys
import asyncio
import edge_tts
from minimal_tts_rvc.infer import VoiceConverter
from minimal_tts_rvc.models_config import MODELS

TTS_WAV = "output/output_tts.wav"
RVC_WAV = "output/output_rvc.mp3"

async def synthesize_tts_async(text, voice, tts_wav):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(tts_wav)

def synthesize_tts(text, voice, tts_wav):
    asyncio.run(synthesize_tts_async(text, voice, tts_wav))

def tts_rvc_pipeline(text, model_choice, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    model = MODELS[model_choice]
    tts_wav = os.path.join(output_dir, f"{model_choice}_tts.wav")
    rvc_wav = os.path.join(output_dir, f"{model_choice}_rvc.mp3")
    print(f"[INFO] Synthesizing TTS with voice: {model['voice']} ({model['desc']})...")
    synthesize_tts(text, model["voice"], tts_wav)
    print(f"[INFO] Running RVC voice conversion with model: {model['pth']} and index: {model['index']}...")
    vc = VoiceConverter()
    vc.convert_audio(
        audio_input_path=tts_wav,
        audio_output_path=rvc_wav,
        model_path=model["pth"],
        index_path=model["index"],
        embedder_model="contentvec",
        f0_method="rmvpe",
        export_format="MP3",
        sid=0,
        pitch=-8,
        clean_audio=True,
        clean_strength=0.5,
        volume_envelope=1.0,
        hop_length=128,
        protect=0.8,
    )
    print(f"[SUCCESS] Output written to {rvc_wav}")
    return rvc_wav

def list_models():
    return MODELS

def main():
    print("=== Minimal TTS + RVC CLI ===")
    text = input("Enter the text to synthesize: ").strip()
    print("Choose a model:")
    for i, (k, v) in enumerate(MODELS.items(), 1):
        print(f"  {i}. {v['desc']} [{k}]")
    model_choice = None
    valid_choices = {str(i): k for i, k in enumerate(MODELS.keys(), 1)}
    valid_choices.update({k: k for k in MODELS.keys()})
    while model_choice not in valid_choices:
        model_choice = input(f"Enter model name or number: ").strip()
        model_choice = valid_choices.get(model_choice, model_choice)
    try:
        tts_rvc_pipeline(text, model_choice)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 