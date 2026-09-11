# start-all.ps1
# One command to start the whole AI Agent Control Panel stack:
#   1) Ollama   (local LLM runner)    :11434
#   2) OmniRoute (AI gateway)         :20128
#   3) Backend  (FastAPI + uvicorn)   :8080
#   4) Frontend (React + Vite)        :5173
# Already-running components are detected by port and skipped.

$ErrorActionPreference = 'SilentlyContinue'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir  = Join-Path $projectRoot 'backend'
$frontendDir = Join-Path $projectRoot 'frontend'
$ollamaApp   = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'

function Test-Port([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

Write-Host ''
Write-Host '=== AI Agent Control Panel - Starter ===' -ForegroundColor Cyan
Write-Host ''

# 1) Ollama
if (Test-Port 11434) {
    Write-Host '[1/4] Ollama     already running      (:11434)' -ForegroundColor Green
} else {
    Write-Host '[1/4] Ollama     starting...' -ForegroundColor Yellow
    if (Test-Path $ollamaApp) {
        Start-Process $ollamaApp -WindowStyle Minimized
    } else {
        Start-Process 'ollama' -ArgumentList 'serve' -WindowStyle Minimized
    }
    Start-Sleep -Seconds 2
}

# 2) OmniRoute
if (Test-Port 20128) {
    Write-Host '[2/4] OmniRoute  already running      (:20128)' -ForegroundColor Green
} else {
    Write-Host '[2/4] OmniRoute  starting...' -ForegroundColor Yellow
    Start-Process cmd -ArgumentList '/k','title OmniRoute_Gateway_20128 && omniroute' -WorkingDirectory $projectRoot
    Start-Sleep -Seconds 2
}

# 3) Backend
if (Test-Port 8080) {
    Write-Host '[3/4] Backend    already running      (:8080)' -ForegroundColor Green
} else {
    Write-Host '[3/4] Backend    starting...' -ForegroundColor Yellow
    Start-Process cmd -ArgumentList '/k','title Backend_uvicorn_8080 && python -m uvicorn app.main:app --reload --port 8080' -WorkingDirectory $backendDir
    Start-Sleep -Seconds 2
}

# 4) Frontend
if (Test-Port 5173) {
    Write-Host '[4/4] Frontend   already running      (:5173)' -ForegroundColor Green
} else {
    Write-Host '[4/4] Frontend   starting...' -ForegroundColor Yellow
    Start-Process cmd -ArgumentList '/k','title Frontend_Vite_5173 && npm run dev' -WorkingDirectory $frontendDir
}

Write-Host ''
Write-Host 'Open  http://localhost:5173  in your browser.' -ForegroundColor Cyan
Write-Host 'Each component runs in its own titled window. Closing a window stops that component.' -ForegroundColor DarkGray
Write-Host ''