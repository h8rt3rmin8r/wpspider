<#
.SYNOPSIS
    This script generates JSON schema files from input JSON files using the genson tool.
.DESCRIPTION
    The script accepts one or more JSON files as input arguments and generates corresponding JSON schema files.
    It uses the genson tool to create the schema based on the provided JSON files.

    NOTE: This script has a hard requirement on the 'genson' tool. Please ensure it is installed and available in your PATH.
.PARAMETER File
    A single JSON file to process.
.PARAMETER Files
    An array of JSON files to process.
.PARAMETER Verbosity
    A switch to enable or disable verbosity messages during processing. Default is enabled.
.PARAMETER Help
    Displays help information about the script.
#>
[CmdletBinding(SupportsShouldProcess=$false,ConfirmImpact='None',DefaultParameterSetName='Default')]
Param(
    [Parameter(Mandatory=$false,ParameterSetName='Default')]
    [Alias('file')]
    [System.String]$InputFile,

    [Parameter(Mandatory=$false,ParameterSetName='Default')]
    [Alias('files')]
    [System.Array]$InputFiles,

    [Parameter(Mandatory=$false,ParameterSetName='Default')]
    [Parameter(Mandatory=$false,ParameterSetName='HelpText')]
    [Alias('v')]
    [System.Boolean]$Verbosity = $true,

    [Parameter(Mandatory=$true,ParameterSetName='HelpText')]
    [Alias("h")]
    [Switch]$Help
)
#______________________________________________________________________________
## Declare Functions

#______________________________________________________________________________
## Declare Variables and Arrays

    $ThisScriptPath = $MyInvocation.MyCommand.Path
    $Sep = [System.IO.Path]::DirectorySeparatorChar
    $schemaUri = 'http://json-schema.org/draft-04/schema#'
    $userInputsCount = $($args.count)
    $inFile = ""
    $inFileBaseName = ""
    $inFileDirectory = ""
    $outSuffix = "_schema.json"
    $outFile = ""
    $runType = $null

#______________________________________________________________________________
## Execute Operations

    # Catch help text requests
    if (($Help) -or ($PSCmdlet.ParameterSetName -eq 'HelpText')) {
        Get-Help $ThisScriptPath -Detailed
        exit
    }

    # Detect if this is a batch job, single input, mixed input, or no input at all (attempt to reassign $runType variable accordingly)
    if ($InputFile) {
        if ($InputFiles) {
            $runType = 'Mixed'
        } else {
            $runType = 'Single'
        }
    } elseif ($InputFiles) {
        $runType = 'Batch'
    } else {
        $runType = $null
    }

    # If $null equals the $runType, display an error message and exit the script
    if ($null -eq $runType) {
        Write-Host "Error: No input files provided. Please specify at least one JSON file to process." -ForegroundColor Red
        exit 1
    }

    if ($runType -eq 'Single') {
        # If the number of inputs is equal to exactly 1, process the single input
        $inFile = $args[0]
        $inFileBaseName = [System.IO.Path]::GetFileNameWithoutExtension("$inFile")
        $inFileDirectory = [System.IO.Path]::GetDirectoryName("$inFile")
        $outFile = -join("$inFileDirectory","$Sep","$inFileBaseName","$outSuffix")
        # Write verbosity message before processing
        if ($Verbosity) {
            Write-Host "Processing file: $inFile -> $outFile"
        }
        genson -i 4 --schema-uri "$schemaUri" "$inFile" > "$outFile"
    } elseif ($runType -eq 'Batch') {
        # Iterate over each input file and generate a schema output for each one
        $InputFilesCount = $InputFiles.Count
        $Counter = 1
        $CounterMax = $InputFilesCount
        foreach ($inFile in $InputFiles) {
            $inFileBaseName = [System.IO.Path]::GetFileNameWithoutExtension("$inFile")
            $inFileDirectory = [System.IO.Path]::GetDirectoryName("$inFile")
            $outFile = -join("$inFileDirectory","$Sep","$inFileBaseName","$outSuffix")
            $verbosityPrefix = "[ $Counter of $CounterMax ] "
            # Write verbosity message before processing
            if ($Verbosity) {
                Write-Host "$verbosityPrefix Processing file: $inFile -> $outFile"
            }
            genson -i 4 --schema-uri "$schemaUri" "$inFile" > "$outFile"
            $Counter++
        }
    }

    # Write final verbosity message
    if ($Verbosity) {
        Write-Host "Schema generation completed. Exiting script."
    }

#______________________________________________________________________________
## End of script