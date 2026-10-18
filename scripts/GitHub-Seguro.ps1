Set-StrictMode -Version Latest

function Find-Git {
    $command = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $desktop = @(Get-ChildItem -Path "$env:LOCALAPPDATA/GitHubDesktop/app-*/resources/app/git/cmd/git.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending)
    if ($desktop.Count) { return $desktop[0].FullName }
    $bundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
    if (Test-Path -LiteralPath $bundled) { return $bundled }
    throw 'No se encontro Git. Instala Git para Windows o GitHub Desktop y volve a ejecutar el BAT.'
}

function Invoke-SafeGit {
    param([string]$Git, [string]$Repo, [string[]]$GitArgs, [switch]$AllowFailure)
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $lines = @(& $Git -c core.quotepath=false -c "core.hooksPath=$Repo/.git/no-hooks" -C $Repo @GitArgs 2>&1)
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $saved }
    $output = ($lines | ForEach-Object { $_.ToString() }) -join "`n"
    if ($code -ne 0 -and -not $AllowFailure) { throw "Git no pudo completar '$($GitArgs[0])':`n$output" }
    return [pscustomobject]@{ Code = $code; Text = $output.Trim() }
}

function Test-PublishPath([string]$Path) {
    if ($Path -match '(^|/)(\.git|\.github-sync|\.gradle|build|__pycache__|\.venv|venv|Datos de ejemplo|Informes de prueba|Originales|Distribuciones)(/|$)') { return $false }
    if ($Path -match '(^|/)(local\.properties|\.env[^/]*|credentials[^/]*|secrets[^/]*)$') { return $false }
    if ($Path -eq 'Android/gradle/wrapper/gradle-wrapper.jar') { return $true }
    if ($Path -match '(^|/)(\.gitignore|gradlew|requirements[^/]*\.txt|LICENSE)$') { return $true }
    return $Path -match '\.(py|java|kt|gradle|properties|xml|md|bat|ps1)$'
}

function Assert-PublishText([string]$Text, [string]$Path) {
    if ($Text -match 'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|AKIA[A-Z0-9]{16}') {
        throw "Posible credencial en $Path. Se bloqueo la publicacion; revisa el archivo."
    }
}

function Get-PublishFiles([string]$Root) {
    $rootPath = [IO.Path]::GetFullPath($Root).TrimEnd('\','/')
    $items = @('.gitignore','README.md','GITHUB.md','LEEME.md','ACTUALIZAR_GITHUB.bat','REVISAR_SIN_SUBIR.bat','Android','Codigo','scripts')
    $queue = New-Object 'System.Collections.Generic.Queue[string]'
    foreach ($item in $items) { $path = Join-Path $rootPath $item; if (Test-Path -LiteralPath $path) { $queue.Enqueue($path) } }
    $files = @()
    while ($queue.Count) {
        $item = Get-Item -LiteralPath $queue.Dequeue() -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "No se publican enlaces: $($item.FullName)" }
        if ($item.PSIsContainer) {
            if ($item.Name -in @('.git','.github-sync','.gradle','build','__pycache__','.venv','venv')) { continue }
            foreach ($child in Get-ChildItem -LiteralPath $item.FullName -Force) { $queue.Enqueue($child.FullName) }
        } else {
            $relative = $item.FullName.Substring($rootPath.Length + 1).Replace('\','/')
            if (-not (Test-PublishPath $relative)) { continue }
            if ($item.Length -gt 5MB) { throw "Archivo de codigo demasiado grande: $relative" }
            if ($relative.EndsWith('.jar')) {
                if ((Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash -ne '498495120A03B9A6AB5D155F5DE3C8F0D986A449153702FB80FC80E134484F17') { throw 'El wrapper de Gradle cambio; requiere revision antes de publicarlo.' }
            } else { Assert-PublishText ([IO.File]::ReadAllText($item.FullName)) $relative }
            $files += $relative
        }
    }
    if ($files -notcontains 'Android/app/build.gradle' -or $files -notcontains 'Codigo/glucose_insights.py') { throw 'La carpeta no contiene el proyecto completo esperado.' }
    return $files | Sort-Object -Unique
}

function Initialize-PublishRepository([string]$Git, [string]$Repo, [string]$Remote) {
    if (Test-Path -LiteralPath $Repo) {
        if ((Get-Item -LiteralPath $Repo -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'La copia de publicacion no puede ser un enlace.' }
        if (-not (Test-Path -LiteralPath (Join-Path $Repo '.git') -PathType Container)) { throw 'La carpeta .github-sync existe pero no es una copia de publicacion valida.' }
        $origin = (Invoke-SafeGit $Git $Repo @('remote','get-url','--all','origin')).Text
        $push = (Invoke-SafeGit $Git $Repo @('remote','get-url','--push','--all','origin')).Text
        if ($origin -ne $Remote -or $push -ne $Remote) { throw 'El destino Git no coincide con el repositorio configurado. Se detuvo la operacion.' }
        $branch = (Invoke-SafeGit $Git $Repo @('symbolic-ref','--short','HEAD')).Text
        if ($branch -ne 'main') { throw 'La copia de publicacion no esta en main; requiere revision.' }
        $head = Invoke-SafeGit $Git $Repo @('rev-parse','--verify','HEAD') -AllowFailure
        if ($head.Code -eq 0) { return }
        if ((Invoke-SafeGit $Git $Repo @('status','--porcelain')).Text) { return }
    } else {
        New-Item -ItemType Directory -Path $Repo | Out-Null
        Invoke-SafeGit $Git $Repo @('init','--initial-branch=main') | Out-Null
        Invoke-SafeGit $Git $Repo @('remote','add','origin',$Remote) | Out-Null
    }
    $heads = (Invoke-SafeGit $Git $Repo @('ls-remote','--heads','origin')).Text
    if ($heads -match 'refs/heads/main(\s|$)') {
        Invoke-SafeGit $Git $Repo @('fetch','origin','refs/heads/main:refs/remotes/origin/main') | Out-Null
        Assert-TreeSafe $Git $Repo 'refs/remotes/origin/main'
        Invoke-SafeGit $Git $Repo @('checkout','-B','main','refs/remotes/origin/main') | Out-Null
    } elseif ($heads) { throw 'El repositorio tiene otras ramas pero no main. Requiere revisar la rama antes de publicar.' }
}

function Assert-RemoteState([string]$Git, [string]$Repo) {
    $heads = (Invoke-SafeGit $Git $Repo @('ls-remote','--heads','origin')).Text
    $local = Invoke-SafeGit $Git $Repo @('rev-parse','--verify','HEAD') -AllowFailure
    if ($heads -match 'refs/heads/main(\s|$)') {
        Invoke-SafeGit $Git $Repo @('fetch','origin','refs/heads/main:refs/remotes/origin/main') | Out-Null
        if ($local.Code -ne 0) { throw 'GitHub ya tiene historial; la copia de publicacion requiere revision antes de continuar.' }
        $ancestor = Invoke-SafeGit $Git $Repo @('merge-base','--is-ancestor','refs/remotes/origin/main','HEAD') -AllowFailure
        if ($ancestor.Code -ne 0) { throw 'Hay cambios en GitHub que no estan incorporados localmente. No se hizo merge ni push forzado; sincroniza el proyecto antes de continuar.' }
    } elseif ($heads) { throw 'No existe main en GitHub; revisa las ramas.' }
    else {
        $old = Invoke-SafeGit $Git $Repo @('rev-parse','--verify','refs/remotes/origin/main') -AllowFailure
        if ($old.Code -eq 0) { throw 'La rama main desaparecio de GitHub; requiere revision.' }
    }
}

function Get-PendingCommits([string]$Git, [string]$Repo) {
    $head = Invoke-SafeGit $Git $Repo @('rev-parse','--verify','HEAD') -AllowFailure
    if ($head.Code -ne 0) { return }
    $origin = Invoke-SafeGit $Git $Repo @('rev-parse','--verify','refs/remotes/origin/main') -AllowFailure
    $range = if ($origin.Code -eq 0) { 'refs/remotes/origin/main..HEAD' } else { 'HEAD' }
    $text = (Invoke-SafeGit $Git $Repo @('rev-list',$range)).Text
    if ($text) { return $text -split "`n" }
}

function Sync-PublishFiles([string]$Git, [string]$Source, [string]$Repo, [string[]]$Files) {
    # Only the dedicated generated checkout is modified, never the user's source files.
    $tracked = (Invoke-SafeGit $Git $Repo @('ls-files')).Text
    foreach ($path in ($tracked -split "`n")) {
        if (-not $path) { continue }
        $owned = $path -match '^(Android/|Codigo/|scripts/|README\.md$|GITHUB\.md$|LEEME\.md$|\.gitignore$|ACTUALIZAR_GITHUB\.bat$|REVISAR_SIN_SUBIR\.bat$)'
        if ($owned -and $Files -notcontains $path) { Invoke-SafeGit $Git $Repo @('rm','-f','--',$path) | Out-Null }
    }
    foreach ($relative in $Files) {
        $destination = [IO.Path]::GetFullPath((Join-Path $Repo $relative))
        $boundary = [IO.Path]::GetFullPath($Repo).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
        if (-not $destination.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase)) { throw 'Ruta de publicacion fuera de la carpeta esperada.' }
        $parent = Split-Path -Parent $destination
        $check = $parent
        while ($check.Length -ge $boundary.Length) {
            if (Test-Path -LiteralPath $check) {
                if ((Get-Item -LiteralPath $check -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Hay un enlace en la copia de publicacion.' }
            }
            $check = Split-Path -Parent $check
        }
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        if (Test-Path -LiteralPath $destination) {
            if ((Get-Item -LiteralPath $destination -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Hay un archivo enlazado en la copia de publicacion.' }
        }
        Copy-Item -LiteralPath (Join-Path $Source $relative) -Destination $destination -Force
        Invoke-SafeGit $Git $Repo @('add','--',$relative) | Out-Null
    }
}

function Assert-TreeSafe([string]$Git, [string]$Repo, [string]$Revision) {
    $command = if ($Revision) { @('ls-tree','-r','--full-tree',$Revision) } else { @('ls-files','--stage') }
    $tree = (Invoke-SafeGit $Git $Repo $command).Text
    foreach ($line in ($tree -split "`n")) {
        if (-not $line) { continue }
        if ($line -notmatch '^(100644|100755) ([a-f0-9]+|blob) ([a-f0-9]+)\t(.+)$') { throw 'El indice contiene enlaces, submodulos o un formato inesperado.' }
        $path = $Matches[4]; $blob = if ($Revision) { $Matches[3] } else { $Matches[2] }
        if (-not (Test-PublishPath $path)) { throw "Archivo no permitido en Git: $path. No se publicara." }
        if ($path.EndsWith('.jar')) {
            if ($blob -ne '2c3521197d7c4586c843d1d3e9090525f1898cde') { throw 'El wrapper de Gradle en Git no coincide con la version revisada.' }
        } else {
            $size = [long](Invoke-SafeGit $Git $Repo @('cat-file','-s',$blob)).Text
            if ($size -gt 5MB) { throw "Archivo demasiado grande en Git: $path" }
            Assert-PublishText (Invoke-SafeGit $Git $Repo @('cat-file','blob',$blob)).Text $path
        }
    }
}
