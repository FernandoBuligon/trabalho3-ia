param([Parameter(Mandatory=$true)][string]$Base)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$here\win32.ps1"
Open-SintaBase $Base
"aberta: $Base"
