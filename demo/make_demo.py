"""Generate demo video with TTS voiceover, subtitles, and synchronized visuals."""
import os
import subprocess
import pyttsx3
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 30
BASE = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(BASE, "frames")
AUDIO_DIR = os.path.join(BASE, "audio")
OUTPUT_DIR = os.path.join(BASE, "output")
FFMPEG = r"D:\workspace\workbook\wb2\projectSoftware\ffmpeg\bin\ffmpeg.exe"

for d in [FRAMES_DIR, AUDIO_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

# Colors
BG = (10, 10, 15)
SURFACE = (20, 20, 32)
BORDER = (42, 42, 62)
ACCENT = (99, 102, 241)
ACCENT2 = (129, 140, 248)
GREEN = (34, 197, 94)
YELLOW = (234, 179, 8)
TEXT = (224, 224, 224)
DIM = (136, 136, 136)
WHITE = (255, 255, 255)

# Narration script per scene
SCENES = [
    {
        "name": "title",
        "narration": "Welcome to Sentinel, a privacy-first multi-agent research network. Built for the UK AI Agent Hackathon.",
        "subtitle": "Sentinel — Privacy-First Multi-Agent Research",
    },
    {
        "name": "architecture",
        "narration": "Sentinel uses three specialized agents working in parallel: Academic for papers, Market for finance, and Code for repositories. All queries are protected by Venice AI's zero data retention, and results are verified on Bittensor.",
        "subtitle": "Multi-Agent Architecture + Privacy Layer",
    },
    {
        "name": "dashboard_idle",
        "narration": "The dashboard provides a clean interface. Simply enter your research topic and click Start Research.",
        "subtitle": "Enter a topic to begin research",
    },
    {
        "name": "working",
        "narration": "Watch as three agents search simultaneously. Academic queries ArXiv, Market checks CoinGecko, and Code scans GitHub. All activity streams to the dashboard in real time.",
        "subtitle": "3 Agents working in parallel",
    },
    {
        "name": "report",
        "narration": "Results are aggregated into a cited research report with source quality metrics. The Bittensor verification score confirms decentralized validation. Download the full report as Markdown.",
        "subtitle": "Cited report + Bittensor verification",
    },
    {
        "name": "closing",
        "narration": "Sentinel. Privacy-first, multi-agent, verified. Check out the code on GitHub.",
        "subtitle": "github.com/ponchy123/sentinel-hack",
    },
]


def get_font(size, bold=False):
    try:
        path = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def draw_rounded(draw, xy, r, fill, outline=None):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline)


def generate_tts(text, output_path):
    """Generate TTS audio using pyttsx3."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)
    engine.save_to_file(text, output_path)
    engine.runAndWait()


def get_audio_duration(path):
    """Get audio duration using ffprobe."""
    result = subprocess.run(
        [FFMPEG.replace("ffmpeg.exe", "ffprobe.exe"), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def render_scene(scene_name, subtitle_text):
    """Render a scene frame."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    if scene_name == "title":
        draw.text((W//2, H//2-120), "Sentinel", fill=ACCENT2, font=get_font(72, True), anchor="mm")
        draw.text((W//2, H//2-40), "Privacy-First Multi-Agent Research Network", fill=TEXT, font=get_font(28), anchor="mm")
        draw.text((W//2, H//2+30), "UK AI Agent Hackathon Ep5 x Conduct", fill=DIM, font=get_font(22), anchor="mm")
        draw.text((W//2, H//2+80), "Fetch.ai  |  Venice.ai  |  Bittensor", fill=ACCENT, font=get_font(20), anchor="mm")

    elif scene_name == "architecture":
        draw.text((W//2, 60), "System Architecture", fill=ACCENT2, font=get_font(36, True), anchor="mm")
        # Boxes
        for label, y, w in [("User", 140, 120), ("Dashboard", 230, 160), ("FastAPI", 320, 160)]:
            draw_rounded(draw, (W//2-w//2, y, W//2+w//2, y+50), 8, SURFACE, BORDER)
            draw.text((W//2, y+25), label, fill=TEXT, font=get_font(18), anchor="mm")
            draw.line([(W//2, y+50), (W//2, y+70)], fill=ACCENT, width=2)
        # Orchestrator
        draw_rounded(draw, (W//2-140, 410, W//2+140, 470), 8, ACCENT, None)
        draw.text((W//2, 440), "Orchestrator Agent", fill=WHITE, font=get_font(22, True), anchor="mm")
        # 3 agents
        for i, (name, src, color) in enumerate([("Academic", "ArXiv", GREEN), ("Market", "CoinGecko", YELLOW), ("Code", "GitHub", ACCENT)]):
            ax = W//2 - 350 + i*350
            draw.line([(W//2, 470), (ax, 530)], fill=color, width=2)
            draw_rounded(draw, (ax-100, 530, ax+100, 590), 8, SURFACE, color)
            draw.text((ax, 555), name, fill=WHITE, font=get_font(20, True), anchor="mm")
            draw.text((ax, 580), src, fill=DIM, font=get_font(14), anchor="mm")
        # Privacy
        draw_rounded(draw, (W//2-200, 640, W//2+200, 700), 8, (30, 20, 60), ACCENT)
        draw.text((W//2, 665), "Venice.ai Privacy Layer", fill=ACCENT2, font=get_font(20, True), anchor="mm")
        draw.text((W//2, 688), "Zero Data Retention", fill=DIM, font=get_font(14), anchor="mm")
        # Bittensor
        draw.line([(W//2, 700), (W//2, 740)], fill=ACCENT, width=2)
        draw_rounded(draw, (W//2-160, 740, W//2+160, 800), 8, SURFACE, GREEN)
        draw.text((W//2, 765), "Bittensor Verification", fill=GREEN, font=get_font(20, True), anchor="mm")

    elif scene_name == "dashboard_idle":
        _draw_dashboard(draw)
        draw.text((W//2, 450), "Enter a topic and click", fill=DIM, font=get_font(20), anchor="mm")
        draw.text((W//2, 480), '"Start Research" to begin.', fill=DIM, font=get_font(20), anchor="mm")

    elif scene_name == "working":
        _draw_dashboard(draw)
        agents = [("Academic", "◉", YELLOW, "Searching ArXiv..."), ("Market", "◉", YELLOW, "Querying CoinGecko..."), ("Code", "✓", GREEN, "Found 12 repos"), ("Bittensor", "○", DIM, "Awaiting")]
        for i, (name, icon, color, msg) in enumerate(agents):
            cx = 200 + i*420
            draw_rounded(draw, (cx, 260, cx+380, 370), 12, SURFACE, color)
            draw.text((cx+10, 275), name, fill=DIM, font=get_font(14))
            draw.text((cx+190, 310), icon, fill=color, font=get_font(36), anchor="mm")
            draw.text((cx+190, 350), msg, fill=DIM, font=get_font(12), anchor="mm")
        # Logs
        draw_rounded(draw, (200, 400, W-200, 650), 12, SURFACE, BORDER)
        draw.text((220, 415), "Agent Activity", fill=ACCENT2, font=get_font(18, True))
        logs = [("14:32:01", "System", "Research started"), ("14:32:02", "academic", "Searching ArXiv..."), ("14:32:03", "market", "Querying CoinGecko..."), ("14:32:04", "code", "Found katanemo/plano (6609 stars)")]
        for j, (t, a, m) in enumerate(logs):
            y = 445 + j*35
            draw.text((220, y), f"[{t}]", fill=DIM, font=get_font(13))
            draw.text((370, y), a, fill=ACCENT2, font=get_font(13, True))
            draw.text((480, y), m, fill=TEXT, font=get_font(13))

    elif scene_name == "report":
        _draw_dashboard(draw)
        for i, (name, icon) in enumerate([("Academic", "✓"), ("Market", "✓"), ("Code", "✓"), ("Bittensor", "✓")]):
            cx = 200 + i*420
            draw_rounded(draw, (cx, 260, cx+380, 330), 12, SURFACE, GREEN)
            draw.text((cx+10, 275), name, fill=DIM, font=get_font(14))
            draw.text((cx+190, 300), icon, fill=GREEN, font=get_font(32), anchor="mm")
        # Source quality
        draw_rounded(draw, (200, 360, W-200, 440), 12, SURFACE, BORDER)
        draw.text((220, 375), "Source Quality", fill=ACCENT2, font=get_font(18, True))
        draw.text((400, 410), "23 Sources", fill=ACCENT2, font=get_font(22, True), anchor="mm")
        draw.text((800, 410), "72% Confidence", fill=ACCENT2, font=get_font(22, True), anchor="mm")
        draw.text((1200, 410), "Score: 0.6", fill=GREEN, font=get_font(22, True), anchor="mm")
        # Report preview
        draw_rounded(draw, (200, 470, W-200, 700), 12, SURFACE, BORDER)
        draw.text((220, 485), "Research Report", fill=ACCENT2, font=get_font(18, True))
        draw.text((220, 520), "# AI agent safety mechanisms", fill=WHITE, font=get_font(16, True))
        draw.text((220, 550), "## Academic Research", fill=ACCENT2, font=get_font(14, True))
        draw.text((220, 575), "AI agent safety is a critical area...", fill=TEXT, font=get_font(12))
        draw.text((220, 605), "## Code Research", fill=ACCENT2, font=get_font(14, True))
        draw.text((220, 630), "- katanemo/plano (6609 stars)", fill=TEXT, font=get_font(12))
        draw.text((220, 660), "## Decentralized Verification", fill=ACCENT2, font=get_font(14, True))
        draw.text((220, 685), "Bittensor Score: 0.6", fill=GREEN, font=get_font(12))

    elif scene_name == "closing":
        draw.text((W//2, H//2-150), "Sentinel", fill=ACCENT2, font=get_font(64, True), anchor="mm")
        draw.text((W//2, H//2-70), "Privacy-First Multi-Agent Research", fill=TEXT, font=get_font(28), anchor="mm")
        draw.text((W//2, H//2+20), "Fetch.ai  •  Venice.ai  •  Bittensor", fill=ACCENT, font=get_font(22, True), anchor="mm")
        draw.text((W//2, H//2+70), "github.com/ponchy123/sentinel-hack", fill=ACCENT2, font=get_font(18), anchor="mm")

    # Subtitle bar at bottom (all scenes)
    draw.rectangle([(0, H-100), (W, H)], fill=(0, 0, 0, 180))
    draw.text((W//2, H-50), subtitle_text, fill=WHITE, font=get_font(24), anchor="mm")

    return img


def _draw_dashboard(draw):
    """Draw common dashboard chrome."""
    draw.rectangle([(0, 0), (W, 50)], fill=(15, 15, 25))
    draw.text((30, 25), "Sentinel", fill=ACCENT2, font=get_font(18, True), anchor="lm")
    draw.text((W//2, 100), "Sentinel", fill=ACCENT2, font=get_font(36, True), anchor="mm")
    draw_rounded(draw, (200, 160, W-200, 210), 12, SURFACE, BORDER)
    draw.text((220, 180), "AI agent safety mechanisms", fill=TEXT, font=get_font(16))


def main():
    print("=== Sentinel Demo Generator ===\n")

    # Step 1: Generate TTS for each scene
    print("1. Generating TTS audio...")
    scene_durations = []
    for i, scene in enumerate(SCENES):
        audio_path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.wav")
        print(f"   Scene {i+1}: {scene['name']}...")
        generate_tts(scene["narration"], audio_path)
        duration = get_audio_duration(audio_path)
        scene_durations.append(duration)
        print(f"     Duration: {duration:.1f}s")

    total_duration = sum(scene_durations)
    print(f"   Total: {total_duration:.1f}s\n")

    # Step 2: Generate frames for each scene
    print("2. Generating frames...")
    frame_index = 0
    for i, scene in enumerate(SCENES):
        img = render_scene(scene["name"], scene["subtitle"])
        num_frames = int(scene_durations[i] * FPS)
        for f in range(num_frames):
            path = os.path.join(FRAMES_DIR, f"frame_{frame_index:05d}.png")
            img.save(path)
            frame_index += 1
        print(f"   Scene {i+1}: {num_frames} frames ({scene_durations[i]:.1f}s)")
    print(f"   Total frames: {frame_index}\n")

    # Step 3: Concatenate audio
    print("3. Concatenating audio...")
    audio_list = os.path.join(AUDIO_DIR, "list.txt")
    with open(audio_list, "w") as f:
        for i in range(len(SCENES)):
            f.write(f"file 'scene_{i:02d}.wav'\n")
    combined_audio = os.path.join(OUTPUT_DIR, "combined_audio.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", audio_list, "-c", "copy", combined_audio], capture_output=True)
    print(f"   Combined audio: {combined_audio}\n")

    # Step 4: Combine video + audio
    print("4. Combining video + audio...")
    video_only = os.path.join(OUTPUT_DIR, "video_only.mp4")
    subprocess.run([
        FFMPEG, "-y", "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "23",
        video_only
    ], capture_output=True)

    final_output = os.path.join(OUTPUT_DIR, "sentinel-demo.mp4")
    subprocess.run([
        FFMPEG, "-y",
        "-i", video_only,
        "-i", combined_audio,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        final_output
    ], capture_output=True)

    # Check result
    size = os.path.getsize(final_output) / 1024
    print(f"   Final video: {final_output}")
    print(f"   Size: {size:.0f} KB")
    print(f"   Duration: {total_duration:.1f}s")
    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
