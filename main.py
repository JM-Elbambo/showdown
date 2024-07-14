import asyncio
import threading
import tkinter as tk
import tkinter.ttk as ttk

from Credentials import Credentials
from run import showdown

class PokemonShowdownSimulator:
    
    def __init__(self):
        # Create the main window
        self.root = tk.Tk() 
        self.root.title('Pokemon Showdown Simulator')
        self.root.geometry('400x400')
        
        IMAGE_BG = tk.PhotoImage(file='images/bg-starfield.png')
        
        # Background image for root
        tk.Label(self.root, image=IMAGE_BG).place(relwidth=1, relheight=1)
        
        # Main frame
        self.frame_main = tk.Frame(self.root)
        tk.Label(self.frame_main, image=IMAGE_BG).place(relwidth=1, relheight=1)
        
        # Credential fields
        self.var_creds = [] # StringVar for Entry
        self.creds = [Credentials, Credentials] # Credentials instances
        self.frame_bot1 = self.__create_bot_fields('Bot 1')
        self.frame_bot2= self.__create_bot_fields('Bot 2')
        
        self.button_start = ttk.Button(self.frame_main, text='Start', command=self.start)
        self.button_start.pack(pady=8)
        
        self.loading = ttk.Progressbar(self.frame_main, mode='indeterminate', style='TProgressbar')
        
        self.frame_main.pack(expand=True)
        self.root.mainloop()
    
    def __create_bot_fields(self, bot_name:str):
        # Create StringVar for fields
        self.var_creds.append(
            {
                'username': tk.StringVar(),
                'password': tk.StringVar()
            }
        )
        cred_index = len(self.var_creds) - 1
        
        # Create frame for widgets
        frame_fields = ttk.Frame(self.frame_main)
        frame_fields.pack(ipadx=8, ipady=8, pady=8)
        
        # Create fields widgets
        ttk.Label(frame_fields, text=bot_name).pack()
        frame_grid = tk.Frame(frame_fields)
        frame_grid.pack(expand=True)
        ttk.Label(frame_grid, text='Username:').grid(row=0, column=0, sticky=tk.E, pady=(0,8))
        ttk.Label(frame_grid, text='Password:').grid(row=1, column=0, sticky=tk.E)
        ttk.Entry(frame_grid, textvariable=self.var_creds[cred_index]['username']).grid(row=0, column=1, pady=(0,8))
        ttk.Entry(frame_grid, textvariable=self.var_creds[cred_index]['password'], show='*').grid(row=1, column=1)
        
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
        
        # Create Credentials object from inputs
        for i in range(len(self.var_creds)):
            username = self.var_creds[i]['username'].get()
            password = self.var_creds[i]['password'].get()
            self.creds[i] = Credentials(username, password)
        
        # Instantiate bots
        threading.Thread(target=self.__start_bots).start()
    
    def __start_bots(self):
        try:
            # Create separate threads
            thread_defender = threading.Thread(target=asyncio.run, args=(self.__thread_defender_bot(),))
            thread_challenger = threading.Thread(target=asyncio.run, args=(self.__thread_challenger_bot(),))
            
            # Start threads
            thread_defender.start()
            thread_challenger.start()
            
            # Wait for threads
            thread_defender.join()
            thread_challenger.join()
        except Exception as e:
            # TODO: stop threads
            print(e)
        
        # Change loading bar to start button
        self.loading.stop()
        self.loading.pack_forget()
        self.button_start.pack(pady=8)
        
        self.activate_entries(True)
    
    async def __thread_defender_bot(self):
        try:
            await showdown(self.creds[0])
        except Exception as e:
            raise Exception('defender_bot ERROR:\n' + str(e))
    
    async def __thread_challenger_bot(self):
        try:
            asyncio.run(showdown(self.creds[1], self.creds[0].username))
        except Exception as e:
            raise Exception('challenger_bot ERROR:\n' + str(e))


if __name__ == '__main__':
    PokemonShowdownSimulator()
