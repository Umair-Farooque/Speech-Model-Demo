import asyncio
import os
from dotenv import load_dotenv
from supabase_client import save_personal_info_only, save_care_details_only

async def test_insert():
    print("🚀 Starting Database Storage Test...")
    
    # 1. Test Personal Info
    print("\n📝 Testing Step 1: Personal Info...")
    personal_info = {
        "care_recipient_name": "Test Senior",
        "estimated_age": 75,
        "relationship": "adult_child",
        "michigan_location": "Royal Oak",
        "current_living_situation": "living independently",
        "lead_name": "Test Lead",
        "phone_number": "555-0123",
        "email": "test@example.com",
        "best_time_to_contact": "morning"
    }
    
    result1 = await save_personal_info_only(**personal_info)
    
    if not result1.get("success"):
        print(f"❌ Step 1 Failed: {result1.get('error')}")
        return
    
    lead_id = result1.get("lead_id")
    print(f"✅ Step 1 Success! Lead ID: {lead_id}")
    
    # 2. Test Care Details
    print("\n📝 Testing Step 2: Care Details...")
    care_details = {
        "lead_id": lead_id,
        "bathing_hygiene": "independent",
        "dressing_grooming": "independent",
        "mobility": "walks independently",
        "safety_concerns": "none",
        "companionship_frequency": "weekly",
        "preferred_activities": "social",
        "meal_preparation": "cooking",
        "housekeeping": "no",
        "transportation_needed": "no",
        "transportation_frequency": "not_applicable",
        "preferred_care_schedule": "flexible",
        "start_care_timing": "planning ahead",
        "sms_consent": True
    }
    
    result2 = await save_care_details_only(**care_details)
    
    if result2.get("success"):
        print(f"✅ Step 2 Success! Complete lead saved.")
    else:
        print(f"❌ Step 2 Failed: {result2.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_insert())
