# Trabalho 3: Sistemas Especialistas (Expert SINTA)

**Entregáveis**

| Arquivo | O que é |
|---|---|
| `saida/Famosos.bcm` | Sistema 1, **Quem é o Famoso?** (97 famosos, 827 regras) |
| `saida/Filmes.bcm` | Sistema 2, **Que Filme Eu Vejo?** (145 filmes, 2.374 regras) |
| `relatorio/Relatorio.md` | Relatório completo |

**Para executar:** abra `ferramenta/ExSINTA.exe` → *Arquivo › Abrir base* → escolha um dos `.bcm` em `saida/` → *Consulta › Iniciar* (F9).
O arquivo `.bcm` não pode estar marcado como somente leitura.

**Para regenerar e validar tudo:** `cd gerador` e `python gerar_tudo.py --avaliar` (Python 3 + PyYAML).

O plano e o registro de validação de cada etapa estão em `PLANO_DE_TRABALHO.md`.

**Revisão de entrega (25/11/2026):** limite de duração obrigatório em todas as
recomendações, diretores individuais e correções de dados documentadas em
[dados/FONTES.md](dados/FONTES.md). São 3.201 regras no total.

A validação atual inclui 881 consultas de regressão, 4.000 consultas aleatórias
sem falha do motor e 1.000 consultas com menores sem violação das classificações
cadastradas. Resultados e hashes: [testes/revisao/manifesto.json](testes/revisao/manifesto.json).
As capturas do ExSINTA e bases regravadas são **históricas**. A revisão atual foi
validada no simulador; não houve nova execução da interface Windows neste ambiente.

Para a entrega, incluir `saida/`, `relatorio/` (com imagens e apêndices), `dados/`,
`gerador/`, `testes/`, `docs/`, este README e o plano. O executável para a
apresentação está em `ferramenta/`. O enunciado não obriga relatório em PDF.
