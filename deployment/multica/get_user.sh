docker exec multica-postgres-1 psql -U multica -d multica -t -c "SELECT id FROM \"user\" LIMIT 1;"
