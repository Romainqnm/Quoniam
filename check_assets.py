import os
import config

def check_audio_assets():
    print("--- QUONIAM AUDIO ASSETS CHECK ---")
    
    missing_count = 0
    found_count = 0
    
    # Ensure directory exists
    sound_dir = "assets/sounds"
    if not os.path.exists(sound_dir):
        print(f"📂 Creating directory: {sound_dir}")
        os.makedirs(sound_dir, exist_ok=True)
    
    print(f"\nChecking {len(config.AUDIO_FILES)} audio items in 'config.AUDIO_FILES'...\n")
    
    print(f"{'PRESET':<12} | {'STATUS':<10} | {'EXPECTED PATH'}")
    print("-" * 60)
    
    for preset, path in config.AUDIO_FILES.items():
        # normalize path
        abs_path = os.path.abspath(path)
        
        if os.path.exists(path):
            print(f"{preset:<12} | ✅ FOUND   | {path}")
            found_count += 1
        else:
            print(f"{preset:<12} | ❌ MISSING | {path}")
            missing_count += 1
            
    print("-" * 60)
    print(f"\n📊 SUMMARY: {found_count} Found, {missing_count} Missing.")
    
    if missing_count > 0:
        print(f"\n⚠️  ACTION REQUIRED: Please copy your MP3 files into the '{sound_dir}' folder.")
        print("   Make sure filenames match the expected paths above!")

if __name__ == "__main__":
    check_audio_assets()
