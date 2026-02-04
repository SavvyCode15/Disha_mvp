import os
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GroqChat:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = groq.Groq(api_key=api_key)
    
    def get_response(self, user_message: str, nearby_monuments: list) -> str:
        try:
            # Build context about nearby monuments (max 2)
            monument_context = ""
            if nearby_monuments:
                for i, monument in enumerate(nearby_monuments[:2]):
                    monument_context += f"\n- {monument['name']} ({monument.get('distance_km', 0):.1f} km away): {monument['description']}"
            
            # Build system prompt
            no_monuments_text = "\nNo monuments nearby."
            context_text = monument_context if monument_context else no_monuments_text
            
            system_prompt = f"""You are a friendly, knowledgeable AI tour guide for Delhi, India. A tourist is standing right in front of a monument and talking to you.

Context - Nearby monuments:{context_text}

Constraints: Reply in under 80 words. Speak naturally as if face-to-face. Use present tense. If you don't know something, say so — do not make up facts. If the tourist asks about pricing or safety, use only the data you have been given."""

            # Make API call
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Return None on any error (429, network, etc.)
            return None

class RuleBasedChat:
    def get_response(self, user_message: str, nearby_monuments: list) -> str:
        message_lower = user_message.lower()
        
        # Greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            if nearby_monuments:
                nearest = nearby_monuments[0]
                return f"Namaste! Welcome to {nearest['name']}, {nearest.get('distance_km', 0):.1f} km away. Want to know about its history, ticket prices, or safety tips?"
            else:
                return "Namaste! Welcome to Delhi. Tell me where you are or what you'd like to explore!"
        
        # Location
        if any(word in message_lower for word in ['where', 'nearby', 'close', 'near me', "what's around"]):
            if nearby_monuments:
                monument_list = ""
                for monument in nearby_monuments[:3]:
                    monument_list += f"• {monument['name']} — {monument.get('distance_km', 0):.1f} km ({monument['category']})\n"
                return f"Here are nearby attractions:\n{monument_list.strip()}"
            else:
                return "You're in Delhi! Popular areas to explore: Connaught Place (CP), Old Delhi/Chandni Chowk, and South Delhi monuments."
        
        # Prices
        if any(word in message_lower for word in ['price', 'cost', 'ticket', 'how much', 'entry fee']):
            if nearby_monuments:
                nearest = nearby_monuments[0]
                pricing = nearest.get('pricing', {})
                fair_prices = nearest.get('fair_prices', {})
                
                price_info = f"Entry fees for {nearest['name']}:\n"
                price_info += f"• Indians: ₹{pricing.get('indian', 'N/A')}\n"
                price_info += f"• Foreigners: ₹{pricing.get('foreigner', 'N/A')}\n"
                price_info += f"• Children under 15: {pricing.get('children_under_15', 'N/A')}\n"
                
                if fair_prices:
                    price_info += "\nAdditional services:\n"
                    for service, price in fair_prices.items():
                        price_info += f"• {service.replace('_', ' ').title()}: {price}\n"
                
                return price_info.strip()
            else:
                return "Please tell me which monument you're interested in for pricing information."
        
        # Safety
        if any(word in message_lower for word in ['safe', 'scam', 'careful', 'cheat', 'danger', 'warning']):
            if nearby_monuments:
                nearest = nearby_monuments[0]
                warnings = nearest.get('safety_warnings', [])
                if warnings:
                    safety_info = f"Safety tips for {nearest['name']}:\n"
                    for warning in warnings[:3]:
                        safety_info += f"• {warning}\n"
                    return safety_info.strip()
            return "General safety tips: Use official guides, keep valuables secure, verify ticket counters, and trust your instincts."
        
        # Food
        if any(word in message_lower for word in ['food', 'eat', 'restaurant', 'hungry', 'lunch', 'dinner']):
            return """Food recommendations by area:
• Old Delhi: Karim's (₹200-500), Chandni Chowk street food (₹50-150)
• Connaught Place: Mid-range restaurants (₹300-800)
• South Delhi: Cafes and fine dining (₹500-1500)
Always choose busy stalls for street food!"""
        
        # History
        if any(word in message_lower for word in ['tell me', 'history', 'about', 'info', 'what is', 'describe']):
            if nearby_monuments:
                nearest = nearby_monuments[0]
                description = nearest.get('description', '')
                audio_script = nearest.get('audio_script', '')
                
                # Return first 200 chars of combined info
                combined_info = f"{description} {audio_script}"
                if len(combined_info) > 200:
                    combined_info = combined_info[:200] + "..."
                
                return f"{nearest['name']}: {combined_info}"
            else:
                return "Please tell me which monument you'd like to know about."
        
        # Directions
        if any(word in message_lower for word in ['how to reach', 'directions', 'route']):
            if nearby_monuments:
                nearest = nearby_monuments[0]
                return f"Coordinates for {nearest['name']}: {nearest['latitude']}, {nearest['longitude']}. Use Google Maps, Uber, or Delhi Metro for directions."
            else:
                return "Please specify which location you want directions to."
        
        # Timings
        if any(word in message_lower for word in ['open', 'hours', 'timing', 'when', 'closed']):
            if nearby_monuments:
                nearest = nearby_monuments[0]
                hours = nearest.get('opening_hours', 'Not available')
                best_time = nearest.get('best_time_to_visit', 'Not specified')
                return f"{nearest['name']} timings:\n• Hours: {hours}\n• Best time: {best_time}"
            else:
                return "Please specify which monument you're asking about."
        
        # Help
        if 'help' in message_lower or 'what can you do' in message_lower:
            return "I can help with: history, prices, safety, food recommendations, directions, and timings. What would you like to know?"
        
        # Default
        return "I can help with history, prices, safety, food, directions, and timings. What would you like to know?"

def get_chat_response(user_message: str, nearby_monuments: list, lat: float, lon: float) -> dict:
    """
    Main function to get chat response - tries Groq first, falls back to rule-based
    """
    try:
        # Try Groq first
        groq_chat = GroqChat()
        groq_response = groq_chat.get_response(user_message, nearby_monuments)
        
        if groq_response is not None:
            return {
                "response": groq_response,
                "ai_powered": True
            }
    except Exception:
        # If Groq initialization fails, fall through to rule-based
        pass
    
    # Fall back to rule-based chat
    rule_chat = RuleBasedChat()
    rule_response = rule_chat.get_response(user_message, nearby_monuments)
    
    return {
        "response": rule_response,
        "ai_powered": False
    }