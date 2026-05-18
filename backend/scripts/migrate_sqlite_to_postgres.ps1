param(
    [string]$DumpFile = "sqlite_dump.json"
)

$ErrorActionPreference = "Stop"

Write-Host "Exporting current SQLite data to $DumpFile"
python backend/manage.py dumpdata --exclude contenttypes --exclude auth.permission --indent 2 --output $DumpFile

Write-Host "Now configure POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, and POSTGRES_PORT."
Write-Host "Then run:"
Write-Host "  python backend/manage.py migrate"
Write-Host "  python backend/manage.py loaddata $DumpFile"
