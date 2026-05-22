[CmdletBinding()]
param(
    [string]$Source,
    [string]$Target = "C:\inetpub\wwwroot"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Source)) {
    $scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    $Source = Split-Path -Parent $scriptRoot
}

$sourcePath = (Resolve-Path -LiteralPath $Source).Path

if (-not (Test-Path -LiteralPath $Target)) {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
}

$targetPath = (Resolve-Path -LiteralPath $Target).Path

if ($sourcePath -eq $targetPath) {
    throw "Source and target are the same path: $sourcePath"
}

Write-Host "Deploying:"
Write-Host "  Source: $sourcePath"
Write-Host "  Target: $targetPath"

& robocopy $sourcePath $targetPath /MIR /XD .git .vscode /R:2 /W:1
$robocopyExitCode = $LASTEXITCODE

if ($robocopyExitCode -le 7) {
    Write-Host "Deploy completed. Robocopy exit code: $robocopyExitCode"
    exit 0
}

Write-Error "Deploy failed. Robocopy exit code: $robocopyExitCode"
exit $robocopyExitCode
