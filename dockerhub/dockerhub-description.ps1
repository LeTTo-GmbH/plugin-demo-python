# Lädt dockerhub/README.md als Beschreibung (Overview) des Docker-Hub-Repositories hoch.
#   powershell -ExecutionPolicy Bypass -File dockerhub\dockerhub-description.ps1
# Zugangsdaten in dieser Reihenfolge:
#   1. -User und -Token (bzw. $env:DOCKERHUB_TOKEN), Token = Personal Access Token mit "Read & Write"
#   2. die Docker-Desktop-Anmeldung aus dem Credential-Store (credsStore in ~/.docker/config.json)
#   3. interaktive Abfrage (nur in einer interaktiven Konsole, sonst Abbruch mit Fehlermeldung)
param(
    [string]$User,
    [string]$Token = $env:DOCKERHUB_TOKEN,
    [string]$Repo = "lettohub/letto-plugin-demopython",
    [string]$Short = "LeTTo Demo-Plugin UhrPy in Python/FastAPI – Vorlage für eigene LeTTo-Plugins",
    [string]$File = "$PSScriptRoot\README.md"
)
$ErrorActionPreference = "Stop"

# liest Benutzer und Kennwort/Token für Docker Hub aus dem Credential-Helper von Docker;
# liefert $null und gibt den Grund als Warnung aus, wenn das nicht möglich ist
function Get-DockerCredential {
    $config = Join-Path $env:USERPROFILE ".docker\config.json"
    if (-not (Test-Path $config)) { Write-Warning "keine Docker-Konfiguration $config"; return $null }
    $store = (Get-Content -Raw $config | ConvertFrom-Json).credsStore
    if (-not $store) { Write-Warning "kein credsStore in $config"; return $null }
    $psi = New-Object Diagnostics.ProcessStartInfo "docker-credential-$store", "get"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    try { $p = [Diagnostics.Process]::Start($psi) } catch { Write-Warning "docker-credential-$store kann nicht gestartet werden: $_"; return $null }
    # ohne Zeilenumbruch schreiben, sonst findet der Helper den Eintrag nicht
    $p.StandardInput.Write("https://index.docker.io/v1/")
    $p.StandardInput.Close()
    $out = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($p.ExitCode -ne 0) {
        Write-Warning "docker-credential-$store liefert keine Docker-Hub-Anmeldung: $(($out + ' ' + $err).Trim())"
        return $null
    }
    $out | ConvertFrom-Json
}

# true, wenn Eingaben über die Konsole möglich sind (nicht bei -NonInteractive oder umgeleiteter Eingabe)
function Test-Interactive {
    if ([Environment]::GetCommandLineArgs() | Where-Object { $_ -like '-NonI*' }) { return $false }
    if ([Console]::IsInputRedirected) { return $false }
    return [Environment]::UserInteractive
}

if (-not $Token) {
    $cred = Get-DockerCredential
    if ($cred -and $cred.Secret -and (-not $User -or $User -eq $cred.Username)) {
        $User = $cred.Username
        $Token = $cred.Secret
        Write-Host "verwende die Docker-Desktop-Anmeldung von $User"
    }
}
if (-not $User -or -not $Token) {
    if (-not (Test-Interactive)) {
        throw "Keine Docker-Hub-Zugangsdaten: -User/-Token bzw. DOCKERHUB_TOKEN setzen oder mit 'docker login' anmelden. " +
              "Eine interaktive Abfrage ist hier nicht möglich."
    }
    if (-not $User) { $User = Read-Host "Docker-Hub-Benutzer" }
    if (-not $Token) {
        $sec = Read-Host -AsSecureString "Docker-Hub Passwort oder Access Token für $User"
        $Token = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    }
}

# Komma-Operator, damit PowerShell das byte[] nicht in ein Object[] entpackt
function ToUtf8Json($obj) { , [Text.Encoding]::UTF8.GetBytes(($obj | ConvertTo-Json -Compress)) }

$login = Invoke-RestMethod -Method Post -Uri "https://hub.docker.com/v2/auth/token" `
    -ContentType "application/json; charset=utf-8" -Body (ToUtf8Json @{ identifier = $User; secret = $Token })

$body = @{
    description      = $Short
    # nicht Get-Content: dessen String trägt PSPath & Co., die ConvertTo-Json mitserialisiert
    full_description = [IO.File]::ReadAllText((Resolve-Path $File).ProviderPath, [Text.Encoding]::UTF8)
}
Invoke-RestMethod -Method Patch -Uri "https://hub.docker.com/v2/repositories/$Repo/" `
    -Headers @{ Authorization = "Bearer $($login.access_token)" } `
    -ContentType "application/json; charset=utf-8" -Body (ToUtf8Json $body) | Out-Null

Write-Host "Beschreibung von $Repo aktualisiert: https://hub.docker.com/r/$Repo"
