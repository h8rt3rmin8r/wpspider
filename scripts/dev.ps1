<#
.SYNOPSIS
    Runs the WPSpider application in development mode.

.DESCRIPTION
    Sets up the PYTHONPATH and executes the WPSpider Python module using the local virtual environment.
    This script ensures the environment is correctly configured before launching the application source.

.PARAMETER Target
    The target WordPress URL or domain to crawl. Corresponds to the --target argument.

.PARAMETER Output
    The path to the output SQLite database file. Corresponds to the --output argument.

.PARAMETER ExtraArguments
    Capture any additional arguments to pass through to the Python script.

.EXAMPLE
    .\scripts\dev.ps1 -Target "https://example.com"
    Runs the crawler against the specified target.

.EXAMPLE
    .\scripts\dev.ps1 -Target "example.com" -Output "data.db" -Verbose
    Runs with explicit output path and enables verbose script logging.
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Position = 0)]
    [string]$Target,

    [Parameter()]
    [string]$Output,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArguments
)

Set-StrictMode -Version Latest

try {
    # Get project root (one level up from scripts/)
    $ProjectRoot = (Resolve-Path "$PSScriptRoot/..").Path
    Write-Verbose "Project Root determined as: $ProjectRoot"

    # Define Python path in .venv
    $PythonPath = Join-Path $ProjectRoot ".venv/Scripts/python.exe"
    
    if (-not (Test-Path -Path $PythonPath)) {
        Write-Warning "Virtual environment not found at '$PythonPath'. Falling back to global 'python' command."
        $PythonPath = "python"
    } else {
        Write-Verbose "Using virtual environment Python: $PythonPath"
    }

    # Set PYTHONPATH so 'wpspider' package can be imported
    $SrcPath = Join-Path $ProjectRoot "src"
    $env:PYTHONPATH = $SrcPath
    Write-Verbose "PYTHONPATH set to: $SrcPath"

    # Build argument list
    $PyArgs = @()
    
    if ($PSBoundParameters.ContainsKey('Target')) {
        $PyArgs += "--target", $Target
    }

    if ($PSBoundParameters.ContainsKey('Output')) {
        $PyArgs += "--output", $Output
    }

    if ($null -ne $ExtraArguments) {
        $PyArgs += $ExtraArguments
    }

    Write-Verbose "Executing module wpspider.main with arguments: $($PyArgs -join ' ')"

    # Run the main script
    & $PythonPath -m wpspider.main @PyArgs

} catch {
    Write-Error "Failed to execute dev script: $_"
    exit 1
}
