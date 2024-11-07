import requests
import tkinter as tk
from tkinter import messagebox, filedialog
import webbrowser
import pandas as pd
import threading
import string
from itertools import product
import time

# Variáveis globais
pausar = False
parar = False
urls_ativas = []

def verificar_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

def atualizar_contador(valor):
    contador_var.set(f"URLs Ativas Encontradas: {valor}")

def verificar_urls_com_combinacoes(url_base, sequencia_n1, sequencia_n2):
    global pausar, parar, urls_ativas
    qtd_n1 = url_base.count("{N1}")
    qtd_n2 = url_base.count("{N2}")
    combinacoes = product(sequencia_n1 if qtd_n1 > 0 else [''], sequencia_n2 if qtd_n2 > 0 else [''])

    for n1, n2 in combinacoes:
        if parar:
            break
        while pausar:
            time.sleep(0.1)

        url_modificada = url_base.replace("{N1}", n1).replace("{N2}", n2)

        resultado_texto.insert(tk.END, f"Pesquisando: {url_modificada}\n")
        resultado_texto.see(tk.END)

        url = verificar_url(url_modificada)
        if url:
            adicionar_resultado(url)
            urls_ativas.append(url)
            atualizar_contador(len(urls_ativas))
    return urls_ativas

def adicionar_resultado(url):
    resultado_texto.insert(tk.END, url + "\n", url)
    resultado_texto.tag_add(url, "end-2c linestart", "end-1c")
    resultado_texto.tag_config(url, foreground="blue", underline=True)
    resultado_texto.tag_bind(url, "<Button-1>", lambda e, link=url: webbrowser.open(link))
    resultado_texto.see(tk.END)

def salvar_arquivo_excel():
    if urls_ativas:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Arquivo Excel", "*.xlsx")])
        if file_path:
            df = pd.DataFrame(urls_ativas, columns=["URLs Ativas"])
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Sucesso", "Arquivo Excel salvo com sucesso!")
    else:
        messagebox.showwarning("Aviso", "Não há URLs para salvar.")

def verificar():
    global pausar, parar, urls_ativas
    pausar = False
    parar = False
    urls_ativas = []
    url_base = entrada_url.get()
    
    if not url_base.startswith("https://"):
        url_base = "https://" + url_base

    if '{N1}' not in url_base and '{N2}' not in url_base:
        messagebox.showerror("Erro", "A URL base deve conter '{N1}', '{N2}', ou ambos onde deseja inserir os valores.")
        return

    tipo_sequencia = var_sequencia.get()

    try:
        if tipo_sequencia == "Números":
            inicio_n1 = int(entrada_inicio_n1.get())
            fim_n1 = int(entrada_fim_n1.get())
            inicio_n2 = int(entrada_inicio_n2.get())
            fim_n2 = int(entrada_fim_n2.get())
            
            # Sequência de N1 com zeros à esquerda (4 dígitos) e N2 sem zeros à esquerda
            sequencia_n1 = [str(i) for i in range(inicio_n1, fim_n1 + 1)]  
            sequencia_n2 = [str(i) for i in range(inicio_n2, fim_n2 + 1)] 

    except ValueError as e:
        messagebox.showerror("Erro", f"Entrada inválida: {e}")
        return

    resultado_texto.delete("1.0", tk.END)
    resultado_texto.insert(tk.END, "Iniciando a pesquisa...\n")
    atualizar_contador(0)

    # Inicia a thread de verificação em background com as duas sequências separadas
    thread = threading.Thread(target=background_verificacao, args=(url_base, sequencia_n1, sequencia_n2))
    thread.start()

def background_verificacao(url_base, sequencia_n1, sequencia_n2):
    verificar_urls_com_combinacoes(url_base, sequencia_n1, sequencia_n2)
    resultado_texto.insert(tk.END, "\n--- Fim da pesquisa ---\n")
    messagebox.showinfo("Fim da Verificação", "A verificação das URLs foi concluída!")

def pausar_pesquisa():
    global pausar
    pausar = True

def retomar_pesquisa():
    global pausar
    pausar = False

def salvar():
    salvar_arquivo_excel()

# Criação da janela principal
janela = tk.Tk()
janela.title("Verificar URLs com Múltiplas Sequências")

# Labels e entradas de texto
tk.Label(janela, text="URL base (use {N1} e/ou {N2} onde deseja colocar o número/letra):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
entrada_url = tk.Entry(janela, width=50)
entrada_url.insert(0, "https://")
entrada_url.grid(row=0, column=1, columnspan=3, padx=10, pady=10)

# Seleção de tipo de sequência
var_sequencia = tk.StringVar(value="Números")
tk.Radiobutton(janela, text="Números", variable=var_sequencia, value="Números").grid(row=3, column=0, padx=10, pady=10, sticky="w")

# Configurações para números N1 e N2
tk.Label(janela, text="Início (N1):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entrada_inicio_n1 = tk.Entry(janela, width=10)
entrada_inicio_n1.grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Label(janela, text="Fim (N1):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entrada_fim_n1 = tk.Entry(janela, width=10)
entrada_fim_n1.grid(row=2, column=1, padx=10, pady=5, sticky="w")

tk.Label(janela, text="Início (N2):").grid(row=1, column=2, padx=10, pady=5, sticky="w")
entrada_inicio_n2 = tk.Entry(janela, width=10)
entrada_inicio_n2.grid(row=1, column=3, padx=10, pady=5, sticky="w")

tk.Label(janela, text="Fim (N2):").grid(row=2, column=2, padx=10, pady=5, sticky="w")
entrada_fim_n2 = tk.Entry(janela, width=10)
entrada_fim_n2.grid(row=2, column=3, padx=10, pady=5, sticky="w")

# Botões de controle
contador_var = tk.StringVar(value="URLs Ativas Encontradas: 0")
tk.Label(janela, textvariable=contador_var).grid(row=4, column=0, columnspan=2, padx=10, pady=10)

tk.Button(janela, text="Verificar URLs", command=verificar).grid(row=5, column=0, padx=10, pady=10, sticky="w")
tk.Button(janela, text="Pausar", command=pausar_pesquisa).grid(row=5, column=1, padx=10, pady=10)
tk.Button(janela, text="Retomar", command=retomar_pesquisa).grid(row=5, column=2, padx=10, pady=10)
tk.Button(janela, text="Salvar Resultado", command=salvar).grid(row=5, column=3, padx=10, pady=10)

resultado_texto = tk.Text(janela, height=20, width=80)
resultado_texto.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

janela.mainloop()
