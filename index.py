# file: gui.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

scores_file = "scores.txt"

def save_score(score):
    with open(scores_file, "a") as f:
        f.write(f"{score}\n")

def show_leaderboard():
    if not os.path.exists(scores_file):
        messagebox.showinfo("Bảng xếp hạng", "Chưa có điểm nào được lưu.")
        return
    with open(scores_file, "r") as f:
        scores = [int(s.strip()) for s in f.readlines() if s.strip().isdigit()]
    scores.sort(reverse=True)
    top_scores = "\n".join([f"{i+1}. {s}" for i, s in enumerate(scores[:5])])
    messagebox.showinfo("Bảng xếp hạng", f"Top điểm số:\n{top_scores}")

def start_game():
    subprocess.run(["python", "game.py"])

def main_menu():
    root = tk.Tk()
    root.title("Fruit Slash Game")
    root.geometry("400x400")

    tk.Label(root, text="Fruit Slice Game 🍉", font=("Helvetica", 20, "bold")).pack(pady=30)

    tk.Button(root, text="🎮 Bắt đầu chơi", font=("Helvetica", 14), width=20, command=start_game).pack(pady=10)
    tk.Button(root, text="📊 Bảng xếp hạng", font=("Helvetica", 14), width=20, command=show_leaderboard).pack(pady=10)
    tk.Button(root, text="❌ Thoát", font=("Helvetica", 14), width=20, command=root.quit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
