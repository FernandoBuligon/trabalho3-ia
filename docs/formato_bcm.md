# Formato binário `.BCM` do Expert SINTA (Etapa 2)

Este formato foi obtido por engenharia reversa de `EXSYSTEM.PAS` (`SaveToFile`/`LoadFromFile`) e validado por round-trip. A implementação está em `gerador/bcm.py`.

## Tipos primitivos
O código foi compilado em Delphi 32 bits com `{$H-}` e `{$A-}`.

| Tipo Pascal | Bytes | Observação |
|-------------|-------|------------|
| `TMyInteger` (smallint) | 2 | inteiro com sinal, little-endian |
| `boolean` | 1 | 0/1 |
| `string` (ShortString) | 256 | 1 byte de tamanho + 255 bytes de texto (cp1252); os bytes após o texto são lixo de memória |
| `string[2]` | 3 | operador da premissa |
| `real` | 6 | **Real48** do Turbo Pascal: expoente com bias 129, mantissa de 39 bits, sinal no bit 7 do último byte |

## Sequência do arquivo

```
Header      10 bytes: 2D 0C BD 16 63 28 F3 97 CA + versão (0x21 = 1.0, 0x22 = 1.1)
Proteção    senha string(256) + permissão int16 + usaSenha bool          = 259 bytes
Info        nome str, autores str, nLinhas int16 + linhas str[], arquivoAjuda str,
            mostrarAbertura bool, [v1.1] 3 × (fórmula str + usarPadrão bool) (E, OU, conclusão)
Variáveis   n int16 + n × {código int16, nome str, multi bool, numérica bool}            (260)
Valores     n int16 + n × {código int16, nome str, códVar int16, posição int16}          (262)
Cabeças     n int16 + n × {códRegra int16, códVar int16, códValor int16, CNF real48}     (12)
Caudas      n int16 + n × {códRegra int16, códVar int16, operador str[2], códValor int16,
                           conectivo int16, negação bool}                                (12)
Regras      n int16 + n × {código int16, nome str, posição int16}                        (260)
Fórmulas    n int16 + n × {código int16, texto str}                                      (258)
Perguntas   n int16 + n × {códVar int16, pergunta str, nPorquê int16 + linhas str[], [v1.1] usaCNF bool}
Objetivos   n int16 + n × {códVar int16, [v1.1] mostrarResultados bool}
Contextos   n int16 + n × {código int16, contexto int16}
Opções      prioridade int16 (0 = E, 1 = OU), CNF mínimo real48 (fração), examinarTudo bool
```

## Semântica (confirmada no código e no SINTA real)
- **Códigos de valor** são globais (únicos entre todas as variáveis). Os valores especiais são `-1` = DESCONHECIDO, `-2` = Sim e `-3` = Não. Uma variável sem valores é lógica (Sim/Não).
- Em uma **variável numérica**, `códValor` aponta para a tabela **Fórmulas**, cujo texto é um número ou uma expressão.
- **Conectivo** (`cnAND` = 0, `cnOR` = 1, `cnTHEN` = 2): é a ligação **com a próxima** premissa. A última premissa da regra recebe `cnTHEN`. O motor monta a expressão como `1E 2OU 3ENTÃO` (`TailResult`).
- A **ordem das premissas e conclusões** de uma regra é a ordem em que aparecem no arquivo (o índice preserva a inserção para códigos iguais).
- O **CNF** é gravado como fração: 1,0 = 100%.
- A **ordem das regras** é dada pelo campo `posição`. O SINTA grava os registros numa ordem "balanceada" para a árvore binária, mas a leitura aceita qualquer ordem.

## Validações realizadas (Etapa 3)
1. As 4 bases de exemplo do SINTA (VINHOS ×2, SECAJU ×2) foram lidas e regravadas **idênticas byte a byte**.
2. Real48 testado com codificação e decodificação de 10 valores.
3. Base sintética (`saida/TESTE.BCM`) com variável lógica, univalorada, multivalorada, duas numéricas, E/OU, NÃO, DESCONHECIDO, `<>`, `>=`, `<`, várias conclusões, perguntas com "por quê", objetivo oculto e acentuação:
   - escrita → leitura → reescrita idêntica;
   - **aberta no ExSINTA real**, regras exibidas corretamente em *Sistema › Visualizar*;
   - **regravada pelo ExSINTA**: semântica idêntica à original (`test_formato.py --comparar`);
   - **consulta executada no ExSINTA** (respostas Sim, ação, 2010, 120): resultado *Filme A, CNF 89,85%*, igual ao cálculo manual 0,855 ⊕ 0,30 = 0,8985.

## Observações práticas
- A flag de negação (`NÃO`) não aparece na visualização de regras do SINTA. Por isso, nas bases deste trabalho usamos o operador `<>`, que é mais legível.
- Arquivos `.BCM` com atributo **somente leitura** não abrem ("File access denied").
