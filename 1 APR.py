import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

class AdvancedBookAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Pro - Book Analyzer v2.0")
        self.root.geometry("700x550")
        self.root.configure(bg="#f0f2f5")
        
        self.df = None
        self.file_path = ""
        self.analysis_results = {}

        # --- Sidebar / Control Panel ---
        self.sidebar = tk.Frame(root, width=200, bg="#2c3e50", height=550)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="CONTROLS", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=20)

        self.btn_load = tk.Button(self.sidebar, text="Load Excel", command=self.browse_file, width=15)
        self.btn_load.pack(pady=10)

        self.sheet_combo = ttk.Combobox(self.sidebar, state="readonly", width=13)
        self.sheet_combo.pack(pady=10)

        # Advanced Toggle: Clean Data (removes rows with empty prices/ratings)
        self.clean_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.sidebar, text="Auto-Clean Data", variable=self.clean_var, 
                       bg="#2c3e50", fg="white", selectcolor="#2c3e50").pack(pady=10)

        self.btn_run = tk.Button(self.sidebar, text="Run Analysis", command=self.analyze_data, 
                                 bg="#27ae60", fg="white", width=15, state="disabled")
        self.btn_run.pack(pady=20)

        self.btn_export = tk.Button(self.sidebar, text="Download Report", command=self.export_to_excel, 
                                    bg="#2980b9", fg="white", width=15, state="disabled")
        self.btn_export.pack(pady=10)

        # --- Main Display Area ---
        self.main_area = tk.Frame(root, bg="white", padx=20, pady=20)
        self.main_area.pack(side="right", fill="both", expand=True)

        self.lbl_title = tk.Label(self.main_area, text="Analysis Dashboard", font=("Arial", 18, "bold"), bg="white")
        self.lbl_title.pack(anchor="w")

        self.txt_display = tk.Text(self.main_area, font=("Consolas", 11), bd=0, bg="#f9f9f9")
        self.txt_display.pack(fill="both", expand=True, pady=20)

    def browse_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_selected:
            self.file_path = file_selected
            xl = pd.ExcelFile(file_selected)
            self.sheet_combo['values'] = xl.sheet_names
            self.sheet_combo.current(0)
            self.btn_run.config(state="normal")
            self.log(f"File loaded: {file_selected}")

    def analyze_data(self):
        try:
            sheet = self.sheet_combo.get()
            self.df = pd.read_excel(self.file_path, sheet_name=sheet)

            if self.clean_var.get():
                self.df = self.df.dropna(subset=['User Rating', 'Price', 'Reviews'])

            # Calculation Logic
            max_rating = self.df['User Rating'].max()
            best_books = self.df[self.df['User Rating'] == max_rating]['Name'].tolist()
            
            self.df['Revenue'] = self.df['Price'] * self.df['Reviews']
            top_earner = self.df.loc[self.df['Revenue'].idxmax()]
            
            pop_year = self.df.groupby('Year')['Reviews'].sum().idxmax()

            # Store for Export
            self.analysis_results = {
                "Highest Rating": max_rating,
                "Top Earner": top_earner['Name'],
                "Total Revenue": f"${top_earner['Revenue']:,.2f}",
                "Most Popular Year": pop_year
            }

            # Update Display
            output = f"SHEET: {sheet}\n{'='*40}\n"
            output += f"1. HIGHEST RATING: {max_rating}\n   Books: {', '.join(best_books[:2])}...\n\n"
            output += f"2. MOST REVENUE: {top_earner['Name']}\n   Amount: ${top_earner['Revenue']:,.2f}\n\n"
            output += f"3. MOST POPULAR YEAR: {pop_year}\n"
            
            self.txt_display.delete('1.0', tk.END)
            self.txt_display.insert(tk.END, output)
            self.btn_export.config(state="normal")

        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))

    def export_to_excel(self):
        if not self.analysis_results: return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            # Convert dictionary to DataFrame for easy export
            report_df = pd.DataFrame([self.analysis_results])
            report_df.to_excel(save_path, index=False)
            messagebox.showinfo("Success", f"Report saved to:\n{save_path}")

    def log(self, message):
        self.txt_display.insert(tk.END, f"> {message}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedBookAnalyzer(root)
    root.mainloop()