# Evidências históricas de regravação

Estes arquivos foram produzidos no Expert SINTA em uma etapa anterior:

| Arquivo | Regras | Variáveis |
|---|---:|---:|
| FAMOSOS_SINTA.BCM | 820 | 32 |
| FILMES_SINTA.BCM | 1.476 | 26 |

**Não são cópias regravadas dos entregáveis atuais.** Não devem ser comparados
às bases finais como se fossem semanticamente idênticos. Foram preservados
como registro histórico; não foram substituídos por arquivos do gerador.

O manifesto em [../revisao/manifesto.json](../revisao/manifesto.json) identifica
os hashes e a diferença em relação às bases atuais.

Para repetir a prova no Windows, abrir cada arquivo de `saida/` no ExSINTA,
salvar uma cópia em uma nova pasta e executar:

```text
python gerador/test_formato.py --comparar saida/Famosos.bcm CAMINHO/FAMOSOS_SINTA.BCM
python gerador/test_formato.py --comparar saida/Filmes.bcm CAMINHO/FILMES_SINTA.BCM
```

Usar as cópias de `saida/` para entrega. O resultado esperado da comparação
com uma nova regravação é `SEMÂNTICA IDÊNTICA`.
