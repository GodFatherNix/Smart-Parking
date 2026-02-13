param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [string]$PostgresHost = $env:POSTGRES_HOST,
    [string]$PostgresPort = $(if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }),
    [string]$PostgresDb = $(if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "smartpark" }),
    [string]$PostgresUser = $(if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "smartpark" }),
    [string]$PostgresPassword = $env:POSTGRES_PASSWORD
)

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}
if (-not $PostgresHost) { $PostgresHost = "localhost" }

$env:PGPASSWORD = $PostgresPassword
$restore = "gunzip -c `"$BackupFile`" | psql --host=$PostgresHost --port=$PostgresPort --username=$PostgresUser --dbname=$PostgresDb"

& cmd /c $restore
if ($LASTEXITCODE -ne 0) {
    throw "Restore failed."
}

Write-Host "Restore completed from: $BackupFile"
