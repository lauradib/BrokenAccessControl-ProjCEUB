"""
Instituto Vertice - portal academico fictício
Demonstração prática de A01:2021 Broken Access Control (site único,
com alternância ao vivo entre modo vulnerável e modo corrigido).

Cenário: um aluno autenticado consegue acessar o painel do professor
(ver e ALTERAR notas de qualquer aluno) só por conhecer a matrícula,
porque a rota do professor confere apenas se existe uma sessão ativa,
não se quem está logado tem o papel de professor.

Uso didático apenas, com dados fictícios. Não usar essa estrutura de
sessão/autenticação em produção.
"""

from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = "chave-de-demonstracao-nao-usar-em-producao"

# Prefixo pra deixar a URL mais fácil de reconhecer na apresentação:
# http://127.0.0.1:5050/site-demonstracao-ld/...
PREFIXO = "/site-demonstracao-ld"

USUARIOS = {
    "aluno1": {
        "senha": "1234",
        "tipo": "aluno",
        "matricula": "2023001",
        "nome": "Beatriz Nogueira Alves",
    },
    "aluno2": {
        "senha": "abcd",
        "tipo": "aluno",
        "matricula": "2023002",
        "nome": "Thiago Ramos Vieira",
    },
    "professor1": {
        "senha": "prof123",
        "tipo": "professor",
        "nome": "Prof. Eduardo Martins Rocha",
    },
}

NOTAS = {
    "2023001": [
        {"disciplina": "Fundamentos de Inteligência Artificial", "nota": 8.9},
        {"disciplina": "Aprendizado de Máquina", "nota": 8.2},
        {"disciplina": "Estrutura de Dados", "nota": 7.5},
        {"disciplina": "Processamento de Linguagem Natural", "nota": 8.6},
        {"disciplina": "Ética e Governança em IA", "nota": 9.4},
    ],
    "2023002": [
        {"disciplina": "Fundamentos de Inteligência Artificial", "nota": 6.8},
        {"disciplina": "Aprendizado de Máquina", "nota": 5.9},
        {"disciplina": "Estrutura de Dados", "nota": 7.1},
        {"disciplina": "Processamento de Linguagem Natural", "nota": 6.4},
        {"disciplina": "Ética e Governança em IA", "nota": 6.3},
    ],
}

MATRICULA_PARA_NOME = {
    dados["matricula"]: dados["nome"]
    for dados in USUARIOS.values()
    if dados["tipo"] == "aluno"
}

# Identificador simples pra usar na URL em vez da matrícula numérica,
# só pra facilitar digitar ao vivo na demonstração.
ALUNO_POR_SLUG = {
    "beatriz": "2023001",
    "thiago": "2023002",
}
SLUG_POR_MATRICULA = {matricula: slug for slug, matricula in ALUNO_POR_SLUG.items()}

# Estado global só pra demonstração ao vivo: liga/desliga a checagem de papel.
CONFIG = {"modo_seguro": False}


def usuario_logado():
    return session.get("usuario")


@app.context_processor
def injetar_contexto():
    return {
        "modo_seguro": CONFIG["modo_seguro"],
        "logado": usuario_logado(),
    }


@app.route("/")
def raiz():
    return redirect(url_for("index"))


@app.route(f"{PREFIXO}/")
def index():
    if not usuario_logado():
        return redirect(url_for("login"))
    if session.get("tipo") == "professor":
        return redirect(url_for("painel_professor"))
    return redirect(url_for("minhas_notas"))


@app.route(f"{PREFIXO}/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        dados = USUARIOS.get(usuario)
        if dados and dados["senha"] == senha:
            session.clear()
            session["usuario"] = usuario
            session["tipo"] = dados["tipo"]
            session["nome"] = dados["nome"]
            if dados["tipo"] == "aluno":
                session["matricula"] = dados["matricula"]
            return redirect(url_for("index"))
        erro = "Usuário ou senha inválidos."
    return render_template("login.html", erro=erro)


@app.route(f"{PREFIXO}/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route(f"{PREFIXO}/notas")
def minhas_notas():
    if not usuario_logado():
        return redirect(url_for("login"))
    matricula = session.get("matricula")
    if not matricula:
        return redirect(url_for("painel_professor"))
    return render_template(
        "minhas_notas.html",
        notas=NOTAS.get(matricula, []),
        nome=session.get("nome"),
        matricula=matricula,
    )


def acesso_professor_autorizado():
    """Ponto central da falha e da correção.

    Modo vulnerável: só confere se existe uma sessão autenticada,
    de qualquer tipo de usuário.

    Modo corrigido: confere também se o papel da sessão é 'professor',
    ou seja, adiciona a checagem de controle de acesso por função que
    faltava (WSTG-ATHZ-02 / WSTG-ATHZ-03).
    """
    if not usuario_logado():
        return False
    if CONFIG["modo_seguro"]:
        return session.get("tipo") == "professor"
    return True  # <- a falha: nenhuma checagem de papel aqui


@app.route(f"{PREFIXO}/professor/painel")
def painel_professor():
    if not acesso_professor_autorizado():
        abort(403)
    alunos = [
        {"slug": slug, "matricula": matricula, "nome": MATRICULA_PARA_NOME[matricula]}
        for slug, matricula in ALUNO_POR_SLUG.items()
    ]
    return render_template("painel_professor.html", alunos=alunos)


@app.route(f"{PREFIXO}/professor/notas/<slug>", methods=["GET", "POST"])
def notas_professor(slug):
    if not acesso_professor_autorizado():
        abort(403)
    matricula = ALUNO_POR_SLUG.get(slug)
    if not matricula or matricula not in NOTAS:
        abort(404)

    mensagem = None
    if request.method == "POST":
        disciplina = request.form.get("disciplina")
        nova_nota = request.form.get("nota")
        for item in NOTAS[matricula]:
            if item["disciplina"] == disciplina:
                try:
                    item["nota"] = round(float(nova_nota), 1)
                    mensagem = f'Nota de "{disciplina}" atualizada.'
                except (TypeError, ValueError):
                    mensagem = "Valor de nota inválido."

    return render_template(
        "professor_notas.html",
        slug=slug,
        matricula=matricula,
        nome=MATRICULA_PARA_NOME.get(matricula, matricula),
        notas=NOTAS[matricula],
        mensagem=mensagem,
    )


@app.route(f"{PREFIXO}/demo/alternar-modo", methods=["POST"])
def alternar_modo():
    CONFIG["modo_seguro"] = not CONFIG["modo_seguro"]
    destino = request.referrer or url_for("index")
    return redirect(destino)


@app.errorhandler(403)
def acesso_negado(_erro):
    return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(port=5050, debug=True)
