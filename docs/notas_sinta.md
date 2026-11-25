# Notas sobre o Expert SINTA (Etapa 0)

Fontes consultadas: `Manual - Expert SINTA.pdf` (v1.1, LIA/UFC), além de
`sinta/SINTA/sintascr/LIBRARY/EXSYSTEM.PAS`, `EXDATAST.PAS` e `EXCONSTS.PAS`.

## 1. Modelo de conhecimento
- Regras de produção `SE ... ENTÃO ...` com **encadeamento para trás** (backward chaining).
- Cauda (premissa): `<conectivo> [NÃO] <atributo> <operador> <valor>`.
  - Conectivos: `E` (cnAND = 0) e `OU` (cnOR = 1). A primeira cauda usa o código 2 (cnTHEN/"SE"); isso será confirmado na Etapa 2.
  - Operadores: `=`, `<>`, `>`, `<`, `>=`, `<=`. Os quatro últimos só valem para variáveis numéricas. O operador é guardado como `string[2]`.
  - Negação: flag booleana por cauda.
- Cabeça (conclusão): `<atributo> = <valor> CNF <0..100>`. O `=` é atribuição, e o CNF vazio equivale a 100%.
- A precedência entre E e OU é configurável. O padrão é `Priority = cnAND`, ou seja, `A e B ou C` é lido como `(A e B) ou C`.

## 2. Variáveis
- **Univalorada:** um valor por vez; um valor novo substitui o anterior.
- **Multivalorada:** acumula valores. A busca continua até toda a base ser explorada, por isso é ideal para objetivos de "recomendação" que devem listar vários itens.
- **Numérica:** sempre univalorada, sem lista de valores. A "lista" guarda apenas um intervalo (`a;b`). Em regras, o valor é uma fórmula/número (tabela `Formulas`; o `ValCode` da cauda aponta para a fórmula).
- Uma variável sem valores definidos é tratada como lógica (Sim/Não: `YES = -2`, `NO = -3`).
- Valor especial `DESCONHECIDO` (código -1): o usuário pode responder "não sei".

## 3. Fatores de confiança (padrão possibilista)
- Conclusão: CNF final = CNF(premissa) × CNF(regra).
- E: c1 × c2.
- OU: c1 + c2 − c1·c2.
- Mesmo valor atribuído duas vezes: ca + cn − ca·cn (acumula evidência).
- Limiar mínimo para considerar uma igualdade/regra verdadeira: **50%** (`MIN_VALUE = 0.5`, configurável).
- As fórmulas de E/OU/conclusão podem ser personalizadas (ex.: `Min(cnf1, cnf2)`).

**Consequências para o projeto:**
1. Uma regra com 3 premissas respondidas com CNF 100% dispara normalmente. Se o usuário responder com CNF 70% em duas delas, o resultado é 0,49 e a regra **falha**. Por isso, as regras de recomendação devem ter poucas premissas (2 a 4), usar **variáveis intermediárias** e aproveitar o **acúmulo de CNF** de várias regras parciais sobre o mesmo valor (ca + cn − ca·cn). Esse é o mecanismo de "pontuação por evidências" da abordagem em camadas.
2. Os objetivos de recomendação devem ser **multivalorados**, para que o SINTA liste vários itens ranqueados por CNF.
3. Respostas DESCONHECIDO fazem as regras daquela premissa falharem. As regras parciais garantem que haja resposta mesmo assim.

## 4. Elementos de uma base
Variáveis + valores, regras (ordem importa: são avaliadas na ordem da lista), **objetivos** (lista ordenada de variáveis, com a flag "mostrar resultados"), perguntas (texto, "por quê?" com várias linhas, e a flag "aceita CNF na resposta"), informações (nome, autores, texto de abertura, exibir abertura), contextos de ajuda (arquivo .HLP, opcional), opções (precedência, CNF mínimo, avaliar regras completamente) e senha.

**Simulação de encadeamento para frente:** colocar variáveis intermediárias na lista de objetivos com "mostrar resultados" desmarcado. Isso força a ordem das perguntas.

## 5. Limites práticos (vindos do código-fonte)
- Strings são `ShortString` (`{$H-}`): **no máximo 255 caracteres** em nomes de variáveis, valores, perguntas e linhas de texto.
- Códigos são `TMyInteger` = inteiro de 16 bits com sinal: **no máximo 32767** variáveis, valores, regras, caudas e cabeças (as contagens totais também são int16).
- O "por quê" e o texto de abertura são listas de linhas, com uma `ShortString` por linha.
- Não há verificação de inconsistência lógica (o manual diz isso explicitamente).
- Codificação de texto: ANSI do Windows (cp1252), então acentos são aceitos.

## 6. Formato do arquivo `.BCM` (detalhado na Etapa 2)
Ordem de gravação: cabeçalho (10 bytes) → proteção → info → variáveis → valores → cabeças → caudas → regras → fórmulas → perguntas → objetivos → contextos → opções gerais.
