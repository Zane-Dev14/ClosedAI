import os
import sys
import asyncio
import edge_tts
from infer import VoiceConverter

MODELS = {
    "obama": {
        "pth": "models/obama.pth",
        "index": "models/obama.index",
        "voice": "en-US-GuyNeural",  # US English, male, neutral, fits Obama
        "desc": "Barack Obama (US President, calm, authoritative, American accent)"
    },
    "srk": {
        "pth": "models/srk.pth",
        "index": "models/srk.index",
        "voice": "en-IN-PrabhatNeural",  # Indian English, male, fits SRK
        "desc": "Shah Rukh Khan (Bollywood actor, charismatic, Indian accent)"
    },
    "modi": {
        "pth": "models/modi.pth",
        "index": "models/modi.index",
        "voice": "en-IN-ArjunNeural",  # Indian English, male, conversational, fits Modi
        "desc": "Narendra Modi (Indian PM, assertive, Indian accent)"
    },
    "trump": {
        "pth": "models/trump.pth",
        "index": "models/trump.index",
        "voice": "en-US-DavisNeural",  # US English, male, expressive, fits Trump
        "desc": "Donald Trump (US President, energetic, American accent)"
    },
    "Hutao": {
        "pth": "models/Hutao.pth",
        "index": "models/Hutao.index",
        "voice": "ja-JP-NanamiNeural",  # Japanese, female, youthful, fits Hu Tao (Genshin Impact)
        "desc": "Hu Tao (Genshin Impact, female, playful, Japanese accent)"
    },
    "technoblade": {
        "pth": "models/technoblade.pth",
        "index": "models/technoblade.index",
        "voice": "en-US-AndrewNeural",  # US English, male, warm, fits Technoblade (American Minecraft YouTuber)
        "desc": "Technoblade (Minecraft YouTuber, witty, American accent)"
    },
    "ChrisPratt": {
        "pth": "models/ChrisPratt.pth",
        "index": None,
        "voice": "en-US-BrianNeural",  # US English, male, friendly, fits Chris Pratt
        "desc": "Chris Pratt (Hollywood actor, friendly, American accent)"
    }
}

TTS_WAV = "output_tts.wav"
RVC_WAV = "output_rvc.wav"

def synthesize_tts(text, voice, tts_wav):
    async def run_tts():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tts_wav)
    asyncio.run(run_tts())

def tts_rvc_pipeline(text, model_choice):
    model = MODELS[model_choice]
    print(f"[INFO] Synthesizing TTS with voice: {model['voice']} ({model['desc']})...")
    synthesize_tts(text, model["voice"], TTS_WAV)
    print(f"[INFO] Running RVC voice conversion with model: {model['pth']} and index: {model['index']}...")
    vc = VoiceConverter()
    vc.convert_audio(
        audio_input_path=TTS_WAV,
        audio_output_path=RVC_WAV,
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
    print(f"[SUCCESS] Output written to {RVC_WAV}")

def main():
    print("=== Minimal TTS + RVC CLI ===")
    text = input("Enter the text to synthesize: ").strip()
    print("Choose a model:")
    print("  1. Obama (Black American Male)")
    print("  2. SRK (Indian Hindi Male)")
    model_choice = None
    while model_choice not in ("1", "2", "obama", "srk"):
        model_choice = input("Enter 1 for Obama or 2 for SRK: ").strip().lower()
        if model_choice == "1":
            model_choice = "obama"
        elif model_choice == "2":
            model_choice = "srk"
    try:
        tts_rvc_pipeline(text, model_choice)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 