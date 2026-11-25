# Funcoes Win32 para operar o ExSINTA por mensagens (sem roubar o foco do usuario).
Add-Type -AssemblyName System.Drawing
if (-not ("Win.U" -as [type])) {
Add-Type @'
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
namespace Win {
public class U {
 public delegate bool EnumProc(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
 [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, string l);
 [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
 [DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string t);
 [DllImport("user32.dll")] public static extern IntPtr GetMenu(IntPtr h);
 [DllImport("user32.dll")] public static extern int GetMenuItemCount(IntPtr m);
 [DllImport("user32.dll")] public static extern IntPtr GetSubMenu(IntPtr m, int i);
 [DllImport("user32.dll")] public static extern uint GetMenuItemID(IntPtr m, int i);
 [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern int GetMenuString(IntPtr m, uint id, StringBuilder s, int n, uint f);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
 public static string T(IntPtr h){ var s=new StringBuilder(512); GetWindowText(h,s,512); return s.ToString(); }
 public static string K(IntPtr h){ var s=new StringBuilder(256); GetClassName(h,s,256); return s.ToString(); }
 public static List<IntPtr> Tops(uint pid){ var l=new List<IntPtr>(); EnumWindows((h,x)=>{uint p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)) l.Add(h); return true;}, IntPtr.Zero); return l; }
 public static List<IntPtr> Kids(IntPtr w){ var l=new List<IntPtr>(); EnumChildWindows(w,(h,x)=>{ l.Add(h); return true;}, IntPtr.Zero); return l; }
}}
'@
}

function Get-SintaTops {
  $p = Get-Process ExSINTA -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { return @() }
  return [Win.U]::Tops([uint32]$p.Id)
}
function Get-Kids($w) { return [Win.U]::Kids($w) }
function Click-Button($w, [string]$text) {
  $b = Get-Kids $w | Where-Object { [Win.U]::K($_) -like "*Button*" -or [Win.U]::K($_) -eq "TBitBtn" } |
       Where-Object { [Win.U]::T($_) -like $text -and [Win.U]::IsWindowVisible($_) } | Select-Object -First 1
  if (-not $b) { throw "botao '$text' nao encontrado em '$([Win.U]::T($w))'" }
  [void][Win.U]::PostMessage($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero)
}
function Get-VisibleOptions($w) {
  return @(Get-Kids $w | Where-Object { [Win.U]::K($_) -eq "TVarOption" -and [Win.U]::IsWindowVisible($_) } |
           ForEach-Object { [Win.U]::T($_) })
}
function Click-Option($w, [string]$text) {
  $o = Get-Kids $w | Where-Object { [Win.U]::K($_) -eq "TVarOption" -and [Win.U]::IsWindowVisible($_) -and [Win.U]::T($_) -eq $text } | Select-Object -First 1
  if (-not $o) { throw "opcao '$text' nao encontrada" }
  # BM_CLICK sincrono para o checkbox alternar antes do OK
  [void][Win.U]::SendMessage($o, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero)
}
function Set-OptionCnf($w, [string]$text, [string]$cnf) {
  # o campo de CNF (TLimitedEdit) de cada opcao vem logo antes dela na lista de filhos
  $kids = @(Get-Kids $w)
  for ($i = 0; $i -lt $kids.Count; $i++) {
    if ([Win.U]::K($kids[$i]) -eq "TVarOption" -and [Win.U]::T($kids[$i]) -eq $text) {
      for ($j = $i - 1; $j -ge 0; $j--) {
        if ([Win.U]::K($kids[$j]) -eq "TLimitedEdit") { [void][Win.U]::SendMessage($kids[$j], 0x000C, [IntPtr]::Zero, $cnf); return }
        if ([Win.U]::K($kids[$j]) -eq "TVarOption") { break }
      }
    }
  }
  throw "campo de CNF da opcao '$text' nao encontrado"
}
function Set-EditText($w, [string]$text) {
  $e = Get-Kids $w | Where-Object { [Win.U]::K($_) -eq "TEdit" -and [Win.U]::IsWindowVisible($_) } | Select-Object -First 1
  if (-not $e) { throw "campo numerico nao encontrado" }
  [void][Win.U]::SendMessage($e, 0x000C, [IntPtr]::Zero, $text)
}
function Test-QuestionReady($w) {
  $k = Get-Kids $w
  return [bool]($k | Where-Object { ([Win.U]::K($_) -eq "TVarOption" -or [Win.U]::K($_) -eq "TEdit") -and [Win.U]::IsWindowVisible($_) } | Select-Object -First 1)
}
function Save-WindowShot($h, [string]$file) {
  $r = New-Object Win.U+RECT; [void][Win.U]::GetWindowRect($h, [ref]$r)
  $w = $r.R - $r.L; $hh = $r.B - $r.T
  $bmp = New-Object Drawing.Bitmap $w, $hh; $g = [Drawing.Graphics]::FromImage($bmp)
  $dc = $g.GetHdc(); [void][Win.U]::PrintWindow($h, $dc, 2); $g.ReleaseHdc($dc); $bmp.Save($file)
}
function Get-MainWindow {
  $h = [Win.U]::FindWindow("TfrmMain", [NullString]::Value)
  return $h
}
function Invoke-SintaMenu([string]$pattern) {
  $h = Get-MainWindow
  function Walk($m, $prefix) {
    $n = [Win.U]::GetMenuItemCount($m)
    for ($i = 0; $i -lt $n; $i++) {
      $sb = New-Object Text.StringBuilder 256
      [void][Win.U]::GetMenuString($m, [uint32]$i, $sb, 256, 0x400)
      $sub = [Win.U]::GetSubMenu($m, $i); $id = [Win.U]::GetMenuItemID($m, $i)
      $txt = "$prefix/$($sb.ToString())"
      if ($sub -ne [IntPtr]::Zero) { Walk $sub $txt } else { [pscustomobject]@{Path=$txt; Id=$id} }
    }
  }
  $it = Walk ([Win.U]::GetMenu($h)) "" | Where-Object { $_.Path -like $pattern } | Select-Object -First 1
  if (-not $it) { throw "menu nao encontrado: $pattern" }
  [void][Win.U]::PostMessage($h, 0x0111, [IntPtr][int]$it.Id, [IntPtr]::Zero)
  return $it.Path
}
function Open-SintaBase([string]$base) {
  $tool = "C:\Users\fbuli\OneDrive\Documentos\Trabalho 3 - Sistemas Especialistas\ferramenta"
  Get-Process ExSINTA -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Milliseconds 800
  (Get-Item $base).IsReadOnly = $false
  $ini = "[Janela Principal]`r`nEstado=0`r`nCima=0`r`nEsquerda=0`r`nLargura=1100`r`nAltura=760`r`n[Geral]`r`nDica do dia=0`r`n[Arquivos]`r`n1=" + $base.ToUpper() + "`r`n"
  New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\VirtualStore\Windows" | Out-Null
  [IO.File]::WriteAllText("$env:LOCALAPPDATA\VirtualStore\Windows\EXSINTA.INI", $ini, [Text.Encoding]::GetEncoding(1252))
  Start-Process -FilePath "$tool\ExSINTA.exe" -WorkingDirectory $tool
  $t = 0; while ((Get-MainWindow) -eq [IntPtr]::Zero -and $t -lt 10000) { Start-Sleep -Milliseconds 200; $t += 200 }
  Start-Sleep -Milliseconds 1500
  Invoke-SintaMenu "*&1 *" | Out-Null
  Start-Sleep -Milliseconds 2500
}
