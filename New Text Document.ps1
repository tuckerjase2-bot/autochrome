<# 
Copy the current project directory into the user's profile folder named "googygoogy".

Usage (PowerShell):
  .\move_to_googygoogy.ps1          # copy files to $env:USERPROFILE\googygoogy (won't overwrite existing unless -Force)
  .\move_to_googygoogy.ps1 -Force  # remove any existing target first, then copy

Notes:
- This script copies the current working directory (where it's run) to the destination.
- Default destination is "$env:USERPROFILE\googygoogy" which does not require admin rights.
- If you prefer copying to `C:\googygoogy`, run the script with `-ToCDrive`.
#>

param(
    [switch]$Force,
    [switch]$ToCDrive
)

$ErrorActionPreference = 'Stop'

$src = (Get-Location).ProviderPath
if ($ToCDrive) {
    $dest = 'C:\googygoogy'
} else {
    $dest = Join-Path $env:USERPROFILE 'googygoogy'
}

Write-Host "Preparing to copy project from:`n  $src`n to:`n  $dest`n"

if (Test-Path $dest) {
    if ($Force) {
        Write-Host "-Force specified: removing existing $dest..."
        Remove-Item -LiteralPath $dest -Recurse -Force
    } else {
        Write-Error "Destination $dest already exists. Use -Force to overwrite. Aborting."
        exit 1
    }
}

Write-Host "Creating destination directory $dest..."
New-Item -ItemType Directory -Path $dest -Force | Out-Null

Write-Host "Copying files..."
try {
    $robocopy = Get-Command robocopy -ErrorAction SilentlyContinue
    if ($null -ne $robocopy) {
        Write-Host "Using robocopy to copy files (this may show many lines)..."
        & robocopy $src $dest /MIR /FFT /Z /XA:H /W:5 /R:3 /NFL /NDL /NJH /NJS | Out-Null
        if ($LASTEXITCODE -ge 8) {
            Write-Error "Robocopy reported an error (exit code $LASTEXITCODE)."
            exit $LASTEXITCODE
        }
    } else {
        Write-Host "Robocopy not found; using Copy-Item instead (slower)..."
        Copy-Item -Path (Join-Path $src '*') -Destination $dest -Recurse -Force
    }
}
catch {
    Write-Error "Copy failed: $_"
    exit 1
}

Write-Host "Copy complete. Files are now at $dest"
Write-Host "If you have a virtual environment, recreate it at the destination by running:`n  $dest\setup.ps1`n"