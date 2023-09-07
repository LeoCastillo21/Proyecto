import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

#Aqui guardo el nombre de las ligas con su respectiva url

class PremierLeagueStatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("League Statistics")
        
        self.url_dict = {
            "Premier League": 'https://www.sport.es/es/resultados/premier-league/estadisticas/',
            "La Liga": 'https://www.sport.es/es/resultados/la-liga/estadisticas/',
            "Bundesliga": 'https://www.sport.es/es/resultados/bundesliga/estadisticas/',
            "Ligue 1": 'https://www.sport.es/es/resultados/liga-francia/estadisticas/',
            "Champions League": 'https://www.sport.es/es/resultados/champions/estadisticas/'
            
        }

       
        
        self.selected_league = tk.StringVar()
        self.search_text = tk.StringVar()

        
        
        self.league_buttons_frame = tk.Frame(root)
        self.league_buttons_frame.pack(pady=10)

        
        
        for league in self.url_dict.keys():
            button = tk.Radiobutton(self.league_buttons_frame, text=league, variable=self.selected_league, value=league, command=self.load_data)
            button.pack(side="left", padx=10)
        
        self.search_frame = tk.Frame(root)
        self.search_frame.pack(pady=10)
        
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_text)
        self.search_entry.pack(side="left", padx=10)
        
        self.search_button = tk.Button(self.search_frame, text="Buscar", command=self.search)
        self.search_button.pack(side="left", padx=10)
        
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(fill="both", expand=True)
        
        self.scroll = None
        self.tree = None
        
        self.chart_button = tk.Button(root, text="Mostrar estadistica seleccionada", command=self.show_statistics_chart)
        self.chart_button.pack(pady=10)
        
        self.selected_category = tk.StringVar()
        self.category_dropdown = ttk.Combobox(root, textvariable=self.selected_category, state="readonly")
        self.category_dropdown.pack(pady=10)
        
    def load_data(self):
        selected_league = self.selected_league.get()
        self.url = self.url_dict[selected_league]
        self.clear_content()
        self.scrape_data()
        self.populate_category_dropdown()
        
    def populate_category_dropdown(self):
        categories = set()
        response = requests.get(self.url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table', class_='table')
            
            for table in tables:
                title = table.find_previous('h2', class_='title').text
                categories.add(title)
                
        self.category_dropdown["values"] = list(categories)
        
    def clear_content(self):
        if self.scroll:
            self.scroll.destroy()
        if self.tree:
            self.tree.destroy()
        
    def scrape_data(self, search_term=None):
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tables = soup.find_all('table', class_='table')
            self.scroll = ttk.Scrollbar(self.content_frame)
            self.scroll.pack(side="right", fill="y")
            
            self.tree = ttk.Treeview(self.content_frame, columns=("Position", "Name", "Total"))
            self.tree.heading("#1", text="Position")
            self.tree.heading("#2", text="Name")
            self.tree.heading("#3", text="Total")
            self.tree.pack(fill="both", expand=True)
            
            self.tree.config(yscrollcommand=self.scroll.set)
            self.scroll.config(command=self.tree.yview)
            
            for table in tables:
                title = table.find_previous('h2', class_='title').text
                rows = table.find_all('tr')
                
                self.tree.insert("", "end", values=("Category", title, ""))
                
                for row in rows[1:]:
                    columns = row.find_all('td')
                    position = columns[0].text
                    name = columns[1].find('span', class_='name').text
                    total = columns[2].text
                    
                    if not search_term or search_term.lower() in name.lower():
                        self.tree.insert("", "end", values=(position, name, total))
                
                self.tree.insert("", "end", values=("-----------------------------------------------------------------------------------------------------", "-----------------------------------------------------------------------------------------------------", "-----------------------------------------------------------------------------------------------------"))
                    
    def show_statistics_chart(self):
        selected_category = self.selected_category.get()
        stats = self.get_statistics(selected_category)
        stats_df = pd.DataFrame(stats)
        stats_df["Total"] = pd.to_numeric(stats_df["Total"])  
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=stats_df.sort_values("Total", ascending=False), x="Total", y="Name", hue="Category", dodge=False)
        plt.title("Estadisticas")
        plt.xlabel("Total")
        plt.ylabel("Nombres")
        plt.legend(title="Categoria", bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.show()
        
    def get_statistics(self, selected_category):
        response = requests.get(self.url)
        stats = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table', class_='table')
            
            for table in tables:
                title = table.find_previous('h2', class_='title').text
                if selected_category.lower() in title.lower():
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:
                        columns = row.find_all('td')
                        name = columns[1].find('span', class_='name').text
                        total = columns[2].text
                        stats.append({"Category": title, "Name": name, "Total": total})
                    
        return stats
        
    def search(self):
        search_term = self.search_text.get()
        self.clear_content()
        self.scrape_data(search_term)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PremierLeagueStatsApp(root)
    app.run()
