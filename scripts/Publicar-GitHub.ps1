param([switch]$SoloRevisar)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot 'GitHub-Seguro.ps1')
$project = Split-Path -Parent $PSScriptRoot
$remote = 'https://github.com/Jmchidini/Glucose-Insights.git'
$lock = $null
try {
    $manifest = @(Get-PublishFiles $project)
    Write-Host "Destino: $remote (rama main)"
    Write-Host 'Se incluyen codigo e instrucciones. Datos, informes, APK y claves quedan afuera.'
    $manifest | ForEach-Object { Write-Host "  $_" }
    if ($SoloRevisar) {
        Write-Host "`nRevision local correcta: $($manifest.Count) archivos. No se conecto con GitHub."
        exit 0
    }
    $lock = [IO.File]::Open((Join-Path $project '.github-sync.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
    $git = Find-Git
    $checkout = Join-Path $project '.github-sync'
    Initialize-PublishRepository $git $checkout $remote
    Assert-RemoteState $git $checkout
    Sync-PublishFiles $git $project $checkout $manifest
    Assert-TreeSafe $git $checkout ''
    $changes = (Invoke-SafeGit $git $checkout @('diff','--cached','--stat','--no-ext-diff','--no-textconv')).Text
    $pending = @(Get-PendingCommits $git $checkout)
    if (-not $changes -and $pending.Count -eq 0) { Write-Host "`nNo hay cambios para subir."; exit 0 }
    foreach ($commit in $pending) { Assert-TreeSafe $git $checkout $commit }
    Write-Host "`nCambios preparados:"; Write-Host $changes
    if ($pending.Count) { Write-Host "Commits locales pendientes de subir: $($pending.Count)" }
    if ((Read-Host 'Escribi S y Enter para guardar y subir estos cambios; Enter cancela') -ine 'S') {
        Write-Host 'Cancelado. No se subio nada. Podes volver a ejecutar el BAT.'; exit 0
    }
    if ($changes) {
        foreach ($field in @('name','email')) {
            $identity = Invoke-SafeGit $git $checkout @('config','--get',"user.$field") -AllowFailure
            if (-not $identity.Text) {
                $value = Read-Host "Git necesita tu $field para identificar el commit"
                if ([string]::IsNullOrWhiteSpace($value)) { throw 'Falta la identidad de Git; no se subio nada.' }
                Invoke-SafeGit $git $checkout @('config','--local',"user.$field",$value) | Out-Null
            }
        }
        Invoke-SafeGit $git $checkout @('commit','-m',('Actualizar Glucose Insights - ' + (Get-Date -Format 'yyyy-MM-dd HH:mm'))) | Out-Null
    }
    Assert-RemoteState $git $checkout
    foreach ($commit in @(Get-PendingCommits $git $checkout)) { Assert-TreeSafe $git $checkout $commit }
    Invoke-SafeGit $git $checkout @('push','--porcelain','origin','HEAD:refs/heads/main') | Out-Null
    Write-Host "`nSubida completada: https://github.com/Jmchidini/Glucose-Insights"
} catch {
    Write-Host "`nDETENIDO: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'No se fuerza la subida ni se sobrescribe el historial remoto.'
    exit 1
} finally { if ($null -ne $lock) { $lock.Dispose() } }
