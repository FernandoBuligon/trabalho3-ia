# Capturas históricas do Expert SINTA

Os diretórios desta pasta contêm registros da execução anterior no Windows.
As imagens são capturas reais preservadas; **não mostram a revisão final**
que corrigiu o limite de duração e os diretores dos filmes.

Em particular, `filmes_2` documenta o defeito antigo: limite de 100 minutos
com recomendação de *A Viagem de Chihiro* (125 minutos). Esse filme é excluído
na versão corrigida. Não reutilizar a captura como prova de correção.

Resultados atuais do **simulador**, com hash da base usada, ficam em
[../revisao/](../revisao/). Não são novas capturas do ExSINTA.

Para repetir os oito casos no Windows, executar `python gerador/casos_gui.py`.
Esse comando substitui os registros dos casos executados; arquivar esta pasta
antes se desejar conservar o histórico. O driver confere perguntas/opções e
captura resultados; a igualdade dos valores nas capturas exige conferência
visual, não é uma asserção automática do driver.
