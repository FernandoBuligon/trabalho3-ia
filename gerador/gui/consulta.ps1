param(
  [Parameter(Mandatory=$true)][string]$Steps,     # JSON: [{"opcoes":[..],"marcar":[..]} | {"numero":"2010"} | {"opcoes":[..],"marcar":[]}]
  [Parameter(Mandatory=$true)][string]$Titulo,    # titulo da janela de perguntas (nome da base)
  [Parameter(Mandatory=$true)][string]$OutDir,    # onde salvar capturas dos resultados
  [int]$NResultados = 1,                           # janelas de resultado esperadas (objetivos visiveis)
  [switch]$FotoPerguntas,                          # salva captura de cada pergunta
  [switch]$ManterUltimo                            # nao fecha a ultima janela de resultado
)
# Executa uma consulta no ExSINTA ja aberto (base carregada), respondendo as
# perguntas por mensagens Win32 (sem foco). Valida, a cada pergunta, se as
# opcoes exibidas sao as esperadas. Ao final captura as janelas de resultado.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$here\win32.ps1"

function Wait-Window([scriptblock]$cond, [int]$ms = 30000) {
  $t = 0
  while ($t -lt $ms) {
    foreach ($w in (Get-SintaTops)) { if (& $cond $w) { return $w } }
    Start-Sleep -Milliseconds 150; $t += 150
  }
  return $null
}

$passos = Get-Content -Raw -Encoding UTF8 $Steps | ConvertFrom-Json
$log = @()
$script:nres = 0
function Save-Result($r) {
  Start-Sleep -Milliseconds 400
  $f = Join-Path $OutDir ("resultado_{0}.png" -f $script:nres); Save-WindowShot $r $f
  $script:log += "RESULTADO $($script:nres) -> $f"
  if ($ManterUltimo -and ($script:nres -eq $NResultados - 1)) { $script:nres++; return }
  Click-Button $r "*Fechar*"; $script:nres++
  Start-Sleep -Milliseconds 600
}
function Test-Result($w) { return [Win.U]::T($w) -eq "Resultados" }
function Test-Question($w) { return ([Win.U]::T($w) -eq $Titulo) -and (Test-QuestionReady $w) }

Invoke-SintaMenu "*&Iniciar*" | Out-Null
$sw0 = [Diagnostics.Stopwatch]::StartNew()
$primeira = Wait-Window { param($w) ([Win.U]::T($w) -eq "Abertura") -or (Test-Question $w) } 60000
if ($primeira -and [Win.U]::T($primeira) -eq "Abertura") {
  $log += ("abertura apos {0:N1}s" -f $sw0.Elapsed.TotalSeconds)
  Start-Sleep -Milliseconds 300; Click-Button $primeira "OK"; Start-Sleep -Milliseconds 400
}

$n = 0
foreach ($s in $passos) {
  $n++
  # resultados de objetivos visiveis podem surgir entre perguntas
  while ($true) {
    $q = Wait-Window { param($w) (Test-Question $w) -or (Test-Result $w) } 90000
    if ($q -and (Test-Result $q)) { $log += "(resultado intermediario antes da P$n)"; Save-Result $q; continue }
    break
  }
  if (-not $q) { $log += "ERRO pergunta $n nao apareceu"; break }
  Start-Sleep -Milliseconds 200
  if ($s.PSObject.Properties.Name -contains "numero") {
    Set-EditText $q $s.numero
    $log += "P$n numero=$($s.numero)"
  } else {
    $vis = Get-VisibleOptions $q
    $exp = @($s.opcoes)
    $okOpts = (@(Compare-Object ($vis | Sort-Object) ($exp | Sort-Object)).Count -eq 0)
    if (-not $okOpts) { $log += "ERRO P${n}: opcoes exibidas [$($vis -join ', ')] esperadas [$($exp -join ', ')]"; break }
    foreach ($m in @($s.marcar)) {
      $partes = $m -split "@@"
      Click-Option $q $partes[0]
      if ($partes.Count -gt 1) { Start-Sleep -Milliseconds 150; Set-OptionCnf $q $partes[0] $partes[1] }
    }
    $log += "P$n opcoes OK; marcado [$(@($s.marcar) -join ', ')]"
  }
  Start-Sleep -Milliseconds 250
  if ($FotoPerguntas) { Save-WindowShot $q (Join-Path $OutDir ("pergunta_{0:D2}.png" -f $n)) }
  Click-Button $q "OK"
  Start-Sleep -Milliseconds 500
}

$sw = [Diagnostics.Stopwatch]::StartNew()
while ($script:nres -lt $NResultados) {
  $r = Wait-Window { param($w) (Test-Result $w) -or (Test-Question $w) } 90000
  if (-not $r) { $log += "ERRO: janela de resultados $($script:nres) nao apareceu"; break }
  if (Test-Question $r) { $log += "ERRO: pergunta nao prevista"; Save-WindowShot $r (Join-Path $OutDir "pergunta_extra.png"); break }
  $log += ("resultado final apos {0:N1}s" -f $sw.Elapsed.TotalSeconds)
  Save-Result $r
}
$extra = $null
if (-not $ManterUltimo) { $extra = Wait-Window { param($w) Test-Question $w } 800 }
if ($extra) { $log += "AVISO: ainda ha pergunta aberta (nao prevista)"; Save-WindowShot $extra (Join-Path $OutDir "pergunta_extra.png") }
$log += "TOTAL perguntas respondidas: $n; janelas de resultado: $($script:nres)"
$log
