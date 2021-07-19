import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.messagebox import showinfo
from datetime import datetime
from datetime import timedelta
import json


#================================layout-TKinter==============================
root = Tk()
root.title('DashFATEC')  # título da janela
root.geometry('1350x750')
root.config(bg='#a9dcd6')

#pegar as datas (d/m/y) de hoje
date1 = datetime.today().strftime('%d-%m-%Y')
#pegar as datas (d/m/y) daqui a 2 semanas
date2 = datetime.today() + timedelta(days=14)
date2 = date2.strftime('%d-%m-%Y')


#================================DATABASE===================================
conn = sqlite3.connect('dados.db')
c = conn.cursor()

#CRIAÇÃO DA TABELA livros
c.execute("""CREATE TABLE IF NOT EXISTS livros (
            id_livro int PRIMARY KEY,
            nome_livro text,
            autor text
    )""")


conn.commit()
conn.close()

#================================FUNÇÕES====================================


#CARREGAR OS REGISTROS PASSADOS DE EMPRÉSTIMOS NO FRAME DE DETALHE
def load():
    with open('save.json', 'r') as f:
        data = json.load(f)

    tree_view.delete(*tree_view.get_children())

    for value in zip(*data.values()):
        tree_view.insert('', 'end', values=value)

#REGISTRAR EMPRÉSTIMOS
def print_text():
    if not entry_id_aluno.get():
        messagebox.showerror("Erro!", "Inserir ID!")
    if not entry_nome.get():
        messagebox.showerror("Erro!", "Inserir Nome do aluno!")
    if not entry_turma.get():
        messagebox.showerror("Erro!", "Inserir Turma do aluno!")
    if not entry_id_livro_detalhe.get():
        messagebox.showerror("Erro!", "Inserir ID do livro!")
        
    else: 
        conn = sqlite3.connect('dados.db')
        c = conn.cursor()     
        c.execute('SELECT nome_livro FROM livros WHERE id_livro = ' + entry_id_livro_detalhe.get())
        detalhe_nome_livro = c.fetchone()
        if not detalhe_nome_livro:
            messagebox.showerror("Erro!", "ID do livro não existe!")
        else:
            tree_view.insert('', 'end', values=(entry_id_aluno.get(), entry_nome.get(), entry_turma.get(), detalhe_nome_livro, date1, date2))
        conn.commit()
        conn.close()

def save():
    dict_save = {'RA': [], 'Nome do aluno': [], 'Turma': [], 'Nome do livro': [], 'Data-Emp': [], 'Data-Dev': []}

    for iid in tree_view.get_children():
        for value, key in zip(tree_view.item(iid)['values'], dict_save.keys()):
            dict_save[key].append(value)
            
    with open('save.json', 'w') as f:
      json.dump(dict_save, f)

    #esvaziar os widgets de entry
    entry_id_aluno.delete(0, END)
    entry_nome.delete(0, END)
    entry_turma.delete(0, END)
    entry_id_livro_detalhe.delete(0, END)

#MOSTRAR DADOS DOS ALUNOS E LIVROS DATAFRAME DETALHE E RIGHT
def mostrar_dados():
    #resetar a tabela pra não mostrar valores duplicados
    tree.delete(*tree.get_children())   
    conn = sqlite3.connect('dados.db')
    c = conn.cursor()
    c.execute('SELECT * FROM livros GROUP BY id_livro')
    lista_livros = c.fetchall()
    #loop para pegar todos os livros da database e inserir na tabela
    for livro in lista_livros:
        tree.insert('', END, values=livro)
    conn.commit()
    conn.close()
    

#FUNÇÃO PARA REMOVER UMA LINHA DO TREEVIEW DE DETALHES
def remover_registro():
    x = tree_view.selection()[0]
    tree_view.delete(x)

#FUNÇÃO PARA FAZER REGISTRO DE NOVOS LIVROS
#VAI ABRIR NOVA JANELA
def registrar():
    newWindow = Toplevel(root)
    newWindow.title("Registro")
    newWindow.geometry("300x150")

    # entry
    entry_id_livro = Entry(newWindow, width=30)
    entry_id_livro.grid(row=0, column=1, padx=20)

    entry_livro_nome= Entry(newWindow, width=30)
    entry_livro_nome.grid(row=1, column=1)

    entry_autor = Entry(newWindow, width=30)
    entry_autor.grid(row=2, column=1)

    # labels
    lab_id_livro = Label(newWindow, text='ID do livro')
    lab_id_livro.grid(row=0, column=0)

    lab_livro_nome = Label(newWindow, text='Nome do livro')
    lab_livro_nome.grid(row=1, column=0)

    lab_autor = Label(newWindow, text='Autor')
    lab_autor.grid(row=2, column=0)

    
    def query_registrar():
        conn = sqlite3.connect('dados.db')
        c = conn.cursor()
        c.execute('SELECT id_livro FROM livros WHERE id_livro = ' + entry_id_livro.get())
        resultado = c.fetchone()
        conn.commit()
        conn.close()
        #SE O ID JÁ EXISTE, EXIBIR AVISO
        if not resultado:
            conn = sqlite3.connect('dados.db')
            c = conn.cursor()
            c.execute('INSERT INTO livros VALUES(:id_livro, :nome_livro, :autor)',
                      {
                          'id_livro': entry_id_livro.get(),
                          'nome_livro': entry_livro_nome.get(),
                          'autor': entry_autor.get()
                      })
            conn.commit()
            conn.close()
            
            entry_id_livro.delete(0, END)
            entry_livro_nome.delete(0, END)
            entry_autor.delete(0, END)        
        else:
            messagebox.showerror("Erro!", "Este ID já existe") 
        
        
    bt_query_registrar = Button(newWindow, text='Registrar', command=query_registrar)
    bt_query_registrar.grid(row=3, column=1)

#FUNÇÃO PARA DELETAR LIVROS
#VAI ABRIR NOVA JANELA
def deletar():
    newWindow_delete = Toplevel(root)
    newWindow_delete.title("Exclusão")
    newWindow_delete.geometry("300x100")

    # entry
    entry_id_livro_delete = Entry(newWindow_delete, width=30)
    entry_id_livro_delete.grid(row=0, column=1, padx=20)


    # label
    lab_id_livro_delete = Label(newWindow_delete, text='ID do livro')
    lab_id_livro_delete.grid(row=0, column=0)

    def query_deletar():
         conn = sqlite3.connect('dados.db')
         c = conn.cursor()
         c.execute('DELETE FROM livros WHERE id_livro = ' + entry_id_livro_delete.get())
         conn.commit()
         conn.close()

         entry_id_livro_delete.delete(0, END)

    bt_query_deletar = Button(newWindow_delete, text='Deletar', command=query_deletar)
    bt_query_deletar.grid(row=1, column=1)
    
#================================FRAMES================================ 

#MAINFRAME
MainFrame = Frame(root)
MainFrame.pack()
MainFrame.config(bg='#a9dcd6')

#FRAME DE TITULO
FrameTitulo = Frame(MainFrame,
                    bg='#cc6666',
                    bd=10,
                    width=1350,
                    pady=20,
                    relief = RIDGE)
FrameTitulo.pack(side=TOP)

Titulo = Label(FrameTitulo,
               width=34,
               text='Sistema de Biblioteca',
               bg='#cc6666',
               font=('arial', 47, 'bold'))
Titulo.pack()

#FRAME DE DETALHES DE EMPRÉSTIMOS (DADOS DE ALUNO E LIVRO)
FrameDetalhe = Frame(MainFrame,
                        bg='#a9dcd6',
                        bd=10,
                        width=1350,
                        height=100,
                        padx=20,
                        relief = RIDGE)
FrameDetalhe.pack(side=BOTTOM)

#DATAFRAME
DataFrame = Frame(MainFrame,
                    bg='#a9dcd6',
                    bd=10,
                    width=1300,
                    height=400,
                    padx=20,
                    relief = RIDGE)
DataFrame.pack(side=BOTTOM)

#DATAFRAME NA ESQUERDA (ONDE OS DADOS DOS ALUNOS SERÃO MOSTRADOS)
DataFrameLEFT = LabelFrame(DataFrame,
                            bg='#a9dcd6',
                            bd=10,
                            width=700,
                            height=300,
                            padx=20,
                            relief = RIDGE,
                            font=('arial', 12, 'bold'),
                            text='Informação do Empréstimo')
DataFrameLEFT.pack(side=LEFT)

#DATAFRAME NA DIREITA (ONDE OS LIVROS VÃO SER MOSTRADOS)
DataFrameRIGHT = LabelFrame(DataFrame,
                            bg='#a9dcd6',
                            bd=10,
                            width=550,
                            height=300,
                            padx=20,
                            relief = RIDGE,
                            font=('arial', 12, 'bold'),
                            text='Livros')
DataFrameRIGHT.pack(side=RIGHT)

#============================DATAFRAME_LEFT_ALUNOS================================ 

#LABEL E ENTRY DE ID ALUNO
label_id_aluno = Label(DataFrameLEFT,
                       text='RA',
                       font=('arial', 12, 'bold'),
                       bg='#a4dfd1',
                       padx=2,
                       pady=2)
label_id_aluno.pack()
label_id_aluno.place(x=10,y=50)

entry_id_aluno = Entry(DataFrameLEFT,
                       font=('arial', 12, 'bold'))
entry_id_aluno.pack()
entry_id_aluno.place(x=140, y=50)

#LABEL E ENTRY DE NOME ALUNO

label_nome = Label(DataFrameLEFT,
                       text='Nome do aluno',
                       font=('arial', 12, 'bold'),
                       bg='#a4dfd1',
                       padx=2,
                       pady=2)
label_nome.pack()
label_nome.place(x=10, y=100)

entry_nome = Entry(DataFrameLEFT,
                       font=('arial', 12, 'bold'))
entry_nome.pack()
entry_nome.place(x=140, y=100)


#LABEL E ENTRY DE ALUNO TURMA

label_turma = Label(DataFrameLEFT,
                       text='Turma',
                       font=('arial', 12, 'bold'),
                       bg='#a4dfd1',
                       padx=2,
                       pady=2)
label_turma.pack()
label_turma.place(x=10, y=150)

entry_turma = Entry(DataFrameLEFT,
                       font=('arial', 12, 'bold'))
entry_turma.pack()
entry_turma.place(x=140, y=150)


#LABEL E ENTRY DE ID LIVRO
label_id_livro = Label(DataFrameLEFT,
                       text='ID do livro',
                       font=('arial', 12, 'bold'),
                       bg='#a4dfd1',
                       padx=2,
                       pady=2)
label_id_livro.pack()
label_id_livro.place(x=350, y=50)

entry_id_livro_detalhe = Entry(DataFrameLEFT,
                       font=('arial', 12, 'bold'))
entry_id_livro_detalhe.pack()
entry_id_livro_detalhe.place(x=450, y=50)


#================================DATAFRAME_RIGHT============================
#criar uma tabela treeview mostrando todos os livros
tree = ttk.Treeview(DataFrameRIGHT, show='headings', height=12)

tree['columns'] = ('ID do livro', 'Nome do livro', 'Autor')

tree.column('#0', width=0, stretch=0, anchor=CENTER)
tree.column('ID do livro', anchor=W, width=70)
tree.column('Nome do livro', anchor=W, width=230)
tree.column('Autor', anchor=CENTER, width=150)

tree.heading('#0', text='', anchor=CENTER)
tree.heading('ID do livro', text='ID do livro', anchor=W)
tree.heading('Nome do livro', text='Nome do livro', anchor=W)
tree.heading('Autor', text='Autor', anchor=CENTER)

tree.pack(side='left')

#adicionar um scrollbar para a tabela tree
treeScroll = ttk.Scrollbar(DataFrameRIGHT)
treeScroll.configure(command=tree.yview)
tree.configure(yscrollcommand=treeScroll.set)
treeScroll.pack(side='right', fill='y')

#================================FRAME_DETALHE================================
tree_view = ttk.Treeview(FrameDetalhe, columns=(0, 1, 2, 3, 4, 5), show='headings', height = 8, selectmode='browse')
tree_view.pack(side='left')
#adicionar um scrollbar para a tabela tree_view
treeScroll_detalhe = ttk.Scrollbar(FrameDetalhe)
treeScroll_detalhe.configure(command=tree.yview)
tree_view.configure(yscrollcommand=treeScroll_detalhe.set)
treeScroll_detalhe.pack(side='right', fill='y')


for index, x in enumerate(['RA', 'Nome do aluno', 'Turma', 'Nome do livro', 'Data-Emp', 'Data-Dev']):
    tree_view.heading(index, text=x)
    tree_view.column(index, anchor='center')

botao_load = Button(DataFrameLEFT,
                    text='Load',
                    command=load,
                    font=('arial', 12, 'bold'),
                    bd=5,
                    bg='#ffba42',
                    height=1)
botao_load.pack()
botao_load.place(x=550, y=200)
#================================FRAME_BOTAO==================================

button_save = Button(
                    font=('arial', 15, 'bold'),
                    text='Salvar',
                    bd=5,
                    width=14,
                    bg='#ffba42',
                    relief = RAISED,
                    command=save)
button_save.pack()
button_save.place(x=450, y=690)


#BOTÃO PARA CARREGAR OS DETALHES DE EMPRÉSTIMOS
button_text_box = Button(
                         font=('arial', 15, 'bold'),
                         text='Adicionar',
                         bd=5,
                         width=14,
                         bg='#ffba42',
                         relief = RAISED,
                         command=print_text)
button_text_box.pack()
button_text_box.place(x=50, y=690)

#BOTÃO PARA DELETAR REGISTRO
botao_deletar_registro = Button(
                       text='Deletar',
                       font=('arial', 15, 'bold'),
                       width=14,
                       bd=5,
                       bg='#ffba42',
                       relief = RAISED,
                       command=remover_registro
                         )
botao_deletar_registro.pack()
botao_deletar_registro.place(x=250, y=690)

#BOTÃO PARA MOSTRAR DADOS DO FRAME DE DETALHE E NO FRAME RIGHT (LIVROS)
botao_mostrar_dados = Button(
                       text='Atualizar Livro',
                       font=('arial', 15, 'bold'),
                       width=14,
                       bd=5,
                       bg='#ffba42',
                       relief = RAISED,
                       command=mostrar_dados
                         )
botao_mostrar_dados.pack()
botao_mostrar_dados.place(x=750, y=690)


#BOTÃO PARA REGISTRAR NOVOS LIVROS NA DATABASE
botao_registrar = Button(
                         text='Registrar Livro',
                         font=('arial', 15, 'bold'),
                         width=14,
                         bd=5,
                         bg='#ffba42',
                         relief = RAISED,
                         command=registrar
                         )
botao_registrar.pack()
botao_registrar.place(x=950, y=690)


#BOTÃO PARA DELETAR LINHAS
botao_deletar = Button(
                       text='Deletar Livro',
                       font=('arial', 15, 'bold'),
                       width=14,
                       bd=5,
                       bg='#ffba42',
                       relief = RAISED,
                       command=deletar
                         )
botao_deletar.pack()
botao_deletar.place(x=1150, y=690)



#======================================================================================================
root.mainloop()


