# AI & Psychology Daily Shorts - Fully Automated

**100% Free • Runs on GitHub Actions • Zero maintenance**

Generates and uploads **2 YouTube Shorts daily**:
- 🤖 **10:00 UTC** — AI Tool tutorial/review
- 🧠 **16:00 UTC** — Psychology fact/habit tip

---

## 🎯 Features

| Component | Technology | Cost |
|-----------|------------|------|
| Script Generation | Groq (Llama 3.1 70B) | **Free** (14,400 req/day) |
| Narration | Microsoft Edge TTS | **Free** (no key) |
| B-roll Footage | Pixabay API | **Free** (200/hr) |
| Video Assembly | FFmpeg | **Free** |
| Thumbnails | Pillow (Python) | **Free** |
| Upload | YouTube Data API | **Free** (10k units/day) |
| Hosting | GitHub Actions | **Free** (public repos) |

**Total monthly cost: $0**

---

## 🚀 Quick Start (15 minutes)

### 1. Fork this repository
Click **Fork** → your GitHub account

### 2. Get Free API Keys (one-time)

| Service | Link | Free Tier |
|---------|------|-----------|
| **Groq** | [console.groq.com](https://console.groq.com) | 14,400 req/day |
| **Pixabay** | [pixabay.com/api/docs](https://pixabay.com/api/docs) | 200 req/hr |
| **YouTube API** | [console.cloud.google.com](https://console.cloud.google.com) | 10,000 units/day |

### 3. Add GitHub Secrets
Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|-------------|-------|
| `GROQ_API_KEY` | `gsk_...` from Groq |
| `PIXABAY_API_KEY` | Your Pixabay API key |
| `YOUTUBE_CLIENT_SECRETS` | JSON from Google Cloud (see below) |
| `YOUTUBE_TOKEN` | *Leave empty for now* |

#### YouTube Client Secrets:
1. Google Cloud Console → APIs & Services → Credentials
2. Create Credentials → OAuth Client ID → Desktop App
3. Download JSON → Copy **entire JSON** as secret value

### 4. First Run: Generate YouTube Token
```bash
# Clone your fork locally
git clone https://github.com/YOUR_USERNAME/ai-psych-shorts-automator
cd ai-psych-shorts-automator

# Install deps
pip install -r requirements.txt

# Run once to generate token (opens browser)
python -c "
from src.shared.youtube_uploader import YouTubeUploader
uploader = YouTubeUploader()
print('Copy the printed token to YOUTUBE_TOKEN secret')
"
Copy the printed token → Add as YOUTUBE_TOKEN secret in GitHub.

5. Enable Actions

Actions tab → "I understand my workflows, go ahead and enable them"

6. Done! 🎉

- Runs automatically daily at 10:00 & 16:00 UTC
- Check Actions tab for logs
- Videos appear on your channel

---

⚙️ Configuration

Edit config.yaml (create from config.example.yaml):

niches:
  ai_tools:
    enabled: true
    schedule: "0 10 * * *"
    prompt_style: "tutorial"  # tutorial, comparison, hidden_gem
  psychology:
    enabled: true
    schedule: "0 16 * * *"
    prompt_style: "fact"  # fact, myth_bust, habit, tip

channel:
  name: "Your Channel Name"
  default_tags: ["shorts", "ai", "psychology"]

---

📊 Expected Output

┌──────────────────┬──────────┬─────────┬─────────┐
│      Metric      │ Month 1  │ Month 3 │ Month 6 │
├──────────────────┼──────────┼─────────┼─────────┤
│ Shorts published │ 60       │ 180     │ 360     │
├──────────────────┼──────────┼─────────┼─────────┤
│ Estimated views  │ 10K-100K │ 100K-1M │ 1M-5M   │
├──────────────────┼──────────┼─────────┼─────────┤
│ Subscribers      │ 100-1K   │ 1K-10K  │ 10K-50K │
└──────────────────┴──────────┴─────────┴─────────┘

Varies by niche competition and algorithm

---

🛠️ Customization

Add new AI tools

Edit src/niches/ai_tools.py → AI_TOOLS_DATABASE

Add psychology topics

Edit src/niches/psychology.py → PSYCHOLOGY_FACTS_DATABASE

Change prompt styles

# config.yaml
niches:
  ai_tools:
    prompt_style: "comparison"  # tutorial, comparison, hidden_gem
  psychology:
    prompt_style: "myth_bust"  # fact, myth_bust, habit, tip

Change visual style

production:
  video:
    font_size: 72
    font_color: "white"
  thumbnail:
    background_style: "gradient"  # gradient, solid, footage

---

🔧 Troubleshooting

┌───────────────────────────┬─────────────────────────────────────────┐
│           Issue           │                   Fix                   │
├───────────────────────────┼─────────────────────────────────────────┤
│ "GROQ_API_KEY not set"    │ Add secret in GitHub Settings           │
├───────────────────────────┼─────────────────────────────────────────┤
│ "PIXABAY_API_KEY not set" │ Add secret in GitHub Settings           │
├───────────────────────────┼─────────────────────────────────────────┤
│ YouTube upload fails      │ Re-run local auth to refresh token      │
├───────────────────────────┼─────────────────────────────────────────┤
│ FFmpeg error              │ Check Actions logs for stderr           │
├───────────────────────────┼─────────────────────────────────────────┤
│ No footage found          │ Pexels rate limit - waits automatically │
└───────────────────────────┴─────────────────────────────────────────┘

---

📝 License

MIT — Free to use, modify, distribute.

---

🙏 Credits

- Groq for free LLM inference
- Microsoft Edge TTS for free voices
- Pixabay for free stock footage
- YouTube API for free uploads
- GitHub Actions for free compute

---