import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os
from datetime import datetime

# config selenium otimizado
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless=new")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
# bloquear imagens, css, videos e fonts p ser mais rapido
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.stylesheets": 2,
    "profile.managed_default_content_settings.plugins": 2,
    "profile.managed_default_content_settings.popups": 2,
    "profile.managed_default_content_settings.geolocation": 2,
    "profile.managed_default_content_settings.notifications": 2,
    "profile.managed_default_content_settings.media_stream": 2,
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# evitar deteccoes
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
})

# buscas
buscas = [
    "empresa de energia solar Goiás",
    "empresas energia solar Goiás",
    "energia solar instalação Goiás",
    "instaladora energia solar Goiás",
    "painel solar empresa Goiás",
    "placas solares instalação Goiás",
    "placas solares empresa Goiás",
    "painel fotovoltaico empresa Goiás",
    "sistema fotovoltaico Goiás",
    "empresa fotovoltaica Goiás",
    "instaladora fotovoltaica Goiás",
    "usina solar empresa Goiás",
    "fornecedora energia solar Goiás",
    "consultoria energia solar Goiás",
    "venda de placas solares Goiás",
    "empresa de energia solar interior de Goiás",
    "empresa de energia solar no estado de Goiás",
    "energia solar serviço Goiás",
    "soluções energia solar Goiás",

    # variações com cidades maiores
    "energia solar Goiânia empresa",
    "empresa energia solar Goiânia",
    "instaladora energia solar Goiânia",
    "painel solar Goiânia empresa",
    "energia solar Anápolis empresa",
    "empresa energia solar Anápolis",
    "energia solar Rio Verde empresa",
    "empresa energia solar Rio Verde",
    "energia solar Catalão empresa",
    "empresa energia solar Catalão",
    "energia solar Aparecida de Goiânia empresa",
    "empresa energia solar Aparecida de Goiânia",
    "energia solar Jataí empresa",
    "empresa energia solar Jataí",

    # variações gerais
    "orçamento energia solar Goiás",
    "melhores empresas energia solar Goiás",
    "empresas fotovoltaicas Goiás",
    "integrador solar Goiás",
    "revenda energia solar Goiás",
    "distribuidora energia solar Goiás",
    "empresa de energia solar residencial Goiás",
    "empresa de energia solar comercial Goiás",
    "empresa de energia solar rural Goiás",
    "energia solar fazenda Goiás",
    "energia solar agronegócio Goiás",
    "energia solar propriedades rurais Goiás",

    # buscas com frases longas (geram resultados diferentes)
    "onde encontrar empresa de energia solar em Goiás",
    "empresa confiável de energia solar em Goiás",
    "empresa para instalar energia solar em Goiás",
    "instalação de energia solar para casas em Goiás",
    "instalação de energia solar para empresas em Goiás",
    "energia solar em municípios de Goiás",

    # complementares
    "manutenção energia solar Goiás",
    "suporte energia solar Goiás",
    "engenharia energia solar Goiás",
]



# dominios bloqueados
dominios_bloqueados = [
    "youtube.com",
    "youtu.be",
    "globo.com",
    "g1.globo.com",
    "reddit.com",
    "play.google.com",
    "apps.apple.com",
]

# limite de links
LIMITE_LINKS = 300
links = set()

print("🔍 Coletando links do DuckDuckGo...\n")

# coletar links
for termo in buscas:
    url = f"https://duckduckgo.com/?q={termo.replace(' ', '+')}&t=h_&ia=web"
    driver.get(url)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "lxml")

    for a in soup.find_all("a", href=True):
        link = a["href"]

        # ignorar domínios bloqueados
        if any(b in link for b in dominios_bloqueados):
            continue

        if link.startswith("http") and "duckduckgo.com" not in link:
            links.add(link)

        if len(links) >= LIMITE_LINKS:
            break

    if len(links) >= LIMITE_LINKS:
        break

driver.quit()

print(f"🔗 TOTAL DE LINKS COLETADOS: {len(links)}\n")

# extrair dados do site
empresas = []

print("📄 Extraindo informações dos sites...\n")

for link in links:
    try:
        r = requests.get(link, timeout=5)
        html = r.text

        soup = BeautifulSoup(html, "lxml")
        texto = soup.get_text(" ", strip=True)

        nome = soup.title.string if soup.title else ""

        # telefone
        telefone = ""
        padrao_tel = r"(\(?\d{2}\)?\s?\d{4,5}-?\d{4})"
        achados_tel = re.findall(padrao_tel, texto)
        if achados_tel:
            telefone = achados_tel[0]

        # e-mail
        padrao_email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        achados_email = re.findall(padrao_email, texto)
        email = achados_email[0] if achados_email else ""

        # endereço
        endereco = ""
        for linha in texto.split("\n"):
            if "GO" in linha or "Goiás" in linha:
                if 5 < len(linha) < 100:
                    endereco = linha.strip()
                    break

        empresas.append({
            "Nome": nome,
            "Site": link,
            "Telefone": telefone,
            "Email": email,
            "Endereço": endereco
        })

        print(f"✔ {nome}")

    except Exception as e:
        print(f"❌ Erro no site {link}: {e}")

# salvar excel com data e hora
agora = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
nome_arquivo = f"empresas_energia_solar_go_{agora}.xlsx"
CAMINHO = os.path.join(os.path.expanduser("~"), "Desktop", nome_arquivo)

df = pd.DataFrame(empresas)
df.to_excel(CAMINHO, index=False)

print("\n🎉 Arquivo salvo na Área de Trabalho:")
print(CAMINHO)