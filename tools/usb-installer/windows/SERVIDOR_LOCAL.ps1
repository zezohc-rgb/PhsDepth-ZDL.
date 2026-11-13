param(
    [switch]$SemNavegador,
    [int]$Porta = 0,
    [string]$Pasta = (Join-Path $PSScriptRoot 'instalador')
)

# Compatible with Windows PowerShell 5.1. No admin rights, downloads or installs.
# Only serves static files on the IPv4 loopback interface; never sends MIDI.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($Pasta)
if (-not (Test-Path -LiteralPath (Join-Path $root 'index.html') -PathType Leaf)) {
    throw 'Instalador nao encontrado. Extraia TODO o ZIP antes de iniciar.'
}
$prefix = $root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $Porta)
$mime = @{
    '.html' = 'text/html; charset=utf-8'
    '.css' = 'text/css; charset=utf-8'
    '.mjs' = 'text/javascript; charset=utf-8'
    '.js' = 'text/javascript; charset=utf-8'
    '.json' = 'application/json; charset=utf-8'
    '.txt' = 'text/plain; charset=utf-8'
    '.png' = 'image/png'
    '.svg' = 'image/svg+xml'
    '.zdl' = 'application/octet-stream'
}

try {
    $listener.Start()
    $url = 'http://127.0.0.1:' + $listener.LocalEndpoint.Port + '/'
    Write-Host ''
    Write-Host 'FILTER DELAY BOOST - instalador experimental' -ForegroundColor Green
    Write-Host ('Endereco local: ' + $url)
    Write-Host 'Abra esse endereco no Microsoft Edge ou Opera.'
    Write-Host 'Nao precisa instalar Python, Node ou executar como administrador.'
    Write-Host 'Mantenha esta janela aberta. Encerre somente apos terminar a operacao USB.'
    Write-Host 'O servidor nao grava na pedaleira; a instalacao exige suas acoes no navegador.'
    Write-Host ''

    if (-not $SemNavegador) {
        try { Start-Process 'msedge.exe' -ArgumentList $url }
        catch {
            try { Start-Process $url }
            catch { Write-Host 'Abra o Edge e copie o endereco local acima.' }
        }
    }

    while ($true) {
        if (-not $listener.Pending()) { Start-Sleep -Milliseconds 50; continue }
        $client = $listener.AcceptTcpClient()
        $stream = $null
        $reader = $null
        try {
            $client.ReceiveTimeout = 5000
            $client.SendTimeout = 5000
            $stream = $client.GetStream()
            $stream.ReadTimeout = 5000
            $stream.WriteTimeout = 5000
            $reader = [IO.StreamReader]::new($stream, [Text.Encoding]::ASCII, $false, 1024, $true)
            $first = $reader.ReadLine()
            if ([string]::IsNullOrEmpty($first)) { continue }
            $parts = $first.Split(' ')
            $headers = 0
            $headerSize = $first.Length
            do {
                $line = $reader.ReadLine()
                $headers++
                $headerSize += $line.Length
                if ($headers -gt 100 -or $headerSize -gt 16384) { throw 'Cabecalho HTTP grande demais.' }
            } while (-not [string]::IsNullOrEmpty($line))

            $status = '200 OK'
            $type = 'text/plain; charset=utf-8'
            $bytes = [Text.Encoding]::UTF8.GetBytes('Requisicao invalida.')
            if ($parts.Length -ne 3 -or $parts[0] -notin @('GET', 'HEAD')) {
                $status = '405 Method Not Allowed'
            }
            else {
                $path = [Uri]::UnescapeDataString(($parts[1] -split '\?', 2)[0])
                $blocked = -not $path.StartsWith('/') -or $path.Contains('\') -or $path.Contains(':') -or $path -match '[\x00-\x1f\x7f]'
                if (-not $blocked -and $path.Equals('/', [StringComparison]::Ordinal)) { $path = '/index.html' }
                if (-not $blocked) {
                    $file = [IO.Path]::GetFullPath((Join-Path $root $path.TrimStart('/')))
                    $blocked = -not $file.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
                }
                if ($blocked) {
                    $status = '403 Forbidden'
                    $bytes = [Text.Encoding]::UTF8.GetBytes('Caminho bloqueado.')
                }
                elseif (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
                    $status = '404 Not Found'
                    $bytes = [Text.Encoding]::UTF8.GetBytes('Arquivo nao encontrado.')
                }
                else {
                    $bytes = [IO.File]::ReadAllBytes($file)
                    $extension = [IO.Path]::GetExtension($file).ToLowerInvariant()
                    if ($mime.ContainsKey($extension)) { $type = $mime[$extension] }
                    else { $type = 'application/octet-stream' }
                }
            }
            $response = "HTTP/1.1 $status`r`nContent-Type: $type`r`nContent-Length: $($bytes.Length)`r`nCache-Control: no-store`r`nX-Content-Type-Options: nosniff`r`nConnection: close`r`n`r`n"
            $header = [Text.Encoding]::ASCII.GetBytes($response)
            $stream.Write($header, 0, $header.Length)
            if ($parts[0] -ne 'HEAD') { $stream.Write($bytes, 0, $bytes.Length) }
            $stream.Flush()
        }
        catch { Write-Host ('Requisicao local interrompida: ' + $_.Exception.Message) }
        finally {
            if ($reader) { $reader.Dispose() }
            if ($stream) { $stream.Dispose() }
            $client.Close()
        }
    }
}
finally { $listener.Stop() }
