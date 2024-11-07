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

def verificar_urls_com_combinacoes(url_base_1, url_base_2, sequencia_n1, sequencia_n2):
    global pausar, parar, urls_ativas
    combinacoes_n1 = product(sequencia_n1, repeat=url_base_1.count("{N1}"))
    combinacoes_n2 = product(sequencia_n2, repeat=url_base_1.count("{N2}"))

    for n1_valores in combinacoes_n1:
        for n2_valores in combinacoes_n2:
            if parar:
                break
            while pausar:
                time.sleep(0.1)

            # Substituir N1 e N2 no primeiro padrão de URL
            url_modificada_1 = url_base_1
            for valor in n1_valores:
                url_modificada_1 = url_modificada_1.replace("{N1}", str(valor), 1)
            for valor in n2_valores:
                url_modificada_1 = url_modificada_1.replace("{N2}", str(valor), 1)

            resultado_texto.insert(tk.END, f"Pesquisando: {url_modificada_1}\n")
            resultado_texto.see(tk.END)

            url = verificar_url(url_modificada_1)
            if url:
                adicionar_resultado(url)
                urls_ativas.append(url)
                atualizar_contador(len(urls_ativas))

            # Substituir N1 e N2 no segundo padrão de URL
            url_modificada_2 = url_base_2
            for valor in n1_valores:
                url_modificada_2 = url_modificada_2.replace("{N1}", str(valor), 1)
            for valor in n2_valores:
                url_modificada_2 = url_modificada_2.replace("{N2}", str(valor), 1)

            resultado_texto.insert(tk.END, f"Pesquisando: {url_modificada_2}\n")
            resultado_texto.see(tk.END)

            url = verificar_url(url_modificada_2)
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
    url_base_1 = entrada_url_1.get()
    url_base_2 = entrada_url_2.get()

    if not url_base_1.startswith("https://"):
        url_base_1 = "https://" + url_base_1
    if not url_base_2.startswith("https://"):
        url_base_2 = "https://" + url_base_2

    if '{N1}' not in url_base_1 or '{N2}' not in url_base_1 or '{N1}' not in url_base_2 or '{N2}' not in url_base_2:
        messagebox.showerror("Erro", "As URLs base devem conter '{N1}' e '{N2}' onde deseja inserir os valores.")
        return

    sequencia_n1 = obter_sequencia(var_sequencia_n1, entrada_inicio_n1, entrada_fim_n1)
    sequencia_n2 = obter_sequencia(var_sequencia_n2, entrada_inicio_n2, entrada_fim_n2)

    resultado_texto.delete("1.0", tk.END)
    resultado_texto.insert(tk.END, "Iniciando a pesquisa...\n")
    atualizar_contador(0)

    thread = threading.Thread(target=background_verificacao, args=(url_base_1, url_base_2, sequencia_n1, sequencia_n2))
    thread.start()

def obter_sequencia(var_sequencia, entrada_inicio, entrada_fim):
    tipo_sequencia = var_sequencia.get()
    try:
        if tipo_sequencia == "Números":
            inicio = int(entrada_inicio.get())
            fim = int(entrada_fim.get())
            if inicio > fim:
                raise ValueError("O número inicial deve ser menor ou igual ao número final.")
            return [str(i) for i in range(inicio, fim + 1)]
        elif tipo_sequencia == "Letras":
            inicio = string.ascii_lowercase.index(entrada_inicio.get().lower())
            fim = string.ascii_lowercase.index(entrada_fim.get().lower())
            if inicio > fim:
                raise ValueError("A letra inicial deve vir antes da letra final.")
            return list(string.ascii_lowercase[inicio:fim + 1])
    except ValueError as e:
        messagebox.showerror("Erro", f"Entrada inválida: {e}")
        return []

def background_verificacao(url_base_1, url_base_2, sequencia_n1, sequencia_n2):
    verificar_urls_com_combinacoes(url_base_1, url_base_2, sequencia_n1, sequencia_n2)
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
tk.Label(janela, text="URL base 1 (use {N1} e {N2}):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
entrada_url_1 = tk.Entry(janela, width=50)
entrada_url_1.insert(0, "https://{N1}url{N2}.com")
entrada_url_1.grid(row=0, column=1, padx=10, pady=10)

tk.Label(janela, text="URL base 2 (use {N1} e {N2}):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
entrada_url_2 = tk.Entry(janela, width=50)
entrada_url_2.insert(0, "https://{N1}url{N2}.com.br")
entrada_url_2.grid(row=1, column=1, padx=10, pady=10)

# Configuração para N1
tk.Label(janela, text="Configuração de N1").grid(row=2, column=0, padx=10, pady=10, sticky="w")
var_sequencia_n1 = tk.StringVar(value="Números")
tk.Radiobutton(janela, text="Números", variable=var_sequencia_n1, value="Números").grid(row=2, column=1, sticky="w")
tk.Radiobutton(janela, text="Letras", variable=var_sequencia_n1, value="Letras").grid(row=2, column=2, sticky="w")

tk.Label(janela, text="Início (N1):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entrada_inicio_n1 = tk.Entry(janela, width=10)
entrada_inicio_n1.grid(row=3, column=1, padx=10, pady=5, sticky="w")

tk.Label(janela, text="Fim (N1):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entrada_fim_n1 = tk.Entry(janela, width=10)
entrada_fim_n1.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Configuração para N2
tk.Label(janela, text="Configuração de N2").grid(row=5, column=0)

# Configuração para N2
tk.Label(janela, text="Configuração de N2").grid(row=5, column=0, padx=10, pady=10, sticky="w")
var_sequencia_n2 = tk.StringVar(value="Números")
tk.Radiobutton(janela, text="Números", variable=var_sequencia_n2, value="Números").grid(row=5, column=1, sticky="w")
tk.Radiobutton(janela, text="Letras", variable=var_sequencia_n2, value="Letras").grid(row=5, column=2, sticky="w")

tk.Label(janela, text="Início (N2):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
entrada_inicio_n2 = tk.Entry(janela, width=10)
entrada_inicio_n2.grid(row=6, column=1, padx=10, pady=5, sticky="w")

tk.Label(janela, text="Fim (N2):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
entrada_fim_n2 = tk.Entry(janela, width=10)
entrada_fim_n2.grid(row=7, column=1, padx=10, pady=5, sticky="w")

# Botões de controle e resultado
contador_var = tk.StringVar(value="URLs Ativas Encontradas: 0")
tk.Label(janela, textvariable=contador_var).grid(row=8, column=0, columnspan=2, padx=10, pady=10)

tk.Button(janela, text="Verificar URLs", command=verificar).grid(row=9, column=0, padx=10, pady=10, sticky="w")
tk.Button(janela, text="Pausar", command=pausar_pesquisa).grid(row=9, column=1, padx=10, pady=10)
tk.Button(janela, text="Retomar", command=retomar_pesquisa).grid(row=9, column=2, padx=10, pady=10)
tk.Button(janela, text="Salvar Resultado", command=salvar).grid(row=9, column=3, padx=10, pady=10)

resultado_texto = tk.Text(janela, height=20, width=80)
resultado_texto.grid(row=10, column=0, columnspan=4, padx=10, pady=10)

janela.mainloop()