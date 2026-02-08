"""
Supabase Client Module for Med Help USA
========================================
Provides async function to save intake leads to two Supabase tables:
- lead_personal_info
- care_details (linked by same UUID)

Usage:
    from supabase_client import save_intake_lead
    
    result = await save_intake_lead(
        care_recipient_name="...",
        estimated_age=75,
        ...
    )
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# SUPABASE CLIENT (Singleton)
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Please set SUPABASE_URL and "
        "SUPABASE_SERVICE_ROLE_KEY in your .env file."
    )

# Create singleton client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# =============================================================================
# MAPPING HELPER FUNCTIONS
# =============================================================================

def map_age_to_range(age: int) -> str:
    """Map numeric age to age range category"""
    if age < 65:
        return "under_65"
    elif 65 <= age <= 70:
        return "65-70"
    elif 71 <= age <= 75:
        return "71-75"
    elif 76 <= age <= 80:
        return "76-80"
    elif 81 <= age <= 85:
        return "81-85"
    elif 86 <= age <= 90:
        return "86-90"
    else:
        return "90+"


def map_relationship(relationship_input: str) -> str:
    """Map free-form relationship input to nearest category"""
    rel = relationship_input.lower().strip()
    
    if "self" in rel or "me" in rel or "myself" in rel:
        return "self"
    elif "spouse" in rel or "husband" in rel or "wife" in rel or "partner" in rel:
        return "spouse_partner"
    elif "son" in rel or "daughter" in rel or "child" in rel:
        return "adult_child"
    elif "brother" in rel or "sister" in rel or "sibling" in rel:
        return "sibling"
    elif "friend" in rel:
        return "friend"
    elif "nurse" in rel or "doctor" in rel or "caregiver" in rel or "healthcare" in rel:
        return "healthcare_professional"
    else:
        return "other_family"


def map_living_situation(situation_input: str) -> str:
    """Map living situation to category"""
    sit = situation_input.lower().strip()
    
    if "alone" in sit or "independent" in sit or "by themselves" in sit or "own home" in sit:
        return "independent"
    else:
        return "living_with_family"


def map_assistance_level(input_text: str) -> str:
    """Map assistance descriptions to: independent, some_assistance, full_assistance"""
    text = input_text.lower().strip()
    
    if "no" in text or "independent" in text or "don't need" in text or "fine" in text:
        return "independent"
    elif "full" in text or "complete" in text or "total" in text or "all the time" in text:
        return "full_assistance"
    else:
        return "some_assistance"


def map_mobility(mobility_input: str) -> str:
    """Map mobility to: walks_independently, walker_cane, wheelchair"""
    mob = mobility_input.lower().strip()
    
    if "wheelchair" in mob or "chair" in mob:
        return "wheelchair"
    elif "walker" in mob or "cane" in mob or "assistance" in mob:
        return "walker_cane"
    else:
        return "walks_independently"


def map_companionship_frequency(freq_input: str) -> str:
    """Map to: daily, few_times_week, weekly, occasionally, not_sure"""
    freq = freq_input.lower().strip()
    
    if "every day" in freq or "daily" in freq or "all the time" in freq:
        return "daily"
    elif "few times" in freq or "2" in freq or "3" in freq or "several" in freq:
        return "few_times_week"
    elif "once a week" in freq or "weekly" in freq:
        return "weekly"
    elif "sometimes" in freq or "occasionally" in freq or "now and then" in freq:
        return "occasionally"
    else:
        return "not_sure"


def map_activities(activity_input: str) -> str:
    """Map to: social, quiet"""
    act = activity_input.lower().strip()
    
    if "quiet" in act or "reading" in act or "tv" in act or "alone" in act or "peaceful" in act:
        return "quiet"
    else:
        return "social"


def map_meal_preparation(meal_input: str) -> str:
    """Map to: planning_shopping, cooking, reheating, cleanup, no_assistance"""
    meal = meal_input.lower().strip()
    
    if "no" in meal or "independent" in meal or "don't need" in meal:
        return "no_assistance"
    elif "plan" in meal or "shop" in meal or "grocery" in meal:
        return "planning_shopping"
    elif "cook" in meal or "prepare" in meal or "make meals" in meal:
        return "cooking"
    elif "reheat" in meal or "warm up" in meal or "microwave" in meal:
        return "reheating"
    elif "clean" in meal or "dishes" in meal or "wash" in meal:
        return "cleanup"
    else:
        return "cooking"  # default


def map_yes_no_to_need(input_text: str, need_type: str) -> str:
    """Map yes/no responses to need_X or no_X format"""
    text = input_text.lower().strip()
    
    if "yes" in text or "need" in text or "help" in text or "assistance" in text:
        return f"need_{need_type}"
    else:
        return f"no_{need_type}"


def map_transportation_frequency(freq_input: str) -> str:
    """Map to: daily, few_times_week, weekly, occasionally, as_needed"""
    freq = freq_input.lower().strip()
    
    if "every day" in freq or "daily" in freq:
        return "daily"
    elif "few times" in freq or "2" in freq or "3" in freq:
        return "few_times_week"
    elif "once a week" in freq or "weekly" in freq:
        return "weekly"
    elif "sometimes" in freq or "occasionally" in freq:
        return "occasionally"
    else:
        return "as_needed"


def map_care_schedule(schedule_input: str) -> str:
    """Map to: morning, afternoon, evening, overnight, flexible, not_sure"""
    sched = schedule_input.lower().strip()
    
    if "morning" in sched or "am" in sched:
        return "morning"
    elif "afternoon" in sched or "pm" in sched or "lunch" in sched:
        return "afternoon"
    elif "evening" in sched or "night" in sched or "dinner" in sched:
        return "evening"
    elif "overnight" in sched or "24" in sched or "around the clock" in sched:
        return "overnight"
    elif "flexible" in sched or "any" in sched or "doesn't matter" in sched:
        return "flexible"
    else:
        return "not_sure"


def map_start_timing(timing_input: str) -> str:
    """Map to: immediately, within_week, within_month, planning_ahead"""
    timing = timing_input.lower().strip()
    
    if "now" in timing or "asap" in timing or "immediately" in timing or "right away" in timing:
        return "immediately"
    elif "week" in timing or "few days" in timing or "soon" in timing:
        return "within_week"
    elif "month" in timing or "couple weeks" in timing:
        return "within_month"
    else:
        return "planning_ahead"


def map_contact_time(time_input: str) -> str:
    """Map to: morning, afternoon, evening, anytime"""
    time = time_input.lower().strip()
    
    if "morning" in time or "am" in time:
        return "morning"
    elif "afternoon" in time or "pm" in time:
        return "afternoon"
    elif "evening" in time or "night" in time:
        return "evening"
    else:
        return "anytime"


# =============================================================================
# SAVE PERSONAL INFO ONLY (Table 1)
# =============================================================================

async def save_personal_info_only(
    care_recipient_name: str,
    estimated_age: int,
    relationship: str,
    michigan_location: str,
    current_living_situation: str,
    lead_name: str,
    phone_number: str,
    email: str,
    best_time_to_contact: str,
) -> dict:
    """
    Save ONLY personal info to lead_personal_info table.
    Returns the generated UUID for later use with care_details.
    """
    try:
        # Type validation
        if isinstance(estimated_age, str):
            try:
                estimated_age_int = int(estimated_age)
            except:
                estimated_age_int = 75
        else:
            estimated_age_int = int(estimated_age)
        
        personal_data = {
            "care_recipient_name": care_recipient_name,
            "estimated_age_range": map_age_to_range(estimated_age_int),
            "relationship": map_relationship(relationship),
            "michigan_location": michigan_location,
            "current_living_situation": map_living_situation(current_living_situation),
            "lead_name": lead_name,
            "phone_number": phone_number,
            "email": email,
            "best_time_to_contact": map_contact_time(best_time_to_contact),
        }
        
        print(f"\n💾 Inserting personal info only...")
        personal_response = supabase.table("lead_personal_info").insert(personal_data).execute()
        
        if not personal_response.data:
            raise Exception("Failed to insert personal info")
        
        lead_id = personal_response.data[0]["id"]
        print(f"✅ Personal info saved with ID: {lead_id}")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "personal_info": personal_response.data[0]
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# SAVE CARE DETAILS ONLY (Table 2)
# =============================================================================

async def save_care_details_only(
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
) -> dict:
    """
    Save ONLY care details to care_details table using provided lead_id.
    """
    try:
        # Type validation for sms_consent
        if isinstance(sms_consent, str):
            sms_consent_bool = sms_consent.lower() in ['true', 'yes', '1', 'ok', 'okay']
        else:
            sms_consent_bool = bool(sms_consent)
        
        care_data = {
            "id": lead_id,
            "bathing_hygiene": map_assistance_level(bathing_hygiene),
            "dressing_grooming": map_assistance_level(dressing_grooming),
            "mobility": map_mobility(mobility),
            "safety_concerns": "none" if "no" in safety_concerns.lower() else safety_concerns,
            "companionship_frequency": map_companionship_frequency(companionship_frequency),
            "preferred_activities": map_activities(preferred_activities),
            "meal_preparation": map_meal_preparation(meal_preparation),
            "housekeeping": map_yes_no_to_need(housekeeping, "housekeeping"),
            "transportation_needed": map_yes_no_to_need(transportation_needed, "transportation"),
            "transportation_frequency": map_transportation_frequency(transportation_frequency) if "need" in map_yes_no_to_need(transportation_needed, "transportation") else "not_applicable",
            "preferred_care_schedule": map_care_schedule(preferred_care_schedule),
            "start_care_timing": map_start_timing(start_care_timing),
            "sms_consent": sms_consent_bool,
        }
        
        print(f"💾 Inserting care details for lead ID: {lead_id}...")
        care_response = supabase.table("care_details").insert(care_data).execute()
        
        if not care_response.data:
            raise Exception("Failed to insert care details")
        
        print(f"✅ Care details saved with ID: {lead_id}")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "care_details": care_response.data[0]
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# SAVE COMPLETE INTAKE (TWO-TABLE INSERT) - LEGACY
# =============================================================================

async def save_intake_lead(
    # Personal Info (Table 1)
    care_recipient_name: str,
    estimated_age: int,
    relationship: str,
    michigan_location: str,
    current_living_situation: str,
    lead_name: str,
    phone_number: str,
    email: str,
    best_time_to_contact: str,
    # Care Details (Table 2)
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
) -> dict:
    """
    Save intake lead to TWO Supabase tables with shared UUID.
    
    Step 1: Insert into lead_personal_info → get UUID
    Step 2: Insert into care_details using same UUID
    
    All mapping is done automatically.
    """
    
    try:
        # =============================================================================
        # DEBUG: Print what was received
        # =============================================================================
        print(f"\n🔍 DEBUG - Received parameters:")
        print(f"   care_recipient_name: {care_recipient_name}")
        print(f"   estimated_age: {estimated_age} (type: {type(estimated_age)})")
        print(f"   relationship: {relationship}")
        print(f"   michigan_location: {michigan_location}")
        print(f"   current_living_situation: {current_living_situation}")
        print(f"   lead_name: {lead_name}")
        print(f"   phone_number: {phone_number}")
        print(f"   email: {email}")
        print(f"   best_time_to_contact: {best_time_to_contact}")
        print(f"   bathing_hygiene: {bathing_hygiene}")
        print(f"   dressing_grooming: {dressing_grooming}")
        print(f"   mobility: {mobility}")
        print(f"   safety_concerns: {safety_concerns}")
        print(f"   companionship_frequency: {companionship_frequency}")
        print(f"   preferred_activities: {preferred_activities}")
        print(f"   meal_preparation: {meal_preparation}")
        print(f"   housekeeping: {housekeeping}")
        print(f"   transportation_needed: {transportation_needed}")
        print(f"   transportation_frequency: {transportation_frequency}")
        print(f"   preferred_care_schedule: {preferred_care_schedule}")
        print(f"   start_care_timing: {start_care_timing}")
        print(f"   sms_consent: {sms_consent} (type: {type(sms_consent)})")
        
        # =============================================================================
        # TYPE VALIDATION & CONVERSION
        # =============================================================================
        
        # Ensure sms_consent is boolean
        if isinstance(sms_consent, str):
            sms_consent_bool = sms_consent.lower() in ['true', 'yes', '1', 'ok', 'okay']
            print(f"⚠️  WARNING: sms_consent was string '{sms_consent}', converted to {sms_consent_bool}")
        else:
            sms_consent_bool = bool(sms_consent)
        
        # Ensure estimated_age is integer
        if isinstance(estimated_age, str):
            try:
                estimated_age_int = int(estimated_age)
                print(f"⚠️  WARNING: estimated_age was string '{estimated_age}', converted to {estimated_age_int}")
            except:
                estimated_age_int = 75  # Default
                print(f"⚠️  WARNING: Could not convert age '{estimated_age}', using default 75")
        else:
            estimated_age_int = int(estimated_age)
        
        # =============================================================================
        # STEP 1: INSERT PERSONAL INFO (Table 1)
        # =============================================================================
        
        personal_data = {
            "care_recipient_name": care_recipient_name,
            "estimated_age_range": map_age_to_range(estimated_age_int),
            "relationship": map_relationship(relationship),
            "michigan_location": michigan_location,
            "current_living_situation": map_living_situation(current_living_situation),
            "lead_name": lead_name,
            "phone_number": phone_number,
            "email": email,
            "best_time_to_contact": map_contact_time(best_time_to_contact),
        }
        
        print(f"\n💾 Inserting into lead_personal_info...")
        personal_response = supabase.table("lead_personal_info").insert(personal_data).execute()
        
        if not personal_response.data:
            raise Exception("Failed to insert personal info")
        
        # Get the generated UUID
        lead_id = personal_response.data[0]["id"]
        print(f"✅ Personal info saved with ID: {lead_id}")
        
        # =============================================================================
        # STEP 2: INSERT CARE DETAILS (Table 2) - USE SAME UUID
        # =============================================================================
        
        care_data = {
            "id": lead_id,  # CRITICAL: Use same UUID from personal info
            "bathing_hygiene": map_assistance_level(bathing_hygiene),
            "dressing_grooming": map_assistance_level(dressing_grooming),
            "mobility": map_mobility(mobility),
            "safety_concerns": "none" if "no" in safety_concerns.lower() else safety_concerns,
            "companionship_frequency": map_companionship_frequency(companionship_frequency),
            "preferred_activities": map_activities(preferred_activities),
            "meal_preparation": map_meal_preparation(meal_preparation),
            "housekeeping": map_yes_no_to_need(housekeeping, "housekeeping"),
            "transportation_needed": map_yes_no_to_need(transportation_needed, "transportation"),
            "transportation_frequency": map_transportation_frequency(transportation_frequency) if "need" in map_yes_no_to_need(transportation_needed, "transportation") else "not_applicable",
            "preferred_care_schedule": map_care_schedule(preferred_care_schedule),
            "start_care_timing": map_start_timing(start_care_timing),
            "sms_consent": sms_consent_bool,
        }
        
        print(f"💾 Inserting into care_details...")
        care_response = supabase.table("care_details").insert(care_data).execute()
        
        if not care_response.data:
            raise Exception("Failed to insert care details")
        
        print(f"✅ Care details saved with ID: {lead_id}")
        
        # =============================================================================
        # SUCCESS
        # =============================================================================
        
        print(f"\n🎉 COMPLETE INTAKE SAVED!")
        print(f"   Lead: {lead_name}")
        print(f"   Care Recipient: {care_recipient_name}")
        print(f"   Phone: {phone_number}")
        print(f"   Shared UUID: {lead_id}")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "personal_info": personal_response.data[0],
            "care_details": care_response.data[0]
        }
        
    except Exception as e:
        print(f"\n❌ SUPABASE ERROR: {e}")
        return {
            "success": False,
            "error": str(e)
        }
