#!/usr/bin/env python3

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from onyx.db.engine.sql_engine import get_session_with_tenant
from onyx.server.api_key.models import APIKeyArgs
from onyx.db.api_key import insert_api_key
from onyx.auth.schemas import UserRole
import uuid

def main():
    # Get user ID from command line or use the first real user
    if len(sys.argv) > 1:
        user_id = uuid.UUID(sys.argv[1])
    else:
        # Use the gretenka@proton.me user ID from our database inspection
        user_id = uuid.UUID("f8f07163-648e-4da5-9457-36f945cc1508")
    
    print(f"Creating API key for user: {user_id}")
    
    with get_session_with_tenant(tenant_id=None) as db_session:
        api_key_args = APIKeyArgs(
            name="MCP Server Key",
            role=UserRole.BASIC
        )
        
        api_key_desc = insert_api_key(db_session, api_key_args, user_id)
        db_session.commit()
        
        print(f"API Key created successfully!")
        print(f"Full API Key: {api_key_desc.api_key}")
        print(f"Display: {api_key_desc.api_key_display}")

if __name__ == "__main__":
    main()