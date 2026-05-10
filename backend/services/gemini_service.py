"""
Gemini AI Service for CivicAid
Handles chat conversations and resource matching using Google Gemini API.
Falls back to a smart demo mode if no API key is configured.
"""

import os
import json
from pathlib import Path


# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def load_resources():
    """Load resources from JSON database."""
    data_path = Path(__file__).parent.parent / "data" / "resources.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


SYSTEM_PROMPT = """You are CivicAid, a friendly and helpful social services navigator for the Davis, Sacramento, and San Francisco, California area. Your role is to help people find local resources for food, housing, legal aid, mental health, safety, transportation, immigration, disability services, and women's support.

IMPORTANT GUIDELINES:
1. Be warm, empathetic, and non-judgmental. Many people seeking help feel vulnerable.
2. Ask clear, simple questions — one at a time. Keep language at a 6th grade reading level.
3. When the user first messages you, begin the intake process by asking these questions one at a time:
   - "Are you a student?" (helps identify UC Davis-specific resources)
   - "What city are you in — Davis, Sacramento, or San Francisco?" (helps filter by location)
   - "Do you need help urgently, or can it wait a few days?" (helps prioritize crisis resources)
   - "Do you prefer help online, by phone, or in person?" (helps filter by service type)
   - "Is there a language you'd prefer to receive help in?" (helps identify multilingual services)
4. After gathering enough information (usually 3-5 questions), provide a personalized list of matching resources.
5. Format your resource recommendations clearly with name, description, phone, and next steps.
6. If someone mentions a crisis (suicide, violence, immediate danger), immediately provide crisis hotline numbers:
   - 988 Suicide & Crisis Lifeline (call/text 988)
   - National DV Hotline: 1-800-799-7233
   - 911 for emergencies
7. Always be encouraging and let them know help is available.

AVAILABLE RESOURCES DATABASE:
{resources}

When recommending resources, use ONLY the resources from the database above. Include the resource name, description, phone number, and any relevant eligibility information.

When you have gathered enough information, output your final resource recommendations in this format:
---RESOURCES_START---
[list the resource IDs that match, one per line, e.g. food-001]
---RESOURCES_END---
Then follow with a friendly summary of why you recommended each one.
"""


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.resources_data = load_resources()
        self.model = None
        
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.use_ai = True
        else:
            self.use_ai = False
    
    def get_system_prompt(self):
        """Build system prompt with embedded resource data."""
        resources_text = json.dumps(self.resources_data["resources"], indent=2)
        return SYSTEM_PROMPT.format(resources=resources_text)
    
    async def chat(self, message: str, history: list, category: str = None) -> dict:
        """
        Process a chat message and return AI response.
        Falls back to demo mode if Gemini isn't available.
        """
        if self.use_ai:
            return await self._gemini_chat(message, history, category)
        else:
            return self._demo_chat(message, history, category)
    
    async def _gemini_chat(self, message: str, history: list, category: str = None) -> dict:
        """Use real Gemini API for chat."""
        try:
            system_prompt = self.get_system_prompt()
            if category:
                system_prompt += f"\n\nThe user has selected the '{category}' category. Focus your questions and recommendations on this area."
            
            # Build conversation for Gemini
            chat = self.model.start_chat(history=[])
            
            # Send system prompt as first message
            chat.send_message(system_prompt)
            
            # Replay history
            for msg in history:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
                    
            # Send current message
            response = chat.send_message(message)
            response_text = response.text
            
            # Extract resource IDs if present
            resource_ids = self._extract_resource_ids(response_text)
            
            # Clean response text (remove resource markers)
            clean_text = response_text
            if "---RESOURCES_START---" in clean_text:
                parts = clean_text.split("---RESOURCES_START---")
                after = parts[1].split("---RESOURCES_END---") if len(parts) > 1 else ["", ""]
                clean_text = parts[0] + (after[1] if len(after) > 1 else "")
                clean_text = clean_text.strip()
            
            return {
                "response": clean_text,
                "resource_ids": resource_ids,
                "resources": self._get_resources_by_ids(resource_ids)
            }
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._demo_chat(message, history, category)
    
    def _demo_chat(self, message: str, history: list, category: str = None) -> dict:
        """Smart demo mode that simulates AI conversation flow."""
        # Count only user messages to track conversation progress reliably
        user_msg_count = len([m for m in history if m.get("role") == "user"])
        message_lower = message.lower()
        
        # Track user responses from history
        user_data = self._extract_user_data(history, message)
        
        if user_msg_count == 0:
            # First message — ask first intake question
            cat_label = self.resources_data["categories"].get(category, {}).get("label", "social services")
            return {
                "response": f"Hi there! 👋 I'm CivicAid, your social services navigator. I see you're looking for help with **{cat_label}** — I'm here to find the best resources for you.\n\nLet me ask a few quick questions to personalize your results.\n\n**Are you a student?** (This helps me find campus-specific resources)",
                "resource_ids": [],
                "resources": []
            }
        elif user_msg_count == 1:
            return {
                "response": "Got it! 📍 **What city are you in — Davis, Sacramento, or San Francisco?**",
                "resource_ids": [],
                "resources": []
            }
        elif user_msg_count == 2:
            return {
                "response": "Thanks! ⏰ **Do you need help urgently (today), or can it wait a few days?**",
                "resource_ids": [],
                "resources": []
            }
        elif user_msg_count == 3:
            return {
                "response": "Almost done! 📞 **Do you prefer help online, by phone, or in person?**",
                "resource_ids": [],
                "resources": []
            }
        elif user_msg_count >= 4:
            # Generate recommendations based on gathered info
            return self._generate_recommendations(category, user_data)
        else:
            return {
                "response": "Thank you for sharing that! Let me continue with the next question...",
                "resource_ids": [],
                "resources": []
            }
    
    def _extract_user_data(self, history: list, current_msg: str) -> dict:
        """Extract structured data from conversation history."""
        data = {
            "is_student": False,
            "city": "Davis",
            "urgent": False,
            "preference": "any"
        }
        
        all_messages = [m["content"].lower() for m in history if m["role"] == "user"]
        all_messages.append(current_msg.lower())
        
        for msg in all_messages:
            if "yes" in msg and any(word in msg for word in ["student", "yes"]):
                data["is_student"] = True
            if "sacramento" in msg:
                data["city"] = "Sacramento"
            if "davis" in msg:
                data["city"] = "Davis"
            if "san francisco" in msg or "sf" in msg:
                data["city"] = "San Francisco"
            if any(word in msg for word in ["urgent", "today", "now", "asap", "immediately"]):
                data["urgent"] = True
            if "phone" in msg:
                data["preference"] = "phone"
            elif "online" in msg:
                data["preference"] = "online"
            elif "in person" in msg or "in-person" in msg:
                data["preference"] = "in-person"
        
        return data
    
    def _generate_recommendations(self, category: str, user_data: dict) -> dict:
        """Generate personalized resource recommendations."""
        resources = self.resources_data["resources"]
        
        # Filter by category
        if category:
            filtered = [r for r in resources if r["category"] == category]
        else:
            filtered = resources
        
        # Filter by city preference
        city_filtered = [r for r in filtered if r["city"].lower() == user_data["city"].lower()]
        if not city_filtered:
            city_filtered = filtered
        
        # Prioritize by preference
        if user_data["preference"] != "any":
            pref_filtered = [r for r in city_filtered if r["type"] == user_data["preference"]]
            if pref_filtered:
                city_filtered = pref_filtered
        
        # If student, boost UC Davis resources
        if user_data["is_student"]:
            student_resources = [r for r in filtered if "UC Davis" in r.get("name", "") or "UC Davis" in r.get("description", "")]
            # Put student resources first
            other = [r for r in city_filtered if r not in student_resources]
            city_filtered = student_resources + other
        
        # Take top 5
        top_resources = city_filtered[:5]
        resource_ids = [r["id"] for r in top_resources]
        
        # Build friendly response
        city = user_data["city"]
        response_lines = [
            f"Great news! 🎉 I found **{len(top_resources)} resources** in **{city}** that match your needs:\n"
        ]
        
        for i, r in enumerate(top_resources, 1):
            response_lines.append(f"**{i}. {r['name']}**")
            response_lines.append(f"   {r['description'][:120]}...")
            response_lines.append(f"   📞 {r['phone']} | 🕐 {r['hours']}")
            response_lines.append("")
        
        response_lines.append("👆 Check out the detailed resource cards below for full information, directions, and direct links!")
        response_lines.append("\nWould you like me to help with anything else? You can ask about a different category or get more details about any resource.")
        
        return {
            "response": "\n".join(response_lines),
            "resource_ids": resource_ids,
            "resources": top_resources
        }
    
    def _extract_resource_ids(self, text: str) -> list:
        """Extract resource IDs from AI response."""
        ids = []
        if "---RESOURCES_START---" in text and "---RESOURCES_END---" in text:
            block = text.split("---RESOURCES_START---")[1].split("---RESOURCES_END---")[0]
            for line in block.strip().split("\n"):
                line = line.strip()
                if line:
                    ids.append(line)
        return ids
    
    def _get_resources_by_ids(self, ids: list) -> list:
        """Look up full resource objects by ID."""
        resources = self.resources_data["resources"]
        return [r for r in resources if r["id"] in ids]

    async def translate(self, text: str, target_language: str) -> str:
        """Translate text using Gemini or return original in demo mode."""
        if self.use_ai:
            try:
                response = self.model.generate_content(
                    f"Translate the following text to {target_language}. Only return the translation, nothing else:\n\n{text}"
                )
                return response.text
            except Exception as e:
                print(f"Translation error: {e}")
                return text
        else:
            # Demo mode: return a note about translation
            return f"[{target_language}] {text}"
