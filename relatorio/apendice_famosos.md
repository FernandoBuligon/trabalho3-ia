# Apêndice: Sistema 1, Quem é o Famoso?

> Gerado automaticamente a partir de `saida/Famosos.bcm` por `gerador/gerar_apendices.py`.

## Números da base

| Item | Quantidade |
|---|---|
| Regras | 827 |
| Premissas (caudas) | 3571 |
| Conclusões (cabeças) | 900 |
| Variáveis | 33 |
| Valores | 455 |
| Perguntas | 22 |
| Objetivos | 9 |
| Itens na base de dados | 97 |
| Tamanho do arquivo .BCM | 404 KB |

## Regras por tipo

| Tipo | Regras |
|---|---|
| compatibilidade | 56 |
| faixa de altura (altura numérica -> faixa) | 5 |
| estatura (faixa de altura -> estatura, fronteiras difusas) | 8 |
| modelo: perfil completo | 97 |
| modelo: cabelo e olhos | 66 |
| modelo: idade e época | 97 |
| modelo: origem | 97 |
| modelo: área (atuação) | 28 |
| evidência: obra (atuação) | 78 |
| evidência: traço marcante | 68 |
| modelo: área (música) | 29 |
| evidência: obra (música) | 81 |
| modelo: área (apresentação) | 8 |
| evidência: obra (programa) | 12 |
| modelo: área (esporte) | 14 |
| evidência: obra (esporte) | 36 |
| modelo: área (mídia) | 23 |
| evidência: obra (franquia) | 24 |

## Objetivos (ordem de busca)

| # | Variável | Exibe resultado? |
|---|---|---|
| 1 | categoria compatível | não (fixa a ordem das perguntas) |
| 2 | sexo compatível | não (fixa a ordem das perguntas) |
| 3 | faixa etária compatível | não (fixa a ordem das perguntas) |
| 4 | cabelo compatível | não (fixa a ordem das perguntas) |
| 5 | olhos compatíveis | não (fixa a ordem das perguntas) |
| 6 | estatura compatível | não (fixa a ordem das perguntas) |
| 7 | origem compatível | não (fixa a ordem das perguntas) |
| 8 | época compatível | não (fixa a ordem das perguntas) |
| 9 | famoso recomendado | sim |

## Variáveis

| Variável | Tipo | Papel | Valores |
|---|---|---|---|
| categoria preferida | multivalorada | pergunta | ator/atriz; cantor(a); atleta; personagem fictício; apresentador(a)/influenciador(a); pessoa real (qualquer área); indiferente |
| categoria compatível | multivalorada | intermediária (inferida) | ator/atriz; cantor(a); atleta; personagem fictício; apresentador(a)/influenciador(a) |
| sexo preferido | univalorada | pergunta | masculino; feminino; indiferente |
| sexo compatível | multivalorada | intermediária (inferida) | masculino; feminino |
| faixa etária preferida | multivalorada | pergunta | criança/adolescente; jovem (até 30); adulto (31 a 50); maduro (51 ou mais); indiferente |
| faixa etária compatível | multivalorada | intermediária (inferida) | criança/adolescente; jovem (até 30); adulto (31 a 50); maduro (51 ou mais) |
| cabelo preferido | multivalorada | pergunta | preto; castanho; loiro; ruivo; grisalho/branco; careca/raspado; colorido; indiferente |
| cabelo compatível | multivalorada | intermediária (inferida) | preto; castanho; loiro; ruivo; grisalho/branco; careca/raspado; colorido |
| olhos preferidos | multivalorada | pergunta | escuros; azuis; verdes; indiferente |
| olhos compatíveis | multivalorada | intermediária (inferida) | escuros; azuis; verdes |
| sabe a altura | lógica (Sim/Não) | pergunta | Sim; Não |
| altura aproximada | numérica | pergunta | faixa 40;230 |
| faixa de altura | univalorada | intermediária (inferida) | até 160 cm; 161 a 170 cm; 171 a 178 cm; 179 a 186 cm; acima de 186 cm |
| estatura compatível | multivalorada | intermediária (inferida) | baixa; média; alta |
| origem preferida | multivalorada | pergunta | brasileira; norte-americana; latino-americana/caribenha; britânica; outra europeia; asiática/oceania; estrangeira (qualquer país); indiferente |
| origem compatível | multivalorada | intermediária (inferida) | brasileira; norte-americana; latino-americana/caribenha; britânica; outra europeia; asiática/oceania |
| época preferida | multivalorada | pergunta | até anos 80; anos 90; anos 2000; anos 2010; anos 2020; clássica (até os anos 90); recente (de 2010 em diante); indiferente |
| época compatível | multivalorada | intermediária (inferida) | até anos 80; anos 90; anos 2000; anos 2010; anos 2020 |
| espécie preferida | multivalorada | pergunta | humano; animal; criatura/monstro; brinquedo/boneco; indiferente |
| espécie compatível | multivalorada | intermediária (inferida) | humano; animal; criatura/monstro; brinquedo/boneco |
| gênero de atuação preferido | multivalorada | pergunta | ação/aventura; comédia; drama; novela; romance; super-herói; fantasia/ficção científica; suspense/terror; indiferente |
| gênero musical preferido | multivalorada | pergunta | sertanejo; funk; pop; rock; MPB; samba/pagode; rap/hip-hop; axé; forró; R&B/soul; eletrônica; reggaeton/latino; romântica; indiferente |
| esporte preferido | multivalorada | pergunta | futebol; basquete; Fórmula 1; tênis; atletismo; ginástica; skate; surfe; lutas; indiferente |
| mídia preferida | multivalorada | pergunta | animação; quadrinhos; games; filme; série de TV; anime/mangá; livros/folclore; indiferente |
| formato preferido | multivalorada | pergunta | programa de auditório; variedades/culinária; internet/YouTube; humor; indiferente |
| traços marcantes | multivalorada | pergunta | barba; bigode; tatuagens; óculos; cicatriz; cabelo cacheado/crespo; chapéu/boné; roupa/fantasia icônica; maquiagem marcante; nenhum em especial |
| quer citar uma obra | lógica (Sim/Não) | pergunta | Sim; Não |
| obra: filme, série ou novela | multivalorada | pergunta | 300; A Bela e a Fera; A Dama de Ferro; A Fantástica Fábrica de Chocolate; A Hora do Rush; A Origem; A Rainha do Sul; Ainda Estou Aqui; … (69 valores) |
| obra: música ou álbum | multivalorada | pergunta | Andar com Fé; Aquele Abraço; Ar Condicionado no 15; Azul da Cor do Mar; Bad; Bad Romance; Balada; Banda Eva; … (80 valores) |
| obra: time ou competição | multivalorada | pergunta | Al-Nassr; Barcelona; Chicago Bulls; Circuito Mundial de Surfe (WSL); Cleveland Cavaliers; Copa do Mundo; Inter Miami; Los Angeles Lakers; … (29 valores) |
| obra: franquia ou universo | multivalorada | pergunta | Chaves; DC Comics; Disney (Mickey e amigos); Dragon Ball; Folclore brasileiro; Frozen; Harry Potter; Marvel; … (19 valores) |
| obra: programa ou canal | multivalorada | pergunta | Caldeirão do Huck; Canal Felipe Neto; Canal Whindersson Nunes; CazéTV; Domingão com Huck; Domingão do Faustão; Mais Você; Programa Silvio Santos; Show do Milhão; Topa ou Não Topa; Xou da Xuxa; Xuxa Park |
| famoso recomendado | multivalorada | objetivo | Wagner Moura; Fernanda Montenegro; Fernanda Torres; Selton Mello; Matheus Nachtergaele; Rodrigo Santoro; Taís Araújo; Lázaro Ramos; … (97 valores) |

## Perguntas e explicações ("Por quê?")

- **categoria preferida**: "Que tipo de famoso você procura?"
  - *por quê:* A categoria (ator, cantor, atleta, personagem...) define quais
  - *por quê:* características de trabalho serão perguntadas depois.
- **sexo preferido**: "O famoso é homem ou mulher (masculino ou feminino)?"
  - *por quê:* Reduz bastante o conjunto de candidatos.
- **faixa etária preferida**: "Qual a faixa etária (idade atual ou aparente)?"
  - *por quê:* Para personagens, considere a idade aparente.
  - *por quê:* Para quem já faleceu, considere a idade com que ficou conhecido.
- **cabelo preferido**: "Como é o cabelo (cor ou visual mais marcante)?"
  - *por quê:* Característica física usada no perfil e na regra 'cabelo e olhos'.
- **olhos preferidos**: "Qual a cor dos olhos?"
  - *por quê:* Se não souber, marque 'indiferente'.
- **sabe a altura**: "Você sabe (ou quer informar) a altura aproximada?"
  - *por quê:* Se sim, a altura em centímetros será usada para estimar a estatura.
- **altura aproximada**: "Qual a altura aproximada, em centímetros?"
  - *por quê:* A altura é convertida em estatura (baixa, média ou alta) com
  - *por quê:* fronteiras difusas: 165 cm conta parcialmente como baixa e como média.
- **origem preferida**: "De onde é o famoso (para personagens, a origem da obra)?"
  - *por quê:* Nacionalidade da pessoa ou origem da obra do personagem.
- **época preferida**: "Em que época o famoso fez (ou faz) mais sucesso?"
  - *por quê:* Marque todas as décadas que quiser.
- **espécie preferida**: "O personagem é humano, animal, criatura ou brinquedo?"
  - *por quê:* Só é perguntado quando a busca inclui personagens fictícios.
- **gênero de atuação preferido**: "Em que tipo de produção o ator/atriz costuma atuar?"
  - *por quê:* Só é perguntado quando a busca inclui atores e atrizes.
- **gênero musical preferido**: "Qual o estilo musical?"
  - *por quê:* Só é perguntado quando a busca inclui cantores.
- **esporte preferido**: "Qual o esporte?"
  - *por quê:* Só é perguntado quando a busca inclui atletas.
- **mídia preferida**: "Em que mídia o personagem aparece?"
  - *por quê:* Só é perguntado quando a busca inclui personagens fictícios.
- **formato preferido**: "Que tipo de programa ou conteúdo o apresentador/influenciador faz?"
  - *por quê:* Só é perguntado quando a busca inclui apresentadores e influenciadores.
- **traços marcantes**: "Ele(a) tem algum traço físico marcante?"
  - *por quê:* Cada traço que coincidir aumenta o grau de confiança da recomendação.
- **quer citar uma obra**: "Você lembra de alguma obra ou trabalho dessa pessoa ou personagem?"
  - *por quê:* Obras são a evidência mais forte. Se sim, listas de obras serão mostradas.
- **obra: filme, série ou novela**: "Em qual filme, série ou novela ele(a) atuou?"
  - *por quê:* Cada obra marcada é uma evidência forte (CNF 85%) a favor de quem atuou nela.
- **obra: música ou álbum**: "Qual música, álbum ou banda você associa a ele(a)?"
  - *por quê:* Cada música ou álbum marcado é uma evidência forte (CNF 85%).
- **obra: time ou competição**: "Qual time, clube ou competição você associa ao atleta?"
  - *por quê:* Times e competições compartilhados (ex.: Copa do Mundo) somam evidências.
- **obra: franquia ou universo**: "De qual franquia ou universo é o personagem?"
  - *por quê:* A franquia identifica o personagem com CNF 85%.
- **obra: programa ou canal**: "Qual programa ou canal você associa a ele(a)?"
  - *por quê:* O programa identifica o apresentador/influenciador com CNF 85%.

## Exemplos de regras (como aparecem no SINTA)

```
REGRA 6: categoria compatível: grupo pessoa real (qualquer área)
  SE    categoria preferida = pessoa real (qualquer área)
  ENTÃO categoria compatível = ator/atriz CNF 100%
  E     categoria compatível = cantor(a) CNF 100%
  E     categoria compatível = atleta CNF 100%
  E     categoria compatível = apresentador(a)/influenciador(a) CNF 100%
```

```
REGRA 7: categoria compatível: indiferente
  SE    categoria preferida = indiferente
  ENTÃO categoria compatível = ator/atriz CNF 100%
  E     categoria compatível = cantor(a) CNF 100%
  E     categoria compatível = atleta CNF 100%
  E     categoria compatível = personagem fictício CNF 100%
  E     categoria compatível = apresentador(a)/influenciador(a) CNF 100%
```

```
REGRA 58: faixa de altura: 161 a 170 cm
  SE    altura aproximada > 160
  E     altura aproximada <= 170
  ENTÃO faixa de altura = 161 a 170 cm CNF 100%
```

```
REGRA 66: estatura compatível: 161 a 170 cm
  SE    sabe a altura = Sim
  E     faixa de altura = 161 a 170 cm
  ENTÃO estatura compatível = baixa CNF 80%
  E     estatura compatível = média CNF 70%
```

```
REGRA 64: estatura compatível: altura em branco
  SE    sabe a altura = Sim
  E     faixa de altura = DESCONHECIDO
  ENTÃO estatura compatível = baixa CNF 100%
  E     estatura compatível = média CNF 100%
  E     estatura compatível = alta CNF 100%
```

```
REGRA 70: Wagner Moura - perfil completo
  SE    categoria compatível = ator/atriz
  E     sexo compatível = masculino
  E     faixa etária compatível = adulto (31 a 50)
  E     cabelo compatível = castanho
  E     olhos compatíveis = escuros
  E     estatura compatível = média
  E     época compatível = anos 2000
  OU    época compatível = anos 2010
  OU    época compatível = anos 2020
  E     origem compatível = brasileira
  ENTÃO famoso recomendado = Wagner Moura CNF 90%
```

```
REGRA 71: Wagner Moura - cabelo e olhos
  SE    categoria compatível = ator/atriz
  E     sexo compatível = masculino
  E     cabelo preferido = castanho
  E     olhos preferidos = escuros
  ENTÃO famoso recomendado = Wagner Moura CNF 45%
```

```
REGRA 74: Wagner Moura - área (atuação)
  SE    categoria compatível = ator/atriz
  E     gênero de atuação preferido = ação/aventura
  OU    gênero de atuação preferido = drama
  E     sexo compatível = masculino
  ENTÃO famoso recomendado = Wagner Moura CNF 55%
```

```
REGRA 75: Wagner Moura - obra: Tropa de Elite
  SE    quer citar uma obra = Sim
  E     categoria compatível = ator/atriz
  E     obra: filme, série ou novela = Tropa de Elite
  ENTÃO famoso recomendado = Wagner Moura CNF 85%
```

```
REGRA 730: Naruto - perfil completo
  SE    categoria compatível = personagem fictício
  E     sexo compatível = masculino
  E     espécie compatível = humano
  E     faixa etária compatível = criança/adolescente
  E     cabelo compatível = loiro
  E     olhos compatíveis = azuis
  E     estatura compatível = baixa
  E     época compatível = anos 2000
  OU    época compatível = anos 2010
  E     origem compatível = asiática/oceania
  ENTÃO famoso recomendado = Naruto CNF 90%
```

```
REGRA 369: Rita Lee - traço marcante: óculos
  SE    categoria compatível = cantor(a)
  E     sexo compatível = feminino
  E     traços marcantes = óculos
  ENTÃO famoso recomendado = Rita Lee CNF 30%
```
