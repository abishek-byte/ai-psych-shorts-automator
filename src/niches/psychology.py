"""Psychology Facts niche generator."""
import json
import random
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from src.shared.llm_client import LLMClient
from src.config import CONFIG

PSYCHOLOGY_FACTS_DATABASE = [
    {
        "category": "cognitive_bias",
        "topics": [
            "Confirmation Bias", "Sunk Cost Fallacy", "Anchoring Effect", "Availability Heuristic",
            "Dunning-Kruger Effect", "Halo Effect", "Survivorship Bias", "Negativity Bias",
            "Bandwagon Effect", "Choice-Supportive Bias", "Blind Spot Bias", "Framing Effect"
        ],
        "pexels_terms": ["brain", "thinking", "decision", "psychology", "mind", "cognitive"]
    },
    {
        "category": "habits",
        "topics": [
            "Habit Loop (Cue-Routine-Reward)", "2-Minute Rule", "Implementation Intentions",
            "Temptation Bundling", "Habit Stacking", "Environment Design", "Identity-Based Habits",
            "Plateau of Latent Potential", "Goldilocks Rule", "Two-Day Rule", "Keystone Habits",
            "Atomic Habits Framework"
        ],
        "pexels_terms": ["habit", "routine", "discipline", "calendar", "checklist", "morning routine"]
    },
    {
        "category": "decision_making",
        "topics": [
            "Regret Minimization Framework", "Second-Order Thinking", "Inversion",
            "Opportunity Cost", "Pareto Principle (80/20)", "Eisenhower Matrix",
            "Satisficing vs Maximizing", "Pre-mortem Analysis", "Decision Fatigue",
            "Information Bias", "Analysis Paralysis", "Reversible vs Irreversible"
        ],
        "pexels_terms": ["decision", "choice", "crossroads", "strategy", "planning", "thinking"]
    },
    {
        "category": "social",
        "topics": [
            "Fundamental Attribution Error", "Spotlight Effect", "Pratfall Effect",
            "Ben Franklin Effect", "Mirroring", "Reciprocity Principle", "Social Proof",
            "Authority Bias", "Liking Principle", "Scarcity Principle", "Unity Principle",
            "Bystander Effect"
        ],
        "pexels_terms": ["social", "conversation", "people", "meeting", "communication", "relationship"]
    },
    {
        "category": "memory",
        "topics": [
            "Spacing Effect", "Active Recall", "Feynman Technique", "Memory Palace",
            "Chunking", "Interleaving", "Elaborative Encoding", "Testing Effect",
            "Forgetting Curve", "Primacy and Recency", "Context-Dependent Memory",
            "Sleep and Memory Consolidation"
        ],
        "pexels_terms": ["memory", "learning", "study", "brain", "neurons", "education"]
    },
    {
        "category": "productivity",
        "topics": [
            "Deep Work", "Flow State", "Parkinson's Law", "Time Blocking",
            "Energy Management vs Time Management", "Ultradian Rhythms", "Single-Tasking",
            "Shallow Work Trap", "Attention Residue", "Digital Minimalism",
            "Maker vs Manager Schedule", "Rest as Productivity"
        ],
        "pexels_terms": ["productivity", "focus", "work", "deep work", "flow", "time management"]
    },
]

PROMPT_TEMPLATES = {
    "fact": """Create a 45-second YouTube Shorts script explaining ONE psychology concept: {topic}.

Format: JSON with:
- title: Viral title (<50 chars)
- hook: First 3 seconds - visual + audio (counter-intuitive claim)
- explanation: 3 parts: what it is, real example, why it matters
- practical_tip: One actionable takeaway
- cta: "Follow for more psychology hacks"
- hashtags: 5 relevant
- thumbnail_text: 3-4 words for thumbnail
- search_terms: 3 Pexels terms

Style: "Did you know..." -> "Here's why..." -> "Use this to..."
Each sentence = one breath. 130 words narration max.""",

    "myth_bust": """Create a 45-second Shorts DEBUNKING a common myth about {topic}.

Format: Same JSON fields.
Hook: "Everyone believes X. Science says WRONG."
Structure: Myth -> Evidence -> Truth -> Practical tip.
CTA: "What myth should I bust next?"
Hashtags: 5 relevant.""",

    "habit": """Create a 45-second Shorts teaching a habit technique: {topic}.

Format: Same JSON fields.
Hook: "Stop relying on willpower. Do this instead."
Structure: Problem -> Technique -> How to apply (3 steps) -> Result.
CTA: "Save and try tomorrow."
Hashtags: 5 relevant.""",

    "tip": """Create a 45-second Shorts with one actionable psychology tip: {topic}.

Format: Same JSON fields.
Hook: "This 10-second trick changes how you [outcome]."
Structure: The tip -> Why it works (psychology) -> How to do it -> When to use.
CTA: "Try it today and comment results."
Hashtags: 5 relevant.""",
}

class PsychologyGenerator:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.used_topics = set()
        self._load_history()

    def _load_history(self):
        history_file = Path("data/psychology_history.json")
        if history_file.exists():
            with open(history_file) as f:
                self.used_topics = set(json.load(f).get("used_topics", []))

    def _save_history(self):
        history_file = Path("data/psychology_history.json")
        history_file.parent.mkdir(exist_ok=True)
        with open(history_file, "w") as f:
            json.dump({"used_topics": list(self.used_topics), "last_updated": datetime.now().isoformat()}, f)

    def pick_topic(self) -> Dict:
        all_topics = []
        for cat in PSYCHOLOGY_FACTS_DATABASE:
            for topic in cat["topics"]:
                all_topics.append({"topic": topic, "category": cat["category"], "pexels_terms": cat["pexels_terms"]})

        available = [t for t in all_topics if t["topic"] not in self.used_topics]
        if not available:
            self.used_topics.clear()
            available = all_topics

        chosen = random.choice(available)
        self.used_topics.add(chosen["topic"])
        self._save_history()
        return chosen

    def generate_script(self, style: str = "fact") -> Dict[str, Any]:
        topic_data = self.pick_topic()
        template = PROMPT_TEMPLATES.get(style, PROMPT_TEMPLATES["fact"])
        prompt = template.format(topic=topic_data["topic"])

        system = f"""You are a viral YouTube Shorts scriptwriter for psychology.
        Topic: {topic_data['topic']}
        Category: {topic_data['category']}

        Return ONLY valid JSON. No markdown. No commentary.
        Make it practical, not academic. Real-life application."""

        response = self.llm.generate(system, prompt, temperature=0.7)
        script = json.loads(response)

        script["topic_data"] = topic_data
        script["niche"] = "psychology"
        script["style"] = style
        script["generated_at"] = datetime.now().isoformat()

        return script