# Validação da revisão de entrega

As consultas JSON desta pasta foram executadas pelo **simulador Python**.
As mesmas oito consultas foram repetidas no **ExSINTA real** em 28/11/2026,
com resultados iguais (registros em `../gui/`), e as bases finais foram
regravadas pelo próprio SINTA com semântica idêntica (`../sinta_regravado/`).
O manifesto relaciona hashes SHA-256 das bases, das regravações e dos artefatos.

Resultados da revisão de 25/11/2026:

- Famosos: 827 regras; Filmes: 2.374 regras; total: 3.201.
- Testes do formato e do gerador aprovados; auditoria sem erros ou avisos.
- 881 consultas de regressão aprovadas: exclusão um minuto abaixo da duração,
  inclusão no limite, respostas em branco/sem limite e diretores individuais.
- 4.000 consultas aleatórias sem falhas do motor.
- 1.000 consultas com menores sem violação das classificações cadastradas.
- Todas as regras alcançadas pelo conjunto de consultas aleatórias e dirigidas.
- Sem recomendações: famosos 37/2.000 (1,85%); filmes 62/2.000 (3,1%).
- Bases conferidas contra compilação do zero: idênticas byte a byte.

O caso `filmes_2.json` demonstra a correção do limite de 100 minutos:
A Viagem de Chihiro e os outros nove filmes acima do limite não aparecem mais,
nem no simulador nem no ExSINTA real (`../gui/filmes_2/`).

Reproduzir toda a validação e atualizar o manifesto:

```bash
cd gerador
python gerar_tudo.py --avaliar
```

Pesquisa factual por amostragem: 26 registros de fontes para 20 itens distintos,
com escopo explícito em `dados/FONTES.md`. Os testes não verificam a verdade de
cada atributo cadastrado.
