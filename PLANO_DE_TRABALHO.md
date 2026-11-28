# Plano de Trabalho — Trabalho 3: Sistemas Especialistas (Expert SINTA)

## 1. O que o trabalho pede

Disciplina: Fundamentos de Sistemas Inteligentes (UTFPR Santa Helena, Prof. Thiago Naves).

Os dois sistemas especialistas devem ser feitos no shell **Expert SINTA**:

| # | Sistema | Recomenda com base em | Conteúdo |
|---|---------|-----------------------|----------|
| 1 | **Famosos** | características físicas e obras/trabalhos | atores, cantores, personagens fictícios, outras celebridades |
| 2 | **Filmes** | estilo, duração, gênero, atores, ano e outros atributos relevantes | filmes nacionais e internacionais (opcional: séries e novelas) |

Requisitos avaliados:
1. Base de dados o mais completa possível, montada com pesquisa sobre o tema.
2. Usar o **máximo de regras possível**.
3. Definir **todos os objetivos e variáveis** necessários.
4. O sistema precisa **rodar de forma funcional no Expert SINTA**.
5. Extras contam pontos: "novas abordagens de conhecimento, base de dados e algoritmos".

Entrega pelo Moodle e apresentação em sala.

## 2. Material disponível na pasta

- `Trabalho 3 - Sistemas Especialistas.pdf`: o enunciado.
- `Manual - Expert SINTA.pdf`: o manual do shell.
- `ferramenta/`: `ExSINTA.exe` (versão 32 bits de 1998), ajuda e a base de exemplo `SECAJU.BCM`, extraídos do pacote original `sinta32.zip`.
- `sinta/SINTA/sintascr/LIBRARY/EXSYSTEM.PAS`: **código-fonte Delphi do motor**, incluindo `SaveToFile`/`LoadFromFile`, que definem o formato binário `.BCM`.
- Bases de exemplo para engenharia reversa e testes: `VINHOS.BCM` e `SECAJU.BCM`.

**Decisão-chave:** cadastrar centenas de regras à mão na interface gráfica do SINTA é lento e sujeito a erro. Como temos o código-fonte do formato, o Claude vai escrever um **gerador em Python** que lê a base de conhecimento a partir de arquivos de dados legíveis (YAML/CSV) e grava o `.BCM` diretamente. Assim a base pode ser grande e fácil de manter. **Plano B** (se o gerador não ficar compatível): gerar um roteiro textual das variáveis e regras para digitar no SINTA, ou automatizar a digitação na interface.

## 3. Conceitos do Expert SINTA usados

- **Variáveis:** univaloradas, multivaloradas ou numéricas, com uma lista de valores possíveis.
- **Objetivos:** as variáveis que o sistema tenta deduzir (aqui, `famoso_recomendado` e `filme_recomendado`).
- **Regras:** `SE <premissas com E/OU> ENTÃO <conclusões> CNF x%`, com encadeamento para trás e grau de confiança.
- **Perguntas:** o texto exibido ao usuário para cada variável, mais o texto "Por quê?".
- **Contextos/ajuda:** explicações exibidas nas respostas (são um extra).

## 4. Arquitetura da solução (o diferencial)

Usar **regras em camadas** em vez de uma regra plana por item. Isso aumenta muito o número de regras, permite consultas parciais e aparece como "nova abordagem de conhecimento":

```
Perguntas ao usuário  ──►  Variáveis intermediárias (perfis)  ──►  Objetivo (recomendação + CNF)
ex.: gênero, década,       ex.: "perfil_ação_clássico",            ex.: filme_recomendado =
duração, idioma, humor     "faixa_duração", "público_alvo"         "Tropa de Elite" CNF 85%
```

- **Camada 1 (classificação):** derivam variáveis intermediárias a partir das respostas. Ex.: `duração_min < 100 → faixa_duração = curta`; `ano entre 1980 e 1989 → década = 80s`.
- **Camada 2 (perfis):** combinam atributos em perfis. Ex.: `gênero = terror E humor = tenso → perfil = suspense_psicológico`.
- **Camada 3 (recomendação):** cada item da base tem várias regras: uma "exata", com todos os atributos e CNF alto, e regras "parciais", com subconjuntos de atributos e CNF menor. Assim o sistema sempre devolve recomendações ranqueadas, mesmo com respostas "não sei".
- Usar o **grau de confiança** nas perguntas e nas regras, que o SINTA combina automaticamente.

## 5. Modelagem de cada sistema

### Sistema 1: Recomendador de Famosos
- **Base:** cerca de 60 a 80 entradas, divididas entre atores e atrizes (BR e internacionais), cantores, personagens fictícios (filmes, animações, games, quadrinhos), atletas e influenciadores.
- **Variáveis perguntadas (exemplos):** categoria (ator/cantor/personagem/atleta...), sexo/gênero, faixa etária, cor do cabelo, cor dos olhos, altura (numérica ou faixa), tom de pele, traço marcante (barba, tatuagens, óculos...), nacionalidade, área/estilo da obra (gênero musical, gênero de filme), obra mais conhecida, época de auge (década), real ou fictício.
- **Intermediárias:** `perfil_fisico`, `era`, `area_atuacao`, `origem`.
- **Objetivo:** `famoso_recomendado` (multivalorado, para listar vários com CNF).

### Sistema 2: Recomendador de Filmes, Séries e Novelas
- **Base:** cerca de 80 a 120 títulos, com mistura de nacionais (ex.: Cidade de Deus, Central do Brasil, Tropa de Elite, O Auto da Compadecida, Bacurau, Ainda Estou Aqui) e internacionais, mais algumas séries e novelas.
- **Variáveis perguntadas:** tipo (filme/série/novela), gênero principal e secundário, duração (numérica → faixa), ano (numérico → década/era), origem (nacional/internacional/país), idioma, classificação indicativa, ator/atriz preferido, diretor, clima/humor desejado (leve, tenso, emocionante...), com quem vai assistir (sozinho/família/casal/amigos), premiações (Oscar etc.), baseado em fatos reais, franquia ou obra única.
- **Intermediárias:** `faixa_duracao`, `era`, `publico_alvo`, `perfil_estilo`.
- **Objetivo:** `filme_recomendado` (multivalorado).

Meta de volume: **mais de 300 regras por sistema**, todas geradas a partir dos dados.

## 6. Etapas para o Claude executar

| Etapa | Tarefa | Entregável |
|-------|--------|------------|
| **0** | Ler os manuais (`Manual - Expert SINTA.pdf`) para confirmar limites: tamanho dos nomes, número máximo de valores e regras, sintaxe dos operadores, CNF | notas em `docs/notas_sinta.md` |
| **1** | Extrair o `sinta32.zip` para `ferramenta/` e verificar se `ExSINTA.exe` abre no Windows 11 (com `VINHOS.BCM`) | ferramenta funcionando ou registro do problema |
| **2** | Engenharia reversa do `.BCM`: mapear os records de `EXSYSTEM.PAS` (`TVarRecord`, `TValRecord`, `TRuleRecord`, `THeadRecord`, `TTailRecord`, `TTargetRecord`, `TPartialQuestionRecord`, opções gerais, Pascal `string[N]`, `TMyInteger`, alinhamento) | `gerador/bcm_format.py` |
| **3** | Escrever um **leitor** de `.BCM` e validar com um *round-trip*: ler `VINHOS.BCM`, regravar e comparar os bytes | `gerador/bcm_reader.py`, teste passando |
| **4** | Escrever o **gerador**: dados (YAML/CSV) → regras em camadas → `.BCM` | `gerador/build.py` |
| **5** | Pesquisar e montar a base do **Sistema 1** (famosos), com atributos conferidos | `dados/famosos.csv` |
| **6** | Pesquisar e montar a base do **Sistema 2** (filmes), com ano, duração, diretor e elenco conferidos | `dados/filmes.csv` |
| **7** | Definir variáveis, perguntas, textos "Por quê?", objetivos e textos de abertura | `dados/*_config.yaml` |
| **8** | Gerar `Famosos.bcm` e `Filmes.bcm` e abrir no ExSINTA. **O usuário testa algumas consultas**, porque o Claude não opera a interface gráfica com segurança | bases funcionando |
| **9** | Ajustes: CNFs, perguntas confusas, regras que nunca disparam (validar também com um motor de inferência em Python que simule o SINTA) | `gerador/simulador.py` + relatório de cobertura |
| **10** | Documentação: relatório (objetivo, modelagem, variáveis, exemplos de regras, estatísticas da base, abordagem em camadas, exemplos de consulta) e roteiro de apresentação | `relatorio/Relatorio.docx` ou `.pdf`, `apresentacao/` |

## 7. Estrutura de pastas proposta

```
Trabalho 3 - Sistemas Especialistas/
├── ferramenta/        # ExSINTA.exe extraído
├── gerador/           # bcm_format.py, bcm_reader.py, build.py, simulador.py
├── dados/             # famosos.csv, filmes.csv, *_config.yaml
├── saida/             # Famosos.bcm, Filmes.bcm  ← entregáveis principais
├── docs/              # notas_sinta.md
└── relatorio/         # relatório + slides
```

## 8. Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| `ExSINTA.exe` (1998) não roda no Windows 11 | modo de compatibilidade (Win 98/XP), executar como administrador ou usar uma VM |
| Detalhes binários (alinhamento de records, `string[N]`, codificação Latin-1) dão erro | validar com *round-trip* nos `.BCM` de exemplo antes de gerar qualquer base nova |
| Limites do SINTA (quantidade de valores por variável ou de regras) | conferir no manual e no fonte, e dividir variáveis grandes (ex.: atores) em categorias |
| Dados factuais errados | manter fontes (IMDb, Wikipedia, AdoroCinema) anotadas no CSV |
| Interface gráfica não automatizável pelo Claude | o usuário faz os testes finais de clique, guiado por um checklist de consultas |

## 9. Decisões do usuário (fechadas)

1. Tamanho da base: livre (Claude escolhe).
2. Sistema 2: **somente filmes** (sem séries/novelas).
3. Relatório em **Markdown (.md)**.
4. Prazo: não importa. Desenvolver o trabalho inteiro, **sem avançar de etapa até a anterior estar fechada e validada**.

## 11. Registro de andamento

| Etapa | Status | Validação |
|-------|--------|-----------|
| 0 | concluída | Manual lido (cap. I–III) e fontes `EXSYSTEM/EXDATAST/EXCONSTS.PAS` analisados; notas em `docs/notas_sinta.md` |
| 1 | concluída | `ferramenta/ExSINTA.exe` abre no Windows 11 sem modo de compatibilidade. `VINHOS.BCM` abriu pelo menu e a lista de regras apareceu. Problema encontrado: bases **somente leitura** dão "File access denied" (o Delphi abre em leitura e escrita), então os `.bcm` gerados não podem ter esse atributo. O exe não aceita base por argumento de linha de comando (com argumento ele tenta gravar). Testes automatizados usam o INI virtualizado (`%LOCALAPPDATA%\VirtualStore\Windows\EXSINTA.INI`, seção `[Arquivos]`) e `WM_COMMAND` no menu, sem tirar o foco do usuário. |
| 2 | concluída | Layout completo documentado em `docs/formato_bcm.md`. Tipos: ShortString de 256 bytes, int16 e Real48. Conectivo é "ligação com a próxima premissa" (a última é cnTHEN); CNF em fração; valores especiais -1/-2/-3. Leitor e escritor em `gerador/bcm.py` (preferi um único módulo a `bcm_format.py` + `bcm_reader.py`). |
| 3 | concluída | `gerador/test_formato.py`: round-trip **byte a byte** das 4 bases de exemplo; Real48; base sintética escrita, lida e reescrita. No **ExSINTA real**: a base sintética abriu, as regras foram exibidas, o SINTA regravou com **semântica idêntica** e a consulta deu Filme A 89,85%, igual ao cálculo manual. API de alto nível em `gerador/kb.py`. |
| 4 | concluída | `gerador/build.py` (DSL de condições, CSV, faixas derivadas, modelos de regra, evidências e validação de vocabulário). `gerador/simulador.py` é um port fiel do motor (adiantado da Etapa 9) e **coincide com o ExSINTA** no VINHOS (base de terceiros) e em 2 casos da base de exemplo, inclusive na ordem das perguntas. Driver de interface em `gerador/gui/` + `gui_check.py`. `test_build.py`: 19 verificações OK. Descobertas de projeto: (1) com prioridade OU as regras são avaliadas em forma normal conjuntiva; (2) uma regra que termine em grupo OU pode quebrar o SINTA com CNF fracionário, então o gerador fecha toda regra com premissa simples; (3) a ordem das perguntas depende do encadeamento para trás, então as bases reais usam objetivos ocultos para fixá-la. |
| 5 | concluída | `dados/famosos.csv`: **97 famosos** (28 atuam como atores, 29 cantam, 14 atletas, 23 personagens, 8 apresentadores; 48 brasileiros), 21 colunas. Esquema com vocabulário controlado em `dados/esquema_famosos.yaml`; `dados/validar_dados.py` deu **VÁLIDO** depois de corrigir 1 lacuna (obras musicais de Zendaya). Os 97 são distinguíveis pelo conjunto de atributos. Decisões: sem classificação de tom de pele de pessoas reais (uso "espécie" para personagens); olhos e altura só quando havia segurança (70% preenchidos). |
| 6 | concluída | `dados/filmes.csv`: **145 filmes** (38 nacionais e 107 internacionais, de 1936 a 2025, 12 países), 13 colunas (ano, duração, país, gêneros, clima, classificação, diretor, atores, prêmios, fatos reais, franquia). Esquema em `dados/esquema_filmes.yaml`, validação **VÁLIDO**. 143/145 com assinatura única; 38 filmes L/10 cobrem 10 gêneros. Somente filmes (decisão do usuário). Observação: a classificação indicativa é aproximada para filmes antigos. |
| 7 | concluída | `dados/famosos.yaml` e `dados/filmes.yaml`. **Famosos:** 820 regras, 32 variáveis, 22 perguntas, 9 objetivos (8 ocultos para ordenar as perguntas e 1 visível). **Filmes:** 1.476 regras, 26 variáveis, 16 perguntas, 9 objetivos (2 visíveis: perfil do espectador e filme recomendado). Camadas: perguntas → compatibilidade gerada (absorve indiferente, sem resposta e grupos) + regras escritas à mão (altura → estatura difusa, idade → classificação, tempo → duração, ocasião, 20 regras de perfil) → modelos e evidências por item (acúmulo de CNF). `gerador/auditoria.py`: **0 erros e 0 avisos** nas duas bases. Simulações de sanidade coerentes. |
| 8 | concluída | `saida/Famosos.bcm` e `saida/Filmes.bcm` abrem no ExSINTA (cerca de 5 s) e foram **regravadas pelo SINTA com semântica idêntica**. 6 consultas completas executadas **no ExSINTA real** (`gerador/casos_gui.py`, capturas em `testes/gui/`), com 11 a 16 perguntas cada, opções conferidas pergunta a pergunta e resultados **idênticos ao simulador** em valores e ordem. Cobriram altura numérica, idade e tempo numéricos, grupos ("estrangeira", "recentes"), respostas em branco, perguntas condicionais (espécie, mídia, obras, atores, diretores) e o objetivo intermediário visível (perfil). Ajuste no driver: o resultado do perfil aparece entre perguntas. O usuário não precisou clicar em nada. |
| 9 | concluída | `gerador/avaliacao.py` (resultados em `testes/avaliacao.json`). **Primeira rodada:** filmes com 12,5% de consultas sem resposta e top-1 de 57% sem ator/diretor. **Correções:** (1) cadeias número → faixa categórica com fallback DESCONHECIDO (idade/tempo/altura em branco); (2) comparação exata `tempo disponível >= duração do filme`; (3) evidências por gênero e clima em comum; (4) sugestões alternativas de baixo CNF. **Final:** famosos com autorreconhecimento top-1 de **100%** (com e sem obra); filmes top-1 de **100%** com ator/diretor e **91%** sem (top-3 100%); consultas sem resposta 0,3% nos filmes e 1,9% nos famosos (respostas de CNF baixo, abaixo do limiar de 50%); **0 falhas do motor** em 4.000 consultas; **100% das regras alcançáveis**; **0 violações de classificação indicativa** em 1.000 consultas com menores. Revalidação no **ExSINTA real** com as bases finais: 8 casos idênticos ao simulador (incluindo idade/tempo em branco e CNFs fracionários). Pipeline único: `gerador/gerar_tudo.py`. |
| 10 | concluída | `relatorio/Relatorio.md` (cerca de 3.800 palavras: requisitos × atendimento, abordagem, 2 sistemas, validação e limitações), com 10 figuras capturadas do ExSINTA real (perguntas, regras no editor, resultados e aba Histórico) em `relatorio/img/`. Apêndices gerados automaticamente das bases (`apendice_famosos.md` e `apendice_filmes.md`, com variáveis, perguntas, "por quê", objetivos e exemplos de regras). `README.md` na raiz. Verificações: todos os números do relatório foram conferidos contra dados, bases e simulador (4 corrigidos no rascunho); todos os links e imagens existem; os `.bcm` entregues são idênticos a uma regeneração do zero e não estão como somente leitura. |

**Registro histórico do desenvolvimento original.** As afirmações de conclusão acima devem ser lidas com a revisão de entrega abaixo, que corrige as limitações encontradas na auditoria.

## 10. Prompt sugerido para iniciar

> "Execute o PLANO_DE_TRABALHO.md a partir da Etapa 0. Pare ao final da Etapa 3 (round-trip do VINHOS.BCM) e me mostre o resultado antes de gerar as bases."

## 12. Revisão de entrega — 25/11/2026

- Corrigido o limite de duração em **todas** as regras que recomendam filmes,
  inclusive ator, diretor, ocasião e prêmios. Campo em branco continua sem limite.
- Pesquisa documentada em `dados/FONTES.md` e `dados/fontes.csv` (26 registros,
  por amostragem; não se afirma verificação factual integral dos 242 itens).
- Corrigidas durações de O Auto da Compadecida 2 e O Agente Secreto; complementadas
  codireções e separados diretores que antes eram uma opção conjunta.
- Bases finais: **827 regras de famosos e 2.374 de filmes; total 3.201**.
- **881 consultas de regressão aprovadas**, incluindo os limites exatos dos 145
  filmes, respostas em branco/sem limite e cada diretor individualmente.
- Avaliação refeita: **4.000 consultas sem falha**, todas as regras alcançadas
  pelo conjunto aleatório + dirigido; **1.000 consultas com menores sem violação
  da classificação cadastrada**. Filmes sem resposta: **3,1%** (limite agora rígido).
- Relatório, apêndices e instruções atualizados; hashes e oito consultas atuais
  do simulador em `testes/revisao/`.
- Evidências do Windows preservadas e identificadas como históricas. Os arquivos
  regravados pelo ExSINTA têm 820/1.476 regras; não são cópias das bases finais.
  Na época não houve nova execução nativa; ela foi feita em 28/11/2026 (seção 13).
- Identificação dos integrantes: solicitada ao usuário; não foram inventados nomes.

## 13. Validação no ExSINTA real — 28/11/2026

- O driver da interface foi reescrito em Python (`gerador/gui/sinta_driver.py`,
  só biblioteca padrão e `ctypes`), substituindo os scripts PowerShell. Roda
  num Python para Windows: o nativo, no Windows, ou o *embeddable* pelo Wine,
  no Linux/macOS. `gui_check.py` escolhe o executor automaticamente.
- Ajustes necessários no Wine: os menus de outro processo não podem ser lidos,
  então o driver usa os IDs de comando do ExSINTA 1.1b, obtidos do recurso
  TFRMMAIN do executável e confirmados ao vivo; `PrintWindow` não renderiza
  janelas Delphi entre processos, então a captura copia a área interna da
  janela; a janela de perguntas é reaproveitada, então o driver espera a
  pergunta realmente mudar (handles, textos e marcações) antes de seguir.
- **Regravação:** `saida/Famosos.bcm` (827 regras) e `saida/Filmes.bcm`
  (2.374 regras) abertas e salvas pelo ExSINTA, com **semântica idêntica**
  (`gerador/regravar_gui.py`, resultado em `testes/sinta_regravado/`).
- **Consultas:** os oito casos de `casos_gui.py` rodaram no ExSINTA com as
  bases finais. Perguntas e opções conferidas automaticamente; valores e
  ordem dos resultados iguais ao simulador (conferência visual). `filmes_2`
  confirma o limite de 100 minutos no SINTA real.
- Figuras do relatório recapturadas das bases finais (`gerador/figuras_gui.py`).
  As capturas de tela ficam no relatório entregue e não são versionadas no repositório.
- Ambiente: Linux, Wine 11.0, Python 3.12.10 embeddable (win32). O modo
  Windows nativo do novo driver não foi executado nesta revisão.
