# wpspider Build Script
# usage: ./scripts/build.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting Build Process for wpspider..."

# Get Project Root (assume script is in scripts/)
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptPath
Set-Location $ProjectRoot

# Determine PyInstaller Command
if (Test-Path ".venv/Scripts/pyinstaller.exe") {
    $PyInstallerCmd = Resolve-Path ".venv/Scripts/pyinstaller.exe"
    Write-Host "Using venv PyInstaller: $PyInstallerCmd"
} elseif (Get-Command "pyinstaller" -ErrorAction SilentlyContinue) {
    $PyInstallerCmd = "pyinstaller"
    Write-Host "Using system PyInstaller"
} else {
    Write-Error "Could not find pyinstaller. Please run: pip install pyinstaller"
}

# Clean previous builds
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }

Write-Host "Running PyInstaller..."
# We use --paths src so it can find the ""wpspider"" package
& $PyInstallerCmd --noconfirm --name wpspider --onefile --clean --paths=src src/wpspider/main.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed with exit code $LASTEXITCODE"
}

# Copy config.json to dist/
Write-Host "Copying config.json to dist/..."
if (Test-Path "config.json") {
    Copy-Item "config.json" -Destination "dist/config.json"
} else {
    Write-Warning "config.json not found in root, skipping copy."
}

Write-Host "Build Complete!"
Write-Host "Executable is at: dist/wpspider.exe"
