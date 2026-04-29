import pandas as pd
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os

class BookAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 書籍分析工具")
        self.root.geometry("900x700")
        self.df = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # 檔案選擇區域
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=20)
        
        tk.Button(file_frame, text="📁 選擇 Excel 檔案", 
                 command=self.load_file, bg="#4CAF50", fg="white",
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.file_label = tk.Label(file_frame, text="尚未選擇檔案", 
                                  font=("Arial", 10), fg="gray")
        self.file_label.pack(side=tk.LEFT, padx=20)
        
        # 分析按鈕
        tk.Button(file_frame, text="🚀 開始分析", command=self.analyze_data,
                 bg="#2196F3", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # 結果顯示區域
        self.result_text = scrolledtext.ScrolledText(self.root, height=35, width=100,
                                                   font=("Consolas", 10))
        self.result_text.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="選擇書籍資料 Excel 檔案",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.file_label.config(text=os.path.basename(file_path), fg="green")
            self.file_path = file_path
            messagebox.showinfo("成功", f"已載入檔案：\n{os.path.basename(file_path)}")
    
    def analyze_data(self):
        if not hasattr(self, 'file_path'):
            messagebox.showerror("錯誤", "請先選擇 Excel 檔案！")
            return
        
        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "📥 正在分析檔案...\n\n")
            self.root.update()
            
            # 讀取檔案 (自動偵測第一個工作表)
            self.df = pd.read_excel(self.file_path)
            
            # 分析結果
            result = self.perform_analysis()
            self.result_text.insert(tk.END, result)
            
            messagebox.showinfo("完成", "分析完成！結果已顯示在下方。")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"分析失敗：\n{str(e)}")
    
    def perform_analysis(self):
        result = f"📊 檔案資訊\n"
        result += f"總筆數：{len(self.df)} 筆\n"
        result += f"欄位：{', '.join(self.df.columns.tolist())}\n\n"
        
        # Top 5 暢銷作者 (最多書籍)
        result += "🏆 Top 5 暢銷作者 (依上榜書籍數量)\n"
        top_authors = self.df['Author'].value_counts().head(5)
        for i, (author, count) in enumerate(top_authors.items(), 1):
            result += f"{i}. {author}: {count} 本\n"
        result += "\n"
        
        # 各 Genre 數量
        result += "📚 各分類 (Genre) 書籍數量\n"
        genre_counts = self.df['Genre'].value_counts()
        for genre, count in genre_counts.items():
            result += f"{genre}: {count} 本\n"
        result += "\n"
        
        # Top 5 最多 Reviews 作者
        result += "💬 獲得最多總評論數的作者 Top 5\n"
        most_reviewed = self.df.groupby('Author')['Reviews'].sum().sort_values(ascending=False).head(5)
        for i, (author, reviews) in enumerate(most_reviewed.items(), 1):
            result += f"{i}. {author}: {reviews:,} 則評論\n"
        result += "\n"
        
        return result

if __name__ == "__main__":
    root = tk.Tk()
    app = BookAnalyzerGUI(root)
    root.mainloop()