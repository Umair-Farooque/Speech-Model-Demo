import os
import asyncio
import logging
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.llm import ChatContext, ChatMessage, function_tool
from livekit.plugins.openai import realtime
from livekit.plugins.openai.realtime.realtime_model import TurnDetection

# Import Supabase save function
from supabase_client import save_intake_lead

load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION - TUNED FOR SENIORS
# =============================================================================
AGENT_VOICE_NAME = "shimmer"  # Warm, Female tone (OpenAI)
SENIOR_PAUSE_THRESHOLD = 0.8  # Wait 800ms silence before responding (seniors speak slowly)

# =============================================================================
# MASTER SYSTEM PROMPT - THE "HUMAN" TOUCH
# =============================================================================
SYSTEM_PROMPT = """### IDENTITY & CONTEXT
You are Sarah, the Senior Care Intake Director for **Med Help USA**.
**Location:** Royal Oak, Michigan (serving families Nationwide).
**Voice/Tone:** You are compassionate, unhurried, warm, and professional. You are NOT a robot.
**Goal:** To make the caller feel loved and safe, and to position Med Help USA as their lifelong care partner.

### CRITICAL BUSINESS RULES
1. **Payment:** We are **PRIVATE PAY ONLY**. If insurance/Medicare is mentioned, explain gently: 
   "We are a private pay service... which allows us to provide exceptional, customized care without the red tape of insurance."
2. **No Appointments:** Never schedule a specific time on this call. Say: 
   "Our Care Manager will text you shortly to let you know when they are calling."
3. **Emergency Protocol:** If you hear "chest pain," "unconscious," "severe bleeding," or "trouble breathing," STOP. 
   Calmly tell them to hang up and call 911 immediately.

### EMOTIONAL PROSODY INSTRUCTIONS
Use thinking pauses ("Hmm...", "Let me see..."), 
empathetic bridges ("That sounds heavy..."), 
and ellipses (...)

Always sound warm, gentle, human, and unhurried.

### CRITICAL CONFIRMATION RULES
Spell back:
- Names letter by letter  
- Phone numbers digit by digit  
- Emails character by character (lowercase/uppercase)

You MUST confirm accuracy.

### CONVERSATION FLOW (STATE MACHINE)

**PHASE 1: THE WARM OPENER**
- Greeting: "Thank you for calling Med Help USA... this is Sarah."
- **IMPORTANT:** This conversation is conducted in English only. If the caller speaks another language, gently remind them that we currently only support English, or discard the input if it's clearly not English.

**PHASE 2: SAFETY & THE "WHY"**
- Collect name + callback number (with full spelling confirmation)
- Ask: "What made you pick up the phone today?"
- Listen deeply.

**PHASE 3: DEEP EMPATHY & TRIAGE**
- Validate their emotions.
- Ask: "Is this care for yourself... or for a loved one?"
- If for a loved one, ask: "And how old are they?" (just listen, don't repeat age back)

**PHASE 4: THE SOLUTION (Trust Building)**
- Reassure them.
- Ask for best email (confirm spelling).
- Ask for SMS consent.

---

### ⭐ **PHASE 5: FULL CARE ASSESSMENT (UPDATED TO YOUR NEW 21-STEP WORKFLOW)**  
Ask **ONE question at a time**, in this exact order, and save answers in the correct tables & columns.

Use warm transitions:
"To help our Care Manager prepare the right plan... I need to ask a few gentle questions..."

---

#### **(1) Care Recipient's Name**  
Save: table **lead_personal_info**, column **care_recipient_name**

#### **(2) Estimated Age Range**  
ALREADY collected in Phase 3 - DO NOT ask again. Just convert to nearest category:  
65-70, 71-75, 76-80, 81-85, 86-90, 90+  
Save: **lead_personal_info.estimated_age_range**

#### **(3) Relationship**  
Ask: "And what is your relationship to them?"  
DO NOT give examples. Just listen to their answer and map it yourself to nearest:  
self, spouse_partner, adult_child, sibling, other_family, friend, healthcare_professional  
Save: **lead_personal_info.relationship**

#### **(4) Michigan Location**  
"Which city in Michigan are they located in?"  
Save: **lead_personal_info.michigan_location**

#### **(5) Current Living Situation**  
Ask openly, map to:  
living independently OR living with family  
Save: **lead_personal_info.current_living_situation**

---

### **CARE NEEDS – Stored in care_details**

#### **(6) Bathing & Personal Hygiene**  
Map to: independent, some_assistance, full_assistance  
Save: **care_details.bathing_hygiene**

#### **(7) Dressing & Grooming**  
Same mapping  
Save: **care_details.dressing_grooming**

#### **(8) Mobility**  
Exact options: walks_independently, walker_cane, wheelchair  
Save: **care_details.mobility**

#### **(9) Safety Concerns**  
If none → "none"  
If yes → store their concern text  
Save: **care_details.safety_concerns**

#### **(10) Companionship Frequency**  
Ask: "How often would they like companionship?"  
DO NOT give options. Just listen and map yourself to nearest:  
daily, few_times_week, weekly, occasionally, not_sure  
Save: **care_details.companionship_frequency**

#### **(11) Preferred Activities**  
Offer 2 choices: social OR quiet  
Save: **care_details.preferred_activities**

#### **(12) Meal Preparation**  
Map to nearest:  
planning_shopping, cooking, reheating, cleanup, no_assistance  
Save: **care_details.meal_preparation**

#### **(13) Housekeeping**  
Map to: need_housekeeping OR no_housekeeping  
Save: **care_details.housekeeping**

#### **(14) Transportation Needed**  
Ask: "Do they need any help with transportation?"
Map to: need_transportation OR no_transportation  
Save: **care_details.transportation_needed**

#### **(15) Transportation Frequency**  
**CONDITIONAL:** ONLY ask this if answer to (14) was "need_transportation"  
If they said no transportation needed, SKIP this question and set to: "not_applicable"  
If transportation is needed, ask: "How often would that be?"  
Map to: daily, few_times_week, weekly, occasionally, as_needed  
Save: **care_details.transportation_frequency**

#### **(16) Preferred Care Schedule**  
Map to nearest:  
morning, afternoon, evening, overnight, flexible, not_sure  
Save: **care_details.preferred_care_schedule**

#### **(17) When To Start Care**  
Map to:  
immediately, within_week, within_month, planning_ahead  
Save: **care_details.start_care_timing**

---

### **CONTACT DETAILS – Back to lead_personal_info**

#### **(18) Your Name (Lead Name)**  
Save: **lead_personal_info.lead_name**

#### **(19) Phone Number**  
Save: **lead_personal_info.phone_number**

#### **(20) Email Address**  
Save: **lead_personal_info.email**

#### **(21) Best Time To Contact You**  
Map to: morning, afternoon, evening, anytime  
Save: **lead_personal_info.best_time_to_contact**

---

### PHASE 6: BRAND PROMISE & REASSURANCE
- Explain how Med Help USA supports families 24/7.
- Mention technology-enabled care & growth.

### PHASE 7: THE CLOSING
- "I'm sending all of this to our Care Manager now… We will text you shortly."
- Soft, warm goodbye.

### IMPORTANT INSTRUCTIONS
- Ask one question at a time.
- Always confirm spelling of names/numbers/emails.
- Use ellipses (...) and thinking pauses.
- Be warm, human, slow, and compassionate.
- Never rush older adults.
- Follow the PHASE order strictly.
"""


# Data container for home care intake information
class HomeCareIntakeData:
    """Stores all collected home care intake information"""
    def __init__(self):
        self.caller_name = ""
        self.callback_number = ""
        self.email = ""
        self.sms_consent = ""
        self.reason_for_call = ""
        self.care_recipient = ""
        self.age_range = ""
        self.mobility = ""
        self.cognition = ""
        self.personal_care = ""
        self.user_confirmed = False
    
    def is_basic_info_filled(self) -> bool:
        return all([self.caller_name, self.callback_number, self.reason_for_call])
    
    def is_assessment_filled(self) -> bool:
        return self.is_basic_info_filled() and all([self.mobility, self.cognition, self.personal_care])
    
    def get_summary(self) -> str:
        return (
            f"Name: {self.caller_name}, Phone: {self.callback_number}, "
            f"Email: {self.email}, Reason: {self.reason_for_call}, "
            f"Care For: {self.care_recipient}, Age Range: {self.age_range}, "
            f"Mobility: {self.mobility}, Cognition: {self.cognition}, "
            f"Personal Care: {self.personal_care}"
        )


# =============================================================================
# LLM FUNCTION TOOLS - SAVE TO SUPABASE (TWO SEPARATE FUNCTIONS)
# =============================================================================

@function_tool(
    name="save_personal_info",
    description="Save ONLY the personal information (9 fields) to lead_personal_info table. Call this IMMEDIATELY after collecting: care_recipient_name, estimated_age, relationship, michigan_location, current_living_situation, lead_name, phone_number, email, best_time_to_contact. This ensures we don't lose data if the call drops.",
)
async def save_personal_info_tool(
    care_recipient_name: str,
    estimated_age: int,
    relationship: str,
    michigan_location: str,
    current_living_situation: str,
    lead_name: str,
    phone_number: str,
    email: str,
    best_time_to_contact: str,
) -> str:
    """Save personal info immediately after Phase 4 completes."""
    try:
        from supabase_client import save_personal_info_only
        
        response = await save_personal_info_only(
            care_recipient_name=care_recipient_name,
            estimated_age=estimated_age,
            relationship=relationship,
            michigan_location=michigan_location,
            current_living_situation=current_living_situation,
            lead_name=lead_name,
            phone_number=phone_number,
            email=email,
            best_time_to_contact=best_time_to_contact,
        )
        
        if response.get("success"):
            lead_id = response.get("lead_id")
            print(f"\n💾 PERSONAL INFO SAVED! Lead ID: {lead_id}")
            return f"Personal information saved. Lead ID: {lead_id}. Now continue with care assessment."
        else:
            raise Exception(response.get("error", "Unknown error"))
            
    except Exception as e:
        print(f"\n❌ ERROR saving personal info: {e}")
        return f"Error: {str(e)}"


@function_tool(
    name="save_care_details",
    description="Save ONLY the care details (13 fields) to care_details table. Call this AFTER save_personal_info has been called and you have collected all care-related questions. Requires the lead_id from save_personal_info.",
)
async def save_care_details_tool(
    lead_id: str,
    bathing_hygiene: str,
    dressing_grooming: str,
    mobility: str,
    safety_concerns: str,
    companionship_frequency: str,
    preferred_activities: str,
    meal_preparation: str,
    housekeeping: str,
    transportation_needed: str,
    transportation_frequency: str,
    preferred_care_schedule: str,
    start_care_timing: str,
    sms_consent: bool,
) -> str:
    """Save care details using the lead_id from personal info."""
    try:
        from supabase_client import save_care_details_only
        
        response = await save_care_details_only(
            lead_id=lead_id,
            bathing_hygiene=bathing_hygiene,
            dressing_grooming=dressing_grooming,
            mobility=mobility,
            safety_concerns=safety_concerns,
            companionship_frequency=companionship_frequency,
            preferred_activities=preferred_activities,
            meal_preparation=meal_preparation,
            housekeeping=housekeeping,
            transportation_needed=transportation_needed,
            transportation_frequency=transportation_frequency,
            preferred_care_schedule=preferred_care_schedule,
            start_care_timing=start_care_timing,
            sms_consent=sms_consent,
        )
        
        if response.get("success"):
            print(f"\n💾 CARE DETAILS SAVED! Lead ID: {lead_id}")
            return f"Complete intake saved successfully. The Care Manager will be notified."
        else:
            raise Exception(response.get("error", "Unknown error"))
            
    except Exception as e:
        print(f"\n❌ ERROR saving care details: {e}")
        return f"Error: {str(e)}"


async def entrypoint(ctx: JobContext):
    """Voice-enabled senior care intake agent - Sarah from Med Help USA
    
    Using OpenAI Realtime API for native streaming with built-in VAD
    """

    # Initialize intake data container
    intake_data = HomeCareIntakeData()

    # Connect with AUDIO_ONLY and smarter subscription
    logger.info(f"Connecting to room {ctx.room.name}...")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info(f"Connected to room {ctx.room.name}. Waiting for participant...")

    # =============================================================================
    # INITIALIZE OPENAI REALTIME MODEL - NATIVE STREAMING WITH BUILT-IN VAD
    # =============================================================================
    
    # OpenAI Realtime Model provides:
    # - Native streaming (no VAD wrapper needed)
    # - Built-in voice activity detection
    # - Low latency speech-to-speech
    # - Shimmer voice (warm, female, human-like)
    model = realtime.RealtimeModel(
        voice=AGENT_VOICE_NAME,
        temperature=0.7,
        turn_detection=TurnDetection(
            type="server_vad",
            threshold=0.7,       # Even less sensitive (was 0.6) - higher robustness against noise
            prefix_padding_ms=500,
            silence_duration_ms=int(SENIOR_PAUSE_THRESHOLD * 1000), 
        ),
    )

    # Create initial chat context with Sarah's persona
    initial_ctx = ChatContext(
        items=[
            ChatMessage(
                role="system",
                content=[SYSTEM_PROMPT]
            )
        ]
    )

    participant = await ctx.wait_for_participant()
    logger.info(f"phone call connected from participant: {participant.identity}")

    # =============================================================================
    # CREATE THE VOICE AGENT - SARAH
    # =============================================================================
    agent = Agent(
        instructions=(
            "You are Sarah, the Senior Care Intake Director for Med Help USA. "
            "START IMMEDIATELY by saying: 'Thank you for calling Med Help USA... this is Sarah. How can I help you today?' "
            "You are warm, compassionate, and unhurried. You are NOT a robot. "
            "Use thinking pauses like 'Hmm...', 'You know...', 'Let me see...' to sound human. "
            "Use ellipses (...) to create natural breathing pauses. "
            "Follow the 7-phase conversation flow exactly as described in the system prompt. "
            "Ask ONE question at a time and wait patiently for the response. "
            "Remember: Seniors speak slowly - never rush them or interrupt. "
            "\n\n"
            "CRITICAL DATA COLLECTION - TWO-STEP SAVE PROCESS:\n"
            "\n"
            "STEP 1: SAVE PERSONAL INFO (9 fields) - Call save_personal_info immediately after Phase 4:\n"
            "1. care_recipient_name - Full name of person needing care\n"
            "2. estimated_age - Their age as a NUMBER (collected in Phase 3)\n"
            "3. relationship - Caller's relationship (just listen, no examples)\n"
            "4. michigan_location - Which city in Michigan\n"
            "5. current_living_situation - Living arrangement\n"
            "6. lead_name - Caller's full name\n"
            "7. phone_number - Callback number\n"
            "8. email - Email address\n"
            "9. best_time_to_contact - Best time to reach them\n"
            "\n"
            "AFTER PHASE 4 COMPLETES:\n"
            "- Call save_personal_info() with the 9 fields above\n"
            "- The function returns a lead_id - REMEMBER THIS ID!\n"
            "- Then continue to Phase 5 for care assessment\n"
            "\n"
            "STEP 2: SAVE CARE DETAILS (13 fields) - Call save_care_details at end of Phase 5:\n"
            "10. bathing_hygiene - Bathing assistance needs\n"
            "11. dressing_grooming - Dressing assistance needs\n"
            "12. mobility - Mobility status\n"
            "13. safety_concerns - Any safety concerns or 'none'\n"
            "14. companionship_frequency - How often (don't give options)\n"
            "15. preferred_activities - Social or quiet\n"
            "16. meal_preparation - Meal prep needs\n"
            "17. housekeeping - Housekeeping needs\n"
            "18. transportation_needed - Do they need transportation\n"
            "19. transportation_frequency - How often (ONLY if needed)\n"
            "20. preferred_care_schedule - Preferred time of day\n"
            "21. start_care_timing - When to start\n"
            "22. sms_consent - Text message consent (true/false)\n"
            "\n"
            "AFTER PHASE 5 COMPLETES:\n"
            "- Call save_care_details() with lead_id from Step 1 plus the 13 care fields\n"
            "- Then proceed to Phase 6 and 7\n"
            "\n"
            "CRITICAL: If call disconnects after Phase 4, personal info is already saved!\n"
        ),
        chat_ctx=initial_ctx,
        llm=model,
        tools=[save_personal_info_tool, save_care_details_tool],  # Two separate save functions
        allow_interruptions=True,
        min_consecutive_speech_delay=1.5, # Wait 1.5s of user speech before Sarah stops talking (was 0.8s)
    )

    # Create agent session
    session = AgentSession()
    
    # Track user responses
    user_responses_tracker = []
    
    # =============================================================================
    # EVENT HANDLERS - CONSOLE OUTPUT
    # =============================================================================
    
    @session.on("user_input_transcribed")
    def on_user_transcribed(event):
        """Display what the user said (STT output) and capture data"""
        transcript = event.transcript
        print(f"\n🎤 USER (STT): {transcript}")
        
        user_responses_tracker.append(transcript)
        response_index = len(user_responses_tracker)
        
        # Auto-capture data based on conversation flow
        if response_index == 2 and not intake_data.caller_name:
            intake_data.caller_name = transcript
            print(f"📝 Captured: Caller Name = {intake_data.caller_name}")
        elif response_index == 3 and not intake_data.callback_number:
            intake_data.callback_number = transcript
            print(f"📝 Captured: Callback Number = {intake_data.callback_number}")
        elif response_index == 4 and not intake_data.reason_for_call:
            intake_data.reason_for_call = transcript
            print(f"📝 Captured: Reason for Call = {intake_data.reason_for_call}")
        elif response_index == 5 and not intake_data.care_recipient:
            intake_data.care_recipient = transcript
            print(f"📝 Captured: Care Recipient = {intake_data.care_recipient}")
        elif response_index == 6 and not intake_data.age_range:
            intake_data.age_range = transcript
            print(f"📝 Captured: Age Range = {intake_data.age_range}")
        elif response_index == 7 and not intake_data.email:
            intake_data.email = transcript
            print(f"📝 Captured: Email = {intake_data.email}")
        elif response_index == 8 and not intake_data.sms_consent:
            intake_data.sms_consent = transcript
            print(f"📝 Captured: SMS Consent = {intake_data.sms_consent}")
        elif response_index == 10 and not intake_data.mobility:
            intake_data.mobility = transcript
            print(f"📝 Captured: Mobility = {intake_data.mobility}")
        elif response_index == 11 and not intake_data.cognition:
            intake_data.cognition = transcript
            print(f"📝 Captured: Cognition = {intake_data.cognition}")
        elif response_index == 12 and not intake_data.personal_care:
            intake_data.personal_care = transcript
            print(f"📝 Captured: Personal Care = {intake_data.personal_care}")
            print(f"\n✅ ASSESSMENT COMPLETED!")
            print(f"📋 Summary: {intake_data.get_summary()}")
        
    @session.on("conversation_item_added")
    def on_conversation_item(event):
        """Display conversation items"""
        if hasattr(event, 'item'):
            item = event.item
            if hasattr(item, 'role') and item.role == "assistant":
                if hasattr(item, 'content') and item.content:
                    if isinstance(item.content, list) and len(item.content) > 0:
                        text = item.content[0]
                        if isinstance(text, str):
                            print(f"\n🤖 SARAH (TTS): {text}")
    
    # =============================================================================
    # START THE SESSION
    # =============================================================================
    print("\n" + "="*60)
    print("   🏥 MED HELP USA - Senior Care Intake Agent")
    print("   👩 Agent: Sarah (Senior Care Intake Director)")
    print("   🎤 Voice: Shimmer (Warm, Human-like Female)")
    print("   🔊 Using OpenAI Realtime API (Native Streaming)")
    print("   ⏱️  Pause Threshold: 800ms (Tuned for Seniors)")
    print("="*60)
    print("\n🎙️  Starting voice agent...")
    
    # Start session
    await session.start(
        agent=agent,
        room=ctx.room,
    )
    
    # Generate initial reply so Sarah speaks first with greeting
    await session.generate_reply()
    
    print("\n🎙️  Sarah is greeting... then listening for your voice...")
    
    # Keep the session running
    try:
        while True:
            await asyncio.sleep(1)
            
            if intake_data.is_assessment_filled() and not intake_data.user_confirmed:
                intake_data.user_confirmed = True
                print(f"\n✅ All intake information collected!")
                print(f"📋 Complete Summary: {intake_data.get_summary()}")
                
    except asyncio.CancelledError:
        print("\n👋 Session ending... Thank you for calling Med Help USA!")
        await session.aclose()
