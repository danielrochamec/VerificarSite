import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import string  # Para manipular as letras do alfabeto

# Função para verificar a URL
def verificar_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"URL {url} está ativa!\n"
        else:
            return f"URL {url} retornou o status {response.status_code}.\n"
    except requests.exceptions.ConnectionError:
        return f"URL {url} está inativa (erro de conexão).\n"
    except requests.exceptions.Timeout:
        return f"URL {url} não respondeu a tempo (timeout).\n"
    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro: {e}\n"

# Função para gerar sequência de números ou letras
def verificar_urls_com_sequencia(url_base, inicio, fim, tipo_sequencia):
    resultado = ""

    if tipo_sequencia == "Números":
        for i in range(inicio, fim + 1):
            url_modificada = url_base.format(n=i)
            resultado += verificar_url(url_modificada)

    elif tipo_sequencia == "Letras":
        letras = string.ascii_lowercase  # a até z
        for letra in letras[inicio:fim + 1]:
            url_modificada = url_base.format(n=letra)
            resultado += verificar_url(url_modificada)

    return resultado

# Função para salvar o resultado em um arquivo txt
def salvar_arquivo(conteudo):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivo de Texto", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(conteudo)
        messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

# Função chamada ao clicar no botão "Verificar URLs"
def verificar():
    url_base = entrada_url.get()

    # Validação da URL base
    if '{n}' not in url_base:
        messagebox.showerror("Erro", "A URL base deve conter '{n}' para inserir a sequência.")
        return

    tipo_sequencia = var_sequencia.get()

    try:
        if tipo_sequencia == "Números":
            inicio = int(entrada_inicio.get())
            fim = int(entrada_fim.get())
            if inicio > fim:
                raise ValueError("O número inicial deve ser menor ou igual ao número final.")

        elif tipo_sequencia == "Letras":
            inicio = string.ascii_lowercase.index(entrada_inicio.get().lower())
            fim = string.ascii_lowercase.index(entrada_fim.get().lower())
            if inicio > fim:
                raise ValueError("A letra inicial deve vir antes da letra final.")

    except ValueError as e:
        messagebox.showerror("Erro", f"Entrada inválida: {e}")
        return

    resultado = verificar_urls_com_sequencia(url_base, inicio, fim, tipo_sequencia)
    resultado_texto.delete("1.0", tk.END)  # Limpa o campo de texto
    resultado_texto.insert(tk.END, resultado)

# Função chamada ao clicar no botão "Salvar Resultado"
def salvar():
    conteudo = resultado_texto.get("1.0", tk.END)
    salvar_arquivo(conteudo)

# Criação da janela principal
janela = tk.Tk()
janela.title("Verificar URLs")

# Labels e entradas de texto
tk.Label(janela, text="URL base (use {n} onde deseja colocar o número/letra):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
entrada_url = tk.Entry(janela, width=50)
entrada_url.grid(row=0, column=1, padx=10, pady=10)

tk.Label(janela, text="Início (número ou letra):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
entrada_inicio = tk.Entry(janela, width=10)
entrada_inicio.grid(row=1, column=1, padx=10, pady=10, sticky="w")

tk.Label(janela, text="Fim (número ou letra):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
entrada_fim = tk.Entry(janela, width=10)
entrada_fim.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Botão de seleção para Números ou Letras
var_sequencia = tk.StringVar(value="Números")
tk.Radiobutton(janela, text="Números", variable=var_sequencia, value="Números").grid(row=3, column=0, padx=10, pady=10, sticky="w")
tk.Radiobutton(janela, text="Letras", variable=var_sequencia, value="Letras").grid(row=3, column=1, padx=10, pady=10, sticky="w")

# Botões para verificar e salvar
botao_verificar = tk.Button(janela, text="Verificar URLs", command=verificar)
botao_verificar.grid(row=4, column=0, padx=10, pady=10)

botao_salvar = tk.Button(janela, text="Salvar Resultado", command=salvar)
botao_salvar.grid(row=4, column=1, padx=10, pady=10)

# Área de texto para mostrar o resultado
resultado_texto = tk.Text(janela, height=10, width=80)
resultado_texto.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Iniciar o loop da interface
janela.mainloop()
