from __future__ import annotations
import sys
sys.path.append("/app")

from onyx.db.connector_credential_pair import get_connector_credential_pair_from_id
from onyx.db.engine.sql_engine import get_session_with_current_tenant
from onyx.background.indexing.run_indexing import run_indexing_entrypoint

def main():
    cc_pair_id = 4
    with get_session_with_current_tenant() as session:
        cc_pair = get_connector_credential_pair_from_id(cc_pair_id, session)
        if not cc_pair:
            print(f"CC Pair {cc_pair_id} not found")
            return
        print(f"Triggering indexing for CC Pair: {cc_pair.id}")
        run_indexing_entrypoint(cc_pair.id)

if __name__ == "__main__":
    main()
