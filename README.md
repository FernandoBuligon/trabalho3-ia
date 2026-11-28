# Trabalho 3: Sistemas Especialistas (Expert SINTA)

Fundamentos de Inteligência Artificial (CC6FIA), UTFPR, Câmpus Santa Helena.
Dois sistemas especialistas construídos no shell **Expert SINTA**, com as bases
geradas a partir de dados por um compilador próprio do formato `.BCM`.

## Entregáveis

| Arquivo | O que é |
|---|---|
| `saida/Famosos.bcm` | Sistema 1, **Quem é o Famoso?** (97 famosos, 827 regras) |
| `saida/Filmes.bcm` | Sistema 2, **Que Filme Eu Vejo?** (145 filmes, 2.374 regras) |
| Relatório (documento entregue no Moodle) | relatório oficial, no modelo da UTFPR, com as figuras do ExSINTA |
| `relatorio/Relatorio.md` | documentação técnica do projeto, com os apêndices das bases |

## Executar no Expert SINTA

Abra `ferramenta/ExSINTA.exe` → *Arquivo › Abrir base* → escolha um dos `.bcm`
em `saida/` → *Consulta › Iniciar* (F9). O arquivo `.bcm` não pode estar marcado
como somente leitura. No Linux ou no macOS, o ExSINTA roda pelo Wine:
`wine ferramenta/ExSINTA.exe`.

## Regenerar e validar

```bash
cd gerador
python gerar_tudo.py --avaliar   # valida dados, testa, gera, audita e avalia (Python 3 + PyYAML)
```

A validação inclui 881 consultas de regressão, 4.000 consultas aleatórias sem
falha do motor e 1.000 consultas com menores sem violação das classificações
cadastradas. Resultados e hashes: [testes/revisao/manifesto.json](testes/revisao/manifesto.json).

**No ExSINTA real** (28/11/2026): as duas bases finais foram abertas e
regravadas pelo próprio SINTA com semântica idêntica, e as oito consultas de
referência rodaram com resultados iguais aos do simulador
([testes/gui/](testes/gui/README.md), [testes/sinta_regravado/](testes/sinta_regravado/README.md)).
O driver da interface (`gerador/gui/sinta_driver.py`) é em Python, roda no
Windows ou, no Linux/macOS, pelo Wine, e falha se o ExSINTA se afastar do previsto.

```bash
cd gerador
python casos_gui.py      # as oito consultas no ExSINTA
python regravar_gui.py   # regravação das bases pelo ExSINTA
```

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `saida/` | bases geradas (`.bcm`), versões legíveis (`.txt`) e estatísticas (`.json`) |
| `dados/` | CSVs dos itens, esquemas, configuração das regras, validador e fontes da pesquisa ([FONTES.md](dados/FONTES.md)) |
| `gerador/` | formato `.BCM`, compilador de bases, simulador do motor, testes e driver do ExSINTA |
| `testes/` | avaliação, regressões, consultas no ExSINTA, bases regravadas e manifesto |
| `docs/` | notas sobre o SINTA e o formato `.BCM` |
| `ferramenta/` | `ExSINTA.exe` e ajuda (distribuição original) |
| `sinta/` | código-fonte do SINTA e bases de exemplo, usados na engenharia reversa |

O plano e o registro de cada etapa estão em [PLANO_DE_TRABALHO.md](PLANO_DE_TRABALHO.md).
As capturas de tela do ExSINTA não são versionadas; ficam no relatório entregue
e podem ser refeitas com `gerador/figuras_gui.py`.
