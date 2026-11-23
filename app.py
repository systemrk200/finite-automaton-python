import math
import tkinter as tk
from tkinter import ttk, messagebox

from automaton import FiniteAutomaton

BG = "#f7f5f2"
TEXT = "#2b2b2b"
EDGE_COLOR = "#9a93a8"
NODE_FILL = "#7c5cbf"
ACTIVE_FILL = "#e0a33e"
NODE_R = 24


class AutomatonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конечный автомат")
        self.geometry("1160x720")
        self.configure(bg=BG)

        self.automaton = None
        self.run_path = []
        self.run_step = 0
        self.animating = False

        self._build_ui()
        self._load_example()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=NODE_FILL)

        controls = tk.Frame(self, bg=BG, padx=16, pady=12, width=400)
        controls.pack(side="left", fill="y")
        controls.pack_propagate(False)

        def field(label):
            ttk.Label(controls, text=label, style="Header.TLabel").pack(anchor="w", pady=(6, 2))
            var = tk.StringVar()
            ttk.Entry(controls, textvariable=var, font=("Segoe UI", 11)).pack(fill="x")
            return var

        self.states_var = field("Состояния (через пробел):")
        self.alphabet_var = field("Алфавит (символы через пробел):")
        self.start_var = field("Начальное состояние:")
        self.finals_var = field("Финальные состояния:")

        ttk.Label(controls, text="Переходы (по одному на строку: откуда символ куда):", style="Header.TLabel").pack(anchor="w", pady=(6, 2))
        self.transitions_box = tk.Text(
            controls, height=8, font=("Consolas", 10), bg="white", fg=TEXT,
            relief="solid", bd=1, highlightthickness=0,
        )
        self.transitions_box.pack(fill="x")

        ttk.Button(controls, text="Построить автомат", command=self.build_automaton).pack(fill="x", pady=(10, 0))

        ttk.Label(controls, text="Входное слово:", style="Header.TLabel").pack(anchor="w", pady=(14, 2))
        self.word_var = tk.StringVar()
        word_entry = ttk.Entry(controls, textvariable=self.word_var, font=("Segoe UI", 11))
        word_entry.pack(fill="x")
        word_entry.bind("<Return>", lambda _: self.start_run())

        run_buttons = tk.Frame(controls, bg=BG)
        run_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(run_buttons, text="Проверить слово", command=self.start_run).pack(side="left")
        ttk.Button(run_buttons, text="Шаг", command=self.step_run).pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="Задайте автомат и нажмите «Построить автомат»")
        ttk.Label(controls, textvariable=self.status_var, wraplength=320, font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(12, 0))

        right = tk.Frame(self, bg=BG, padx=16, pady=12)
        right.pack(side="left", fill="both", expand=True)

        self.word_display = tk.Label(right, text="", bg=BG, fg=TEXT, font=("Consolas", 20, "bold"))
        self.word_display.pack(anchor="center", pady=(4, 4))

        self.graph = tk.Canvas(right, bg="white", highlightthickness=1, highlightbackground="#d9d4e3")
        self.graph.pack(fill="both", expand=True)

    def _load_example(self):
        self.states_var.set("q0 q1 q2")
        self.alphabet_var.set("0 1")
        self.start_var.set("q0")
        self.finals_var.set("q2")
        self.transitions_box.insert("1.0", "\n".join([
            "q0 0 q1",
            "q0 1 q0",
            "q1 0 q1",
            "q1 1 q2",
            "q2 0 q1",
            "q2 1 q0",
        ]))
        self.word_var.set("101")
        self.build_automaton()

    def _parse_automaton(self):
        transitions = []
        for line in self.transitions_box.get("1.0", "end").splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.replace(",", " ").split()
            if len(parts) != 3:
                raise ValueError(f"Строка «{line}» должна содержать три элемента: откуда, символ, куда")
            transitions.append(tuple(parts))
        return FiniteAutomaton(
            states=self.states_var.get().split(),
            alphabet=self.alphabet_var.get().split(),
            transitions=transitions,
            start_state=self.start_var.get().strip(),
            final_states=self.finals_var.get().split(),
        )

    def build_automaton(self):
        try:
            self.automaton = self._parse_automaton()
        except ValueError as error:
            messagebox.showerror("Ошибка в описании автомата", str(error))
            return
        self.animating = False
        self.run_path = []
        self.word_display.configure(text="")
        self.status_var.set(
            f"Автомат построен: состояний — {len(self.automaton.states)}, "
            f"переходов — {sum(len(t) for t in self.automaton.transitions.values())}"
        )
        self._draw(set())

    def start_run(self):
        if not self.automaton:
            self.build_automaton()
            if not self.automaton:
                return
        word = self.word_var.get().strip()
        try:
            self.run_path = self.automaton.run(word)
        except ValueError as error:
            messagebox.showerror("Ошибка во входном слове", str(error))
            return
        self.run_step = 0
        self.animating = True
        self._show_step()

    def step_run(self):
        if not self.run_path:
            self.start_run()
            return
        if self.run_step < len(self.run_path) - 1:
            self.run_step += 1
        self._show_step()

    def _show_step(self):
        if not self.animating:
            return
        word = self.word_var.get().strip()
        current = self.run_path[self.run_step]
        consumed = word[: self.run_step]
        rest = word[self.run_step :]
        self.word_display.configure(text=f"{consumed}‸{rest}")
        states = ", ".join(sorted(current)) if current else "∅"
        self.status_var.set(f"Шаг {self.run_step}/{len(word)}: текущие состояния — {states}")
        self._draw(current)

        if self.run_step == len(self.run_path) - 1:
            self.animating = False
            if len(self.run_path) == len(word) + 1 and current & self.automaton.final_states:
                self.status_var.set(f"✅ Слово «{word}» допускается автоматом")
            elif not current:
                self.status_var.set(f"❌ Слово «{word}» не допускается: автомат застрял на префиксе «{consumed}»")
            else:
                self.status_var.set(f"❌ Слово «{word}» не допускается: автомат остановился не в финальном состоянии")
        else:
            self.after(800, self._auto_step)

    def _auto_step(self):
        if self.animating and self.run_step < len(self.run_path) - 1:
            self.run_step += 1
            self._show_step()

    def _node_positions(self, count, width, height):
        cx, cy = width / 2, height / 2
        radius = max(80, min(width, height) / 2 - NODE_R - 40)
        return {
            name: (cx + radius * math.cos(2 * math.pi * i / count - math.pi / 2),
                   cy + radius * math.sin(2 * math.pi * i / count - math.pi / 2))
            for i, name in enumerate(self.automaton.states)
        }

    def _draw(self, active):
        self.graph.delete("all")
        self.graph.update_idletasks()
        width = max(self.graph.winfo_width(), 400)
        height = max(self.graph.winfo_height(), 300)

        positions = self._node_positions(len(self.automaton.states), width, height)
        labels = self.automaton.edge_labels()

        for (source, target), symbols in labels.items():
            caption = ", ".join(sorted(symbols))
            if source == target:
                self._draw_loop(positions[source], caption)
            else:
                curved = (target, source) in labels
                self._draw_arrow(positions[source], positions[target], caption, curved)

        start_x, start_y = positions[self.automaton.start_state]
        self.graph.create_line(
            start_x - NODE_R - 45, start_y, start_x - NODE_R - 4, start_y,
            fill=NODE_FILL, width=2, arrow=tk.LAST,
        )

        for name, (x, y) in positions.items():
            fill = ACTIVE_FILL if name in active else NODE_FILL
            self.graph.create_oval(x - NODE_R, y - NODE_R, x + NODE_R, y + NODE_R, fill=fill, outline="")
            if name in self.automaton.final_states:
                self.graph.create_oval(x - NODE_R + 4, y - NODE_R + 4, x + NODE_R - 4, y + NODE_R - 4, outline="white", width=2)
            self.graph.create_text(x, y, text=name, fill="white", font=("Segoe UI", 11, "bold"))

    def _draw_loop(self, pos, caption):
        x, y = pos
        self.graph.create_oval(x - 14, y - NODE_R - 30, x + 14, y - NODE_R + 2, outline=EDGE_COLOR, width=2)
        self.graph.create_line(x + 12, y - NODE_R - 2, x + 5, y - NODE_R + 5, fill=EDGE_COLOR, width=2, arrow=tk.LAST)
        self.graph.create_text(x, y - NODE_R - 38, text=caption, fill=TEXT, font=("Segoe UI", 10, "bold"))

    def _draw_arrow(self, start, end, caption, curved):
        x1, y1 = start
        x2, y2 = end
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        ux, uy = dx / dist, dy / dist
        sx, sy = x1 + ux * NODE_R, y1 + uy * NODE_R
        ex, ey = x2 - ux * NODE_R, y2 - uy * NODE_R
        if curved:
            mx, my = (sx + ex) / 2 - uy * 30, (sy + ey) / 2 + ux * 30
            self.graph.create_line(sx, sy, mx, my, ex, ey, fill=EDGE_COLOR, width=2, smooth=True, arrow=tk.LAST)
            lx, ly = mx - uy * 14, my + ux * 14
        else:
            self.graph.create_line(sx, sy, ex, ey, fill=EDGE_COLOR, width=2, arrow=tk.LAST)
            lx, ly = (sx + ex) / 2, (sy + ey) / 2 - 12
        self.graph.create_text(lx, ly, text=caption, fill=TEXT, font=("Segoe UI", 10, "bold"))


if __name__ == "__main__":
    AutomatonApp().mainloop()
