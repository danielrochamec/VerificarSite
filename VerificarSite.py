import requests
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import threading
import itertools

pause_event = threading.Event()
pause_event.set()

total_encontradas = 0

# ==============================
# VERIFICAR URL
# ==============================
def verificar_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False


# ==============================
# GERADOR DE COMBINAÇÕES
# ==============================
def gerar_combinacoes(caracteres, tamanho):
    for combinacao in itertools.product(caracteres, repeat=tamanho):
        yield ''.join(combinacao)


# ==============================
# BACKGROUND
# ==============================
def background_verificacao():
    global total_encontradas
    total_encontradas = 0
    atualizar_contador()

    url_base = entrada_url.get()

    if "{n}" not in url_base:
        messagebox.showerror("Erro", "A URL base deve conter {n}")
        return

    resultado_texto.delete("1.0", tk.END)

    tipo = var_tipo.get()

    numeros_inicio = entrada_num_inicio.get()
    numeros_fim = entrada_num_fim.get()

    letras_inicio = entrada_letra_inicio.get().lower()
    letras_fim = entrada_letra_fim.get().lower()

    caracteres = ""

    # NUMEROS
    if tipo in ["Numeros", "Ambos"] and numeros_inicio and numeros_fim:
        for i in range(int(numeros_inicio), int(numeros_fim) + 1):
            caracteres += str(i)

    # LETRAS
    if tipo in ["Letras", "Ambos"] and letras_inicio and letras_fim:
        for c in range(ord(letras_inicio), ord(letras_fim) + 1):
            caracteres += chr(c)

    if not caracteres:
        messagebox.showerror("Erro", "Defina números e/ou letras válidos.")
        return

    quantidade_n = url_base.count("{n}")

    resultado_texto.insert(tk.END, "Iniciando pesquisa...\n")

    for combinacao in gerar_combinacoes(caracteres, quantidade_n):

        pause_event.wait()

        url_final = url_base
        for valor in combinacao:
            url_final = url_final.replace("{n}", valor, 1)

        resultado_texto.insert(tk.END, f"Testando: {url_final}\n")
        resultado_texto.see(tk.END)

        if verificar_url(url_final):
            total_encontradas += 1
            atualizar_contador()

            resultado_texto.insert(tk.END, f"OK: {url_final}\n")
            resultado_texto.see(tk.END)

    resultado_texto.insert(tk.END, "\n--- FIM ---\n")
    messagebox.showinfo("Concluído", "Verificação finalizada!")


# ==============================
# CONTADOR VISUAL
# ==============================
def atualizar_contador():
    contador_label.config(text=f"URLs Encontradas: {total_encontradas}")


# ==============================
# BOTÕES
# ==============================
def iniciar():
    thread = threading.Thread(target=background_verificacao)
    thread.start()


def pausar():
    pause_event.clear()


def retomar():
    pause_event.set()


def salvar_excel():
    linhas = resultado_texto.get("1.0", tk.END).splitlines()
    urls_ok = [linha.replace("OK: ", "") for linha in linhas if linha.startswith("OK:")]

    if not urls_ok:
        messagebox.showwarning("Aviso", "Nenhuma URL OK encontrada.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df = pd.DataFrame(urls_ok, columns=["URLs OK"])
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")


# ==============================
# INTERFACE
# ==============================
janela = tk.Tk()
janela.title("URL Scanner Avançado")

tk.Label(janela, text="URL base (use {n}):").grid(row=0, column=0, sticky="w")
entrada_url = tk.Entry(janela, width=50)
entrada_url.grid(row=0, column=1, columnspan=3)

# NUMEROS
tk.Label(janela, text="Número Inicial:").grid(row=1, column=0, sticky="w")
entrada_num_inicio = tk.Entry(janela, width=10)
entrada_num_inicio.grid(row=1, column=1)

tk.Label(janela, text="Número Final:").grid(row=2, column=0, sticky="w")
entrada_num_fim = tk.Entry(janela, width=10)
entrada_num_fim.grid(row=2, column=1)

# LETRAS
tk.Label(janela, text="Letra Inicial:").grid(row=1, column=2, sticky="w")
entrada_letra_inicio = tk.Entry(janela, width=5)
entrada_letra_inicio.grid(row=1, column=3)

tk.Label(janela, text="Letra Final:").grid(row=2, column=2, sticky="w")
entrada_letra_fim = tk.Entry(janela, width=5)
entrada_letra_fim.grid(row=2, column=3)

# OPÇÕES
var_tipo = tk.StringVar(value="Numeros")

tk.Radiobutton(janela, text="Numeros", variable=var_tipo, value="Numeros").grid(row=3, column=0)
tk.Radiobutton(janela, text="Letras", variable=var_tipo, value="Letras").grid(row=3, column=1)
tk.Radiobutton(janela, text="Ambos", variable=var_tipo, value="Ambos").grid(row=3, column=2)

# BOTÕES
tk.Button(janela, text="Iniciar", command=iniciar).grid(row=4, column=0)
tk.Button(janela, text="Pausar", command=pausar).grid(row=4, column=1)
tk.Button(janela, text="Retomar", command=retomar).grid(row=4, column=2)
tk.Button(janela, text="Salvar Excel", command=salvar_excel).grid(row=4, column=3)

# CONTADOR VISUAL
contador_label = tk.Label(janela, text="URLs Encontradas: 0", font=("Arial", 12, "bold"))
contador_label.grid(row=5, column=0, columnspan=4, pady=5)

# RESULTADO
resultado_texto = tk.Text(janela, height=20, width=90)
resultado_texto.grid(row=6, column=0, columnspan=4)

scroll = tk.Scrollbar(janela, command=resultado_texto.yview)
scroll.grid(row=6, column=4, sticky='ns')
resultado_texto.config(yscrollcommand=scroll.set)

janela.mainloop()
