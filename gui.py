from tkinter import Tk, Label, Button, Entry, IntVar, END, W, E

class drone_console:

    def __init__(self, master):
        self.master = master
        master.title("Multi-Drone Console")

        # self.drone1 = drone(1)
        # self.drone5 = drone(5)

        self.total = 0
        self.entered_number = 0

        self.total_label_text = IntVar()
        self.total_label_text.set(self.total)
        self.total_label = Label(master, textvariable=self.total_label_text)

        self.label1 = Label(master, text="Drone 1 Console")
        self.label1x = Label(master, text="Desired x:")
        self.label1y = Label(master, text="Desired y:")
        self.label5 = Label(master, text="Drone 5 Console")
        self.label5x = Label(master, text="Desired x:")
        self.label5y = Label(master, text="Desired y:")

        vcmd = master.register(self.validate) # we have to wrap the command
        self.entry_1_x = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.entry_1_y = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.execute_button1 = Button(master, text="Execute 1", command=lambda: self.update("execute 1"))

        self.entry_5_x = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.entry_5_y = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.execute_button5 = Button(master, text="Execute 5", command=lambda: self.update("execute 5"))


        # LAYOUT

        self.label1.grid(row=0, column=0, sticky=W)

        self.label1x.grid(row=1, column=0, columnspan=1, sticky=W)
        self.label1y.grid(row=2, column=0, columnspan=1, sticky=W)

        self.entry_1_x.grid(row=1, column=1, columnspan=2, sticky=W+E)
        self.entry_1_y.grid(row=2, column=1, columnspan=2, sticky=W+E)

        self.execute_button1.grid(row=2, column=4, sticky=W+E)

        self.label5.grid(row=4, column=0, sticky=W)

        self.label5x.grid(row=5, column=0, columnspan=1, sticky=W)
        self.label5y.grid(row=6, column=0, columnspan=1, sticky=W)

        self.entry_5_x.grid(row=5, column=1, columnspan=2, sticky=W+E)
        self.entry_5_y.grid(row=6, column=2, columnspan=2, sticky=W+E)

        self.execute_button5.grid(row=6, column=4, sticky=W+E)

    def validate(self, new_text):
        if not new_text: # the field is being cleared
            self.entered_number = 0
            return True

        try:
            self.entered_number = int(new_text)
            return True
        except ValueError:
            return False

    def update(self, method):
        if method == "execute 1":
            self.drone1.set_desired(d1x, d1y)
        elif method == "execute 5":
            self.drone5.set_desired(d5x, d5y)

        if method == "add":
            self.total += self.entered_number
        elif method == "subtract":
            self.total -= self.entered_number
        else: # reset
            self.total = 0

        self.total_label_text.set(self.total)
        self.entry.delete(0, END)

root = Tk()
my_gui = drone_console(root)
root.mainloop()