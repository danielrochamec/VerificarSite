import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import string  # Para manipular as letras do alfabeto
import webbrowser  # Para abrir URLs no navegador
import pandas as pd  # Para salvar em Excel
import threading  # Para rodar as verificações em background

# Função para verificar a URL
def verificar_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return url  # Retorna a URL ativa
        else:
            return None  # Ignora URLs inativas
    except requests.exceptions.ConnectionError:
        return None  # Ignora URLs inativas
    except requests.exceptions.Timeout:
        return None  # Ignora URLs inativas
    except requests.exceptions.RequestException:
        return None  # Ignora URLs inativas

# Função para gerar sequência de números ou letras
def verificar_urls_com_sequencia(url_base, inicio, fim, tipo_sequencia):
    urls_ativas = []  # Armazena as URLs ativas para salvar posteriormente
    if tipo_sequencia == "Números":
        for i in range(inicio, fim + 1):
            url_modificada = url_base.format(n=i)
            url = verificar_url(url_modificada)
            if url:  # Exibe apenas URLs ativas
                adicionar_resultado(url)
                urls_ativas.append(url)  # Adiciona a URL ativa à lista

    elif tipo_sequencia == "Letras":
        letras = string.ascii_lowercase  # a até z
        for letra in letras[inicio:fim + 1]:
            url_modificada = url_base.format(n=letra)
            url = verificar_url(url_modificada)
            if url:  # Exibe apenas URLs ativas
                adicionar_resultado(url)
                urls_ativas.append(url)  # Adiciona a URL ativa à lista
    
    return urls_ativas

# Função para adicionar o resultado na área de texto e torná-lo clicável
def adicionar_resultado(url):
    resultado_texto.insert(tk.END, url, url)
    resultado_texto.insert(tk.END, "\n")
    resultado_texto.tag_add(url, "end-1c linestart", "end-1c")
    resultado_texto.tag_config(url, foreground="blue", underline=True)
    resultado_texto.tag_bind(url, "<Button-1>", lambda e, link=url: webbrowser.open(link))
    resultado_texto.see(tk.END)  # Move a barra de rolagem para o final

# Função para salvar o resultado em um arquivo Excel
def salvar_arquivo_excel():
    urls_ativas = resultado_texto.get("1.0", tk.END).splitlines()  # Obtém as URLs ativas exibidas
    if urls_ativas:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Arquivo Excel", "*.xlsx")])
        if file_path:
            # Cria um DataFrame com as URLs ativas
            df = pd.DataFrame(urls_ativas, columns=["URLs Ativas"])
            # Salva o DataFrame em um arquivo Excel
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Sucesso", "Arquivo Excel salvo com sucesso!")
    else:
        messagebox.showwarning("Aviso", "Não há URLs para salvar.")

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

    resultado_texto.delete("1.0", tk.END)  # Limpa o campo de texto

    # Exibe mensagem de início de pesquisa
    resultado_texto.insert(tk.END, "Iniciando a pesquisa...\n")
    resultado_texto.see(tk.END)  # Move a barra de rolagem para o final

    # Iniciar a verificação das URLs em uma nova thread
    thread = threading.Thread(target=background_verificacao, args=(url_base, inicio, fim, tipo_sequencia))
    thread.start()

# Função para rodar a verificação em segundo plano (background)
def background_verificacao(url_base, inicio, fim, tipo_sequencia):
    verificar_urls_com_sequencia(url_base, inicio, fim, tipo_sequencia)

    # Exibe mensagem de fim de pesquisa
    resultado_texto.insert(tk.END, "\n--- Fim da pesquisa ---\n")
    resultado_texto.see(tk.END)  # Move a barra de rolagem para o final
    messagebox.showinfo("Fim da Verificação", "A verificação das URLs foi concluída!")

# Função chamada ao clicar no botão "Salvar Resultado"
def salvar():
    salvar_arquivo_excel()

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
resultado_texto = tk.Text(janela, height=10, width=80, wrap="word")
resultado_texto.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Adicionando barra de rolagem
scrollbar = tk.Scrollbar(janela, command=resultado_texto.yview)
scrollbar.grid(row=5, column=2, sticky='nsew')
resultado_texto['yscrollcommand'] = scrollbar.set

# Iniciar o loop da interface
janela.mainloop()
