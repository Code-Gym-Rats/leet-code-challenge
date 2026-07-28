import os
import re
from github import Github # pip install PyGithub

# --- Configurações ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY")
# Nomes dos desenvolvedores devem ser usados para nomear os arquivos de solução (minúsculas, sem espaços)
DEVELOPERS = ["adriel", "allyne", "arthencia", "calebe", "tiago"]

# --- Inicializa o cliente GitHub ---
g = Github(GITHUB_TOKEN)
repo = g.get_user().get_repo(REPO_NAME.split('/')[-1])

def get_solutions_count_from_main(developer_name):
    """Conta o número de arquivos de solução de um desenvolvedor na branch main,
    considerando a estrutura desafio-XX/nome_dev.ext, independentemente da extensão."""
    count = 0
    try:
        main_tree = repo.get_git_tree(repo.get_branch("main").commit.sha, recursive=True)
        for item in main_tree.tree:
            # Ex: desafio-01/arthencia.js, desafio-02/adriel.py
            # Verifica se o caminho do arquivo começa com "desafio-" e se o nome do arquivo
            # (sem a extensão) corresponde ao nome do desenvolvedor.
            if item.path.startswith("desafio-") and item.type == "blob":
                # Extrai o nome do arquivo (ex: "arthencia.js")
                file_name_with_ext = os.path.basename(item.path)
                # Extrai o nome base do arquivo (ex: "arthencia")
                file_base_name = os.path.splitext(file_name_with_ext)[0]
            if file_base_name == developer_name:
                count += 1
except Exception as e:
    print(f"Erro ao contar soluções na main para {developer_name}: {e}")
return count
def get_checklist_marks_count(developer_name):
    """Conta quantas vezes o desenvolvedor marcou seu nome em checklists de issues.
    Esta função é para acompanhamento, não para pontuação principal do ranking."""
    count = 0
    issues = repo.get_issues(state="closed") # Pega issues fechadas (ou "all" para todas)
    for issue in issues:
        # Procura pelo nome do desenvolvedor no corpo da issue com um checkbox marcado
        # Nota: O nome no checklist deve ser o mesmo que o nome completo na lista DEVELOPERS
        # ou uma versão capitalizada/formatada que o script possa encontrar.
        # Ex: "Arthencia" no checklist para "arthencia" no DEVELOPERS.
        if f"- [x] {developer_name.capitalize()}" in issue.body or f"- [x] {developer_name.replace('_', ' ').title()}" in issue.body:
            count += 1
    return count

def generate_ranking_table(ranking_data):
    """Gera a string da tabela de ranking em Markdown."""
    header = "| Posição | Desenvolvedor | Pontuação Total | Problemas Resolvidos |\n"
    separator = "|---------|---------------|-----------------|----------------------|\n"
    rows = []
    for i, (dev, data) in enumerate(ranking_data):
        # Formata o nome do desenvolvedor para exibição (ex: "arthencia" -> "Arthencia")
        display_name = dev.replace('_', ' ').title()
        rows.append(f"| {i+1} | {display_name} | {data['score']} | {data['solutions']} |\n")
    return header + separator + "".join(rows)

def update_readme(ranking_table):
    """Atualiza o README.md com a nova tabela de ranking."""
    readme_content = repo.get_contents("README.md").decoded_content.decode("utf-8")
start_marker = "&lt;!-- RANKING_START --&gt;"
end_marker = "&lt;!-- RANKING_END --&gt;"

# Se os marcadores não existirem, adiciona no final
if start_marker not in readme_content or end_marker not in readme_content:
    new_readme_content = readme_content.strip() + f"\n\n{start_marker}\n# 🏆 Ranking LeetCode da Equipe 🏆\n{ranking_table}\n{end_marker}\n"
else:
    # Substitui o conteúdo entre os marcadores
    new_readme_content = re.sub(
        f"{start_marker}.*{end_marker}",
        f"{start_marker}\n# 🏆 Ranking LeetCode da Equipe 🏆\n{ranking_table}\n{end_marker}",
        readme_content,
        flags=re.DOTALL
    )

repo.update_file(
    path="README.md",
    message="🤖 Atualiza ranking LeetCode",
    content=new_readme_content,
    sha=repo.get_contents("README.md").sha,
    branch="main"
)
print("README.md atualizado com sucesso!")
def main():
    scores = {}
    for dev in DEVELOPERS:
        solutions = get_solutions_count_from_main(dev) # Conta soluções mergeadas na main
        # checklists = get_checklist_marks_count(dev) # Mantido para acompanhamento, mas não pontua
    # A pontuação é diretamente o número de soluções mergeadas (1 ponto por solução)
    score = solutions

    scores[dev] = {"solutions": solutions, "score": score}

# Ordena o ranking pela pontuação total (decrescente)
sorted_ranking = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)

ranking_table = generate_ranking_table(sorted_ranking)
update_readme(ranking_table)
if __name__ == "__main__":
    main()