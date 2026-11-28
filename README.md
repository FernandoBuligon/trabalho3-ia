# Trabalho 3: Sistemas Especialistas (Expert SINTA)

**Entregáveis**

| Arquivo | O que é |
|---|---|
| `saida/Famosos.bcm` | Sistema 1, **Quem é o Famoso?** (97 famosos, 827 regras) |
| `saida/Filmes.bcm` | Sistema 2, **Que Filme Eu Vejo?** (145 filmes, 2.374 regras) |
| `relatorio/Relatorio.md` | Relatório completo |

**Para executar:** abra `ferramenta/ExSINTA.exe` → *Arquivo › Abrir base* → escolha um dos `.bcm` em `saida/` → *Consulta › Iniciar* (F9).
O arquivo `.bcm` não pode estar marcado como somente leitura.
No Linux ou no macOS, o ExSINTA roda pelo Wine: `wine ferramenta/ExSINTA.exe`.

**Para regenerar e validar tudo:** `cd gerador` e `python gerar_tudo.py --avaliar` (Python 3 + PyYAML).

O plano e o registro de validação de cada etapa estão em `PLANO_DE_TRABALHO.md`.

**Revisão de entrega (25/11/2026):** limite de duração obrigatório em todas as
recomendações, diretores individuais e correções de dados documentadas em
[dados/FONTES.md](dados/FONTES.md). São 3.201 regras no total.

A validação inclui 881 consultas de regressão, 4.000 consultas aleatórias
sem falha do motor e 1.000 consultas com menores sem violação das classificações
cadastradas. Resultados e hashes: [testes/revisao/manifesto.json](testes/revisao/manifesto.json).

**Validação no ExSINTA real (28/11/2026):** as duas bases finais foram abertas e
regravadas pelo próprio SINTA com semântica idêntica, e as oito consultas de
referência rodaram no ExSINTA com resultados iguais aos do simulador
([testes/gui/](testes/gui/README.md), [testes/sinta_regravado/](testes/sinta_regravado/README.md)).
O driver da interface (`gerador/gui/sinta_driver.py`) é em Python e roda no
Windows ou, no Linux/macOS, pelo Wine. Esta validação foi feita no Linux, pelo Wine.

Para a entrega, incluir `saida/`, `relatorio/` (com imagens e apêndices), `dados/`,
`gerador/`, `testes/`, `docs/`, este README e o plano. O executável para a
apresentação está em `ferramenta/`. O enunciado não obriga relatório em PDF.
