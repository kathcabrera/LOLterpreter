import tkinter as tk
from PIL import Image
from tkinter import filedialog
import lol_lexer as lexer
import parser_try as parser
# from dataclasses import dataclass
from parser_try import ScanError, ParseError

# Source - https://www.w3resource.com/python-exercises/tkinter/python-tkinter-dialogs-and-file-handling-exercise-3.php

# Source - https://stackoverflow.com/a
# Posted by James Kent
# Retrieved 2025-11-24, License - CC BY-SA 3.0

# Source - https://stackoverflow.com/a
# Posted by Universe Whole-Xuan, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-24, License - CC BY-SA 4.0

# from PIL import Image as pil
# from pkg_resources import parse_version

# if parse_version(pil.__version__)>=parse_version('10.0.0'):
#     Image.ANTIALIAS=Image.LANCZOS


# def Resize_Image(image, maxsize):
#     r1 = image.size[0]/maxsize[0] # width ratio
#     r2 = image.size[1]/maxsize[1] # height ratio
#     ratio = max(r1, r2)
#     newsize = (int(image.size[0]/ratio), int(image.size[1]/ratio))
#     image = image.resize(newsize, Image.ANTIALIAS)
#     return image

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
            
                
        elif isinstance(iterable[0], parser.Token):
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
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("LOL files", "*.lol *.txt"), ("All files", "*.*")])
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
    # lexemes.delete(0, tk.END)
    lexemes.clear()
    symbol_table.clear()
    outputText.delete("1.0", tk.END)
    # symbolTable_listbox.delete(0, tk.END)
    
    # Analyze; No need to call parser.analyze()
    try:
        tokens = parser.lex(textEditor.get("1.0", "end-1c"))        
    except ScanError as e:
        outputText.insert(tk.END, e)
    except Exception as e:        
        outputText.insert(tk.END, e)
    else:
        # for token in tokens:
            # lexemes.insert(tk.END, f"{token.lexeme}    -    {token.type}")

        lexemes.populate(tokens)
            # continue

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
                # symbolTable_listbox.insert(tk.END, "None    -    None")
                symbol_table.populate({"None": "None"})
            else:
                # for k, v in p.symbols.items():
                    # symbolTable_listbox.insert(tk.END, f"{k}    -    {v}")
                symbol_table.populate(p.symbols)
                    # continue
            
            for i in range(1,len(ast[2])):
                if ast[2][i][0] == "PRINT":
                    outputText.insert(tk.END, f"{ast[2][i][1]}\n")
            # outputText.insert(tk.END, ast[2][1][0])



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
