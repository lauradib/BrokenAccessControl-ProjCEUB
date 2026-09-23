# Centro Universitário Synapse: demonstração ao vivo de A01:2021 Broken Access Control

## Sobre este projeto
Aplicação intencionalmente vulnerável, criada como demonstração prática de um Projeto de Pesquisa sobre a vulnerabilidade A01:2021 Broken Access Control (OWASP Top 10). Simula o portal acadêmico fictício de um curso de Inteligência Artificial: um aluno autenticado consegue chegar ao painel do professor e alterar a nota de outro aluno, e a mesma tentativa é bloqueada ao vivo quando a correção é ativada, sem reiniciar o servidor.

Todos os dados são fictícios.

## Projeto de pesquisa
O artigo científico completo, com conceito, impactos, formas de detecção e boas práticas de mitigação da falha, está disponível aqui: [Projeto de Pesquisa – Broken Access Control](docs/Projeto_de_Pesquisa_Broken_Access_Control.pdf)

## Aviso
Aplicação apenas para fins didáticos. Chave de sessão fixa no código, sem persistência real de dados e sem nenhum dado de pessoa real. Não usar essa estrutura de autenticação em produção.

## Contas de teste

| usuário | senha | papel |
|---|---|---|
| aluno1 | 1234 | aluno, Beatriz Nogueira Alves (matrícula 2023001) |
| aluno2 | abcd | aluno, Thiago Ramos Vieira (matrícula 2023002) |
| professor1 | prof123 | professor, Prof. Eduardo Martins Rocha |

## Como obter os arquivos

**Sem Terminal:** clique no botão verde "Code" no topo da página do repositório e escolha "Download ZIP". Extraia o arquivo como qualquer outro zip.

**Com Terminal:**

git clone https://github.com/lauradib/BrokenAccessControl-ProjCEUB.git


## Como rodar

python3 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install flask
python app.py


Abra `http://127.0.0.1:5050/site-demonstracao-ld/` no navegador (quem digitar só `http://127.0.0.1:5050/` é redirecionado automaticamente).

## Como conduzir a demonstração ao vivo

O site sempre começa em modo vulnerável (banner vermelho no topo). Roteiro:

1. Login como aluno1 (1234). A tela "Minhas notas" mostra só o boletim da própria Beatriz.
2. Na barra de endereço, digite `http://127.0.0.1:5050/site-demonstracao-ld/professor/notas/thiago`. O boletim de Thiago (aluno2) abre normalmente, mesmo Beatriz nunca tendo feito login como professor.
3. Troque uma nota e clique em "Salvar". A alteração fica salva de verdade, confirme voltando à página ou logando como professor1.
4. Logout, entre como professor1 (prof123) e clique em "Ativar correção" no banner.
5. Logout de novo, entre como aluno1 e repita o passo 2: a página agora retorna 403, Acesso negado, tanto pra ver quanto pra alterar.
6. Se quiser, mostre que professor1, logado de verdade, continua acessando `/site-demonstracao-ld/professor/painel` normalmente. A correção não quebra a funcionalidade legítima, só fecha a falha.

## Onde está a falha e a correção

Tudo se resolve numa única função em `app.py`, `acesso_professor_autorizado()`:

- Vulnerável: confere só se existe uma sessão autenticada, sem checar o papel dela.
- Corrigido: com o modo seguro ligado, confere também se `session.get("tipo") == "professor"`, controle de acesso por função, aplicado no servidor, antes de responder.

O botão do banner alterna a variável `CONFIG["modo_seguro"]` em memória, pra ligar e desligar a proteção ao vivo, sem reiniciar o servidor.

## Screenshots

A pasta `screenshots/` tem capturas do fluxo completo: login, "Minhas notas", o acesso indevido em modo vulnerável, o painel do professor e o bloqueio 403 depois da correção.
