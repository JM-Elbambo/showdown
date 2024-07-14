import asyncio
import threading
import tkinter as tk
import tkinter.ttk as ttk

from run import showdown

class PokemonShowdownSimulator:
    
    def __init__(self):
        # Create the main window
        self.root = tk.Tk() 
        self.root.title("Pokemon Showdown Simulator")
        self.root.geometry("400x400")
        
        IMAGE_BG = tk.PhotoImage(file="images/bg-starfield.png")
        
        # Background image for root
        tk.Label(self.root, image=IMAGE_BG).place(relwidth=1, relheight=1)
        
        # Main frame
        self.frame_main = tk.Frame(self.root)
        tk.Label(self.frame_main, image=IMAGE_BG).place(relwidth=1, relheight=1)
        
        # Credential fields
        self.creds = []
        self.frame_bot1 = self.__create_bot_fields("Bot 1")
        self.frame_bot2= self.__create_bot_fields("Bot 2")
        
        self.button_start = ttk.Button(self.frame_main, text="Start", command=self.start)
        self.button_start.pack(pady=8)
        
        self.loading = ttk.Progressbar(self.frame_main, mode="indeterminate", style="TProgressbar")
        
        self.frame_main.pack(expand=True)
        self.root.mainloop()
    
    def __create_bot_fields(self, bot_name:str):
        # Create StringVar for fields
        self.creds.append(
            {
                "username": tk.StringVar(),
                "password": tk.StringVar()
            }
        )
        cred_index = len(self.creds) - 1
        
        # Create frame for widgets
        frame_fields = ttk.Frame(self.frame_main)
        frame_fields.pack(ipadx=8, ipady=8, pady=8)
        
        # Create fields widgets
        ttk.Label(frame_fields, text=bot_name).pack()
        frame_grid = tk.Frame(frame_fields)
        frame_grid.pack(expand=True)
        ttk.Label(frame_grid, text="Username:").grid(row=0, column=0, sticky=tk.E, pady=(0,8))
        ttk.Label(frame_grid, text="Password:").grid(row=1, column=0, sticky=tk.E)
        ttk.Entry(frame_grid, textvariable=self.creds[cred_index]["username"]).grid(row=0, column=1, pady=(0,8))
        ttk.Entry(frame_grid, textvariable=self.creds[cred_index]["password"], show="*").grid(row=1, column=1)
        
        return frame_fields
    
    def __set_widget_states_recursive(widget: ttk.Widget, state):
        for child in widget.winfo_children():
            if isinstance(child, tk.Frame):
                PokemonShowdownSimulator.__set_widget_states_recursive(child, state)
            else:
                child.configure(state=state)
    
    def activate_entries(self, activate:bool):
        state = tk.NORMAL if activate else tk.DISABLED
        PokemonShowdownSimulator.__set_widget_states_recursive(self.frame_bot1, state)
        PokemonShowdownSimulator.__set_widget_states_recursive(self.frame_bot2, state)
    
    def start(self):
        # Change start button to loading bar
        self.button_start.pack_forget()
        self.loading.pack(fill=tk.X, pady=8)
        self.loading.start()
        
        self.activate_entries(False)
        
        thread = threading.Thread(target=asyncio.run, args=(self.__start_thread(),))
        thread.start()
    
    async def __start_thread(self):
        try:
            await asyncio.sleep(5)
            asyncio.run(showdown())
        except Exception as e:
            print(e)
        
        # Change loading bar to start button
        self.loading.stop()
        self.loading.pack_forget()
        self.button_start.pack(pady=8)
        
        self.activate_entries(True)


if __name__ == "__main__":
    PokemonShowdownSimulator()
