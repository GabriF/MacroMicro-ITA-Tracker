import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import ttkbootstrap as tb
import webbrowser
from data import Data

d = Data()

def read_table(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        return [row for row in reader]


def write_tsv(file_path, data, headers):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(data)

def load_blank_table():
    return read_table('blank_table.tsv')


def switch_language(event):
    language = current_language.get()
    d.switch_language(language)


def add_food():
    food_name = food_var.get()
    try:
        quantity = float(quantity_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for quantity.")
        return
    
    if food_name not in d.get_food_list():
        messagebox.showerror("Error", "Food not found in the database.")
        return

    food_id = d.get_food_id(food_name)
    try:
        food_details = d.read_food_details(food_id)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Details file for food ID {food_id} not found.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the food details: {e}")
        return

    actual_amounts = {}
    for micronutrient in micronutrient_totals:
        if micronutrient in food_details:
            actual_amounts[micronutrient] = food_details[micronutrient] * (quantity / 100.0)

    lipid_total = actual_amounts.get(micronutrient_list[4], 0.0)
    aa_total = actual_amounts.get(micronutrient_list[3], 0.0)

    for micronutrient, amount in actual_amounts.items():
        micronutrient_index = micronutrient_list.index(micronutrient)
        if micronutrient_index in proplipids:
            micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * lipid_total
        elif micronutrient_index in propaa:
            micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * aa_total
        else:
            micronutrient_totals[micronutrient] += amount

    messagebox.showinfo("Info", f"Added {quantity}g of {food_name}")
    added_foods.append((food_name, quantity))
    update_added_foods_list()


def update_added_foods_list():
    for widget in added_foods_frame.winfo_children():
        widget.destroy()
    
    for i, (food_name, quantity) in enumerate(added_foods):
        frame = tk.Frame(added_foods_frame)
        frame.pack(anchor='w')
        tk.Label(frame, text=f"{food_name} - {quantity}g", height=2).pack(side='left')
        tb.Button(frame, text="Duplicate", command=lambda i=i: duplicate_food(i), bootstyle='secondary-outline').pack(side='right', padx=5)
        tb.Button(frame, text="Delete", command=lambda i=i: delete_food(i), bootstyle='danger-outline').pack(side='right', padx=5)


def delete_food(index):
    if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {added_foods[index][1]}g of {added_foods[index][0]}?"):
        return
    
    food_name, quantity = added_foods.pop(index)
    food_id = d.get_food_id(food_name)
    try:
        food_details = d.read_food_details(food_id)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Details file for food ID {food_id} not found.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the food details: {e}")
        return
    
    actual_amounts = {}
    for micronutrient in micronutrient_totals:
        if micronutrient in food_details:
            actual_amounts[micronutrient] = food_details[micronutrient] * (quantity / 100.0)
    
    lipid_total = actual_amounts.get(micronutrient_list[4], 0.0)
    aa_total = actual_amounts.get(micronutrient_list[3], 0.0)
    
    for micronutrient, amount in actual_amounts.items():
        micronutrient_index = micronutrient_list.index(micronutrient)
        if micronutrient_index in proplipids:
            micronutrient_totals[micronutrient] -= (food_details[micronutrient] / 100.0) * lipid_total
        elif micronutrient_index in propaa:
            micronutrient_totals[micronutrient] -= (food_details[micronutrient] / 100.0) * aa_total
        else:
            micronutrient_totals[micronutrient] -= amount
    
    update_added_foods_list()


def duplicate_food(index):
    food_name, quantity = added_foods[index]
    added_foods.append((food_name, quantity))
    
    food_id = d.get_food_id(food_name)
    try:
        food_details = d.read_food_details(food_id)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Details file for food ID {food_id} not found.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the food details: {e}")
        return
    
    actual_amounts = {}
    for micronutrient in micronutrient_totals:
        if micronutrient in food_details:
            actual_amounts[micronutrient] = food_details[micronutrient] * (quantity / 100.0)
    
    lipid_total = actual_amounts.get(micronutrient_list[4], 0.0)
    aa_total = actual_amounts.get(micronutrient_list[3], 0.0)
    
    for micronutrient, amount in actual_amounts.items():
        micronutrient_index = micronutrient_list.index(micronutrient)
        if micronutrient_index in proplipids:
            micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * lipid_total
        elif micronutrient_index in propaa:
            micronutrient_totals[micronutrient] += (food_details[micronutrient] / 100.0) * aa_total
        else:
            micronutrient_totals[micronutrient] += amount
    
    messagebox.showinfo("Info", f"Duplicated {quantity}g of {food_name}")
    update_added_foods_list()


def search_foods(event):
    search_term = search_var.get()
    food_menu['values'] = d.search_food(search_term)


def export_data():
    file_path = filedialog.asksaveasfilename(defaultextension=".tsv", filetypes=[("TSV files", "*.tsv")])
    if not file_path:
        return

    data_to_export = [{'micronutrient': k, 'total_amount': v} for k, v in micronutrient_totals.items()]
    headers = ['micronutrient', 'total_amount']
    write_tsv(file_path, data_to_export, headers)
    messagebox.showinfo("Info", f"Data exported to {file_path}")


def wipe_data():
    if messagebox.askyesno("Confirm Wipe", "Are you sure you want to wipe all data? Unsaved data will be lost."):
        global micronutrient_totals, added_foods
        micronutrient_totals = {micronutrient: 0.0 for micronutrient in micronutrient_list}
        added_foods = []
        update_added_foods_list()
        food_var.set('')
        quantity_var.set('')


URL_MAP = {
    "https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker": "https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker",
    "https://www.crea.gov.it/alimenti-e-nutrizione": "https://www.crea.gov.it/alimenti-e-nutrizione",
    "https://www.alimentinutrizione.it": "https://www.alimentinutrizione.it"
}

def open_link(event):
    widget = event.widget
    index = widget.index(tk.CURRENT)
    clicked_text = widget.get(f"{index} linestart", f"{index} lineend")
    url = URL_MAP.get(clicked_text.strip())
    if url:
        webbrowser.open_new(url)

def show_info():
    info_window = tk.Toplevel(root)
    info_window.title("Program Info")
    info_window.iconbitmap('logo.ico')
    
    text_widget = tk.Text(info_window, wrap="word", padx=10, pady=10, width=50, height=10)
    text_widget.pack(expand=True, fill='both')
    
    text_widget.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
    text_widget.tag_configure("link", foreground="blue", underline=True)
    text_widget.tag_bind("link", "<Button-1>", open_link)
    
    text_widget.insert("1.0", "MacroMicro-ITA-Tracker\n", "bold")
    text_widget.insert("end", "Version: 1.0\nMaintainer: Fabbrini Marco\nContact: fabbrinimarco.mf@gmail.com\n\nFor usage instructions, visit:\n")
    text_widget.insert("end", "https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker\n", "link")
    text_widget.insert("end", "\nFood tables have been obtained from CREA, Centro di ricerca Alimenti e Nutrizione, original source web pages:\n")
    text_widget.insert("end", "https://www.crea.gov.it/alimenti-e-nutrizione\n", "link")
    text_widget.insert("end", "https://www.alimentinutrizione.it", "link")
    
    text_widget.config(state=tk.DISABLED)
    
    close_button = ttk.Button(info_window, text="Close", command=info_window.destroy)
    close_button.pack(pady=10)
    
    info_window.geometry("800x380")
    info_window.transient(root)
    info_window.grab_set()
    root.wait_window(info_window)


def open_github():
    webbrowser.open_new("https://github.com/FabbriniMarco/MacroMicro-ITA-Tracker")


# Tk/tb
current_theme = "sandstone"
root = tb.Window(themename=current_theme)
root.title("MacroMicro-ITA-Tracker")
root.geometry("900x900")
root.iconbitmap('logo.ico')

food_var = tk.StringVar()
quantity_var = tk.StringVar()
search_var = tk.StringVar()

current_language = tk.StringVar(value="Italian")
blank_table = load_blank_table()
micronutrient_list = [row['nutrients'] for row in blank_table]
micronutrient_totals = {micronutrient: 0.0 for micronutrient in micronutrient_list}
added_foods = []
proplipids = range(37, 59)
propaa = range(60, 77)

main_frame = tb.Frame(root)
main_frame.pack(expand=True, fill='both')

tb.Label(main_frame, text="Select Language:").pack(pady=5)
language_menu = tb.Combobox(main_frame, textvariable=current_language, values=["Italian", "English"], state="readonly", bootstyle = "dark", width = 6)
language_menu.pack(pady=5)
language_menu.bind('<<ComboboxSelected>>', switch_language)

tb.Label(main_frame, text="Search Food:").pack(pady=5)
search_entry = tb.Entry(main_frame, textvariable=search_var, width=50)
search_entry.pack(pady=5)
search_entry.bind('<KeyRelease>', search_foods)

sorted_food_names = sorted(d.get_food_list())
tb.Label(main_frame, text="Select Food:").pack(pady=5)
food_menu = tb.Combobox(main_frame, textvariable=food_var, values=sorted_food_names, width=50, state="readonly", bootstyle = "primary")
food_menu.pack(pady=5)

tb.Label(main_frame, text="Enter Quantity (grams):").pack(pady=5)
quantity_entry = tb.Entry(main_frame, textvariable=quantity_var, width=50)
quantity_entry.pack(pady=5)

add_button = tb.Button(main_frame, text="Add Food", command=add_food)
add_button.pack(pady=10)

added_foods_container = tb.Frame(main_frame)
added_foods_container.pack(fill='both', pady=10, expand=True)
tb.Label(added_foods_container, text="Added Foods:").pack(pady=5)
canvas = tk.Canvas(added_foods_container, height=60)
scrollbar = tb.Scrollbar(added_foods_container, orient="vertical", command=canvas.yview)
scrollable_frame = tb.Frame(canvas)
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
added_foods_frame = scrollable_frame
buffer_frame = tb.Frame(scrollable_frame, height=60)
buffer_frame.pack()

export_button = tb.Button(main_frame, text="Export Data", command=export_data)
export_button.pack(pady=10)

wipe_button = tb.Button(main_frame, text="Wipe Data", command=wipe_data, bootstyle='danger')
wipe_button.pack(pady=10)

button_frame = tb.Frame(main_frame)
button_frame.pack(pady=10)

info_button = tb.Button(button_frame, text="Info", command=show_info, bootstyle='secondary')
info_button.pack(side="left", padx=5)

website1_button = tb.Button(button_frame, text="Github", command=open_github, bootstyle='secondary')
website1_button.pack(side="left", padx=5)

root.resizable(width=False, height=True)
root.mainloop()
