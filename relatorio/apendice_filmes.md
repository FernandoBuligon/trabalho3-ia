# Apêndice: Sistema 2, Que Filme Eu Vejo?

> Gerado automaticamente a partir de `saida/Filmes.bcm` por `gerador/gerar_apendices.py`.

## Números da base

| Item | Quantidade |
|---|---|
| Regras | 2374 |
| Premissas (caudas) | 17551 |
| Conclusões (cabeças) | 2481 |
| Variáveis | 28 |
| Valores | 578 |
| Perguntas | 16 |
| Objetivos | 9 |
| Itens na base de dados | 145 |
| Tamanho do arquivo .BCM | 1025 KB |

## Regras por tipo

| Tipo | Regras |
|---|---|
| compatibilidade | 44 |
| faixa etária do espectador mais novo (idade numérica -> faixa) | 5 |
| classificação indicativa (faixa -> classificações permitidas) | 8 |
| faixa de tempo (tempo numérico -> faixa) | 5 |
| duração aceitável (faixa de tempo -> durações, com tolerância) | 8 |
| gêneros indicados para a ocasião | 4 |
| perfil do espectador | 20 |
| modelo: perfil completo | 145 |
| modelo: gênero e clima | 145 |
| modelo: gênero e época | 145 |
| modelo: origem e gênero | 145 |
| modelo: ideal para a ocasião | 145 |
| modelo: aclamado pela crítica | 99 |
| modelo: obra única | 89 |
| modelo: sugestão pelo gênero | 145 |
| modelo: sugestão pelo clima | 145 |
| evidência: gênero em comum | 325 |
| evidência: clima em comum | 259 |
| evidência: ator | 255 |
| evidência: diretor | 155 |
| modelo: grande premiado | 27 |
| modelo: saga ou franquia | 56 |

## Objetivos (ordem de busca)

| # | Variável | Exibe resultado? |
|---|---|---|
| 1 | classificação permitida | não (fixa a ordem das perguntas) |
| 2 | gênero compatível | não (fixa a ordem das perguntas) |
| 3 | clima compatível | não (fixa a ordem das perguntas) |
| 4 | duração aceitável | não (fixa a ordem das perguntas) |
| 5 | origem compatível | não (fixa a ordem das perguntas) |
| 6 | época compatível | não (fixa a ordem das perguntas) |
| 7 | tipo de história compatível | não (fixa a ordem das perguntas) |
| 8 | perfil do espectador | sim |
| 9 | filme recomendado | sim |

## Variáveis

| Variável | Tipo | Papel | Valores |
|---|---|---|---|
| há menores assistindo | lógica (Sim/Não) | pergunta | Sim; Não |
| idade do mais novo | numérica | pergunta | faixa 3;17 |
| faixa do mais novo | univalorada | intermediária (inferida) | menos de 10 anos; 10 ou 11 anos; 12 ou 13 anos; 14 ou 15 anos; 16 ou 17 anos |
| classificação permitida | multivalorada | intermediária (inferida) | L; 10; 12; 14; 16; 18 |
| gênero preferido | multivalorada | pergunta | ação; aventura; animação; comédia; drama; crime; terror; suspense; … (15 valores) |
| gênero compatível | multivalorada | intermediária (inferida) | ação; aventura; animação; comédia; drama; crime; terror; suspense; ficção científica; fantasia; romance; musical; guerra; biografia |
| clima desejado | multivalorada | pergunta | divertido; emocionante; tenso; assustador; reflexivo; romântico; inspirador; épico; indiferente |
| clima compatível | multivalorada | intermediária (inferida) | divertido; emocionante; tenso; assustador; reflexivo; romântico; inspirador; épico |
| tem limite de tempo | lógica (Sim/Não) | pergunta | Sim; Não |
| tempo disponível | numérica | pergunta | faixa 60;300 |
| faixa de tempo | univalorada | intermediária (inferida) | menos de 100 min; 100 a 129 min; 130 a 159 min; 160 a 189 min; 190 min ou mais |
| duração aceitável | multivalorada | intermediária (inferida) | curta; média; longa; muito longa |
| origem preferida | univalorada | pergunta | nacional; internacional; indiferente |
| origem compatível | multivalorada | intermediária (inferida) | nacional; internacional |
| época preferida | multivalorada | pergunta | clássico (até 1979); anos 80; anos 90; anos 2000; anos 2010; anos 2020; clássicos e antigos (até os anos 90); recentes (de 2010 em diante); indiferente |
| época compatível | multivalorada | intermediária (inferida) | clássico (até 1979); anos 80; anos 90; anos 2000; anos 2010; anos 2020 |
| tipo de história preferido | univalorada | pergunta | baseada em fatos reais; ficção; indiferente |
| tipo de história compatível | multivalorada | intermediária (inferida) | baseada em fatos reais; ficção |
| companhia | univalorada | pergunta | sozinho(a); em casal; com amigos; com a família |
| gênero indicado para a ocasião | multivalorada | intermediária (inferida) | ação; aventura; animação; comédia; drama; crime; terror; suspense; ficção científica; fantasia; romance; musical; guerra; biografia |
| perfil do espectador | multivalorada | objetivo | Caçador(a) de adrenalina; Romântico(a) incurável; Destemido(a) do terror; Cinéfilo(a) reflexivo(a); Rei/Rainha da comédia; Coração mole; Sonhador(a) da fantasia e ficção; Nostálgico(a); Fã do cinema nacional; Sessão em família; Explorador(a) de histórias reais; Eclético(a) |
| quer premiados | lógica (Sim/Não) | pergunta | Sim; Não |
| interesse em franquias | univalorada | pergunta | gosto de sagas e franquias; prefiro filmes únicos; indiferente |
| quer escolher ator | lógica (Sim/Não) | pergunta | Sim; Não |
| ator preferido | multivalorada | pergunta | Al Pacino; Albert Brooks; Alexandre Rodrigues; Alice Braga; Amy Poehler; Andrew Garfield; André Ramiro; Anne Hathaway; … (191 valores) |
| quer escolher diretor | lógica (Sim/Não) | pergunta | Sim; Não |
| diretor preferido | multivalorada | pergunta | Aaron Horvath; Alejandro González Iñárritu; Alfonso Cuarón; Alfred Hitchcock; Alê Abreu; Andrew Adamson; Andrew Stanton; André Pellenz; … (116 valores) |
| filme recomendado | multivalorada | objetivo | Cidade de Deus; Central do Brasil; Tropa de Elite; Tropa de Elite 2; O Auto da Compadecida; O Auto da Compadecida 2; Ainda Estou Aqui; Bacurau; … (145 valores) |

## Perguntas e explicações ("Por quê?")

- **há menores assistindo**: "Alguém com menos de 18 anos vai assistir?"
  - *por quê:* A classificação indicativa é um filtro obrigatório: nenhum filme
  - *por quê:* acima da idade do espectador mais novo será recomendado.
- **idade do mais novo**: "Qual a idade do espectador mais novo?"
  - *por quê:* Usada para calcular as classificações indicativas permitidas (L, 10, 12, 14, 16, 18).
  - *por quê:* Se ficar em branco, por segurança só filmes livres (L) serão recomendados.
- **gênero preferido**: "Quais gêneros você quer ver?"
  - *por quê:* Marque quantos quiser. O gênero é um dos critérios principais.
- **clima desejado**: "Que sensação você procura no filme?"
  - *por quê:* divertido, emocionante (de chorar), tenso (adrenalina), assustador,
  - *por quê:* reflexivo (pra pensar), romântico, inspirador ou épico (grandioso).
- **tem limite de tempo**: "Você tem um limite de tempo para o filme?"
  - *por quê:* Se sim, o sistema evita filmes mais longos que o seu tempo.
- **tempo disponível**: "Quanto tempo você tem disponível (em minutos)?"
  - *por quê:* Todas as recomendações respeitam a duração exata cadastrada do filme.
  - *por quê:* Se ficar em branco, considera-se que não há limite.
- **origem preferida**: "Prefere filme nacional (brasileiro) ou internacional?"
  - *por quê:* Filtra o perfil completo e alimenta a regra 'origem e gênero'.
- **época preferida**: "De que época?"
  - *por quê:* Marque as décadas que quiser, ou um dos grupos.
- **tipo de história preferido**: "Prefere história baseada em fatos reais ou ficção?"
  - *por quê:* 22 filmes da base são baseados em fatos reais (biografias e eventos históricos).
- **companhia**: "Com quem você vai assistir?"
  - *por quê:* A ocasião sugere gêneros (ex.: casal -> romance, família -> animação).
- **quer premiados**: "Você prefere filmes premiados ou aclamados pela crítica?"
  - *por quê:* Filmes premiados (Oscar, Cannes, Berlim, Veneza, Globo de Ouro) ganham pontos extras.
- **interesse em franquias**: "Você gosta de sagas e franquias?"
  - *por quê:* Sagas (Star Wars, Harry Potter, Marvel...) ou filmes únicos ganham pontos extras.
- **quer escolher ator**: "Quer indicar atores ou atrizes de que você gosta?"
  - *por quê:* Se sim, será mostrada a lista de atores presentes na base.
- **ator preferido**: "Quais atores ou atrizes você gostaria de ver?"
  - *por quê:* Cada ator escolhido aumenta a confiança dos filmes em que atua.
- **quer escolher diretor**: "Quer indicar diretores de que você gosta?"
  - *por quê:* Se sim, será mostrada a lista de diretores presentes na base.
- **diretor preferido**: "Quais diretores você prefere?"
  - *por quê:* Cada diretor escolhido aumenta a confiança dos filmes que dirigiu (CNF 60%).

## Exemplos de regras (como aparecem no SINTA)

```
REGRA 47: faixa do mais novo: 12 ou 13 anos
  SE    idade do mais novo >= 12
  E     idade do mais novo < 14
  ENTÃO faixa do mais novo = 12 ou 13 anos CNF 100%
```

```
REGRA 55: classificação: 12 ou 13 anos
  SE    há menores assistindo = Sim
  E     faixa do mais novo = 12 ou 13 anos
  ENTÃO classificação permitida = L CNF 100%
  E     classificação permitida = 10 CNF 100%
  E     classificação permitida = 12 CNF 100%
```

```
REGRA 52: classificação: idade não informada
  SE    há menores assistindo = Sim
  E     faixa do mais novo = DESCONHECIDO
  ENTÃO classificação permitida = L CNF 100%
```

```
REGRA 68: duração: 130 a 159 min
  SE    tem limite de tempo = Sim
  E     faixa de tempo = 130 a 159 min
  ENTÃO duração aceitável = curta CNF 100%
  E     duração aceitável = média CNF 100%
  E     duração aceitável = longa CNF 60%
```

```
REGRA 71: ocasião: em casal
  SE    companhia = em casal
  ENTÃO gênero indicado para a ocasião = romance CNF 100%
  E     gênero indicado para a ocasião = comédia CNF 80%
  E     gênero indicado para a ocasião = drama CNF 70%
  E     gênero indicado para a ocasião = musical CNF 70%
```

```
REGRA 75: perfil: adrenalina (ação)
  SE    gênero preferido = ação
  OU    gênero preferido = suspense
  OU    gênero preferido = crime
  E     clima desejado = tenso
  ENTÃO perfil do espectador = Caçador(a) de adrenalina CNF 100%
```

```
REGRA 84: perfil: fantasia e ficção
  SE    gênero preferido = fantasia
  OU    gênero preferido = ficção científica
  OU    gênero preferido = animação
  E     clima desejado = épico
  OU    clima desejado = emocionante
  OU    clima desejado = divertido
  E     duração aceitável = longa
  ENTÃO perfil do espectador = Sonhador(a) da fantasia e ficção CNF 80%
```

```
REGRA 38: época compatível: grupo recentes (de 2010 em diante)
  SE    época preferida = recentes (de 2010 em diante)
  ENTÃO época compatível = anos 2010 CNF 100%
  E     época compatível = anos 2020 CNF 100%
```

```
REGRA 1561: A Origem - perfil completo
  SE    gênero compatível = ficção científica
  OU    gênero compatível = ação
  OU    gênero compatível = suspense
  E     clima compatível = tenso
  OU    clima compatível = reflexivo
  E     época compatível = anos 2010
  E     origem compatível = internacional
  E     tipo de história compatível = ficção
  E     tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 148
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 14
  ENTÃO filme recomendado = A Origem CNF 90%
```

```
REGRA 1562: A Origem - gênero e clima
  SE    gênero preferido = ficção científica
  OU    gênero preferido = ação
  OU    gênero preferido = suspense
  E     clima desejado = tenso
  OU    clima desejado = reflexivo
  E     tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 148
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 14
  ENTÃO filme recomendado = A Origem CNF 50%
```

```
REGRA 2082: Parasita - grande premiado
  SE    quer premiados = Sim
  E     gênero compatível = suspense
  OU    gênero compatível = drama
  OU    gênero compatível = comédia
  E     tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 132
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 16
  ENTÃO filme recomendado = Parasita CNF 20%
```

```
REGRA 1570: A Origem - gênero em comum: ficção científica
  SE    tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 148
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 14
  E     gênero preferido = ficção científica
  ENTÃO filme recomendado = A Origem CNF 12%
```

```
REGRA 1575: A Origem - ator: Leonardo DiCaprio
  SE    quer escolher ator = Sim
  E     tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 148
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 14
  E     ator preferido = Leonardo DiCaprio
  ENTÃO filme recomendado = A Origem CNF 70%
```

```
REGRA 1577: A Origem - diretor: Christopher Nolan
  SE    quer escolher diretor = Sim
  E     tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 148
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 14
  E     diretor preferido = Christopher Nolan
  ENTÃO filme recomendado = A Origem CNF 60%
```

```
REGRA 116: Central do Brasil - origem e gênero
  SE    gênero compatível = drama
  E     origem preferida = nacional
  E     tem limite de tempo = Não
  OU    tem limite de tempo = DESCONHECIDO
  OU    tempo disponível >= 113
  OU    faixa de tempo = DESCONHECIDO
  E     classificação permitida = 12
  ENTÃO filme recomendado = Central do Brasil CNF 30%
```
