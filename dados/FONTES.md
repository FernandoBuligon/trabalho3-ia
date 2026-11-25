# Pesquisa e critérios da base de conhecimento

Revisão documental: **25/11/2026**. O registro [fontes.csv](fontes.csv) relaciona
item, campos efetivamente conferidos, resultado da consulta, instituição, URL
e data de acesso. A pesquisa usa fichas de produtoras e exibidores, festivais,
arquivos de televisão e entidades esportivas. As referências cobrem ambos os
sistemas e diferentes categorias de celebridades.

## Alcance da conferência

Os 26 registros documentam uma **conferência por amostragem**, com prioridade
para exemplos de apresentação e inconsistências identificadas na revisão.
Não representam certificação factual de todos os atributos dos 242 itens.
Os dados originais foram compilados de conhecimento geral; a revisão acrescentou
pesquisa rastreável e corrigiu os campos com divergências confirmadas. Os demais
campos foram preservados e não devem ser apresentados como verificados nas fontes
listadas. `validar_dados.py` verifica estrutura, não verdade factual.

## Critérios de modelagem

- **Duração:** minutos inteiros da versão cadastrada. A comparação é exata para
  esse valor. Edições de cinema, streaming e relançamentos podem divergir.
  Para *Toy Story*, foram mantidos os 81 minutos da ficha histórica D23; a página
  comercial atual da Disney informa 85. O limite não promete cobrir todas as edições.
- **Ano:** ano da obra/estreia original, não necessariamente o lançamento brasileiro.
- **País:** um país de referência; a coluna não enumera todas as coproduções.
- **Diretores:** nomes individuais separados por `|`. Cada codiretor pode ser
  selecionado e gera uma evidência própria. Elenco é uma seleção de participantes,
  incluindo vozes originais em animações; não é a ficha técnica completa.
- **Prêmios:** seleção de premiações conhecidas; campo vazio não significa que
  a obra jamais recebeu prêmio. Indicação ao Oscar é diferente de vitória.
- **Classificação:** faixa brasileira cadastrada para fins didáticos. Não se
  converte automaticamente G/PG/PG-13 estrangeiro em classificação brasileira.
  Os testes garantem respeito ao cadastro, não uma auditoria de todas as
  classificações oficiais ou de todas as versões de cada filme.
- **Idade:** data de referência da revisão, 25/11/2026, para pessoas vivas;
  idade ao falecer para falecidos. Personagens usam a representação escolhida,
  não os anos decorridos desde a criação. A faixa infantil tem precedência
  sobre “jovem (até 30)”. As idades explicitamente pesquisadas estão no CSV de fontes.
- **Aparência:** cabelo, olhos, estatura e traços são descritores aproximados
  de reconhecimento e podem variar com época, caracterização ou adaptação.
  Não são medições biométricas. Campo vazio significa ausência de informação;
  a regra correspondente omite essa condição. Personagens estilizados usam
  categorias visuais; “humano” inclui humanoides na taxonomia simplificada.
- **Clima, época de sucesso, gênero e perfil:** categorias editoriais para o
  exercício de engenharia do conhecimento; não são fatos exclusivos ou universais.
- **Fatos reais:** inclui inspiração em acontecimentos reais; não afirma que
  todos os personagens e eventos da narrativa sejam documentais.

## Correções sustentadas pela pesquisa

| Obra | Correção |
|---|---|
| O Auto da Compadecida 2 | 105 → 114 minutos; inclusão de Flávia Lacerda na direção |
| O Agente Secreto | 158 → 161 minutos, conforme ficha do IFFR e programação do Cine Cultura |
| Bacurau | inclusão de Juliano Dornelles |
| Frozen | inclusão de Jennifer Lee |
| O Rei Leão | inclusão de Rob Minkoff |
| Moana | inclusão de John Musker |
| Homem-Aranha no Aranhaverso | inclusão de Peter Ramsey e Rodney Rothman |
| Como Treinar o Seu Dragão | inclusão de Chris Sanders |
| Matrix e Intocáveis | separação dos nomes dos diretores em opções individuais |

As fontes específicas de cada correção constam em [fontes.csv](fontes.csv).
Para novas entradas, registrar a fonte e os campos conferidos, manter a versão
da obra explícita quando necessário e regenerar bases, apêndices e testes.
