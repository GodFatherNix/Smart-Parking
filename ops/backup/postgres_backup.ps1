param(
    [string]$PostgresHost = $env:POSTGRES_HOST,
    [string]$PostgresPort = $(if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }),
    [string]$PostgresDb = $(if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "smartpark" }),
    [string]$PostgresUser = $(if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "smartpark" }),
    [string]$PostgresPassword = $env:POSTGRES_PASSWORD,
    [string]$BackupDir = ".\backups"
)

if (-not $PostgresHost) { $PostgresHost = "localhost" }

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = Join-Path $BackupDir "$PostgresDb`_$timestamp.sql.gz"

$env:PGPASSWORD = $PostgresPassword
$dump = "pg_dump --host=$PostgresHost --port=$PostgresPort --username=$PostgresUser --dbname=$PostgresDb --format=plain --no-owner --no-privileges"

& cmd /c "$dump | gzip > `"$outputFile`""
if ($LASTEXITCODE -ne 0) {
    throw "Backup failed."
}

Write-Host "Backup created: $outputFile"
