import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

class BookAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Sheet Analyzer")
        self.root.geometry("600x500")
        self.file_path = ""
        self.xl = None

        # --- UI Elements ---
        # 1. File Selection
        self.btn_file = tk.Button(root, text="Step 1: Select Excel File", command=self.load_file)
        self.btn_file.pack(pady=10)

        # 2. Sheet Selection Dropdown
        self.lbl_sheet = tk.Label(root, text="Step 2: Choose Sheet")
        self.lbl_sheet.pack()
        self.sheet_combo = ttk.Combobox(root, state="readonly", width=40)
        self.sheet_combo.pack(pady=5)

        # 3. Run Analysis Button
        self.btn_run = tk.Button(root, text="Step 3: Run Analysis", command=self.analyze, bg="#2196F3", fg="white")
        self.btn_run.pack(pady=10)

        # 4. Results Output
        self.output_text = scrolledtext.ScrolledText(root, width=70, height=15, font=("Consolas", 10))
        self.output_text.pack(pady=10, padx=10)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if self.file_path:
            try:
                # Load the Excel file object to get sheet names
                self.xl = pd.ExcelFile(self.file_path)
                self.sheet_combo['values'] = self.xl.sheet_names
                self.sheet_combo.current(0) # Set default to first sheet
                messagebox.showinfo("Success", f"Found {len(self.xl.sheet_names)} sheets.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def analyze(self):
        selected_sheet = self.sheet_combo.get()
        if not self.file_path or not selected_sheet:
            messagebox.showwarning("Warning", "Please select a file and a sheet first!")
            return

        try:
            # Read only the selected sheet
            df = pd.read_excel(self.file_path, sheet_name=selected_sheet)
            
            # Basic validation to ensure required columns exist
            required = ['Name', 'Author', 'User Rating', 'Reviews', 'Price']
            if not all(col in df.columns for col in required):
                messagebox.showerror("Column Error", f"Sheet must contain: {required}")
                return

            # --- Calculations ---
            # 1. Highest Rating
            max_rating = df['User Rating'].max()
            top_rated = df[df['User Rating'] == max_rating]['Name'].unique()

            # 2. Most Sales (Price * Reviews)
            df['Sales'] = df['Price'] * df['Reviews']
            author_sales = df.groupby('Author')['Sales'].sum()
            top_author = author_sales.idxmax()
            sales_val = author_sales.max()

            # 3. Top 5 Popularity
            top_5 = df.sort_values(by='Reviews', ascending=False).head(5)

            # --- Display ---
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"ANALYSIS FOR SHEET: {selected_sheet}\n")
            self.output_text.insert(tk.END, "="*50 + "\n\n")
            
            self.output_text.insert(tk.END, f"1. HIGHEST RATING ({max_rating}):\n")
            for name in top_rated[:5]: # Show top 5 if many
                self.output_text.insert(tk.END, f"   - {name}\n")

            self.output_text.insert(tk.END, f"\n2. TOP SELLING AUTHOR:\n")
            self.output_text.insert(tk.END, f"   - {top_author} (Est. Revenue: ${sales_val:,.2f})\n")

            self.output_text.insert(tk.END, f"\n3. TOP 5 MOST POPULAR (By Reviews):\n")
            for _, row in top_5.iterrows():
                self.output_text.insert(tk.END, f"   - [{row['Reviews']} reviews] {row['Name']}\n")

        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = BookAnalyzerGUI(root)
    root.mainloop()