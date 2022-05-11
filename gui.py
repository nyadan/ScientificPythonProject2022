import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from ctypes import windll

import PyProc


class Root(Tk):
    """
    Gui class
    """
    def __init__(self):
        """
        Init gui
        """
        super(Root, self).__init__()
        self.title("Scientific python project")
        self.minsize(600,500)
        self.filename = ""
        self.selected = []
        self.selected_string = tkinter.StringVar()


        self.openFrame = ttk.LabelFrame(self, text = "Please select a file")
        self.openFrame.grid(column = 0, row = 0, padx = 20, pady = 20)
        self.openButton()


        self.selectionFrame = ttk.LabelFrame(self, text = "Select optional calulations (can cancel)")
        self.selectionFrame.grid(column = 0, row = 1, padx = 20, pady = 20)
        self.dropDownSelect()


        self.okFrame = ttk.LabelFrame(self, text = "Press OK after selecting everything")
        self.okFrame.grid(column = 1, row = 1, padx = 20, pady = 200)
        self.okButton()

    def openButton(self):
        """
        Create open button
        """
        self.openButton = ttk.Button(self.openFrame, text = "Open file", command = self.fileDialog)
        self.openButton.grid(column = 20, row = 20)
    
    def okButton(self):
        """
        Create OK button
        """
        self.okButton = ttk.Button(self.okFrame, text = "OK", command =  self.okEvent)
        self.okButton.grid(column = 0, row = 0)


    def fileDialog(self):
        """
        For file read-in
        """
        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("CSV", ".csv"),("all files","*.*")) )
        self.label = ttk.Label(self.openFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = self.filename)

    def dropDownSelect(self):
        """
        For drop-down menu
        """
        self.dropDown = ttk.Combobox(self.selectionFrame,
                                     values = ["max", "min", "mean", "variance", "range", "median", "std"])
        self.dropDown.bind("<<ComboboxSelected>>",self.selectionChange)
        self.dropDown.grid(column = 0, row = 0)

    def selectionChange(self, event):
        """
        For selection logic
        If you select it again, it is deselected.
        """
        event = self.dropDown.get()
        if not event in self.selected:
            self.selected.append(self.dropDown.get())
        else:
            self.selected.remove(event)
            self.labelSelection.destroy()

        temp_selected = ""
        for i in range(len(self.selected)):
            temp_selected += self.selected[i] + "\n"

        self.selected_string.set(temp_selected)
        self.update()
        self.labelSelection = ttk.Label(self.selectionFrame, text = "")
        self.labelSelection.grid(column = 1, row = 2)
        self.labelSelection.configure(textvariable = self.selected_string)


    def okEvent(self):
        """
        For OK button logic.
        It sends the data for getting metadata.
        """
        self.label = ttk.Label(self.okFrame, text = "")
        self.label.grid(column = 20, row = 20)
        self.label.destroy()
        if self.filename == "":
            self.label = ttk.Label(self.okFrame, text = "")
            self.label.grid(column = 20, row = 20)
            self.label.configure(text = "File not selected!")
            return

        file_datas = {
            "infile":self.filename,
            "metafile":self.filename[:-3]+"json"
        }
        PyProc.run_analysis(file_datas, self.selected)
        self.label = ttk.Label(self.okFrame, text = "")
        self.label.grid(column = 20, row = 20)
        self.label.configure(text="The file is ready!")

def main():
    """
    Main function, this is needed for the run.
    """
    # For better visuals
    windll.shcore.SetProcessDpiAwareness(1)
    root = Root()
    root.mainloop()

if __name__ == "__main__":
    main()
