# Diretrizes para Agentes

## Objetivo
Ajudar a concluir projetos, não iniciar novos.

## Limite de Foco
Limite de um projeto ativo por vez.

## Permissões de Escrita
- **ideias.md**: só recebe linhas novas no fim (nunca edita as existentes).
- **projetos/*.md**: é editado apenas a partir de uma tarefa aprovada.
- **decisoes.md**: é registrado após decisão minha.

## Proibido
- Criar projeto novo sem pedido explícito.
- Apagar histórico.
- Reescrever seções que não fazem parte da tarefa.

## Modo de Entrevista
Ao receber uma nova demanda, ideia ou solicitação de tarefa, o agente não deve começar a construir imediatamente. Deve entrar em **Modo de Entrevista**:
- Fazer perguntas curtas e diretas (uma por vez ou em bloco mínimo) para clarificar escopo e intenção.
- Determinar se o item é uma ideia para a caixa de captura (`ideias.md`) ou uma tarefa ligada ao projeto ativo.
- Exigir sempre:
  1. **Critério de conclusão** ("Pronto quando: ...").
  2. **Próximo passo concreto** e acionável com tempo estimado.
- Lembrar e proteger o limite de **um projeto ativo por vez** (se for proposta de novo projeto, questionar o destino do projeto ativo atual antes de qualquer criação).
- Finalizar a entrevista gerando o bloco estruturado correspondente (`PROJETO:` ou `IDEIA:`).


## Formato Obrigatório dos Projetos
```markdown
# [Nome do projeto]

**Status:** ativo | pausado | concluído | arquivado
**Prioridade:** 1 | 2 | 3
**Última atualização:** [dd/mm]

## Objetivo
[uma frase]

## Onde parei
[2 a 3 linhas]

## Próximo passo
[uma ação concreta, com tempo estimado]

## Histórico
- [dd/mm]: [evento]
```
