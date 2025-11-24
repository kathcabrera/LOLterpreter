import tkinter as tk
from PIL import Image


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

root = tk.Tk()

# Window properties
root.title("LOLterpreter")
root.geometry("985x600+300+120")
root.config(bg="skyblue")

# Left frame content
left_frame = tk.Frame(root)

file_frame = tk.Frame(left_frame)

file = tk.Label(file_frame, width=35, text='(None selected)')
file.grid(row=0, column=0)
# folderIcon = Image.open("folder.png")
# resized_folderIcon = folderIcon.resize((10,10), Image.Resampling.LANCZOS)
# folderImage = folderIcon.subsample(3,3)
# folderIcon.zoom(50,50)
# fileButton = tk.Button(file_frame, text="File Select", image=resized_folderIcon, compound="left")
fileButton = tk.Button(file_frame, text="File Select")
fileButton.grid(row=0, column=1, padx=5)

file_frame.pack(side=tk.TOP, anchor=tk.NW)

textEditor_frame =  tk.Frame(left_frame)
text = tk.Text(textEditor_frame, width=40, height=33)
text.pack()
executeButton = tk.Button(textEditor_frame, text="EXECUTE", width=45)
executeButton.pack(pady=5)
textEditor_frame.pack(side=tk.TOP, anchor=tk.NW)
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
symbolTable = tk.Listbox(middle_frame, width=55, height=17, yscrollcommand=st_scrollbar.set)
st_scrollbar.config(command=symbolTable.yview)
symbolTable.pack()
middle_frame.grid(row=0, column=1, sticky=tk.W+tk.E)

# Right frame content
right_frame = tk.Frame(root)
outputText = tk.Text(right_frame, height=37, width=40)
outputText.pack()

right_frame.grid(row=0, column=2, sticky=tk.W+tk.E)

root.mainloop()