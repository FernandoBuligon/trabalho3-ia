"""
Etapa 8: consultas executadas no ExSINTA REAL (via interface, sem foco) e
comparadas com o simulador. As capturas ficam em testes/gui/<caso>/.

    python casos_gui.py            # roda todos
    python casos_gui.py filmes_2   # roda um caso
"""
import os
import sys

from gui_check import checar

AQUI = os.path.dirname(os.path.abspath(__file__))
FAM = os.path.join(AQUI, "..", "saida", "Famosos.bcm")
FIL = os.path.join(AQUI, "..", "saida", "Filmes.bcm")

CASOS = {
    # Wagner Moura descrito pela aparência + obra
    "famosos_1": (FAM, {
        "categoria preferida": ["ator/atriz"], "sexo preferido": "masculino",
        "faixa etária preferida": ["adulto (31 a 50)"], "cabelo preferido": ["castanho"],
        "olhos preferidos": ["escuros"], "sabe a altura": "Sim", "altura aproximada": 174,
        "origem preferida": ["brasileira"], "época preferida": ["anos 2000", "anos 2010"],
        "gênero de atuação preferido": ["ação/aventura"], "traços marcantes": ["nenhum em especial"],
        "quer citar uma obra": "Sim", "obra: filme, série ou novela": ["Tropa de Elite"]}),
    # personagem: loiro de olhos azuis, anime (Naruto), sem altura, época em grupo
    "famosos_2": (FAM, {
        "categoria preferida": ["personagem fictício"], "sexo preferido": "masculino",
        "faixa etária preferida": ["indiferente"], "cabelo preferido": ["loiro"],
        "olhos preferidos": ["azuis"], "sabe a altura": "Não",
        "origem preferida": ["estrangeira (qualquer país)"], "época preferida": ["indiferente"],
        "espécie preferida": ["humano"], "mídia preferida": ["anime/mangá"],
        "traços marcantes": ["roupa/fantasia icônica"], "quer citar uma obra": "Não"}),
    # cantora brasileira ruiva de óculos, respostas em branco em várias perguntas
    "famosos_3": (FAM, {
        "categoria preferida": ["cantor(a)"], "sexo preferido": "feminino",
        "faixa etária preferida": None, "cabelo preferido": ["ruivo"],
        "olhos preferidos": None, "sabe a altura": "Não",
        "origem preferida": ["brasileira"], "época preferida": ["clássica (até os anos 90)"],
        "gênero musical preferido": ["rock"], "traços marcantes": ["óculos"],
        "quer citar uma obra": "Não"}),
    # adulto, comédia nacional com amigos
    "filmes_1": (FIL, {
        "há menores assistindo": "Não", "gênero preferido": ["comédia"], "clima desejado": ["divertido"],
        "tem limite de tempo": "Não", "origem preferida": "nacional", "época preferida": ["indiferente"],
        "tipo de história preferido": "indiferente", "companhia": "com amigos", "quer premiados": "Não",
        "interesse em franquias": "indiferente", "quer escolher ator": "Não", "quer escolher diretor": "Não"}),
    # criança de 8 anos, animação, 100 minutos, premiados
    "filmes_2": (FIL, {
        "há menores assistindo": "Sim", "idade do mais novo": 8, "gênero preferido": ["animação"],
        "clima desejado": ["divertido", "emocionante"], "tem limite de tempo": "Sim", "tempo disponível": 100,
        "origem preferida": "indiferente", "época preferida": ["indiferente"],
        "tipo de história preferido": "indiferente", "companhia": "com a família", "quer premiados": "Sim",
        "interesse em franquias": "indiferente", "quer escolher ator": "Não", "quer escolher diretor": "Não"}),
    # fã de ficção científica, sagas, Nolan e DiCaprio, 15 anos, recentes
    "filmes_3": (FIL, {
        "há menores assistindo": "Sim", "idade do mais novo": 15, "gênero preferido": ["ficção científica", "ação"],
        "clima desejado": ["tenso", "épico"], "tem limite de tempo": "Sim", "tempo disponível": 170,
        "origem preferida": "internacional", "época preferida": ["recentes (de 2010 em diante)"],
        "tipo de história preferido": "ficção", "companhia": "sozinho(a)", "quer premiados": "Sim",
        "interesse em franquias": "gosto de sagas e franquias", "quer escolher ator": "Sim",
        "ator preferido": ["Leonardo DiCaprio"], "quer escolher diretor": "Sim",
        "diretor preferido": ["Christopher Nolan"]}),
    # menores sem idade informada e limite de tempo sem tempo informado (fallbacks)
    "filmes_4": (FIL, {
        "há menores assistindo": "Sim", "idade do mais novo": None, "gênero preferido": ["aventura", "comédia"],
        "clima desejado": ["indiferente"], "tem limite de tempo": "Sim", "tempo disponível": None,
        "origem preferida": "indiferente", "época preferida": None,
        "tipo de história preferido": "indiferente", "companhia": "com a família", "quer premiados": "Não",
        "interesse em franquias": "gosto de sagas e franquias", "quer escolher ator": "Não",
        "quer escolher diretor": "Não"}),
    # graus de confiança fracionários digitados na interface + altura em branco
    "famosos_4": (FAM, {
        "categoria preferida": [("atleta", 90)], "sexo preferido": [("masculino", 80)],
        "faixa etária preferida": ["indiferente"], "cabelo preferido": [("careca/raspado", 70)],
        "olhos preferidos": ["indiferente"], "sabe a altura": "Sim", "altura aproximada": None,
        "origem preferida": ["indiferente"], "época preferida": [("anos 90", 80), ("anos 2000", 60)],
        "esporte preferido": [("basquete", 90)], "traços marcantes": ["nenhum em especial"],
        "quer citar uma obra": "Não"}),
}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    nomes = sys.argv[1:] or list(CASOS)
    for n in nomes:
        base, resp = CASOS[n]
        checar(base, resp, n)
