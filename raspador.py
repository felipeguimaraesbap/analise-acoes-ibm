import os
import re
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup

def obter_caminho_salvamento():
    # Salva direto no seu usuário (C:\Users\felip\Extracoes_Web) fugindo do OneDrive
    caminho = os.path.join(os.path.expanduser('~'), 'Extracoes_Web')
    if not os.path.exists(caminho):
        os.makedirs(caminho)
    return caminho

def limpar_nome_arquivo(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome).strip()

def extrair_texto():
    url = url_input.get().strip()
    
    if not url:
        messagebox.showwarning("Aviso", "Por favor, insira uma URL válida.")
        return
    
    texto_output.delete("1.0", tk.END)
    texto_output.insert(tk.END, "Carregando conteúdo... Aguarde.\n")
    window.update()

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titulo_pagina = soup.title.string if soup.title else "Texto_Extraido"
        titulo_valido = limpar_nome_arquivo(titulo_pagina)[:50]
        
        for script_or_style in soup(['script', 'style', 'footer', 'nav', 'header']):
            script_or_style.decompose()
            
        texto_limpo = soup.get_text()
        
        linhas = (linha.strip() for linha in texto_limpo.splitlines())
        blocos = (bloco for bloco in linhas if bloco)
        texto_final = '\n\n'.join(blocos)
        
        texto_output.delete("1.0", tk.END)
        
        if texto_final:
            texto_output.insert(tk.END, texto_final)
            
            pasta_destino = obter_caminho_salvamento()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"{titulo_valido}_{timestamp}.txt"
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            
            with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(f"Fonte: {url}\n")
                arquivo.write(f"Data da extração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                arquivo.write("=" * 60 + "\n\n")  
                arquivo.write(texto_final)
            
            messagebox.showinfo("Sucesso!", f"Texto extraído com sucesso!\n\nSalvo em:\n{caminho_completo}")
        else:
            texto_output.insert(tk.END, "Nenhum texto visível foi encontrado nesta página.")
            
    except requests.exceptions.RequestException as e:
        texto_output.delete("1.0", tk.END)
        messagebox.showerror("Erro de Conexão", f"Não foi possível acessar a página.\nDetalhes: {e}")
    except Exception as e:
        texto_output.delete("1.0", tk.END)
        messagebox.showerror("Erro ao salvar", f"Ocorreu um erro ao salvar o arquivo.\nDetalhes: {e}")

window = tk.Tk()
window.title("Extrator de Texto Web")
window.geometry("800x600")

frame_topo = tk.Frame(window)
frame_topo.pack(pady=10, fill=tk.X, padx=10)

label_url = tk.Label(frame_topo, text="Cole a URL do site aqui:")
label_url.pack(side=tk.LEFT, padx=5)

url_input = tk.Entry(frame_topo, width=60)
url_input.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

btn_extrair = tk.Button(frame_topo, text="Extrair e Salvar", command=extrair_texto, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
btn_extrair.pack(side=tk.LEFT, padx=5)

label_resultado = tk.Label(window, text="Texto extraído:")
label_resultado.pack(anchor=tk.W, padx=15, pady=(5, 0))

texto_output = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 11))
texto_output.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

window.mainloop()