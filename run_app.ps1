$ErrorActionPreference = "Stop"

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonCandidates = @(
    "C:\Users\Pc\anaconda3\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "python"
)

$Python = $null
foreach ($Candidate in $PythonCandidates) {
    try {
        $Resolved = Get-Command $Candidate -ErrorAction Stop
        $Python = $Resolved.Source
        break
    }
    catch {
        if (Test-Path $Candidate) {
            $Python = $Candidate
            break
        }
    }
}

if (-not $Python) {
    throw "No Python executable was found. Install Python or update run_app.ps1."
}

Set-Location $AppRoot
Write-Host "Starting Bank Churn Prediction app..."
Write-Host "Local URL: http://127.0.0.1:8501"
& $Python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
