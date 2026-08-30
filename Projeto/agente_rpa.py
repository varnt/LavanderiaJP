import asyncio
import ollama
from playwright.async_api import async_playwright
#ele reserva o horário desejado, mas não consegue clicar no botão de confirmação, então o horário fica reservado.
EMAIL = "varnt@outlook.com"
SENHA = "0portunidades2023"
DIA_SELECIONADO = "2026-08-29" # Formato YYYY-MM-DD
HORARIO_DESEJADO = "04:00 PM - 05:50 PM"  # Exemplo de horário desejado
    
    # URL direta extraída da sua macro (com a data embutida dinamicamente)
URL_ALVO = f"https://app.townsq.com.br/w/63652bfecd1a8c03d0e88066/reservations/68a8a363f9b7ed5c085a9bd7?day={DIA_SELECIONADO}"


async def main():
    # Inicia o Playwright (headless=False permite ver o robô trabalhando)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🤖 [RPA] Passo 1: Realizando Login...")
        await page.goto('https://app.townsq.com.br/login')
        
        # Preenche email (usando os seletores da sua macro)
        await page.locator('id=email-form--input--email').fill(EMAIL)
        await page.locator('xpath=/html/body/comm-app-root/comm-login-v2/comm-auth-card/div/div/div/comm-login-email-form/form/div[2]/tsq-button/button/span').click()
        
        # Preenche senha
        await page.locator('id=password-form--input--email').fill(SENHA)
        await page.locator('xpath=/html/body/comm-app-root/comm-login-v2/comm-auth-card/div/div/div/comm-login-password-form/form/div[3]/tsq-button/button').click()

        # Aguarda a página inicial carregar para garantir que o login concluiu
        await page.wait_for_selector('comm-home-top-header', timeout=15000)

        print("🤖 [RPA] Passo 2: Pulando direto para a URL da Lavanderia...")
        await page.goto(URL_ALVO)
        print("🤖 [RPA] Passo 2.1: espera 3 segs")
        await asyncio.sleep(3)  # Pequena pausa para garantir que a página carregou
        
        print("🤖 [RPA] Passo 2.2: Aguarda a lista de horários renderizar na tela")
        # Aguarda a lista de horários renderizar na tela
        #await page.wait_for_selector('day-timeslots')

        print("🤖 [RPA] Passo 3: Extraindo horários...")

        

        texto_horarios = await page.locator('day-timeslots').inner_text()

        print("\n========== HORÁRIOS ENCONTRADOS ==========")
        print(texto_horarios)
        print("===========================================\n")

        # ============================================================
        # PROCURA O HORÁRIO
        # ============================================================

        print(
            f"🔎 Procurando horário: {HORARIO_DESEJADO}"
        )

        # Pega todos os elementos de horário
        slots = page.locator(
            "day-timeslots > div > div"
        )

        quantidade = await slots.count()

        print(
            f"🔎 {quantidade} slots encontrados."
        )

        horario_encontrado = None

        for i in range(quantidade):

            slot = slots.nth(i)

            texto = await slot.inner_text()

            print(
                f"\n--- SLOT {i + 1} ---\n"
                f"{texto}"
            )

            # Normaliza para facilitar comparação
            texto_normalizado = texto.lower()

            # Procura o horário desejado
            if HORARIO_DESEJADO.lower() in texto_normalizado:

                horario_encontrado = slot

                print(
                    f"🎯 Horário encontrado: "
                    f"{HORARIO_DESEJADO}"
                )

                break

        # ============================================================
        # HORÁRIO NÃO ENCONTRADO
        # ============================================================

        if horario_encontrado is None:

            print(
                f"❌ Horário {HORARIO_DESEJADO} "
                f"não encontrado."
            )

            await browser.close()
            return

        # ============================================================
        # VERIFICA DISPONIBILIDADE
        # ============================================================

        texto_slot = await horario_encontrado.inner_text()

        texto_slot_lower = texto_slot.lower()

        if (
            "reserved" in texto_slot_lower
            or
            "waiting list" in texto_slot_lower
        ):

            print(
                f"❌ Horário {HORARIO_DESEJADO} "
                f"está indisponível."
            )

            print(
                f"Motivo:\n{texto_slot}"
            )

            await browser.close()
            return

        # ============================================================
        # DISPONÍVEL → CLICA
        # ============================================================

        print(
            f"✅ Horário {HORARIO_DESEJADO} "
            f"está disponível!"
        )

        botao = horario_encontrado.locator(
            "button"
        )

        await botao.click()

        print(
            "🤖 [RPA] Confirmando reserva..."
        )

        botao_confirmar = page.get_by_role(
            "button",
            name="Reserve",
            exact=True
        )

        await botao_confirmar.wait_for(
            state="visible",
            timeout=5000
        )

        await botao_confirmar.click()

        print(
            "✅ Reserva confirmada!"
        )

        await asyncio.sleep(5)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())