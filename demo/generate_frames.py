"""Generate demo frames for Sentinel hackathon video."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
BG = (10, 10, 15)
SURFACE = (20, 20, 32)
BORDER = (42, 42, 62)
ACCENT = (99, 102, 241)
ACCENT2 = (129, 140, 248)
GREEN = (34, 197, 94)
YELLOW = (234, 179, 8)
RED = (239, 68, 68)
TEXT = (224, 224, 224)
DIM = (136, 136, 136)
WHITE = (255, 255, 255)

FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", size)
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
    except:
        return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)

def scene_title():
    """Scene 1: Title card"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.text((W//2, H//2 - 120), "Sentinel", fill=ACCENT2, font=get_font(72, True), anchor="mm")
    draw.text((W//2, H//2 - 40), "Privacy-First Multi-Agent Research Network", fill=TEXT, font=get_font(28), anchor="mm")
    draw.text((W//2, H//2 + 30), "UK AI Agent Hackathon Ep5 x Conduct", fill=DIM, font=get_font(22), anchor="mm")
    draw.text((W//2, H//2 + 80), "Fetch.ai  |  Venice.ai  |  Bittensor", fill=ACCENT, font=get_font(20), anchor="mm")
    # Decorative line
    draw.line([(W//2 - 200, H//2 + 120), (W//2 + 200, H//2 + 120)], fill=BORDER, width=2)
    draw.text((W//2, H//2 + 160), "3 AI Agents  •  Real-time Dashboard  •  Decentralized Verification", fill=DIM, font=get_font(18), anchor="mm")
    return img

def scene_architecture():
    """Scene 2: Architecture diagram"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.text((W//2, 60), "System Architecture", fill=ACCENT2, font=get_font(36, True), anchor="mm")

    # User box
    draw_rounded_rect(draw, (W//2-80, 130, W//2+80, 180), 8, SURFACE, BORDER)
    draw.text((W//2, 155), "User", fill=TEXT, font=get_font(20), anchor="mm")
    draw.line([(W//2, 180), (W//2, 220)], fill=ACCENT, width=2)

    # Dashboard
    draw_rounded_rect(draw, (W//2-120, 220, W//2+120, 270), 8, SURFACE, BORDER)
    draw.text((W//2, 245), "React Dashboard", fill=TEXT, font=get_font(18), anchor="mm")
    draw.line([(W//2, 270), (W//2, 310)], fill=ACCENT, width=2)

    # FastAPI
    draw_rounded_rect(draw, (W//2-120, 310, W//2+120, 360), 8, SURFACE, BORDER)
    draw.text((W//2, 335), "FastAPI + WebSocket", fill=TEXT, font=get_font(18), anchor="mm")
    draw.line([(W//2, 360), (W//2, 400)], fill=ACCENT, width=2)

    # Orchestrator
    draw_rounded_rect(draw, (W//2-140, 400, W//2+140, 460), 8, ACCENT, None)
    draw.text((W//2, 430), "Orchestrator Agent", fill=WHITE, font=get_font(22, True), anchor="mm")

    # 3 agents
    agents = [("Academic", "ArXiv + Web"), ("Market", "CoinGecko"), ("Code", "GitHub")]
    colors = [GREEN, YELLOW, ACCENT]
    for i, (name, src) in enumerate(agents):
        ax = W//2 - 350 + i * 350
        draw.line([(W//2, 460), (ax, 520)], fill=colors[i], width=2)
        draw_rounded_rect(draw, (ax-100, 520, ax+100, 580), 8, SURFACE, colors[i])
        draw.text((ax, 545), name, fill=WHITE, font=get_font(20, True), anchor="mm")
        draw.text((ax, 570), src, fill=DIM, font=get_font(14), anchor="mm")

    # Privacy layer
    draw.line([(W//2-350, 610), (W//2+350, 610)], fill=ACCENT, width=1)
    draw_rounded_rect(draw, (W//2-200, 630, W//2+200, 690), 8, (30, 20, 60), ACCENT)
    draw.text((W//2, 655), "Venice.ai Privacy Layer", fill=ACCENT2, font=get_font(20, True), anchor="mm")
    draw.text((W//2, 678), "Zero Data Retention", fill=DIM, font=get_font(14), anchor="mm")

    # Bittensor
    draw.line([(W//2, 690), (W//2, 730)], fill=ACCENT, width=2)
    draw_rounded_rect(draw, (W//2-160, 730, W//2+160, 790), 8, SURFACE, GREEN)
    draw.text((W//2, 755), "Bittensor Verification", fill=GREEN, font=get_font(20, True), anchor="mm")
    draw.text((W//2, 778), "Decentralized Quality Scoring", fill=DIM, font=get_font(14), anchor="mm")

    # Output
    draw.line([(W//2, 790), (W//2, 830)], fill=ACCENT, width=2)
    draw_rounded_rect(draw, (W//2-140, 830, W//2+140, 890), 8, SURFACE, BORDER)
    draw.text((W//2, 860), "Cited Research Report", fill=TEXT, font=get_font(20), anchor="mm")

    return img

def scene_dashboard_idle():
    """Scene 3: Dashboard - idle state"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _draw_dashboard_chrome(draw)

    # Title
    draw.text((W//2, 100), "Sentinel", fill=ACCENT2, font=get_font(36, True), anchor="mm")
    draw.text((W//2, 140), "Privacy-First Multi-Agent Research Network", fill=DIM, font=get_font(16), anchor="mm")

    # Input bar
    draw_rounded_rect(draw, (200, 190, W-200, 250), 12, SURFACE, BORDER)
    draw.text((220, 215), "Enter research topic (e.g., AI Agent safety mechanisms)", fill=DIM, font=get_font(16))
    draw_rounded_rect(draw, (W-420, 200, W-220, 240), 8, ACCENT, None)
    draw.text((W-320, 218), "Start Research", fill=WHITE, font=get_font(16, True), anchor="mm")

    # Empty state
    draw.text((W//2, 450), "Enter a topic and click", fill=DIM, font=get_font(20), anchor="mm")
    draw.text((W//2, 480), '"Start Research" to begin.', fill=DIM, font=get_font(20), anchor="mm")
    draw.text((W//2, 530), "Three specialized agents will search academic,", fill=DIM, font=get_font(14), anchor="mm")
    draw.text((W//2, 555), "market, and code sources in parallel,", fill=DIM, font=get_font(14), anchor="mm")
    draw.text((W//2, 580), "protected by Venice.ai privacy infrastructure.", fill=DIM, font=get_font(14), anchor="mm")

    return img

def scene_dashboard_working():
    """Scene 4: Dashboard - agents working"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _draw_dashboard_chrome(draw)

    draw.text((W//2, 100), "Sentinel", fill=ACCENT2, font=get_font(36, True), anchor="mm")

    # Input bar with topic
    draw_rounded_rect(draw, (200, 160, W-200, 210), 12, SURFACE, BORDER)
    draw.text((220, 180), "AI agent safety mechanisms", fill=TEXT, font=get_font(16))

    # Agent cards
    agent_data = [
        ("Academic", "◉", YELLOW, "Searching ArXiv...", 0.4),
        ("Market", "◉", YELLOW, "Querying CoinGecko...", 0.3),
        ("Code", "✓", GREEN, "Found 12 repos", 1.0),
        ("Bittensor", "○", DIM, "Awaiting", 0),
    ]
    for i, (name, icon, color, msg, prog) in enumerate(agent_data):
        cx = 200 + i * 420
        draw_rounded_rect(draw, (cx, 240, cx+380, 370), 12, SURFACE, color if prog < 1 else GREEN)
        draw.text((cx+10, 260), name, fill=DIM, font=get_font(14))
        draw.text((cx+190, 300), icon, fill=color, font=get_font(36), anchor="mm")
        draw.text((cx+190, 345), msg, fill=DIM, font=get_font(12), anchor="mm")
        if prog > 0 and prog < 1:
            draw_rounded_rect(draw, (cx+20, 355, cx+360, 362), 3, BORDER, None)
            draw_rounded_rect(draw, (cx+20, 355, cx+20+int(340*prog), 362), 3, ACCENT, None)

    # Log entries
    draw_rounded_rect(draw, (200, 400, W-200, 700), 12, SURFACE, BORDER)
    draw.text((220, 415), "Agent Activity", fill=ACCENT2, font=get_font(18, True))
    logs = [
        ("14:32:01", "System", "Research started: AI agent safety mechanisms"),
        ("14:32:02", "academic", "Searching ArXiv for: AI agent safety"),
        ("14:32:03", "market", "Querying CoinGecko for: AI agent safety"),
        ("14:32:04", "code", "Found katanemo/plano (6609 stars)"),
        ("14:32:05", "code", "Found nextlevelbuilder/goclaw (3364 stars)"),
        ("14:32:06", "academic", "Found 8 academic sources"),
        ("14:32:07", "market", "Found 3 trending coins"),
    ]
    for j, (time, agent, msg) in enumerate(logs):
        y = 445 + j * 35
        draw.text((220, y), f"[{time}]", fill=DIM, font=get_font(13))
        draw.text((370, y), agent, fill=ACCENT2, font=get_font(13, True))
        draw.text((480, y), msg, fill=TEXT, font=get_font(13))

    return img

def scene_dashboard_report():
    """Scene 5: Dashboard - report complete"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _draw_dashboard_chrome(draw)

    draw.text((W//2, 100), "Sentinel", fill=ACCENT2, font=get_font(36, True), anchor="mm")

    # Input bar
    draw_rounded_rect(draw, (200, 160, W-200, 210), 12, SURFACE, BORDER)
    draw.text((220, 180), "AI agent safety mechanisms", fill=TEXT, font=get_font(16))

    # Agent cards - all done
    for i, (name, icon, color) in enumerate([
        ("Academic", "✓", GREEN), ("Market", "✓", GREEN),
        ("Code", "✓", GREEN), ("Bittensor", "✓", GREEN),
    ]):
        cx = 200 + i * 420
        draw_rounded_rect(draw, (cx, 240, cx+380, 330), 12, SURFACE, GREEN)
        draw.text((cx+10, 255), name, fill=DIM, font=get_font(14))
        draw.text((cx+190, 285), icon, fill=GREEN, font=get_font(32), anchor="mm")

    # Source quality
    draw_rounded_rect(draw, (200, 360, W-200, 460), 12, SURFACE, BORDER)
    draw.text((220, 375), "Source Quality", fill=ACCENT2, font=get_font(18, True))
    draw.text((300, 420), "23", fill=ACCENT2, font=get_font(32, True), anchor="mm")
    draw.text((300, 448), "Total Sources", fill=DIM, font=get_font(12), anchor="mm")
    draw.text((700, 420), "72%", fill=ACCENT2, font=get_font(32, True), anchor="mm")
    draw.text((700, 448), "Avg Confidence", fill=DIM, font=get_font(12), anchor="mm")
    draw.text((1100, 420), "0.6", fill=GREEN, font=get_font(32, True), anchor="mm")
    draw.text((1100, 448), "Bittensor Score", fill=DIM, font=get_font(12), anchor="mm")

    # Report preview
    draw_rounded_rect(draw, (200, 490, W-200, 780), 12, SURFACE, BORDER)
    draw.text((220, 505), "Research Report", fill=ACCENT2, font=get_font(18, True))
    draw_rounded_rect(draw, (W-400, 500, W-220, 530), 6, SURFACE, BORDER)
    draw.text((W-310, 513), "Download Markdown", fill=TEXT, font=get_font(12), anchor="mm")
    draw.text((220, 545), "# Research Report: AI agent safety mechanisms", fill=WHITE, font=get_font(16, True))
    draw.text((220, 575), "## Academic Research", fill=ACCENT2, font=get_font(14, True))
    draw.text((220, 600), "AI agent safety is a critical area of research...", fill=TEXT, font=get_font(12))
    draw.text((220, 620), "Key findings include multi-agent verification...", fill=TEXT, font=get_font(12))
    draw.text((220, 650), "## Code Research", fill=ACCENT2, font=get_font(14, True))
    draw.text((220, 675), "- katanemo/plano (6609 stars) - AI-native proxy", fill=TEXT, font=get_font(12))
    draw.text((220, 695), "- nextlevelbuilder/goclaw (3364 stars) - Go agent", fill=TEXT, font=get_font(12))
    draw.text((220, 725), "## Decentralized Verification", fill=ACCENT2, font=get_font(14, True))
    draw.text((220, 750), "Bittensor Score: 0.6 | Confidence: 50%", fill=GREEN, font=get_font(12))

    return img

def scene_closing():
    """Scene 7: Closing card"""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.text((W//2, H//2 - 150), "Sentinel", fill=ACCENT2, font=get_font(64, True), anchor="mm")
    draw.text((W//2, H//2 - 70), "Privacy-First Multi-Agent Research", fill=TEXT, font=get_font(28), anchor="mm")
    draw.line([(W//2 - 150, H//2 - 30), (W//2 + 150, H//2 - 30)], fill=BORDER, width=2)
    draw.text((W//2, H//2 + 20), "Built with", fill=DIM, font=get_font(18), anchor="mm")
    draw.text((W//2, H//2 + 60), "Fetch.ai  •  Venice.ai  •  Bittensor", fill=ACCENT, font=get_font(22, True), anchor="mm")
    draw.text((W//2, H//2 + 110), "UK AI Agent Hackathon Ep5 x Conduct", fill=DIM, font=get_font(16), anchor="mm")
    draw.text((W//2, H//2 + 160), "github.com/ponchy123/sentinel-hack", fill=ACCENT2, font=get_font(18), anchor="mm")
    return img

def _draw_dashboard_chrome(draw):
    """Draw common dashboard chrome (nav bar, etc.)"""
    draw.rectangle([(0, 0), (W, 50)], fill=(15, 15, 25))
    draw.text((30, 25), "Sentinel", fill=ACCENT2, font=get_font(18, True), anchor="lm")
    draw.text((W-30, 25), "API: Running", fill=GREEN, font=get_font(12), anchor="rm")

# Generate all frames
scenes = [
    ("01_title", scene_title, 3),
    ("02_architecture", scene_architecture, 4),
    ("03_dashboard_idle", scene_dashboard_idle, 3),
    ("04_dashboard_working", scene_dashboard_working, 4),
    ("05_dashboard_report", scene_dashboard_report, 4),
    ("06_closing", scene_closing, 3),
]

for name, func, duration in scenes:
    img = func()
    # Save multiple frames for duration (30fps)
    for frame_num in range(duration * 30):
        path = os.path.join(FRAMES_DIR, f"{name}_{frame_num:04d}.png")
        img.save(path)
    print(f"Generated {name}: {duration}s ({duration*30} frames)")

total = sum(d for _, _, d in scenes)
print(f"\nTotal: {total}s ({total*30} frames)")
