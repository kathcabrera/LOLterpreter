import tkinter as tk
from PIL import Image
from tkinter import filedialog
import lol_lexer as lexer
import parser_try as parser
# from dataclasses import dataclass
from parser_try import ScanError, ParseError

# Source - https://www.w3resource.com/python-exercises/tkinter/python-tkinter-dialogs-and-file-handling-exercise-3.php


class MultiList:
    def __init__(self, parent, title, name1, name2, side):
        self.parent = parent
        self.title = title
        self.name1 = name1
        self.name2 = name2
        self.list1 = 0
        self.list2 = 0
        self.scrollbar = 0
        self.side = side
    
    def clear(self):
        self.list1.delete(0, tk.END)
        self.list2.delete(0, tk.END)

    def populate(self, iterable):
        if len(iterable) == 0:
            self.list1.insert(tk.END, "None")
            self.list2.insert(tk.END, "None")
            
        
        elif type(iterable) is dict:
            for k, v in iterable.items():
                self.list1.insert(tk.END, k)
                self.list2.insert(tk.END, v)
            
                
        elif isinstance(iterable[0], lexer.Token):
            for i in range(0, len(iterable)):
                self.list1.insert(tk.END, iterable[i].lexeme)
                self.list2.insert(tk.END, iterable[i].type)


    def scroll_all(self, *args):
        self.list1.yview(*args)
        self.list2.yview(*args)
    
    def make(self):
        main_frame = tk.Frame(self.parent)
        sub_frame = tk.Frame(main_frame)
        left_list = tk.Frame(sub_frame)
        right_list = tk.Frame(sub_frame)

        title = tk.Label(main_frame, text=self.title)
        title.pack()

        self.list1 = tk.Listbox(left_list, width=27, height=15)
        name1 = tk.Label(left_list, text=self.name1)
        self.list1.pack(side=tk.BOTTOM)
        name1.pack(side=tk.TOP)


        self.list2 = tk.Listbox(right_list, width=27, height=15)
        name2 = tk.Label(right_list, text=self.name2)
        self.list2.pack(side=tk.BOTTOM)
        name2.pack(side=tk.TOP)

        self.scrollbar = tk.Scrollbar(sub_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.list1.config(yscrollcommand=self.scrollbar.set)
        self.list2.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.scroll_all)

        left_list.pack(side=tk.LEFT)
        right_list.pack(side=tk.LEFT)
        sub_frame.pack()
        main_frame.pack(side=self.side, pady=6)

# taken from www.w3resource.com
def select_file():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("LOL files", "*.lol"), ("All files", "*.*")])
    if file_path:
        file_label.config(text=f"{file_path}")
        process_file(file_path)

# taken from www.w3resource.com
def process_file(file_path):
    # Implement your file processing logic here
    # For demonstration, let's just display the contents of the selected file
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            textEditor.delete('1.0', tk.END)
            textEditor.insert(tk.END, file_contents)
    except Exception as e:
        file_label.config(text=f"Error: {str(e)}")

def execute_code():
    # clear GUI
    lexemes.clear()
    symbol_table.clear()
    outputText.delete("1.0", tk.END)
    
    # Analyze
    try:
        tokens = lexer.clean_lex(textEditor.get("1.0", "end-1c"))        
    except ScanError as e:
        outputText.insert(tk.END, e)
    except Exception as e:        
        outputText.insert(tk.END, e)
    else:
        lexemes.populate(tokens)

        try:
            p = parser.Parser(tokens)
            ast = p.parse()
        except ParseError as e:
            outputText.insert(tk.END, e)
        except Exception as e:        
            outputText.insert(tk.END, e)
        else:
            if len(p.symbols) == 0:
                print(f"{p.symbols}")
                symbol_table.populate({"None": "None"})
            else:
                symbol_table.populate(p.symbols)
                parser.pp_tree(ast)
                print("=======================================")
            
        #     statement_list = ast[2]
        #     for i in range(1,len(statement_list)):
        #         if statement_list[i][0] == "PRINT":
        #             outputText.insert(tk.END, f"{statement_list[i][1]}\n")



    # Print output in console
    # outputText.delete("1.0", tk.END)
    # outputText.insert(tk.END, str(parser.pp_tree(ast)))

# ================================ GUI Widgets ================================
root = tk.Tk()

# Window properties
root.title("LOLterpreter")
root.geometry("1080x600+300+120")
root.config(bg="skyblue")

# Left frame content
left_frame = tk.Frame(root)

file_frame = tk.Frame(left_frame)

file_label = tk.Label(file_frame, width=48, text='(None selected)')
file_label.grid(row=0, column=0)
fileButton = tk.Button(file_frame, text="File Select", command=select_file)
fileButton.grid(row=0, column=1, padx=5)

file_frame.pack(side=tk.TOP, anchor=tk.NW)

# textEditor_frame =  tk.Frame(left_frame)
textEditor = tk.Text(left_frame, width=50, height=33)
textEditor.pack()
executeButton = tk.Button(left_frame, text="EXECUTE", width=45, command=execute_code)
executeButton.pack(padx=5, pady=5)

left_frame.grid(row=0, column=0, sticky=tk.W+tk.E)


# Middle frame content
middle_frame = tk.Frame(root)

lexemes = MultiList(middle_frame, "LEXEMES", "Lexeme", "Classification", tk.TOP)
lexemes.make()

symbol_table = MultiList(middle_frame, "SYMBOL TABLE", "Identifier", "Value", tk.BOTTOM)
symbol_table.make()

middle_frame.grid(row=0, column=1, sticky=tk.W+tk.E)

# Right frame content
right_frame = tk.Frame(root)
outputText = tk.Text(right_frame, height=37, width=39)
outputText.pack()

right_frame.grid(row=0, column=2, sticky=tk.W+tk.E)


root.mainloop()
