# Consultas no Expert SINTA real

Os diretórios `famosos_*` e `filmes_*` registram as oito consultas executadas no
**ExSINTA 1.1b real** com as bases finais (`saida/Famosos.bcm`, 827 regras, e
`saida/Filmes.bcm`, 2.374 regras), em 28/11/2026, no Linux pelo Wine 11.0.

Cada diretório contém:

| Arquivo | Conteúdo |
|---|---|
| `passos.json` | respostas dadas e opções que cada pergunta deve exibir |
| `simulador.json` | perguntas e resultados previstos pelo simulador Python |

O driver confere, pergunta a pergunta, se a ordem das perguntas e as opções
exibidas são exatamente as previstas pelo simulador. Os valores das janelas de
resultados (`TValuesGrid`, componente desenhado pelo próprio Delphi) não podem
ser lidos por mensagens, então a comparação com `simulador.json` é **visual**,
pelas capturas `resultado_N.png` que o driver grava em cada diretório. As
capturas não são versionadas (`.gitignore`); as usadas como figuras estão no
relatório entregue.
Nas oito consultas, todos os itens e graus de confiança visíveis coincidem com
o simulador, na mesma ordem. O ponto decimal (99.831 em vez de 99,831) vem do
locale en_US do Wine.

`filmes_2` (limite de 100 minutos) confirma a correção do limite de duração no
ExSINTA real: *A Viagem de Chihiro* (125 minutos) e os demais filmes acima do
limite não aparecem.


## Repetir

```bash
cd gerador
python casos_gui.py            # os oito casos (substitui estes diretórios)
python casos_gui.py filmes_2   # um caso
python regravar_gui.py         # prova de regravação (testes/sinta_regravado/)
python figuras_gui.py          # recaptura as figuras do relatório
```

- **Windows:** basta o Python instalado. (Nesta revisão o driver foi executado só pelo Wine;
  no Windows ele usa as mesmas chamadas Win32 do antigo driver PowerShell.)
- **Linux/macOS:** precisa do Wine e do Python *embeddable* para Windows (32 bits),
  extraído em `ferramenta/python-win32/` ou indicado pela variável `SINTA_PYWIN`:

  ```bash
  mkdir -p ferramenta/python-win32 && cd ferramenta/python-win32
  curl -LO https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-win32.zip
  unzip python-3.12.10-embed-win32.zip
  ```

O driver (`gerador/gui/sinta_driver.py`) opera o ExSINTA por mensagens Win32,
sem mouse nem teclado. No Wine, os menus de outro processo não podem ser lidos,
então ele usa os IDs de comando fixos do ExSINTA 1.1b (ver o comentário
`MENU_ESTATICO` no código).
