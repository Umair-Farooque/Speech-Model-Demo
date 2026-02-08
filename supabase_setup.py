"""
Supabase Setup Script for Med Help USA - Intake Lead Storage
=============================================================

This script:
1. Connects to Supabase using the service role key
2. Checks if the 'save_intake_lead' table exists
3. If not, shows the SQL to create it (one-time setup)
4. Once table exists, you can use this module to save leads

FIRST TIME SETUP:
-----------------
1. Run: python supabase_setup.py
2. If table doesn't exist, copy the SQL shown
3. Go to: https://supabase.com/dashboard
4. Select your project > SQL Editor > New Query
5. Paste the SQL and click "Run"
6. Run this script again to verify

Author: Med Help USA
"""

from supabase import create_client, Client

# =============================================================================
# SUPABASE CREDENTIALS (Service Role Key for full access)
# =============================================================================
SUPABASE_URL = "https://yegljtwihlrwhfpcaojy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InllZ2xqdHdpaGxyd2hmcGNhb2p5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1MzUyMDQsImV4cCI6MjA4NjExMTIwNH0.Ol4yb-WsxIDE1iJvn5ubGWIVFwcFdco8-XqIkx3fOJU"

# =============================================================================
# SQL TO CREATE THE TABLES (Copy this to Supabase SQL Editor)
# =============================================================================
CREATE_TABLE_SQL = """
-- =============================================
-- MED HELP USA - DATABASE SCHEMA (v2)
-- Copy this entire block and run in Supabase
-- Dashboard > SQL Editor > New Query > Run
-- =============================================

-- 1. Create the lead_personal_info table
CREATE TABLE IF NOT EXISTS lead_personal_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    care_recipient_name TEXT,
    estimated_age_range TEXT,
    relationship TEXT,
    michigan_location TEXT,
    current_living_situation TEXT,
    lead_name TEXT,
    phone_number TEXT,
    email TEXT,
    best_time_to_contact TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Create the care_details table (linked by ID)
CREATE TABLE IF NOT EXISTS care_details (
    id UUID PRIMARY KEY REFERENCES lead_personal_info(id) ON DELETE CASCADE,
    bathing_hygiene TEXT,
    dressing_grooming TEXT,
    mobility TEXT,
    safety_concerns TEXT,
    companionship_frequency TEXT,
    preferred_activities TEXT,
    meal_preparation TEXT,
    housekeeping TEXT,
    transportation_needed TEXT,
    transportation_frequency TEXT,
    preferred_care_schedule TEXT,
    start_care_timing TEXT,
    sms_consent BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE lead_personal_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE care_details ENABLE ROW LEVEL SECURITY;

-- Create policies for service role
CREATE POLICY "Service role full access on leads" ON lead_personal_info FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on care" ON care_details FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions
GRANT ALL ON lead_personal_info TO service_role;
GRANT ALL ON care_details TO service_role;
GRANT INSERT ON lead_personal_info TO anon;
GRANT INSERT ON care_details TO anon;
"""


# =============================================================================
# SUPABASE CLIENT FUNCTIONS
# =============================================================================

def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.
    Call this once and reuse the client.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def check_tables_exist(supabase: Client) -> dict:
    """
    Check if the required tables exist.
    """
    results = {}
    for table in ["lead_personal_info", "care_details"]:
        try:
            supabase.table(table).select("id").limit(1).execute()
            results[table] = True
        except Exception:
            results[table] = False
    return results


def save_intake_lead(supabase: Client, data: dict) -> dict | None:
    """
    Save an intake lead to Supabase.
    
    Args:
        supabase: Supabase client instance
        data: Dictionary containing lead data:
            - caller_name (str)
            - callback_number (str)
            - language_preference (str)
            - email_address (str)
            - sms_consent (bool)
            - care_recipient (str)
            - age_group (str)
            - mobility_status (str)
            - cognition_status (str)
            - hygiene_needs (str)
    
    Returns:
        The saved record with ID, or None if failed
    """
    try:
        response = supabase.table("save_intake_lead").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Failed to save lead: {e}")
        return None


def get_all_leads(supabase: Client, limit: int = 100) -> list:
    """
    Retrieve all intake leads from Supabase.
    
    Args:
        supabase: Supabase client instance
        limit: Maximum number of records to return
    
    Returns:
        List of lead records
    """
    try:
        response = (
            supabase.table("save_intake_lead")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"❌ Failed to fetch leads: {e}")
        return []


def get_lead_by_id(supabase: Client, lead_id: str) -> dict | None:
    """
    Get a specific lead by its ID.
    
    Args:
        supabase: Supabase client instance
        lead_id: UUID of the lead
    
    Returns:
        Lead record or None if not found
    """
    try:
        response = (
            supabase.table("save_intake_lead")
            .select("*")
            .eq("id", lead_id)
            .single()
            .execute()
        )
        return response.data
    except Exception:
        return None


# =============================================================================
# MAIN - SETUP VERIFICATION
# =============================================================================

def main():
    """Run setup verification."""
    
    print("\n" + "="*60)
    print("   🏥 MED HELP USA - SUPABASE SETUP")
    print("="*60)
    
    # Connect to Supabase
    print("\n🔗 Connecting to Supabase...")
    try:
        supabase = get_supabase_client()
        print("✅ Connected successfully!")
        print(f"   URL: {SUPABASE_URL}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check if tables exist
    print("\n🔍 Checking for database tables...")
    
    table_status = check_tables_exist(supabase)
    
    all_exist = all(table_status.values())
    
    for table, exists in table_status.items():
        status = "✅ exists" if exists else "❌ NOT found"
        print(f"   - {table}: {status}")
    
    if all_exist:
        print("\n" + "-"*60)
        print("✅ DATABASE READY - Tables are correctly set up!")
        print("-"*60)
    else:
        print("\n⚠️  Schema is missing! Please run the SQL query provided earlier in your Supabase SQL Editor.")
    
    print("\n" + "="*60)
    print("   🏁 DONE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
