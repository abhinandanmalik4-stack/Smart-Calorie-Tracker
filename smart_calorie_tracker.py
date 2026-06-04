import tkinter as tk
from tkinter import ttk
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsRegressor
import os

COLOR_BG = "#F0F4F8"
COLOR_CARD = "#FFFFFF"
COLOR_PRIMARY = "#2D5CFE"
COLOR_SECONDARY = "#47C860"
COLOR_ACCENT = "#FF4757"
COLOR_TEXT = "#1E293B"
COLOR_TEXT_LIGHT = "#64748B"

FONT_MAIN = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 24, "bold")

file_path = r"E:\Indian_Food_Nutrition_Processed.csv"

try:
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame({
            "Dish Name": ["Paneer Tikka","Butter Chicken","Roti","Naan","Dosa","Idli"],
            "Calories (kcal)": [250,450,80,150,150,60]
        })
except:
    df = pd.DataFrame({
        "Dish Name": ["Sample Food"],
        "Calories (kcal)": [100]
    })

df = df[["Dish Name", "Calories (kcal)"]].dropna()
df["Calories (kcal)"] = pd.to_numeric(df["Calories (kcal)"], errors="coerce")
df.dropna(inplace=True)
df["Dish Name"] = df["Dish Name"].astype(str).str.strip()

food_list = sorted(df["Dish Name"].unique().tolist())

le = LabelEncoder()
df["Food_Encoded"] = le.fit_transform(df["Dish Name"])

X = df[["Food_Encoded"]]
y = df["Calories (kcal)"]

model = KNeighborsRegressor(n_neighbors=3)
model.fit(X, y)

class AutoCompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self["values"] = self._completion_list
        self.bind("<KeyRelease>", self.handle_keyrelease)

    def handle_keyrelease(self, event):
        if event.keysym in ["Up", "Down", "Left", "Right", "Return", "Escape", "Tab"]:
            return

        typed = self.get().strip().lower()

        if typed == "":
            data = self._completion_list
        else:
            data = [item for item in self._completion_list if item.lower().startswith(typed)]

        self["values"] = data

        if typed and data:
            self.event_generate("<Down>")

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, color, command=None, width=150, height=40):
        super().__init__(parent, width=width, height=height,
                         bg=COLOR_CARD, highlightthickness=0, cursor="hand2")

        self.command = command
        self.color = color

        self.rect = self.create_polygon(
            5,5, width-5,5, width-5,height-5, 5,height-5,
            fill=color, outline=color, smooth=True
        )

        self.label = self.create_text(
            width/2, height/2, text=text,
            fill="white", font=FONT_BOLD
        )

        self.bind("<Button-1>", lambda e: self.command() if self.command else None)

meal_boxes = []
qty_boxes = []
cap_boxes = []

def calculate_total():
    total = 0
    output = []
    foods_lower = [x.lower() for x in df["Dish Name"].tolist()]

    for i in range(10):
        meal = meal_boxes[i].get().strip()
        qty = qty_boxes[i].get().strip()
        cap = cap_boxes[i].get().strip()

        if not meal:
            continue

        try:
            q = int(qty) if qty else 1
            c = float(cap) if cap else 100
        except:
            output.append(f"Meal {i+1}: Invalid input")
            continue

        if meal.lower() in foods_lower:
            real_name = df["Dish Name"].tolist()[foods_lower.index(meal.lower())]
            encoded = le.transform([real_name])[0]
            calories = model.predict([[encoded]])[0]

            final = (calories * c / 100) * q
            total += final

            output.append(f"{real_name}: {q} x {int(c)}g = {final:.1f} kcal")
        else:
            output.append(f"{meal}: Not found")

    total_val_label.config(text=f"{total:.1f}")
    result_text.set("\n".join(output) if output else "No meals added yet.")

def clear_all():
    for i in range(10):
        meal_boxes[i].set("")
        qty_boxes[i].set("1")
        cap_boxes[i].delete(0, tk.END)
        cap_boxes[i].insert(0, "100")

    total_val_label.config(text="0.0")
    result_text.set("No meals added yet.")

root = tk.Tk()
root.title("Calories Tracking")
root.geometry("1150x950")
root.configure(bg=COLOR_BG)

style = ttk.Style()
style.theme_use("clam")


header = tk.Frame(root, bg=COLOR_BG)
header.pack(fill="x", padx=40, pady=(30, 10))

tk.Label(header, text="Calories Tracking",
         font=FONT_TITLE, fg=COLOR_PRIMARY, bg=COLOR_BG).pack(side="left")

tk.Label(header, text="Track Your Daily Meals & Calories",
         font=("Segoe UI", 10), fg=COLOR_TEXT_LIGHT,
         bg=COLOR_BG).pack(side="left", padx=15, pady=(15, 0))


content = tk.Frame(root, bg=COLOR_BG)
content.pack(fill="both", expand=True, padx=40, pady=10)

input_card = tk.Frame(content, bg=COLOR_CARD, padx=25, pady=25,
                      highlightbackground="#DDE5ED", highlightthickness=1)
input_card.place(relx=0, rely=0, relwidth=0.65, relheight=0.88)

header_row = tk.Frame(input_card, bg=COLOR_CARD)
header_row.pack(fill="x", pady=(0, 10))

tk.Label(header_row, text="Meals", width=35, anchor="w",
         font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left", padx=(45,5))

tk.Label(header_row, text="Quantity", width=10,
         font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left", padx=10)

tk.Label(header_row, text="Capacity", width=10,
         font=FONT_BOLD, bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left", padx=5)


for i in range(10):
    row = tk.Frame(input_card, bg=COLOR_CARD)
    row.pack(fill="x", pady=6)

    tk.Label(row, text=str(i+1), width=3,
             bg="#EEF3FF", fg=COLOR_PRIMARY,
             font=FONT_BOLD).pack(side="left", padx=(0,12))

    meal = AutoCompleteCombobox(row, width=35, font=FONT_MAIN)
    meal.set_completion_list(food_list)
    meal.pack(side="left", padx=5)
    meal_boxes.append(meal)

    qty = ttk.Combobox(row, values=[str(x) for x in range(1,11)],
                       width=8, state="readonly", font=FONT_MAIN)
    qty.set("1")
    qty.pack(side="left", padx=10)
    qty_boxes.append(qty)

    cap = tk.Entry(row, width=10, justify="center", font=FONT_MAIN)
    cap.insert(0, "100")
    cap.pack(side="left", padx=5)
    cap_boxes.append(cap)

btn_row = tk.Frame(input_card, bg=COLOR_CARD)
btn_row.pack(pady=25)

ModernButton(btn_row, "Calculate Total", COLOR_PRIMARY,
             calculate_total).pack(side="left", padx=10)

ModernButton(btn_row, "Reset All", COLOR_ACCENT,
             clear_all, width=110).pack(side="left", padx=10)


dash = tk.Frame(content, bg=COLOR_CARD, padx=25, pady=25,
                highlightbackground="#DDE5ED", highlightthickness=1)
dash.place(relx=0.68, rely=0, relwidth=0.30, relheight=0.88)

tk.Label(dash, text="Daily Summary",
         font=FONT_BOLD, bg=COLOR_CARD,
         fg=COLOR_TEXT).pack(anchor="w")

box = tk.Frame(dash, bg="#F8FAFC", pady=20)
box.pack(fill="x", pady=20)

total_val_label = tk.Label(
    box, text="0.0",
    font=("Segoe UI", 32, "bold"),
    fg=COLOR_SECONDARY, bg="#F8FAFC"
)
total_val_label.pack()

tk.Label(box, text="TOTAL KCAL",
         font=FONT_BOLD, bg="#F8FAFC",
         fg=COLOR_TEXT_LIGHT).pack()

tk.Label(dash, text="Breakdown:",
         font=FONT_BOLD, bg=COLOR_CARD,
         fg=COLOR_TEXT).pack(anchor="w", pady=(10,5))

result_text = tk.StringVar(value="No meals added yet.")

tk.Label(
    dash,
    textvariable=result_text,
    justify="left",
    wraplength=250,
    bg=COLOR_CARD,
    fg=COLOR_TEXT_LIGHT,
    font=("Segoe UI", 10)
).pack(anchor="w")

root.mainloop()