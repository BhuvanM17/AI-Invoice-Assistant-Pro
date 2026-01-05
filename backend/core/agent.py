import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class QuestionType(Enum):
    PRICING = "pricing"
    CONTACT = "contact"
    LOCATION = "location"
    FACILITY = "facility"
    GENERAL = "general"


@dataclass
class UserIntent:
    """Detect what user wants"""
    type: QuestionType
    is_specific: bool
    entity: Optional[str] = None  # e.g., "whitefield", "co-working", "parking"
    timeframe: Optional[str] = None


@dataclass
class ChatResponse:
    """Structured response format"""
    answer: str
    confidence: float
    follow_up_questions: List[str]
    source: str


class IntentParser:
    """Parse user questions to understand what they want"""

    def __init__(self):
        self.pricing_patterns = {
            'co-working': ['coworking', 'shared desk', 'hot desk', 'shared space', 'per seat', 'seat cost'],
            'private_office': ['private office', 'private cabin', 'dedicated office', 'team room'],
            'day_pass': ['day pass', 'daily pass', 'trial', 'visit day'],
            'virtual_office': ['virtual office', 'business address', 'mail service'],
            'meeting_room': ['meeting room', 'conference room', 'board room'],
            'parking': ['parking', 'car parking', 'vehicle parking']
        }

        self.location_patterns = {
            'koramangala': ['koramangala', 'koramangla'],
            'whitefield': ['whitefield', 'itpl'],
            'electronic_city': ['electronic city', 'ecity'],
            'indiranagar': ['indiranagar', 'indira nagar'],
            'mg_road': ['mg road', 'brigade road']
        }

        self.contact_patterns = {
            'sales': ['sales', 'visit', 'tour', 'demo', 'book'],
            'support': ['support', 'help', 'issue', 'problem', 'complaint'],
            'corporate': ['corporate', 'business', 'enterprise', 'company'],
            'general': ['contact', 'phone', 'email', 'number', 'reach']
        }

    def parse(self, question: str) -> UserIntent:
        """Analyze user question and extract intent"""
        question_lower = question.lower()

        if any(word in question_lower for word in ['price', 'cost', 'how much', 'rate', 'fee']):
            return self._parse_pricing_intent(question_lower)

        elif any(word in question_lower for word in ['contact', 'call', 'email', 'phone', 'number', 'visit', 'tour']):
            return self._parse_contact_intent(question_lower)

        elif any(word in question_lower for word in ['where', 'location', 'address', 'center', 'branch']):
            return self._parse_location_intent(question_lower)

        elif any(word in question_lower for word in
                 ['facility', 'amenity', 'service', 'wifi', 'internet', 'parking', 'meeting']):
            return self._parse_facility_intent(question_lower)

        else:
            return UserIntent(
                type=QuestionType.GENERAL,
                is_specific=False
            )

    def _parse_pricing_intent(self, question: str) -> UserIntent:
        """Parse pricing-related questions"""
        entity = None
        timeframe = None

        for entity_type, patterns in self.pricing_patterns.items():
            if any(pattern in question for pattern in patterns):
                entity = entity_type
                break

        # Detect timeframe
        if 'month' in question or 'monthly' in question:
            timeframe = 'monthly'
        elif 'day' in question or 'daily' in question:
            timeframe = 'daily'
        elif 'hour' in question or 'hourly' in question:
            timeframe = 'hourly'

        return UserIntent(
            type=QuestionType.PRICING,
            is_specific=entity is not None,
            entity=entity,
            timeframe=timeframe
        )

    def _parse_contact_intent(self, question: str) -> UserIntent:
        """Parse contact-related questions"""
        entity = None

        for entity_type, patterns in self.contact_patterns.items():
            if any(pattern in question for pattern in patterns):
                entity = entity_type
                break

        return UserIntent(
            type=QuestionType.CONTACT,
            is_specific=entity is not None,
            entity=entity
        )

    def _parse_location_intent(self, question: str) -> UserIntent:
        """Parse location-related questions"""
        entity = None

        for location, patterns in self.location_patterns.items():
            if any(pattern in question for pattern in patterns):
                entity = location
                break

        return UserIntent(
            type=QuestionType.LOCATION,
            is_specific=entity is not None,
            entity=entity
        )

    def _parse_facility_intent(self, question: str) -> UserIntent:
        """Parse facility-related questions"""
        entity = None

        if 'parking' in question:
            entity = 'parking'
        elif 'wifi' in question or 'internet' in question:
            entity = 'internet'
        elif 'meeting' in question:
            entity = 'meeting_room'
        elif '24/7' in question or '24 hour' in question:
            entity = 'access_hours'

        return UserIntent(
            type=QuestionType.FACILITY,
            is_specific=entity is not None,
            entity=entity
        )


class BizzHubKnowledgeBase:
    """Structured knowledge base for BizzHub"""

    def __init__(self):
        self.data = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict:
        """Load structured knowledge about BizzHub"""
        return {
            'pricing': {
                'co-working': {
                    'description': 'Hot desk in shared workspace',
                    'monthly': '₹8,000 - ₹12,000',
                    'daily': '₹800 - ₹1,200',
                    'includes': ['Workspace access', 'High-speed WiFi', 'Tea/Coffee', 'Community events',
                                 'Basic printing']
                },
                'dedicated_desk': {
                    'description': 'Personal dedicated desk',
                    'monthly': '₹10,000 - ₹15,000',
                    'includes': ['Personal desk', '24/7 access', 'Lockable storage', 'Meeting room credits',
                                 'Priority support']
                },
                'private_cabin_2p': {
                    'description': 'Private office for 2 people',
                    'monthly': '₹25,000 - ₹30,000',
                    'includes': ['Private locked room', '2 ergonomic chairs', 'Custom branding',
                                 '2 meeting room hours/day']
                },
                'private_cabin_4p': {
                    'description': 'Private office for 4 people',
                    'monthly': '₹35,000 - ₹40,000',
                    'includes': ['Private locked room', '4 ergonomic chairs', 'Custom layout',
                                 '4 meeting room hours/day']
                },
                'day_pass': {
                    'description': 'Daily workspace access',
                    'daily': '₹800 - ₹1,200',
                    'includes': ['Basic workspace', 'WiFi', 'Tea/Coffee', 'Common areas']
                },
                'virtual_office': {
                    'description': 'Business address & mail services',
                    'monthly': '₹2,000 - ₹5,000',
                    'includes': ['Business address', 'Mail handling', 'Meeting room discount', 'Call answering']
                },
                'parking': {
                    'description': 'Dedicated parking spot',
                    'monthly': '₹800 - ₹2,000',
                    'variations': {
                        'koramangala': '₹1,000/month',
                        'whitefield': '₹1,500/month',
                        'electronic_city': '₹800/month',
                        'indiranagar': '₹1,200/month',
                        'mg_road': '₹2,000/month'
                    }
                },
                'meeting_room': {
                    'description': 'Meeting/conference room',
                    'hourly': '₹500 - ₹1,500',
                    'variations': {
                        '4_seats': '₹500/hour',
                        '8_seats': '₹800/hour',
                        '12_seats': '₹1,200/hour',
                        'board_room': '₹1,500/hour'
                    }
                }
            },

            'contact': {
                'general': {
                    'phone': '080-4111-1000',
                    'email': 'info@bizzhub.com',
                    'hours': '9 AM - 7 PM',
                    'website': 'https://www.bizzhubworkspaces.com'
                },
                'sales': {
                    'phone': '080-4111-2000',
                    'email': 'sales@bizzhub.com',
                    'person': 'Priya Patel',
                    'hours': '9 AM - 8 PM',
                    'whatsapp': '+91-9876543210'
                },
                'support': {
                    'phone': '080-4111-3000',
                    'email': 'support@bizzhub.com',
                    'hours': '24/7',
                    'emergency': '+91-9000000000'
                },
                'centers': {
                    'koramangala': {'phone': '080-4111-2222', 'manager': 'Rajesh'},
                    'whitefield': {'phone': '080-4111-3333', 'manager': 'Meera'},
                    'electronic_city': {'phone': '080-4111-4444', 'manager': 'Arjun'},
                    'indiranagar': {'phone': '080-4111-5555', 'manager': 'Sanjay'},
                    'mg_road': {'phone': '080-4111-6666', 'manager': 'Priya'}
                }
            },

            'locations': {
                'koramangala': '3rd Block, 80ft Road, Koramangala',
                'whitefield': 'ITPL Main Road, Whitefield',
                'electronic_city': 'Phase 1, Near Infosys, Electronic City',
                'indiranagar': '100ft Road, Indiranagar',
                'mg_road': 'Brigade Road Cross, MG Road'
            },

            'facilities': {
                'internet': {
                    'description': 'High-speed dedicated fiber',
                    'speed': '100 Mbps',
                    'included': True
                },
                'parking': {
                    'description': 'Secure parking facilities',
                    'availability': 'All centers',
                    'cost': '₹800 - ₹2,000/month'
                },
                'meeting_rooms': {
                    'description': 'Fully equipped meeting spaces',
                    'sizes': ['4-seater', '8-seater', '12-seater', 'Board room'],
                    'cost': '₹500 - ₹1,500/hour'
                },
                'access_hours': {
                    'description': 'Center access hours',
                    'co_working': '8 AM - 10 PM',
                    'dedicated_desk': '24/7',
                    'private_office': '24/7'
                },
                'additional': [
                    'Pantry with tea/coffee',
                    'Printing & scanning (100 pages free)',
                    'Mail handling services',
                    'Reception support',
                    'Community events',
                    'IT support (basic included)'
                ]
            }
        }

    def get_pricing(self, entity: str, timeframe: str = None) -> Dict:
        """Get pricing information"""
        if entity in self.data['pricing']:
            item = self.data['pricing'][entity].copy()
            if timeframe and timeframe in item:
                # Filter for specific timeframe
                filtered = {
                    'description': item['description'],
                    timeframe: item[timeframe],
                    'includes': item.get('includes', [])
                }
                if 'variations' in item:
                    filtered['variations'] = item['variations']
                return filtered
            return item
        return {}

    def get_contact(self, entity: str = 'general') -> Dict:
        """Get contact information"""
        if entity in self.data['contact']:
            return self.data['contact'][entity]
        return self.data['contact']['general']

    def get_location(self, center: str = None) -> Dict:
        """Get location information"""
        if center and center in self.data['locations']:
            return {
                center: {
                    'address': self.data['locations'][center],
                    'contact': self.data['contact']['centers'][center]
                }
            }
        return self.data['locations']

    def get_facility(self, facility: str = None) -> Dict:
        """Get facility information"""
        if facility and facility in self.data['facilities']:
            return self.data['facilities'][facility]
        return self.data['facilities']


class ResponseGenerator:
    """Generate professional, conversational responses"""

    def __init__(self, knowledge_base: BizzHubKnowledgeBase):
        self.kb = knowledge_base

    def generate_response(self, intent: UserIntent, original_question: str) -> ChatResponse:
        """Generate response based on user intent"""

        if intent.type == QuestionType.PRICING:
            return self._generate_pricing_response(intent, original_question)
        elif intent.type == QuestionType.CONTACT:
            return self._generate_contact_response(intent, original_question)
        elif intent.type == QuestionType.LOCATION:
            return self._generate_location_response(intent, original_question)
        elif intent.type == QuestionType.FACILITY:
            return self._generate_facility_response(intent, original_question)
        else:
            return self._generate_general_response(original_question)

    def _generate_pricing_response(self, intent: UserIntent, question: str) -> ChatResponse:
        """Generate pricing response"""

        if not intent.is_specific:
            # User asked general pricing
            return ChatResponse(
                answer=self._format_general_pricing(),
                confidence=0.9,
                follow_up_questions=[
                    "Are you looking for co-working or private office?",
                    "How many people are in your team?",
                    "Do you need daily or monthly plans?"
                ],
                source="knowledge_base"
            )

        # Specific pricing request
        entity = intent.entity
        timeframe = intent.timeframe or 'monthly'

        pricing_info = self.kb.get_pricing(entity, timeframe)

        if not pricing_info:
            return ChatResponse(
                answer="I understand you're asking about pricing. Could you specify if you're interested in co-working spaces, private offices, or other services?",
                confidence=0.6,
                follow_up_questions=self._get_pricing_follow_ups(),
                source="knowledge_base"
            )

        # Format the specific response
        answer = self._format_specific_pricing(entity, pricing_info, timeframe)

        return ChatResponse(
            answer=answer,
            confidence=0.95,
            follow_up_questions=self._get_pricing_follow_ups(entity),
            source="knowledge_base"
        )

    def _format_general_pricing(self) -> str:
        """Format general pricing overview"""
        return """💼 **Pricing Overview:**

**Co-Working Spaces:**
• Hot Desk: ₹8,000 - ₹12,000/month
• Dedicated Desk: ₹10,000 - ₹15,000/month
• Day Pass: ₹800 - ₹1,200/day

**Private Offices:**
• 2-person cabin: ₹25,000 - ₹30,000/month
• 4-person cabin: ₹35,000 - ₹40,000/month
• Team suites (6-10p): ₹60,000 - ₹90,000/month

**Additional Services:**
• Parking: ₹800 - ₹2,000/month
• Meeting Rooms: ₹500 - ₹1,500/hour
• Virtual Office: ₹2,000 - ₹5,000/month

*Note: All prices exclude GST. Exact rates depend on location and contract terms.*

📞 For a personalized quote, contact our sales team at **080-4111-2000** or email **sales@bizzhub.com**."""

    def _format_specific_pricing(self, entity: str, info: Dict, timeframe: str) -> str:
        """Format specific pricing information"""

        if entity == 'co-working':
            price = info.get('monthly', info.get('daily', '₹8,000 - ₹12,000'))
            timeframe_display = '/month' if timeframe == 'monthly' else '/day'

            return f"""💺 **Co-Working Space Pricing:**

• **Price:** {price}{timeframe_display}
• **Includes:** {', '.join(info.get('includes', ['Workspace access', 'WiFi', 'Basic amenities']))}

💡 *Perfect for freelancers, remote workers, and small teams.*
📞 **Get exact quote:** Call 080-4111-2000 or visit our website."""

        elif entity == 'private_office':
            price = info.get('monthly', '₹25,000 - ₹40,000')

            return f"""🚪 **Private Office Pricing:**

• **Price:** {price}/month
• **Includes:** {', '.join(info.get('includes', ['Private locked room', 'Ergonomic chairs', 'Custom layout']))}

💡 *Ideal for growing teams needing privacy and branding.*
📞 **Schedule a tour:** Call 080-4111-2000"""

        elif entity == 'parking':
            price = info.get('monthly', '₹800 - ₹2,000')

            return f"""🚗 **Parking Information:**

• **Monthly parking:** {price}
• **Availability:** All centers
• **Security:** CCTV monitored, 24/7

📍 **Center-specific rates:**
- Koramangala: ₹1,000/month
- Whitefield: ₹1,500/month
- Electronic City: ₹800/month

📞 **Confirm availability:** Call your nearest center."""

        # Default formatting
        return f"**{info.get('description', 'Service')}:** {info.get(timeframe, 'Contact for pricing')}"

    def _get_pricing_follow_ups(self, entity: str = None) -> List[str]:
        """Get relevant follow-up questions"""
        if entity == 'co-working':
            return ["Do you need 24/7 access?", "How many meeting room hours do you need?",
                    "Would you like to see our available centers?"]
        elif entity == 'private_office':
            return ["How many people in your team?", "Do you need custom branding?", "Would you like a virtual tour?"]
        else:
            return ["What's your team size?", "Which location are you interested in?",
                    "Do you need parking facilities?"]

    def _generate_contact_response(self, intent: UserIntent, question: str) -> ChatResponse:
        """Generate contact response"""

        if intent.entity == 'sales' or 'visit' in question.lower() or 'tour' in question.lower():
            contact = self.kb.get_contact('sales')

            answer = f"""📅 **Schedule a Site Visit:**

• **Contact:** {contact['person']} (Sales Manager)
• **Phone:** {contact['phone']}
• **Email:** {contact['email']}
• **WhatsApp:** {contact['whatsapp']}
• **Hours:** {contact['hours']}

📍 **Available at all centers:**
- Koramangala: 080-4111-2222
- Whitefield: 080-4111-3333
- Electronic City: 080-4111-4444

🌐 **Book online:** {self.kb.get_contact('general')['website']}/book-tour"""

            return ChatResponse(
                answer=answer,
                confidence=0.95,
                follow_up_questions=["Which center would you like to visit?", "What time works for you?",
                                     "How many people in your team?"],
                source="knowledge_base"
            )

        else:
            contact = self.kb.get_contact(intent.entity or 'general')

            answer = f"""📞 **Contact BizzHub Workspaces:**

**General Enquiries:**
• Phone: {contact['phone']}
• Email: {contact['email']}
• Hours: {contact['hours']}

**Website:** {self.kb.get_contact('general')['website']}

**Center Contacts:**
- Koramangala: 080-4111-2222
- Whitefield: 080-4111-3333  
- Electronic City: 080-4111-4444
- Indiranagar: 080-4111-5555
- MG Road: 080-4111-6666

**24/7 Support:** 080-4111-3000"""

            return ChatResponse(
                answer=answer,
                confidence=0.9,
                follow_up_questions=["Are you looking for sales, support, or general info?",
                                     "Which center are you interested in?", "Can I help with anything specific?"],
                source="knowledge_base"
            )

    def _generate_location_response(self, intent: UserIntent, question: str) -> ChatResponse:
        """Generate location response"""

        if intent.entity:
            # Specific location
            location_info = self.kb.get_location(intent.entity)
            center = intent.entity

            answer = f"""📍 **BizzHub {center.title()} Center:**

**Address:** {self.kb.data['locations'][center]}
**Contact:** {self.kb.data['contact']['centers'][center]['phone']}
**Manager:** {self.kb.data['contact']['centers'][center]['manager']}

**Features:**
- High-speed WiFi
- Meeting rooms
- Parking available
- 24/7 access (for members)
- Pantry facilities

🚗 **Get directions:** {self.kb.get_contact('general')['website']}/locations/{center}"""

            return ChatResponse(
                answer=answer,
                confidence=0.95,
                follow_up_questions=["Would you like to book a tour?", "Do you need parking information?",
                                     "What are your working hours?"],
                source="knowledge_base"
            )

        else:
            # All locations
            locations = self.kb.get_location()

            answer = "📍 **Our Bangalore Centers:**\n\n"
            for center, address in locations.items():
                contact = self.kb.data['contact']['centers'][center]
                answer += f"• **{center.title()}:** {address}\n   📞 {contact['phone']} (Manager: {contact['manager']})\n\n"

            answer += f"🌐 **View all centers:** {self.kb.get_contact('general')['website']}/locations"

            return ChatResponse(
                answer=answer,
                confidence=0.9,
                follow_up_questions=["Which center are you closest to?",
                                     "Would you like directions to a specific center?",
                                     "Do you need center-specific pricing?"],
                source="knowledge_base"
            )

    def _generate_facility_response(self, intent: UserIntent, question: str) -> ChatResponse:
        """Generate facility response"""

        if intent.entity == 'parking':
            pricing = self.kb.get_pricing('parking')

            answer = f"""🚗 **Parking Facilities:**

**Availability:** All centers
**Cost:** {pricing.get('monthly', '₹800 - ₹2,000')}/month

**Center-Specific Rates:**
{pricing.get('description', 'Secure parking available')}

**Features:**
• CCTV monitored 24/7
• Dedicated slots for members
• Visitor parking available
• EV charging (Whitefield & Electronic City)

📞 **Reserve parking:** Contact your nearest center"""

            return ChatResponse(
                answer=answer,
                confidence=0.95,
                follow_up_questions=["Which center are you at?", "Do you need monthly or visitor parking?",
                                     "Do you have an electric vehicle?"],
                source="knowledge_base"
            )

        elif intent.entity == 'internet':
            facility = self.kb.get_facility('internet')

            answer = f"""🌐 **Internet Services:**

**Speed:** {facility['speed']} dedicated fiber
**Availability:** Included in all plans
**Reliability:** 99.9% uptime guarantee

**Features:**
• Enterprise-grade security
• Separate guest network
• IT support available
• Backup connection

💡 *Perfect for video calls, large uploads, and remote teams.*"""

            return ChatResponse(
                answer=answer,
                confidence=0.95,
                follow_up_questions=["Do you need dedicated bandwidth?", "How many devices will connect?",
                                     "Do you require VPN setup?"],
                source="knowledge_base"
            )

        else:
            facilities = self.kb.get_facility()

            answer = """🛠️ **Our Facilities & Amenities:**

**Core Services:**
• High-speed internet (100 Mbps, included)
• Meeting rooms (book by hour/day)
• 24/7 access for members
• Secure parking (additional cost)

**Additional Amenities:**
• Pantry with tea/coffee
• Printing & scanning
• Mail handling
• Reception support
• Community events
• Basic IT support

**Premium Services:**
• Dedicated internet lines
• Premium IT support
• Custom branding
• Event space rental

📞 **Learn more:** 080-4111-1000"""

            return ChatResponse(
                answer=answer,
                confidence=0.9,
                follow_up_questions=["Which facility are you most interested in?", "Do you need specific equipment?",
                                     "What's your team size?"],
                source="knowledge_base"
            )

    def _generate_general_response(self, question: str) -> ChatResponse:
        """Generate response for general questions"""

        answer = """🏢 **Welcome to BizzHub Workspaces!**

I can help you with:
• **Pricing & Plans** - Co-working, private offices, day passes
• **Locations** - Our 5 centers across Bangalore  
• **Facilities** - Internet, parking, meeting rooms
• **Contact Information** - Phone, email, site visits

What would you like to know about?"""

        return ChatResponse(
            answer=answer,
            confidence=0.7,
            follow_up_questions=[
                "What type of workspace do you need?",
                "How many people are in your team?",
                "Which area of Bangalore are you in?"
            ],
            source="general_knowledge"
        )


class BizzHubChatbot:
    """Professional BizzHub Customer Service Chatbot"""

    def __init__(self):
        self.intent_parser = IntentParser()
        self.knowledge_base = BizzHubKnowledgeBase()
        self.response_generator = ResponseGenerator(self.knowledge_base)
        self.conversation_history = []

        print("🤖 BizzHub Chatbot Initialized")
        print("=" * 50)
        print("I can help with: Pricing • Locations • Facilities • Contact Info")
        print("=" * 50)

    def process_message(self, user_message: str) -> str:
        """Process user message and return response"""

        # Store in history
        self.conversation_history.append({
            'user': user_message,
            'timestamp': self._get_timestamp()
        })

        # Parse user intent
        intent = self.intent_parser.parse(user_message)

        # Generate response
        response = self.response_generator.generate_response(
            intent, user_message)

        # Store response
        self.conversation_history[-1]['response'] = response.answer

        # Format final output
        return self._format_output(response)

    def _format_output(self, response: ChatResponse) -> str:
        """Format the chatbot output professionally"""

        output = f"{response.answer}\n\n"

        return output

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


def run_chatbot_demo():
    """Run interactive chatbot demo"""

    print("\n" + "=" * 60)
    print("🏢 BIZZHUB WORKSAPCES - PROFESSIONAL CHATBOT")
    print("=" * 60)
    print("Type 'quit' to exit | Type 'help' for assistance")
    print("=" * 60)

    # Initialize chatbot
    chatbot = BizzHubChatbot()

    # Test scenarios
    test_cases = [
        "What's the per seat cost?",
        "Do you have parking at Whitefield?",
        "Whom can I contact for a site visit?",
        "Where is your Electronic City center?",
        "What facilities do you offer?",
        "How much for a private office for 4 people?",
        "What's your phone number?",
        "Do you have meeting rooms?"
    ]

    print("\n🧪 **Example Questions:**")
    for i, question in enumerate(test_cases, 1):
        print(f"{i}. {question}")


def quick_test():
    """Quick test of the chatbot"""

    chatbot = BizzHubChatbot()

    test_questions = [
        "What's the per seat cost?",
        "Do you have parking at Whitefield?",
        "Whom can I contact for enquiry or site visit?",
        "How much for a private cabin for 2 people?",
        "What's your email address?",
        "Where is your MG Road center?"
    ]

    print("🤖 Testing Professional Chatbot:")
    print("=" * 60)

    for question in test_questions:
        print(f"\n👤 Question: {question}")
        response = chatbot.process_message(question)
        print(f"🤖 Response:\n{response}")
        print("-" * 60)


if __name__ == "__main__":
    print("Choose mode:")
    print("1. Quick test (sample questions)")
    print("2. Interactive chatbot")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == '1':
        quick_test()
    elif choice == '2':
        run_chatbot_demo()
    else:
        print("Exiting.")
