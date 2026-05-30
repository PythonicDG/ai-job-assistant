"""
Supabase client initializer module.
Loads configuration from environment variables and exposes a client connection object
for interacting with the Supabase Postgres instance.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Extract database parameters from env variables
SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing database credentials. Please check SUPABASE_URL and SUPABASE_KEY in your .env file.")

# Expose a global database client connection
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
