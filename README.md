<<<<<<< HEAD
# Projeto de Assistente por Voz com OpenAI

Projeto simples de assistente por voz em português:
1. captura o áudio do usuário;
2. faz a transcrição;
3. envia o texto para a LLM;
4. imprime a resposta;
5. gera a fala da resposta.

## Melhorias aplicadas
- tratamento básico de erros e interrupção por teclado;
- comando de saída por voz (`sair`, `encerrar`, `exit`);
- limite de contexto da conversa para reduzir custo;
- mensagem de sistema para manter respostas curtas e em português;
- salvamento de histórico em `conversation_log.txt`;
- organização do código em funções mais claras;
- validação da variável `OPENAI_API_KEY`.

## Como executar
```bash
pip install -r requirements.txt
python projeto_openai.py
```

Crie um arquivo `.env` com:
```env
OPENAI_API_KEY=sua_chave_aqui
```

## Próximos passos graduais
- adicionar ativação por palavra-chave;
- permitir escolha de voz e idioma por configuração;
- mostrar transcrição parcial antes da resposta final;
- salvar histórico em JSON para facilitar análise futura;
- criar modo CLI e modo interface web simples;
- adicionar testes para funções isoladas.