import requests
import tkinter as tk
from tkinter import messagebox, filedialog
import webbrowser
import pandas as pd
import threading
import time
import string

pausado = False
parar = False
urls_ok_global = []

# ==============================
# Verificar URL
# ==============================
def verificar_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def mostrar_teste(url):
    resultado_texto.insert(tk.END, f"Testando: {url}\n")
    resultado_texto.see(tk.END)

def adicionar_resultado(url):
    resultado_texto.insert(tk.END, f"OK: {url}\n", url)
    resultado_texto.tag_config(url, foreground="green")
    resultado_texto.tag_bind(url, "<Button-1>", lambda e, link=url: webbrowser.open(link))
    resultado_texto.see(tk.END)

def verificar_pausa():
    while pausado:
        time.sleep(0.2)

# ==============================
# Processo principal
# ==============================
def background_verificacao(url_base, lista):

    global parar, urls_ok_global
    urls_ok_global = []

    contador_n = url_base.count("{n}")

    if contador_n >= 2:

        for esquerda in lista:
            for direita in lista:

                if parar:
                    break

                verificar_pausa()

                url_temp = url_base.replace("{n}", esquerda, 1)
                url = url_temp.replace("{n}", direita, 1)

                mostrar_teste(url)

                if verificar_url(url):
                    adicionar_resultado(url)
                    urls_ok_global.append(url)

    else:
        for valor in lista:

            if parar:
                break

            verificar_pausa()

            url = url_base.replace("{n}", valor)

            mostrar_teste(url)

            if verificar_url(url):
                adicionar_resultado(url)
                urls_ok_global.append(url)

    resultado_texto.insert(tk.END, "\n--- Fim da Pesquisa ---\n")
    messagebox.showinfo("Concluído", "Pesquisa finalizada!")

# ==============================
# Botão Verificar
# ==============================
def verificar():
    global parar
    parar = False

    url_base = entrada_url.get()

    if "{n}" not in url_base:
        messagebox.showerror("Erro", "A URL deve conter {n}")
        return

    tipo = var_tipo.get()

    if tipo == "Numero":
        try:
            inicio = int(entrada_num_inicio.get())
            fim = int(entrada_num_fim.get())
            lista = [str(i) for i in range(inicio, fim + 1)]
        except:
            messagebox.showerror("Erro", "Números inválidos.")
            return

    elif tipo == "Letra":
        try:
            letras = string.ascii_lowercase
            i = letras.index(entrada_letra_inicio.get().lower())
            f = letras.index(entrada_letra_fim.get().lower())
            lista = [letras[x] for x in range(i, f + 1)]
        except:
            messagebox.showerror("Erro", "Letras inválidas.")
            return

    resultado_texto.delete("1.0", tk.END)
    resultado_texto.insert(tk.END, "Iniciando pesquisa...\n")

    thread = threading.Thread(
        target=background_verificacao,
        args=(url_base, lista)
    )
    thread.start()

# ==============================
# Controles
# ==============================
def pausar():
    global pausado
    pausado = True

def retomar():
    global pausado
    pausado = False

def parar_execucao():
    global parar
    parar = True

# ==============================
# Salvar Excel
# ==============================
def salvar_excel():
    if not urls_ok_global:
        messagebox.showwarning("Aviso", "Nenhuma URL OK encontrada.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Arquivo Excel", "*.xlsx")]
    )

    if file_path:
        df = pd.DataFrame(urls_ok_global, columns=["URLs OK"])
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

# ==============================
# Interface
# ==============================
janela = tk.Tk()
janela.title("Verificador de URLs")

tk.Label(janela, text="URL base (use {n})").grid(row=0, column=0, sticky="w")
entrada_url = tk.Entry(janela, width=50)
entrada_url.grid(row=0, column=1, columnspan=3)

# Número
tk.Label(janela, text="Número Inicial").grid(row=1, column=0)
entrada_num_inicio = tk.Entry(janela)
entrada_num_inicio.grid(row=1, column=1)

tk.Label(janela, text="Número Final").grid(row=2, column=0)
entrada_num_fim = tk.Entry(janela)
entrada_num_fim.grid(row=2, column=1)

# Letras
tk.Label(janela, text="Letra Inicial").grid(row=1, column=2)
entrada_letra_inicio = tk.Entry(janela, width=5)
entrada_letra_inicio.grid(row=1, column=3)

tk.Label(janela, text="Letra Final").grid(row=2, column=2)
entrada_letra_fim = tk.Entry(janela, width=5)
entrada_letra_fim.grid(row=2, column=3)

# Tipo
var_tipo = tk.StringVar(value="Numero")

tk.Radiobutton(janela, text="Numero", variable=var_tipo, value="Numero").grid(row=3, column=0)
tk.Radiobutton(janela, text="Letra", variable=var_tipo, value="Letra").grid(row=3, column=1)

# Botões
tk.Button(janela, text="Verificar", command=verificar).grid(row=4, column=0)
tk.Button(janela, text="Pausar", command=pausar).grid(row=4, column=1)
tk.Button(janela, text="Retomar", command=retomar).grid(row=4, column=2)
tk.Button(janela, text="Parar", command=parar_execucao).grid(row=4, column=3)

tk.Button(janela, text="Salvar Excel", command=salvar_excel).grid(row=5, column=0, columnspan=4)

resultado_texto = tk.Text(janela, height=15, width=90)
resultado_texto.grid(row=6, column=0, columnspan=4)

janela.mainloop()
