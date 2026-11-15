"""AI Tools Daily niche generator."""
import json
import random
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from src.shared.llm_client import LLMClient
from src.config import CONFIG

AI_TOOLS_DATABASE = [
    {
        "name": "ChatGPT",
        "category": "LLM Chat",
        "free_tier": "Free tier available",
        "use_cases": ["writing", "coding", "analysis", "brainstorming"],
        "pexels_terms": ["artificial intelligence", "coding", "laptop", "chatbot"]
    },
    {
        "name": "Claude",
        "category": "LLM Chat",
        "free_tier": "Free tier available",
        "use_cases": ["long documents", "coding", "analysis", "creative writing"],
        "pexels_terms": ["ai assistant", "coding", "document analysis"]
    },
    {
        "name": "Perplexity",
        "category": "Search",
        "free_tier": "Free tier available",
        "use_cases": ["research", "fact-checking", "citations", "real-time info"],
        "pexels_terms": ["search", "research", "internet", "browser"]
    },
    {
        "name": "Leonardo AI",
        "category": "Image Generation",
        "free_tier": "150 credits/day free",
        "use_cases": ["art", "concepts", "marketing", "game assets"],
        "pexels_terms": ["ai art", "digital art", "generative art", "creative"]
    },
    {
        "name": "Runway Gen-3",
        "category": "Video Generation",
        "free_tier": "Free credits on signup",
        "use_cases": ["video creation", "animation", "motion graphics"],
        "pexels_terms": ["video editing", "animation", "motion graphics", "ai video"]
    },
    {
        "name": "ElevenLabs",
        "category": "Voice Synthesis",
        "free_tier": "10k chars/month free",
        "use_cases": ["voiceovers", "narration", "accessibility", "content creation"],
        "pexels_terms": ["voice recording", "podcast", "microphone", "audio"]
    },
    {
        "name": "Notion AI",
        "category": "Productivity",
        "free_tier": "Free tier with limits",
        "use_cases": ["notes", "summaries", "action items", "writing"],
        "pexels_terms": ["productivity", "notes", "organization", "workspace"]
    },
    {
        "name": "Gamma",
        "category": "Presentations",
        "free_tier": "Free tier available",
        "use_cases": ["slides", "pitch decks", "documents", "webpages"],
        "pexels_terms": ["presentation", "slides", "pitch deck", "meeting"]
    },
    {
        "name": "Cursor",
        "category": "Code Editor",
        "free_tier": "Free tier available",
        "use_cases": ["coding", "debugging", "refactoring", "learning"],
        "pexels_terms": ["programming", "code editor", "software development", "debugging"]
    },
    {
        "name": "Opus Clip",
        "category": "Video Repurposing",
        "free_tier": "Free tier available",
        "use_cases": ["shorts", "highlights", "social media", "content repurposing"],
        "pexels_terms": ["video editing", "social media", "content creation", "shorts"]
    },
    {
        "name": "HeyGen",
        "category": "AI Avatars",
        "free_tier": "Free credits on signup",
        "use_cases": ["talking head videos", "localization", "training", "marketing"],
        "pexels_terms": ["avatar", "virtual human", "video presentation", "spokesperson"]
    },
    {
        "name": "Suno",
        "category": "Music Generation",
        "free_tier": "Free credits daily",
        "use_cases": ["background music", "jingles", "soundtracks", "creative projects"],
        "pexels_terms": ["music production", "composer", "audio", "creative"]
    },
]

PROMPT_TEMPLATES = {
    "tutorial": """Create a 50-second YouTube Shorts script teaching ONE specific feature of {tool_name}.

Format: JSON with these fields:
- title: Viral title (<50 chars)
- hook: First 3 seconds - visual + audio (stop the scroll)
- steps: Array of 3-4 steps, each with: visual_description, narration, duration_seconds
- cta: Call to action (follow for more AI tools)
- hashtags: 5 relevant hashtags
- thumbnail_text: Main text for thumbnail (3-4 words)
- search_terms: 3 Pexels search terms for B-roll

Style: Fast-paced, practical, screen-record style. Each step = one breath.
No fluff. No "in this video". Jump straight to value.
Target: 150 words narration total.""",

    "comparison": """Create a 50-second YouTube Shorts script comparing {tool_name} vs one alternative for a specific use case.

Format: JSON with same fields as tutorial.
Style: "X vs Y for [task]" - quick verdict format.
Hook: Bold claim about which wins.
Steps: 3 comparison points (speed, quality, price, ease).
CTA: "Which do you use? Comment below."
Hashtags: 5 relevant.""",

    "hidden_gem": """Create a 50-second YouTube Shorts script revealing a hidden/underrated feature of {tool_name}.

Format: JSON with same fields.
Style: "Nobody talks about this feature..."
Hook: Secret/insider feel.
Steps: What it is, how to access, demo result, why it matters.
CTA: "Save this so you don't lose it."
Hashtags: 5 relevant.""",
}

class AIToolsGenerator:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.used_tools = set()
        self._load_history()

    def _load_history(self):
        history_file = Path("data/ai_tools_history.json")
        if history_file.exists():
            with open(history_file) as f:
                self.used_tools = set(json.load(f).get("used_tools", []))

    def _save_history(self):
        history_file = Path("data/ai_tools_history.json")
        history_file.parent.mkdir(exist_ok=True)
        with open(history_file, "w") as f:
            json.dump({"used_tools": list(self.used_tools), "last_updated": datetime.now().isoformat()}, f)

    def pick_tool(self) -> Dict:
        """Pick a tool not used recently, or reset if all used."""
        available = [t for t in AI_TOOLS_DATABASE if t["name"] not in self.used_tools]
        if not available:
            self.used_tools.clear()
            available = AI_TOOLS_DATABASE
        tool = random.choice(available)
        self.used_tools.add(tool["name"])
        self._save_history()
        return tool

    def generate_script(self, style: str = "tutorial") -> Dict[str, Any]:
        tool = self.pick_tool()
        template = PROMPT_TEMPLATES.get(style, PROMPT_TEMPLATES["tutorial"])
        prompt = template.format(tool_name=tool["name"])

        system = f"""You are a viral YouTube Shorts scriptwriter for AI tools.
        Tool: {tool['name']} ({tool['category']})
        Free tier: {tool['free_tier']}
        Best for: {', '.join(tool['use_cases'])}

        Return ONLY valid JSON. No markdown. No commentary."""

        response = self.llm.generate(system, prompt, temperature=0.7)
        script = json.loads(response)

        script["tool"] = tool
        script["niche"] = "ai_tools"
        script["style"] = style
        script["generated_at"] = datetime.now().isoformat()

        return script