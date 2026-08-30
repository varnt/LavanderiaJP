import asyncio
from browser_use import Agent, ChatOllama


async def main():
    # 1. Defina suas variáveis aqui
    EMAIL = "varnt@outlook.com"
    SENHA = "0portunidades2023"
    DIA_SELECIONADO = "2026-08-18" # Formato YYYY-MM-DD
    HORARIO_DESEJADO = "4PM"  # Exemplo de horário desejado

    # URL direta extraída da sua macro (com a data embutida dinamicamente)
    URL_ALVO = f"https://app.townsq.com.br/w/63652bfecd1a8c03d0e88066/reservations/68a8a363f9b7ed5c085a9bd7?day={DIA_SELECIONADO}"

    # 2. Inicializa o TinyLlama restrito
    llm = ChatOllama(model="tinyllama")

    # 3. Prompt com checklist atômico baseado no HTML real
    task = f"""
    Siga EXATAMENTE estes passos em ordem, executando apenas UMA ação por vez:
    
    Passo 1: Navegue DIRETAMENTE para a URL: '{URL_ALVO}'.
    Passo 2: Preencha o campo de email com '{EMAIL}' e clique no botão de avançar.
    Passo 3: Preencha o campo de senha com '{SENHA}' e clique no botão de entrar.
    Passo 4: Navegue DIRETAMENTE para a URL: '{URL_ALVO}'.
    Passo 5: A página exibirá botões com horários. IMPORTANTE: ignore botões que possuam a classe HTML 'unavailable' ou que estejam próximos aos textos 'Reserved' ou 'Waiting list'. Clique no primeiro botão de horário que estiver DISPONÍVEL (por exemplo, um botão com o texto '06:00 AM - 07:50 AM' ou '08:00 AM - 09:50 AM').
    Passo 6: Um modal de confirmação será aberto. Clique no botão de confirmação que possui o atributo id='confirm-button'.
    Passo 7: Finalize a execução e retorne a mensagem "Tentativa de reserva concluída."
    """

    # 4. Configuração do Agente com trava de ações simultâneas
    agent = Agent(
        task=task,
        llm=llm,
        use_vision=False,
        max_actions_per_step=1,
    )
    
    # Executa a tarefa e imprime o resultado
    resultado = await agent.run()
    print("\n=== STATUS DA RESERVA ===")
    print(resultado)

if __name__ == "__main__":
    asyncio.run(main())