"""
Driver do ExSINTA por mensagens Win32 (substitui win32.ps1/consulta.ps1).

Roda em um Python *para Windows* (somente biblioteca padrão):
  - Windows: o próprio Python instalado;
  - Linux/macOS: o Python "embeddable" para Windows executado pelo Wine.
O lado portátil (gui_check.py) escolhe o executor automaticamente.

Comandos:
  abrir    --ferramenta DIR --base ARQ   fecha o ExSINTA, abre-o e carrega a base
  menu                                   lista os itens do menu principal
  executar --caminho PADRAO              aciona um item do menu (fnmatch)
  consulta --passos JSON --titulo T --saida DIR [--nresultados N] [--fotos] [--manter-ultimo]
  aba      --nome N --x X --arquivo PNG    clica numa aba dos resultados e captura
  regra    --indice I --arquivo PNG       abre uma regra no editor e captura
  capturar-base --arquivo PNG            captura a janela da base aberta
  salvar   --base ARQ                    Arquivo › Salvar base (prova de regravação)
  fechar                                 encerra o ExSINTA
"""
import argparse
import ctypes
import fnmatch
import json
import os
import struct
import subprocess
import sys
import time
import zlib
from ctypes import wintypes as W

u32 = ctypes.WinDLL("user32", use_last_error=True)
g32 = ctypes.WinDLL("gdi32")
k32 = ctypes.WinDLL("kernel32")

EnumProc = ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
u32.EnumWindows.argtypes = [EnumProc, W.LPARAM]
u32.EnumChildWindows.argtypes = [W.HWND, EnumProc, W.LPARAM]
u32.SendMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]
u32.SendMessageW.restype = W.LPARAM
u32.PostMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]
u32.FindWindowW.argtypes = [W.LPCWSTR, W.LPCWSTR]
u32.FindWindowW.restype = W.HWND
u32.GetMenu.argtypes = [W.HWND]
u32.GetMenu.restype = W.HMENU
u32.GetSubMenu.argtypes = [W.HMENU, ctypes.c_int]
u32.GetSubMenu.restype = W.HMENU
u32.GetMenuItemCount.argtypes = [W.HMENU]
u32.GetMenuItemID.argtypes = [W.HMENU, ctypes.c_int]
u32.GetMenuItemID.restype = W.UINT
u32.GetMenuStringW.argtypes = [W.HMENU, W.UINT, W.LPWSTR, ctypes.c_int, W.UINT]
u32.GetWindowRect.argtypes = [W.HWND, ctypes.POINTER(W.RECT)]
u32.PrintWindow.argtypes = [W.HWND, W.HDC, W.UINT]
u32.GetWindowDC.argtypes = [W.HWND]
u32.GetWindowDC.restype = W.HDC
u32.IsWindow.argtypes = [W.HWND]
u32.SetWindowPos.argtypes = [W.HWND, W.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, W.UINT]
u32.IsWindowVisible.argtypes = [W.HWND]
u32.GetDC.argtypes = [W.HWND]
u32.GetDC.restype = W.HDC
u32.GetClientRect.argtypes = [W.HWND, ctypes.POINTER(W.RECT)]
u32.ReleaseDC.argtypes = [W.HWND, W.HDC]
g32.CreateCompatibleDC.argtypes = [W.HDC]
g32.CreateCompatibleDC.restype = W.HDC
g32.CreateCompatibleBitmap.argtypes = [W.HDC, ctypes.c_int, ctypes.c_int]
g32.CreateCompatibleBitmap.restype = W.HBITMAP
g32.SelectObject.argtypes = [W.HDC, W.HGDIOBJ]
g32.SelectObject.restype = W.HGDIOBJ
g32.GetDIBits.argtypes = [W.HDC, W.HBITMAP, W.UINT, W.UINT, ctypes.c_void_p, ctypes.c_void_p, W.UINT]
g32.DeleteObject.argtypes = [W.HGDIOBJ]
g32.DeleteDC.argtypes = [W.HDC]
g32.BitBlt.argtypes = [W.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                       W.HDC, ctypes.c_int, ctypes.c_int, W.DWORD]

BM_CLICK, BM_GETCHECK, WM_SETTEXT, WM_COMMAND = 0x00F5, 0x00F0, 0x000C, 0x0111


def texto(h):
    b = ctypes.create_unicode_buffer(512)
    u32.GetWindowTextW(h, b, 512)
    return b.value


def classe(h):
    b = ctypes.create_unicode_buffer(256)
    u32.GetClassNameW(h, b, 256)
    return b.value


def visivel(h):
    return bool(u32.IsWindowVisible(h))


def pid_de(h):
    p = W.DWORD()
    u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    return p.value


def janela_principal():
    return u32.FindWindowW("TfrmMain", None)


def topos():
    m = janela_principal()
    if not m:
        return []
    pid, lst = pid_de(m), []

    def cb(h, _):
        if pid_de(h) == pid and visivel(h):
            lst.append(h)
        return True
    u32.EnumWindows(EnumProc(cb), 0)
    return lst


def filhos(w):
    lst = []

    def cb(h, _):
        lst.append(h)
        return True
    u32.EnumChildWindows(w, EnumProc(cb), 0)
    return lst


def clicar_botao(w, padrao):
    for b in filhos(w):
        k = classe(b)
        if ("Button" in k or k == "TBitBtn") and visivel(b) and fnmatch.fnmatchcase(texto(b), padrao):
            u32.PostMessageW(b, BM_CLICK, 0, 0)
            return
    raise RuntimeError(f"botão '{padrao}' não encontrado em '{texto(w)}'")


def opcoes_visiveis(w):
    return [texto(h) for h in filhos(w) if classe(h) == "TVarOption" and visivel(h)]


def marcar_opcoes(w, desejadas):
    """Deixa marcadas exatamente as opções desejadas. BM_CLICK alterna o estado,
    então só clica onde o estado atual (BM_GETCHECK) difere do desejado."""
    faltando = set(desejadas)
    for h in filhos(w):
        if classe(h) == "TVarOption" and visivel(h):
            t = texto(h)
            quer = t in faltando
            faltando.discard(t)
            if bool(u32.SendMessageW(h, BM_GETCHECK, 0, 0)) != quer:
                u32.SendMessageW(h, BM_CLICK, 0, 0)  # síncrono: alterna antes do OK
    if faltando:
        raise RuntimeError(f"opções não encontradas: {sorted(faltando)}")


def set_texto(h, t):
    buf = ctypes.create_unicode_buffer(t)
    u32.SendMessageW(h, WM_SETTEXT, 0, ctypes.cast(buf, ctypes.c_void_p).value)


def cnf_da_opcao(w, t, cnf):
    # o campo de CNF (TLimitedEdit) de cada opção vem antes dela na lista de filhos
    k = filhos(w)
    for i, h in enumerate(k):
        if classe(h) == "TVarOption" and texto(h) == t:
            for j in range(i - 1, -1, -1):
                if classe(k[j]) == "TLimitedEdit":
                    set_texto(k[j], cnf)
                    return
                if classe(k[j]) == "TVarOption":
                    break
    raise RuntimeError(f"campo de CNF da opção '{t}' não encontrado")


def separador_decimal():
    b = ctypes.create_unicode_buffer(8)
    k32.GetLocaleInfoW(0x0400, 0x000E, b, 8)  # LOCALE_USER_DEFAULT, LOCALE_SDECIMAL
    return b.value or ","


def campo_numerico(w, t):
    # o Delphi lê o número com o separador decimal do sistema (vírgula em pt-BR)
    t = str(t).replace(",", ".").replace(".", separador_decimal())
    for h in filhos(w):
        if classe(h) == "TEdit" and visivel(h):
            set_texto(h, t)
            return
    raise RuntimeError("campo numérico não encontrado")


def impressao(w):
    """Identifica a pergunta exibida. A janela é reaproveitada entre perguntas e
    os handles das opções podem ser reutilizados, por isso entram também o texto
    e o estado de marcação (BM_GETCHECK)."""
    return tuple((h, classe(h), texto(h), u32.SendMessageW(h, BM_GETCHECK, 0, 0))
                 for h in filhos(w) if classe(h) in ("TVarOption", "TEdit") and visivel(h))


def pergunta_pronta(w):
    return any(classe(h) in ("TVarOption", "TEdit") and visivel(h) for h in filhos(w))


def _png(path, larg, alt, bgra):
    raw = bytearray()
    for y in range(alt):
        lin = bgra[y * larg * 4:(y + 1) * larg * 4]
        rgb = bytearray(larg * 3)
        rgb[0::3], rgb[1::3], rgb[2::3] = lin[2::4], lin[1::4], lin[0::4]
        raw += b"\x00" + rgb

    def chunk(tipo, dados):
        c = tipo + dados
        return struct.pack(">I", len(dados)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", larg, alt, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


def _bits(dc_origem, x, y, larg, alt):
    mdc = g32.CreateCompatibleDC(dc_origem)
    bmp = g32.CreateCompatibleBitmap(dc_origem, larg, alt)
    old = g32.SelectObject(mdc, bmp)
    return mdc, bmp, old


def _ler(mdc, bmp, old, larg, alt):
    hdr = struct.pack("<IiiHHIIiiII", 40, larg, -alt, 1, 32, 0, 0, 0, 0, 0, 0)
    bi = ctypes.create_string_buffer(hdr, 40 + 16)
    buf = ctypes.create_string_buffer(larg * alt * 4)
    g32.SelectObject(mdc, old)
    g32.GetDIBits(mdc, bmp, 0, alt, buf, bi, 0)
    g32.DeleteObject(bmp)
    g32.DeleteDC(mdc)
    return buf.raw


def _vazia(px):
    """Imagem inteira de uma só cor (janela ainda não desenhada)."""
    return px == px[:4] * (len(px) // 4)


def _aparar(px, larg, alt):
    """Remove faixas pretas à direita/embaixo (área ainda não repintada)."""
    preto = b"\x00\x00\x00"
    def linha_preta(y):
        lin = px[y * larg * 4:(y + 1) * larg * 4]
        return all(lin[i:i + 3] == preto for i in range(0, len(lin), 4 * 7))
    while alt > 1 and linha_preta(alt - 1):
        alt -= 1
    return px[:larg * alt * 4], alt


def captura(h, path):
    """Captura a janela. No Windows, PrintWindow; se vier vazia (o Wine não
    renderiza PrintWindow entre processos), copia a área interna pela DC da
    janela. Não traz a janela para frente: o usuário pode continuar usando a tela."""
    r = W.RECT()
    u32.GetWindowRect(h, ctypes.byref(r))
    larg, alt = r.right - r.left, r.bottom - r.top
    sdc = u32.GetWindowDC(h)
    mdc, bmp, old = _bits(sdc, 0, 0, larg, alt)
    u32.PrintWindow(h, mdc, 2)
    px = _ler(mdc, bmp, old, larg, alt)
    u32.ReleaseDC(h, sdc)
    if not _vazia(px):
        _png(path, larg, alt, px)
        return "printwindow"
    c = W.RECT()
    u32.GetClientRect(h, ctypes.byref(c))
    larg, alt = c.right, c.bottom
    sdc = u32.GetDC(h)
    mdc, bmp, old = _bits(sdc, 0, 0, larg, alt)
    g32.BitBlt(mdc, 0, 0, larg, alt, sdc, 0, 0, 0x00CC0020)
    px = _ler(mdc, bmp, old, larg, alt)
    u32.ReleaseDC(h, sdc)
    if _vazia(px):
        return "vazia"
    px, alt = _aparar(px, larg, alt)
    _png(path, larg, alt, px)
    return "clientdc"


# IDs de comando do menu principal do ExSINTA 1.1b. A VCL numera os TMenuItem
# de 0 em diante, na ordem de criação (ordem do recurso TFRMMAIN no .exe).
# No Wine o menu de outro processo não pode ser lido (GetMenuItemCount = -1),
# então usamos esta tabela; confirmada no Wine (70 abre "Sobre o Expert SINTA").
MENU_ESTATICO = [
    ("/&Arquivo/&Nova base", 2), ("/&Arquivo/&Abrir base...", 3),
    ("/&Arquivo/&Salvar base", 4), ("/&Arquivo/Salvar &como...", 5),
    ("/&Arquivo/&1 ", 13), ("/&Arquivo/&2 ", 14), ("/&Arquivo/&3 ", 15), ("/&Arquivo/&4 ", 16),
    ("/&Arquivo/Sai&r", 18),
    ("/&Sistema/Visuali&zar...", 36), ("/&Sistema/&Variáveis", 38),
    ("/&Sistema/&Objetivos", 39), ("/&Sistema/Infor&mações", 43),
    ("/&Consulta/&Iniciar", 45), ("/&Consulta/&Finalizar", 46),
    ("/&Consulta/&Interromper a consulta", 48),
    ("/&?/So&bre o Expert SINTA...", 70),
]


def itens_menu():
    if u32.GetMenuItemCount(u32.GetMenu(janela_principal())) < 0:
        return list(MENU_ESTATICO)
    out = []

    def walk(m, pref):
        for i in range(u32.GetMenuItemCount(m)):
            b = ctypes.create_unicode_buffer(256)
            u32.GetMenuStringW(m, i, b, 256, 0x400)
            sub = u32.GetSubMenu(m, i)
            p = f"{pref}/{b.value}"
            if sub:
                walk(sub, p)
            else:
                out.append((p, u32.GetMenuItemID(m, i)))
    walk(u32.GetMenu(janela_principal()), "")
    return out


def executar_menu(padrao):
    for p, i in itens_menu():
        if fnmatch.fnmatchcase(p, padrao):
            u32.PostMessageW(janela_principal(), WM_COMMAND, i, 0)
            return p
    raise RuntimeError(f"menu não encontrado: {padrao}")


def esperar(cond, ms=30000):
    t0 = time.time()
    while (time.time() - t0) * 1000 < ms:
        for w in topos():
            try:
                if cond(w):
                    return w
            except OSError:
                pass
        time.sleep(0.15)
    return None


def fechar():
    subprocess.run(["taskkill", "/F", "/IM", "ExSINTA.exe"], capture_output=True)
    t0 = time.time()
    while janela_principal() and time.time() - t0 < 5:
        time.sleep(0.2)


def gravar_ini(base):
    ini = ("[Janela Principal]\r\nEstado=0\r\nCima=0\r\nEsquerda=0\r\nLargura=1100\r\nAltura=760\r\n"
           "[Geral]\r\nDica do dia=0\r\n[Arquivos]\r\n1=" + base.upper() + "\r\n").encode("cp1252")
    windir = os.environ.get("WINDIR", r"C:\Windows")
    destinos = [os.path.join(windir, "EXSINTA.INI")]
    if os.environ.get("LOCALAPPDATA"):  # Windows Vista+: virtualização de C:\Windows
        destinos.append(os.path.join(os.environ["LOCALAPPDATA"], "VirtualStore", "Windows", "EXSINTA.INI"))
    ok = False
    for d in destinos:
        try:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            open(d, "wb").write(ini)
            ok = True
        except OSError:
            pass
    if not ok:
        raise RuntimeError("não foi possível gravar EXSINTA.INI")


def abrir(ferramenta, base):
    fechar()
    time.sleep(0.5)
    os.chmod(base, 0o666)  # base somente leitura dá "File access denied"
    gravar_ini(os.path.abspath(base))
    # sem herdar stdout/stderr: o ExSINTA sobrevive ao driver e prenderia o pipe de quem chamou
    subprocess.Popen([os.path.join(ferramenta, "ExSINTA.exe")], cwd=ferramenta,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, close_fds=True)
    t0 = time.time()
    while not janela_principal() and time.time() - t0 < 20:
        time.sleep(0.2)
    if not janela_principal():
        raise RuntimeError("ExSINTA não abriu")
    time.sleep(1.5)
    executar_menu("*&1 *")
    t0 = time.time()
    nome = os.path.basename(base).upper()
    while time.time() - t0 < 90:  # a base aparece como janela MDI (TfrmBase) com o nome do arquivo
        if janela_base(nome):
            break
        time.sleep(0.3)
    else:
        raise RuntimeError(f"base não carregou: {base}")
    time.sleep(1.0)
    print(f"aberta em {time.time() - t0:.1f}s: {base}")


def janela_base(nome=None):
    for h in filhos(janela_principal()):
        if classe(h) == "TfrmBase" and (nome is None or texto(h).upper() == nome):
            return h
    return None


def aba(nome, x, arquivo):
    """Na janela de resultados aberta, clica na aba (TTabSet) na posição x e captura."""
    r = esperar(lambda w: texto(w) == "Resultados", 10000)
    if not r:
        raise RuntimeError("janela de resultados não está aberta")
    ts = next(h for h in filhos(r) if classe(h) == "TTabSet")
    pos = (8 << 16) | x
    u32.PostMessageW(ts, 0x0201, 1, pos)  # WM_LBUTTONDOWN
    u32.PostMessageW(ts, 0x0202, 0, pos)  # WM_LBUTTONUP
    time.sleep(1.5)
    print(f"aba {nome}:", captura(r, arquivo))


def regra(indice, arquivo):
    """Seleciona a regra (posição na lista da base, a partir de 0), abre no editor e captura."""
    base = janela_base()
    lista = next(h for h in filhos(base) if classe(h) == "TListBox")
    u32.SendMessageW(lista, 0x0186, indice, 0)  # LB_SETCURSEL
    antes = set(h for h in filhos(janela_principal()) if classe(h) != "TfrmBase")
    clicar_botao(base, "Abrir &Regra")
    t0 = time.time()
    ed = None
    while time.time() - t0 < 15 and not ed:
        time.sleep(0.3)
        ed = next((h for h in filhos(janela_principal())
                   if h not in antes and texto(h).startswith("Regra ") and visivel(h)), None)
    if not ed:
        raise RuntimeError("editor de regra não abriu")
    u32.SetWindowPos(ed, 0, 0, 0, 760, 520, 0x0002 | 0x0004)
    time.sleep(1.0)
    print(f"{texto(ed)}:", captura(ed, arquivo))
    u32.PostMessageW(ed, 0x0010, 0, 0)  # WM_CLOSE
    time.sleep(0.8)


def capturar_base(arquivo):
    """Captura a janela da base aberta (lista de regras)."""
    print("janela da base:", captura(janela_base(), arquivo))


def salvar(base):
    """Aciona Arquivo › Salvar base e espera o ExSINTA regravar o arquivo."""
    antes = os.stat(base).st_mtime_ns
    executar_menu("/&Arquivo/&Salvar base")
    t0 = time.time()
    while time.time() - t0 < 120:
        time.sleep(0.5)
        if os.stat(base).st_mtime_ns != antes:
            tam = -1
            while tam != os.path.getsize(base):  # espera terminar de escrever
                tam = os.path.getsize(base)
                time.sleep(1.0)
            print(f"regravada em {time.time() - t0:.1f}s: {base} ({tam} bytes)")
            return
    raise RuntimeError("o ExSINTA não regravou a base")


def consulta(passos_arq, titulo, saida, nres=1, fotos=False, manter_ultimo=False):
    passos = json.load(open(passos_arq, encoding="utf-8"))
    log, estado = [], {"n": 0}

    def eh_result(w):
        return texto(w) == "Resultados"

    # "Fim da consulta" é o único ShowMessage do SINTA e usa o título do aplicativo;
    # avisos e erros (MessageDlg) têm título próprio ("Error", "Warning"...).
    def eh_fim(w):
        return classe(w) == "TMessageForm" and texto(w) == "Expert SINTA"

    def eh_dialogo_erro(w):
        return classe(w) == "TMessageForm" and texto(w) != "Expert SINTA"

    def tratar_dialogo(w):
        f = os.path.join(saida, f"dialogo_{len(log)}.png")
        captura(w, f)
        log.append(f"ERRO: diálogo inesperado do SINTA '{texto(w)}' -> {os.path.basename(f)}")
        clicar_botao(w, "*OK*")

    def eh_perg(w):
        return texto(w) == titulo and pergunta_pronta(w)

    def objetivo(r):
        return next((texto(h) for h in filhos(r) if classe(h) == "TPanel" and texto(h)), "")

    def salvar_result(r):
        f = os.path.join(saida, f"resultado_{estado['n']}.png")
        # janela maior que a padrão: mostra mais linhas da lista ordenada por CNF
        u32.SetWindowPos(r, 0, 0, 0, 640, 620, 0x0002 | 0x0004)  # SWP_NOMOVE | SWP_NOZORDER
        for _ in range(10):  # a janela pode ainda não ter sido desenhada
            time.sleep(0.6)
            metodo = captura(r, f)
            if not metodo.startswith("vazia"):
                break
        alvo = objetivo(r)
        log.append(f"RESULTADO {estado['n']} ({alvo}) -> {os.path.basename(f)} [{metodo}]")
        if manter_ultimo and estado["n"] == nres - 1:
            estado["n"] += 1
            return

        # O formulário de resultados é único: "Fechar" o esconde e ele pode
        # reaparecer logo com o próximo objetivo. Conta como fechado se sumir,
        # se trocar de objetivo ou se surgir a próxima pergunta.
        def fim_da_consulta():
            # após o último resultado o SINTA abre o aviso modal "Fim da consulta"
            # e a janela de resultados continua visível atrás dele até o OK
            for w in topos():
                if eh_fim(w):
                    clicar_botao(w, "OK")
                    return True
                if eh_dialogo_erro(w):
                    tratar_dialogo(w)
                    return True
            return False

        def fechou():
            return (not u32.IsWindow(r) or not visivel(r) or objetivo(r) != alvo
                    or any(nova_perg(w) for w in topos()) or fim_da_consulta())
        t0 = time.time()
        while not fechou() and time.time() - t0 < 20:
            clicar_botao(r, "*Fechar*")  # repete: o clique pode chegar antes de a janela aceitar
            t1 = time.time()
            while not fechou() and time.time() - t1 < 2.0:
                time.sleep(0.05)
        if not fechou():
            raise RuntimeError(f"a janela de resultados ({alvo}) não fechou")
        estado["n"] += 1
        time.sleep(0.3)

    anterior = None  # impressão da pergunta já respondida (ainda pode estar na tela)

    def nova_perg(w):
        return eh_perg(w) and impressao(w) != anterior

    executar_menu("*&Iniciar*")
    t0 = time.time()
    w = esperar(lambda w: texto(w) == "Abertura" or eh_perg(w), 120000)
    if w and texto(w) == "Abertura":
        log.append(f"abertura após {time.time() - t0:.1f}s")
        time.sleep(0.3)
        clicar_botao(w, "OK")
        time.sleep(0.4)
    n = 0
    for s in passos:
        n += 1
        while True:
            q = esperar(lambda w: nova_perg(w) or eh_result(w) or eh_dialogo_erro(w), 120000)
            if q and eh_dialogo_erro(q):
                tratar_dialogo(q)
                q = None
                break
            if q and eh_result(q):
                log.append(f"(resultado intermediário antes da P{n})")
                salvar_result(q)
                continue
            break
        if not q:
            log.append(f"ERRO pergunta {n} não apareceu")
            break
        time.sleep(0.25)
        if "numero" in s:
            campo_numerico(q, s["numero"])
            log.append(f"P{n} numero={s['numero']}")
        else:
            vis = opcoes_visiveis(q)
            if sorted(vis) != sorted(s["opcoes"]):
                log.append(f"ERRO P{n}: opções exibidas {vis} esperadas {s['opcoes']}")
                break
            marcar_opcoes(q, [m.split("@@")[0] for m in s["marcar"]])
            for m in s["marcar"]:
                partes = m.split("@@")
                if len(partes) > 1:
                    time.sleep(0.15)
                    cnf_da_opcao(q, partes[0], partes[1])
            log.append(f"P{n} opções OK; marcado {s['marcar']}")
        time.sleep(0.25)
        if fotos:
            for _ in range(8):
                metodo = captura(q, os.path.join(saida, f"pergunta_{n:02d}.png"))
                if not metodo.startswith("vazia"):
                    break
                time.sleep(0.5)
            log.append(f"  foto P{n} [{metodo}]")
        anterior = impressao(q)
        clicar_botao(q, "OK")
        time.sleep(0.3)
    t1 = time.time()
    while estado["n"] < nres:
        r = esperar(lambda w: eh_result(w) or nova_perg(w) or eh_dialogo_erro(w), 120000)
        if r and eh_dialogo_erro(r):
            tratar_dialogo(r)
            break
        if not r:
            log.append(f"ERRO: janela de resultados {estado['n']} não apareceu")
            break
        if not eh_result(r):
            log.append("ERRO: pergunta não prevista")
            captura(r, os.path.join(saida, "pergunta_extra.png"))
            break
        log.append(f"resultado final após {time.time() - t1:.1f}s")
        salvar_result(r)
    extra = None if manter_ultimo else esperar(nova_perg, 800)
    if extra:
        log.append("AVISO: ainda há pergunta aberta (não prevista)")
        captura(extra, os.path.join(saida, "pergunta_extra.png"))
    if estado["n"] < nres:
        log.append(f"ERRO: {estado['n']} de {nres} janelas de resultado capturadas")
    log.append(f"TOTAL perguntas respondidas: {n}; janelas de resultado: {estado['n']}")
    print("\n".join(log))
    if any(l.startswith(("ERRO", "AVISO")) for l in log):
        sys.exit(1)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("abrir")
    a.add_argument("--ferramenta", required=True)
    a.add_argument("--base", required=True)
    sp.add_parser("menu")
    e = sp.add_parser("executar")
    e.add_argument("--caminho", required=True)
    c = sp.add_parser("consulta")
    c.add_argument("--passos", required=True)
    c.add_argument("--titulo", required=True)
    c.add_argument("--saida", required=True)
    c.add_argument("--nresultados", type=int, default=1)
    c.add_argument("--fotos", action="store_true")
    c.add_argument("--manter-ultimo", action="store_true")
    t = sp.add_parser("aba")
    t.add_argument("--nome", required=True)
    t.add_argument("--x", type=int, required=True)
    t.add_argument("--arquivo", required=True)
    rg = sp.add_parser("regra")
    rg.add_argument("--indice", type=int, required=True)
    rg.add_argument("--arquivo", required=True)
    cb = sp.add_parser("capturar-base")
    cb.add_argument("--arquivo", required=True)
    g = sp.add_parser("salvar")
    g.add_argument("--base", required=True)
    sp.add_parser("fechar")
    sp.add_parser("janelas")
    x = ap.parse_args()
    if x.cmd == "abrir":
        abrir(x.ferramenta, x.base)
    elif x.cmd == "menu":
        for p, i in itens_menu():
            print(i, p)
    elif x.cmd == "executar":
        print(executar_menu(x.caminho))
    elif x.cmd == "consulta":
        consulta(x.passos, x.titulo, x.saida, x.nresultados, x.fotos, x.manter_ultimo)
    elif x.cmd == "aba":
        aba(x.nome, x.x, x.arquivo)
    elif x.cmd == "regra":
        regra(x.indice, x.arquivo)
    elif x.cmd == "capturar-base":
        capturar_base(x.arquivo)
    elif x.cmd == "salvar":
        salvar(x.base)
    elif x.cmd == "fechar":
        fechar()
    elif x.cmd == "janelas":
        for w in topos():
            print(hex(w), classe(w), repr(texto(w)))


if __name__ == "__main__":
    main()
