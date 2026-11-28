# Bases regravadas pelo Expert SINTA

Prova de compatibilidade do formato: cada base final de `saida/` foi aberta no
**ExSINTA 1.1b real** e salva pelo próprio SINTA (*Arquivo › Salvar base*).
Executado em 28/11/2026, no Linux pelo Wine 11.0.

| Arquivo | Origem | Regras | Comparação com `saida/` |
|---|---|---:|---|
| `FAMOSOS_SINTA.BCM` | `saida/Famosos.bcm` regravada pelo ExSINTA | 827 | semântica idêntica |
| `FILMES_SINTA.BCM` | `saida/Filmes.bcm` regravada pelo ExSINTA | 2.374 | semântica idêntica |

"Semântica idêntica" significa mesmas variáveis, valores, regras, premissas,
conclusões, perguntas, objetivos e opções. Os bytes diferem só no preenchimento
não usado das strings Pascal de tamanho fixo, que o Delphi grava com o conteúdo
que estava na memória.

Usar as bases de `saida/` para a entrega. Os hashes estão em
[../revisao/manifesto.json](../revisao/manifesto.json).

## Repetir

```bash
cd gerador
python regravar_gui.py
# ou, para comparar uma regravação feita à mão:
python test_formato.py --comparar ../saida/Filmes.bcm CAMINHO/FILMES_SINTA.BCM
```

Os requisitos (Windows, ou Wine + Python embeddable) estão em
[../gui/README.md](../gui/README.md).
