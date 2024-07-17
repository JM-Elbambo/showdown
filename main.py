import asyncio
import json
import os
import sys
import threading
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

from bot_config import BotConfig
from run import showdown


class PokemonShowdownSimulator:
    CONFIG_FILE = "config.dat"
    
    def __init__(self):
        # Create the main window
        self.root = tk.Tk() 
        self.root.title('Pokemon Showdown Simulator')
        self.root.geometry('400x400')
        
        IMAGE_BG = tk.PhotoImage(file=resource_path('images/bg-starfield.png'))
        self.var_bot_configs = [] # StringVar for fields
        self.var_remember = tk.IntVar()
        
        # Background image for root
        tk.Label(self.root, image=IMAGE_BG).place(relwidth=1, relheight=1)
        
        # Main frame
        self.frame_main =ttk.Frame(self.root)
        tk.Label(self.frame_main, image=IMAGE_BG).place(relwidth=1, relheight=1)
        
        # Config fields
        self.bot_configs = [BotConfig, BotConfig] # BotConfig instances
        self.frame_bot1 = self.__create_bot_fields('Bot 1')
        self.frame_bot2= self.__create_bot_fields('Bot 2')
        
        # Load saved config if exists
        self.__load_config()
        
        self.frame_footer = ttk.Frame(self.frame_main)
        self.frame_footer.pack(fill=tk.BOTH, pady=8, ipadx=32)
        
        # Remember checkbutton
        ttk.Label(self.frame_footer, text="Remember Config: ").pack(side=tk.LEFT)
        ttk.Checkbutton(self.frame_footer, variable=self.var_remember).pack(side=tk.LEFT)
        
        # Start button
        ttk.Button(self.frame_footer, text='Start', command=self.start).pack(side=tk.RIGHT)
        
        # Status widgets
        self.loading = ttk.Progressbar(self.frame_main, mode='indeterminate', style='TProgressbar')
        self.label_message = ttk.Label(self.frame_main)
        
        self.frame_main.pack(expand=True)
        self.root.mainloop()
    
    def __create_bot_fields(self, bot_name:str):
        # Create StringVar for fields
        self.var_bot_configs.append({
            'username': tk.StringVar(),
            'password': tk.StringVar(),
            'team_file': tk.StringVar()
            })
        config_index = len(self.var_bot_configs) - 1
        
        # Create frame for widgets
        frame_fields = ttk.Frame(self.frame_main)
        frame_fields.pack(ipadx=8, ipady=8, pady=8)
        
        # Create widgets for credentials
        ttk.Label(frame_fields, text=bot_name).pack(pady=(4,0))
        frame_grid =ttk.Frame(frame_fields)
        frame_grid.pack(expand=True)
        ttk.Label(frame_grid, text='Username:').grid(row=0, column=0, sticky=tk.E)
        ttk.Label(frame_grid, text='Password:').grid(row=1, column=0, sticky=tk.E)
        ttk.Label(frame_grid, text='Team File:').grid(row=2, column=0, sticky=tk.E)
        ttk.Entry(frame_grid, textvariable=self.var_bot_configs[config_index]['username']).grid(row=0, column=1, sticky=tk.EW)
        ttk.Entry(frame_grid, textvariable=self.var_bot_configs[config_index]['password'], show='*').grid(row=1, column=1, pady=8, sticky=tk.EW)
        
        # Create widgets for team file
        frame_filedialog = ttk.Frame(frame_grid)
        frame_filedialog.grid(row=2, column=1)
        ttk.Entry(frame_filedialog, textvariable=self.var_bot_configs[config_index]['team_file']).pack(side=tk.LEFT)
        ttk.Button(frame_filedialog, text='Browse',
                   command=lambda:self.__select_team_file(self.var_bot_configs[config_index]['team_file'])).pack(side=tk.RIGHT)
        
        return frame_fields
    
    def __select_team_file(self, var:tk.StringVar):
        filename = filedialog.askopenfilename()
        var.set(filename)
    
    def __set_widget_states_recursive(widget: ttk.Widget, state):
        for child in widget.winfo_children():
            if isinstance(child,ttk.Frame):
                PokemonShowdownSimulator.__set_widget_states_recursive(child, state)
            else:
                child.configure(state=state)
    
    def activate_entries(self, activate:bool):
        state = tk.NORMAL if activate else tk.DISABLED
        PokemonShowdownSimulator.__set_widget_states_recursive(self.frame_bot1, state)
        PokemonShowdownSimulator.__set_widget_states_recursive(self.frame_bot2, state)
    
    def show_message(self, message:str):
        self.label_message.config(text=message)
        self.label_message.pack(pady=8, side=tk.BOTTOM)
    
    def hide_message(self):
        self.label_message.pack_forget()
        
    def start(self):
        # Update BotConfig object from inputs
        for i in range(len(self.var_bot_configs)):
            username = self.var_bot_configs[i]['username'].get()
            password = self.var_bot_configs[i]['password'].get()
            team_file = self.var_bot_configs[i]['team_file'].get()
            
            config = BotConfig(username, password, team_file)
            if config.is_valid():
                self.bot_configs[i] = config
            else:
                self.show_message("Invalid inputs. Please try again.")
                return
        
        self.activate_entries(False)
        self.hide_message()
        
        # Change start button to loading bar
        self.frame_footer.pack_forget()
        self.loading.pack(fill=tk.X, pady=8)
        self.loading.start()
        
        self.__save_config()
        
        # Instantiate bots
        threading.Thread(target=self.__start_bots).start()
    
    def __start_bots(self):
        try:
            # Create separate threads
            thread_defender = threading.Thread(target=asyncio.run, args=(self.__thread_defender_bot(),))
            thread_challenger = threading.Thread(target=asyncio.run, args=(self.__thread_challenger_bot(),))
            
            # Start threads
            thread_defender.start()
            asyncio.sleep(10)
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
        self.frame_footer.pack(pady=8)
        
        self.activate_entries(True)
    
    async def __thread_defender_bot(self):
        try:
            await showdown(self.bot_configs[0], None)
        except Exception as e:
            raise Exception('defender_bot ERROR:\n' + str(e))
    
    async def __thread_challenger_bot(self):
        try:
            await showdown(self.bot_configs[1], self.bot_configs[0].username)
        except Exception as e:
            raise Exception('challenger_bot ERROR:\n' + str(e))

    def __save_config(self):
        if self.var_remember.get() == 1:
            data = []
            for i in range(len(self.bot_configs)):
                data.append({
                    "username": self.bot_configs[i].username,
                    "password": self.bot_configs[i].password,
                    "team_file": self.bot_configs[i].team_file
                })
            with open(PokemonShowdownSimulator.CONFIG_FILE, 'w') as file:
                json.dump(data, file)
        # Delete if exists
        else:
            if os.path.exists(PokemonShowdownSimulator.CONFIG_FILE):
                os.remove(PokemonShowdownSimulator.CONFIG_FILE)
    
    def __load_config(self):
        try:
            if os.path.exists(PokemonShowdownSimulator.CONFIG_FILE):
                with open(PokemonShowdownSimulator.CONFIG_FILE, 'r') as file:
                    data = json.load(file)
                    
                    # Load data into fields
                    for i in range(len(data)):
                        if i < len(self.var_bot_configs):
                            self.var_bot_configs[i]["username"].set(data[i]["username"])
                            self.var_bot_configs[i]["password"].set(data[i]["password"])
                            self.var_bot_configs[i]["team_file"].set(data[i]["team_file"])
                self.var_remember.set(1)
        except Exception as e:
            print("Corrupted config file:", str(e))

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for development and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    try:
        PokemonShowdownSimulator()
    except Exception as e:
        print("Error:\n" + str(e))
        input()
