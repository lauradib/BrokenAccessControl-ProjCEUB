# Centro Universitário Synapse — demonstração ao vivo de A01:2021 Broken Access Control

## Sobre este projeto

Aplicação intencionalmente vulnerável, criada como demonstração prática do
Projeto de Pesquisa sobre OWASP Top 10 (vulnerabilidade A01: Broken Access
Control). Simula o portal acadêmico fictício de um curso de Inteligência
Artificial e mostra, com clique na tela em vez de comando de terminal, um
aluno autenticado alcançando o painel do professor e alterando a nota de
outro aluno — e depois a mesma tentativa sendo bloqueada com a correção
ligada, ao vivo, sem reiniciar o servidor.

Todos os dados são fictícios. Este site complementa, não substitui, a
transcrição de `curl` que documenta o mesmo cenário linha a linha
(disponível na pasta principal do projeto), usada como evidência técnica
reproduzível no artigo científico.

**Aviso:** aplicação apenas para fins didáticos. Chave de sessão fixa no
código, sem persistência real de dados, sem qualquer dado de pessoa real.
Não usar essa estrutura de autenticação em produção.

## Contas de teste

| usuário | senha | papel |
|---|---|---|
| aluno1 | 1234 | aluno — Beatriz Nogueira Alves (matrícula 2023001) |
| aluno2 | abcd | aluno — Thiago Ramos Vieira (matrícula 2023002) |
| professor1 | prof123 | professor — Prof. Eduardo Martins Rocha |

## Como rodar

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask
python app.py
```

Abra http://127.0.0.1:5050/site-demonstracao-ld/ no navegador (quem digitar só
`http://127.0.0.1:5050/` é redirecionado pra lá automaticamente).

## Como conduzir a demonstração ao vivo

O site sempre começa em **modo vulnerável** (o banner no topo mostra isso em
vermelho). O roteiro:

1. **Login como aluno1** (1234). Mostre a tela "Minhas notas": só aparece o
   boletim da própria Beatriz, com as disciplinas de Inteligência Artificial.
2. Na barra de endereço, digite diretamente
   `http://127.0.0.1:5050/site-demonstracao-ld/professor/notas/thiago` — a
   página do Thiago (aluno2). O boletim dele abre normalmente, mesmo Beatriz
   nunca tendo feito login como professor.
3. Troque o valor de uma nota e clique em "Salvar". A alteração é real e
   fica salva — mostre voltando à mesma página, ou logando como professor1
   pra confirmar.
4. Faça logout, entre como **professor1** (prof123) e clique em
   "Ativar correção" no banner vermelho do topo.
5. Faça logout de novo, entre como **aluno1** e repita o passo 2: agora a
   página retorna **403 — Acesso negado**, tanto pra ver quanto pra alterar.
6. Se quiser, mostre também que o professor1, logado de verdade, continua
   acessando `/site-demonstracao-ld/professor/painel` normalmente — a
   correção não quebrou a funcionalidade legítima, só fechou a falha.

## Onde está a falha e onde está a correção

Tudo se resolve numa única função em `app.py`, `acesso_professor_autorizado()`:

- **Vulnerável**: confere só se existe uma sessão autenticada
  (`usuario_logado()`), sem checar qual é o papel dela.
- **Corrigido**: quando o modo seguro está ligado, confere também
  `session.get("tipo") == "professor"` — controle de acesso por função,
  aplicado do lado do servidor, antes de responder qualquer coisa.

O botão do banner apenas alterna a variável `CONFIG["modo_seguro"]` em
memória, pra você poder ligar e desligar a proteção ao vivo, na frente da
turma, sem reiniciar o servidor nem trocar de aba.

## Screenshots

A pasta `screenshots/` tem capturas reais do fluxo completo: tela de login,
"Minhas notas", o acesso indevido ao boletim de outro aluno em modo
vulnerável, o painel do professor e o bloqueio 403 depois da correção.
