import pandas as pd
import math
import os

# 1. Carregar e limpar os dados do Excel
df = pd.read_excel('Preços P7.xlsx')
df = df.dropna(how='all', axis=1) # Remove colunas vazias
if 'Secção' not in df.columns:
    df.columns = df.iloc[0] # Define a primeira linha como cabeçalho
    df = df[1:]
df = df.dropna(subset=['Secção', 'Nome PT']) # Remove linhas sem dados

# 2. Configurações das Línguas
linguas = {
    'pt': {'ficheiro': 'index.html', 'col_nome': 'Nome PT', 'esgotado': 'Indisponível', 'aviso_pag': 'SÓ DINHEIRO', 'bandeiras': '<a href="en.html"><img src="uk_flag.png" alt="EN"></a> <a href="fr.html"><img src="frc_flag.png" alt="FR"></a> <a href="es.html"><img src="esp_flag.jpg" alt="ES"></a>'},
    'en': {'ficheiro': 'en.html', 'col_nome': 'Nome EN', 'esgotado': 'Unavailable', 'aviso_pag': 'CASH ONLY', 'bandeiras': '<a href="index.html"><img src="pt_flag.png" alt="PT"></a> <a href="fr.html"><img src="frc_flag.png" alt="FR"></a> <a href="es.html"><img src="esp_flag.jpg" alt="ES"></a>'},
    'fr': {'ficheiro': 'fr.html', 'col_nome': 'Nome FR', 'esgotado': 'Indisponible', 'aviso_pag': 'ESPÈCES UNIQUEMENT', 'bandeiras': '<a href="index.html"><img src="pt_flag.png" alt="PT"></a> <a href="en.html"><img src="uk_flag.png" alt="EN"></a> <a href="es.html"><img src="esp_flag.jpg" alt="ES"></a>'},
    'es': {'ficheiro': 'es.html', 'col_nome': 'Nome ES', 'esgotado': 'Agotado', 'aviso_pag': 'SOLO EFECTIVO', 'bandeiras': '<a href="index.html"><img src="pt_flag.png" alt="PT"></a> <a href="en.html"><img src="uk_flag.png" alt="EN"></a> <a href="fr.html"><img src="frc_flag.png" alt="FR"></a>'}
}

# 3. O Design do Site (CSS embutido e Grafismos Vetorizados)
html_base = """<!DOCTYPE html>
<html lang="{lang_code}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Menu - Posto 7</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap');
    body {{ font-family: 'Montserrat', sans-serif; background-color: #f7f3eb; color: #333333; margin: 0; padding: 20px; }}
    .language-switcher {{ position: absolute; top: 20px; right: 20px; display: flex; gap: 10px; z-index: 10; }}
    .language-switcher img {{ width: 32px; height: 22px; cursor: pointer; border: 1px solid #ccc; border-radius: 3px; transition: transform 0.2s; object-fit: cover; }}
    .language-switcher img:hover {{ transform: scale(1.1); }}
    .menu-container {{ max-width: 800px; margin: 0 auto; padding: 20px; position: relative; }}
    .header-logo {{ text-align: center; margin-bottom: 30px; margin-top: 30px; }}
    .header-logo img {{ max-width: 200px; height: auto; }}
    .main-cat-title {{ text-align: center; color: #cc2525; font-size: 32px; font-weight: 800; letter-spacing: 2px; margin-top: 50px; margin-bottom: 30px; border-bottom: 2px solid #cc2525; padding-bottom: 10px; text-transform: uppercase; }}
    .grid-layout {{ display: grid; grid-template-columns: 1fr; gap: 40px; }}
    @media (min-width: 768px) {{ .grid-layout {{ grid-template-columns: 1fr 1fr; }} }}
    .category-title {{ color: #cc2525; font-size: 22px; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; }}
    .item-group {{ border-left: 3px solid #cc2525; padding-left: 20px; position: relative; margin-bottom: 30px; }}
    .item-group::before, .item-group::after {{ content: ''; position: absolute; left: -8px; width: 10px; height: 10px; background-color: #f7f3eb; border: 3px solid #cc2525; transform: rotate(45deg); }}
    .item-group::before {{ top: 0; }} .item-group::after {{ bottom: 0; }}
    .menu-item {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; font-size: 16px; }}
    .item-name {{ flex-grow: 1; padding-right: 15px; }}
    .item-price {{ font-weight: 700; white-space: nowrap; }}
    .footer-section {{ text-align: center; margin-top: 60px; display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 40px; }}
    .footer-section img.pagamentos {{ max-width: 150px; width: 100%; height: auto; }}
</style>
</head>
<body>
<div class="language-switcher">{bandeiras}</div>
<div class="menu-container">
    <div class="header-logo">
        <img src="Logo P7.jpeg" alt="Logotipo Posto 7" onerror="this.style.display='none'">
    </div>
{conteudo}
    <div class="footer-section">
        <img src="pagamentos.png" class="pagamentos" alt="Não aceitamos cartões" onerror="this.style.display='none'">
        <div style="font-weight: 800; font-size: 18px; color: #cc2525; letter-spacing: 1px;">{aviso_pag}</div>
    </div>
</div>
</body>
</html>
"""

# 4. Construir os menus
for lang_code, info in linguas.items():
    conteudo_html = ""
    
    # Agrupar por grandes Secções (BEBIDAS, ESPIRITUOSAS, etc.)
    seccoes = df['Secção'].unique()
    for seccao in seccoes:
        conteudo_html += f'    <div class="main-cat-title">{seccao}</div>\n    <div class="grid-layout">\n'
        
        # Agrupar as Categorias da Secção atual
        df_seccao = df[df['Secção'] == seccao]
        categorias = df_seccao['Categoria'].unique()
        
        # Dividir em 2 colunas
        meio = math.ceil(len(categorias) / 2)
        colunas = [categorias[:meio], categorias[meio:]]
        
        for coluna in colunas:
            conteudo_html += '        <div class="column">\n'
            for categoria in coluna:
                conteudo_html += f'            <div class="category">\n                <div class="category-title">{categoria}</div>\n                <div class="item-group">\n'
                
                df_cat = df_seccao[df_seccao['Categoria'] == categoria]
                for _, linha in df_cat.iterrows():
                    nome = str(linha[info['col_nome']]).strip()
                    if nome == "nan" or not nome:
                        nome = str(linha['Nome PT']).strip() # Usa PT como fallback
                    
                    preco = str(linha['Preço']).strip()
                    
                    # Verifica a nova coluna de Esgotado
                    esta_esgotado = False
                    if 'Esgotado' in linha.index:
                        val = str(linha['Esgotado']).strip().lower()
                        if val in ['x', 'sim', 'v', '1']:
                            esta_esgotado = True
                    
                    # Aplica a lógica: se está esgotado ou se o preço foi posto a zero/x
                    if esta_esgotado or preco.lower() in ["x", "0", "indisponível", "esgotado", "nan"]:
                        preco_final = info['esgotado']
                    elif preco.replace('.', '', 1).isdigit():
                        preco_final = f"{preco}€"
                    else:
                        preco_final = preco
                        
                    conteudo_html += f'                    <div class="menu-item"><span class="item-name">{nome}</span><span class="item-price">{preco_final}</span></div>\n'
                
                conteudo_html += '                </div>\n            </div>\n'
            conteudo_html += '        </div>\n'
        conteudo_html += '    </div>\n'

    # 5. Guardar o ficheiro final
    html_final = html_base.format(lang_code=lang_code, bandeiras=info['bandeiras'], conteudo=conteudo_html, aviso_pag=info['aviso_pag'])
    with open(info['ficheiro'], "w", encoding="utf-8") as f:
        f.write(html_final)

print("Menus gerados com sucesso nas 4 linguas!")