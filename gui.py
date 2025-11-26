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
    lexemes.delete(0, tk.END)
    outputText.delete("1.0", tk.END)
    symbolTable_listbox.delete(0, tk.END)
    
    # Analyze; No need to call parser.analyze()
    try:
        tokens = parser.lex(textEditor.get("1.0", "end-1c"))        
    except ScanError as e:
        outputText.insert(tk.END, e)
    except Exception as e:        
        outputText.insert(tk.END, e)
    else:
        for token in tokens:
            lexemes.insert(tk.END, f"{token.lexeme}    -    {token.type}")

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
                symbolTable_listbox.insert(tk.END, "None    -    None")
            else:
                for k, v in p.symbols.items():
                    symbolTable_listbox.insert(tk.END, f"{k}    -    {v}")
            
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
root.geometry("1000x600+300+120")
root.config(bg="skyblue")

# Left frame content
left_frame = tk.Frame(root)

file_frame = tk.Frame(left_frame)

file_label = tk.Label(file_frame, width=35, text='(None selected)')
file_label.grid(row=0, column=0)
# folderIcon = Image.open("folder.png")
# resized_folderIcon = folderIcon.resize((10,10), Image.Resampling.LANCZOS)
# folderImage = folderIcon.subsample(3,3)
# folderIcon.zoom(50,50)
# fileButton = tk.Button(file_frame, text="File Select", image=resized_folderIcon, compound="left")
fileButton = tk.Button(file_frame, text="File Select", command=select_file)
fileButton.grid(row=0, column=1, padx=5)

file_frame.pack(side=tk.TOP, anchor=tk.NW)

# textEditor_frame =  tk.Frame(left_frame)
textEditor = tk.Text(left_frame, width=40, height=33)
textEditor.pack()
executeButton = tk.Button(left_frame, text="EXECUTE", width=45, command=execute_code)
executeButton.pack(padx=5, pady=5)
# textEditor_frame.pack(side=tk.TOP, anchor=tk.NW)
left_frame.grid(row=0, column=0, sticky=tk.W+tk.E)


# Middle frame content
middle_frame = tk.Frame(root)

lexeme_label = tk.Label(middle_frame, width=47, text="LEXEMES")
lexeme_label.pack()

l_scrollbar = tk.Scrollbar(middle_frame)
lexemes = tk.Listbox(middle_frame, width=55, height=17, yscrollcommand=l_scrollbar.set)
l_scrollbar.config(command=lexemes.yview)
lexemes.pack()

symbolTable_label = tk.Label(middle_frame, width=47, text="SYMBOL TABLE")
symbolTable_label.pack()
st_scrollbar = tk.Scrollbar(middle_frame)
symbolTable_listbox = tk.Listbox(middle_frame, width=55, height=17, yscrollcommand=st_scrollbar.set)
st_scrollbar.config(command=symbolTable_listbox.yview)
symbolTable_listbox.pack()
middle_frame.grid(row=0, column=1, sticky=tk.W+tk.E)

# Right frame content
right_frame = tk.Frame(root)
outputText = tk.Text(right_frame, height=37, width=40)
outputText.pack()

right_frame.grid(row=0, column=2, sticky=tk.W+tk.E)


root.mainloop()
