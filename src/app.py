import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
import utils
import webbrowser
from data import Data

URL_MAP = {
    "https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker": "https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker",
    "https://www.crea.gov.it/alimenti-e-nutrizione": "https://www.crea.gov.it/alimenti-e-nutrizione",
    "https://www.alimentinutrizione.it": "https://www.alimentinutrizione.it"
}

def open_github():
    webbrowser.open_new("https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker")

class MacroMicro(ttk.Frame):
    data_source = Data()
    blank_table = utils.load_blank_table()
    micronutrient_list = [row['nutrients'] for row in blank_table]
    micronutrient_totals = {micronutrient: 0.0 for micronutrient in micronutrient_list}
    added_foods = []
    proplipids = range(37, 59)
    propaa = range(60, 77)

    def open_link(self, event):
        widget = event.widget
        index = widget.index(ttk.CURRENT)
        clicked_text = widget.get(f"{index} linestart", f"{index} lineend")
        url = URL_MAP.get(clicked_text.strip())
        if url:
            webbrowser.open_new(url)

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".tsv", filetypes=[("TSV files", "*.tsv")])
        if not file_path:
            return

        data_to_export = [{'micronutrient': k, 'total_amount': v} for k, v in self.micronutrient_totals.items()]
        headers = ['micronutrient', 'total_amount']
        utils.write_tsv(file_path, data_to_export, headers)
        messagebox.showinfo("Info", f"Data exported to {file_path}")

    def add_food(self):
        food_name = self.food_var.get()
        try:
            quantity = float(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for quantity.")
            return
        
        if food_name not in self.data_source.get_food_list():
            messagebox.showerror("Error", "Food not found in the database.")
            return

        food_id = self.data_source.get_food_id(food_name)
        try:
            food_details = self.data_source.read_food_details(food_id)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Details file for food ID {food_id} not found.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the food details: {e}")
            return

        actual_amounts = {}
        for micronutrient in self.micronutrient_totals:
            if micronutrient in food_details:
                actual_amounts[micronutrient] = food_details[micronutrient] * (quantity / 100.0)

        lipid_total = actual_amounts.get(self.micronutrient_list[4], 0.0)
        aa_total = actual_amounts.get(self.micronutrient_list[3], 0.0)

        for micronutrient, amount in actual_amounts.items():
            micronutrient_index = self.micronutrient_list.index(micronutrient)
            if micronutrient_index in self.proplipids:
                self.micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * lipid_total
            elif micronutrient_index in self.propaa:
                self.micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * aa_total
            else:
                self.micronutrient_totals[micronutrient] += amount

        messagebox.showinfo("Info", f"Added {quantity}g of {food_name}")
        self.added_foods.append((food_name, quantity))
        self.update_added_foods_list()

    def switch_language(self, event):
        language = self.current_language.get()
        self.data_source.switch_language(language)

    def update_added_foods_list(self):
        for widget in self.added_foods_frame.winfo_children():
            widget.destroy()
        
        for i, (food_name, quantity) in enumerate(self.added_foods):
            frame = ttk.Frame(self.added_foods_frame)
            frame.pack(anchor='w')
            ttk.Label(frame, text=f"{food_name} - {quantity}g").pack(side='left')
            ttk.Button(frame, text="Duplicate", command=lambda i=i: self.duplicate_food(i), bootstyle='secondary-outline').pack(side='right', padx=5)
            ttk.Button(frame, text="Delete", command=lambda i=i: self.delete_food(i), bootstyle='danger-outline').pack(side='right', padx=5)

    def duplicate_food(self, index):
        food_name, quantity = self.added_foods[index]
        self.added_foods.append((food_name, quantity))
        
        food_id = self.data_source.get_food_id(food_name)
        try:
            food_details = self.data_source.read_food_details(food_id)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Details file for food ID {food_id} not found.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the food details: {e}")
            return
        
        actual_amounts = {}
        for micronutrient in self.micronutrient_totals:
            if micronutrient in food_details:
                actual_amounts[micronutrient] = food_details[micronutrient] * (quantity / 100.0)
        
        lipid_total = actual_amounts.get(self.micronutrient_list[4], 0.0)
        aa_total = actual_amounts.get(self.micronutrient_list[3], 0.0)
        
        for micronutrient, amount in actual_amounts.items():
            micronutrient_index = self.micronutrient_list.index(micronutrient)
            if micronutrient_index in self.proplipids:
                self.micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * lipid_total
            elif micronutrient_index in self.propaa:
                self.micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * aa_total
            else:
                self.micronutrient_totals[micronutrient] += amount
        
        messagebox.showinfo("Info", f"Duplicated {quantity}g of {food_name}")
        self.update_added_foods_list()

    def search_foods(self, event):
        search_term = self.search_var.get()
        self.food_menu['values'] = self.data_source.search_food(search_term)

    def wipe_data(self):
        if messagebox.askyesno("Confirm Wipe", "Are you sure you want to wipe all data? Unsaved data will be lost."):
            self.micronutrient_totals = {micronutrient: 0.0 for micronutrient in self.micronutrient_list}
            self.added_foods = []
            self.update_added_foods_list()
            self.food_var.set('')
            self.quantity_var.set('')

    def show_info(self):
        info_window = ttk.Toplevel(self)
        info_window.title("Program Info")
        info_window.iconbitmap('logo.ico')
        
        text_widget = ttk.Text(info_window, wrap="word", padx=10, pady=10, width=50, height=10)
        text_widget.pack(expand=True, fill='both')
        
        text_widget.tag_configure("bold", font=("ttkDefaultFont", 10, "bold"))
        text_widget.tag_configure("link", foreground="blue", underline=True)
        text_widget.tag_bind("link", "<Button-1>", self.open_link)
        
        text_widget.insert("1.0", "MacroMicro-ITA-Tracker\n", "bold")
        text_widget.insert("end", "Version: 1.0\nMaintainer: Fabbrini Marco\nContact: fabbrinimarco.mf@gmail.com\n\nFor usage instructions, visit:\n")
        text_widget.insert("end", "https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker\n", "link")
        text_widget.insert("end", "\nFood tables have been obtained from CREA, Centro di ricerca Alimenti e Nutrizione, original source web pages:\n")
        text_widget.insert("end", "https://www.crea.gov.it/alimenti-e-nutrizione\n", "link")
        text_widget.insert("end", "https://www.alimentinutrizione.it", "link")
        
        text_widget.config(state=ttk.DISABLED)
        
        close_button = ttk.Button(info_window, text="Close", command=info_window.destroy)
        close_button.pack(pady=10)
        
        info_window.geometry("800x380")
        info_window.transient(self)
        info_window.grab_set()
        self.wait_window(info_window)

    def delete_food(self, index):
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.added_foods[index][1]}g of {self.added_foods[index][0]}?"):
            return
        
        food_name, quantity = self.added_foods.pop(index)
        food_id = self.data_source.get_food_id(food_name)
        try:
            food_details =self.data_source.read_food_details(food_id)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Details file for food ID {food_id} not found.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the food details: {e}")
            return
        
        actual_amounts = {}
        for micronutrient in self.micronutrient_totals:
            if micronutrient in food_details:
                actual_amounts[micronutrient] = food_details[micronutrient] * (quantity / 100.0)
        
        lipid_total = actual_amounts.get(self.micronutrient_list[4], 0.0)
        aa_total = actual_amounts.get(self.micronutrient_list[3], 0.0)
        
        for micronutrient, amount in actual_amounts.items():
            micronutrient_index = self.micronutrient_list.index(micronutrient)
            if micronutrient_index in self.proplipids:
                self.micronutrient_totals[micronutrient] -= (food_details[micronutrient] / 100.0) * lipid_total
            elif micronutrient_index in self.propaa:
                self.micronutrient_totals[micronutrient] -= (food_details[micronutrient] / 100.0) * aa_total
            else:
                self.micronutrient_totals[micronutrient] -= amount
        
        self.update_added_foods_list()

    def __init__(self, master : ttk.Window):
        super().__init__(master)
        self.pack(expand=True, fill='both')
        
        self.food_var = ttk.StringVar()
        self.quantity_var = ttk.StringVar()
        self.search_var = ttk.StringVar()
        self.current_language = ttk.StringVar(value="Italian")

        ttk.Label(self, text="Select Language:").pack(pady=5)
        language_menu = ttk.Combobox(self, textvariable=self.current_language, values=["Italian", "English"], state="readonly", bootstyle = "dark", width = 6)
        language_menu.pack(pady=5)
        language_menu.bind('<<ComboboxSelected>>', self.switch_language)

        ttk.Label(self, text="Search Food:").pack(pady=5)
        search_entry = ttk.Entry(self, textvariable=self.search_var, width=50)
        search_entry.pack(pady=5)
        search_entry.bind('<KeyRelease>', self.search_foods)

        sorted_food_names = sorted(self.data_source.get_food_list())
        ttk.Label(self, text="Select Food:").pack(pady=5)
        self.food_menu = ttk.Combobox(self, textvariable=self.food_var, values=sorted_food_names, width=50, state="readonly", bootstyle = "primary")
        self.food_menu.pack(pady=5)

        ttk.Label(self, text="Enter Quantity (grams):").pack(pady=5)
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_var, width=50)
        self.quantity_entry.pack(pady=5)

        add_button = ttk.Button(self, text="Add Food", command=self.add_food)
        add_button.pack(pady=10)

        self.added_foods_container = ttk.Frame(self)
        self.added_foods_container.pack(fill='both', pady=10, expand=True)
        ttk.Label(self.added_foods_container, text="Added Foods:").pack(pady=5)
        canvas = ttk.Canvas(self.added_foods_container, height=60)
        scrollbar = ttk.Scrollbar(self.added_foods_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((450, 50), window=scrollable_frame, anchor="center")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.added_foods_frame = scrollable_frame
        buffer_frame = ttk.Frame(scrollable_frame, height=60)
        buffer_frame.pack()

        export_button = ttk.Button(self, text="Export Data", command=self.export_data)
        export_button.pack(pady=10)

        wipe_button = ttk.Button(self, text="Wipe Data", command=self.wipe_data, bootstyle='danger')
        wipe_button.pack(pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        info_button = ttk.Button(button_frame, text="Info", command=self.show_info, bootstyle='secondary')
        info_button.pack(side="left", padx=5)

        website1_button = ttk.Button(button_frame, text="Github", command=open_github, bootstyle='secondary')
        website1_button.pack(side="left", padx=5)

if __name__ == '__main__':
    app = ttk.Window(
        title = 'MacroMicro-ITA-Tracker',
        themename='sandstone',
        size=(900, 900),
        resizable=(False, True),
        iconphoto='logo.ico'
    )
    MacroMicro(app)
    app.mainloop()
