from __future__ import annotations
import asyncio
from onyx.db.engine import get_session_context_manager
from onyx.db.workspace_settings import update_workspace_settings, get_workspace_settings
from onyx.server.documents.models import WorkspaceSettingsUpdate

async def main():
    async with get_session_context_manager() as session:
        settings = get_workspace_settings(session)
        print("Before update, image_extraction_and_analysis_enabled:", settings.image_extraction_and_analysis_enabled)
        
        # update setting
        settings_update = WorkspaceSettingsUpdate(
            image_extraction_and_analysis_enabled=True,
            image_analysis_max_size_mb=20
        )
        update_workspace_settings(session, settings_update)
        print("Updated settings successfully.")

asyncio.run(main())
