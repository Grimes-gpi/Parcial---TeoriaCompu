import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from logic import (
    Automaton,
    dfa_as_automaton,
    equations_to_regex,
    regex_text,
    subset_construction,
    verify_equivalence,
)


SAMPLE = {
    "version": 1,
    "tipo": "AFND",
    "estados": ["q0", "q1", "q2"],
    "alfabeto": ["a", "b"],
    "inicial": "q0",
    "finales": ["q2"],
    "transiciones": [
        {"desde": "q0", "simbolo": "a", "hacia": "q0"},
        {"desde": "q0", "simbolo": "a", "hacia": "q1"},
        {"desde": "q1", "simbolo": "b", "hacia": "q2"},
    ],
}


class Graph(ttk.Frame):
    """Lienzo sencillo de estados y transiciones."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.positions = {}
        self.node_positions = {}
        self._drag_state = None
        self._automaton = None
        self._labels = {}
        self.canvas = tk.Canvas(self, height=310, background="white", highlightthickness=1,
                                highlightbackground="#cbd5e1", **kwargs)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        vertical = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<Configure>", self._on_resize)

    def draw(self, automaton: Automaton | None, labels: dict[str, str] | None = None):
        canvas = self.canvas
        canvas.delete("all")
        self._automaton = automaton
        self._labels = labels or {}
        if not automaton:
            canvas.create_text(300, 130, text="Valide un autómata para ver el grafo", fill="#64748b")
            return
        labels = self._labels
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 650)
        height = max(canvas.winfo_height(), 300)
        states = automaton.states
        count = len(states)
        center_x, center_y = width / 2, height / 2
        radius_x = max(55, min(width * .28, width / 2 - 45))
        radius_y = max(45, min(height * .25, height / 2 - 35))
        coords = {}
        for index, state in enumerate(states):
            angle = (-1.5708 + index * 6.28318 / count) if count > 1 else 0
            default = (center_x + radius_x * __import__("math").cos(angle),
                       center_y + radius_y * __import__("math").sin(angle))
            coords[state] = self.positions.get(state, default)
        self.node_positions = coords
        groups: dict[tuple[str, str], list[str]] = {}
        for (origin, symbol), destinations in automaton.transitions.items():
            for destination in destinations:
                groups.setdefault((origin, destination), []).append(symbol)
        for (origin, destination), symbols in groups.items():
            x1, y1 = coords[origin]
            x2, y2 = coords[destination]
            title = ",".join(sorted(symbols))
            if origin == destination:
                canvas.create_line(x1 - 18, y1 - 17, x1 - 27, y1 - 54, x1 + 27, y1 - 54,
                                   x1 + 18, y1 - 17, fill="#475569", width=2,
                                   arrow=tk.LAST, smooth=True, splinesteps=20)
                canvas.create_text(x1, y1 - 58, text=title, fill="#0f172a")
            else:
                dx, dy = x2 - x1, y2 - y1
                length = max((dx * dx + dy * dy) ** .5, 1)
                ux, uy = dx / length, dy / length
                sx, sy = x1 + ux * 28, y1 + uy * 28
                ex, ey = x2 - ux * 31, y2 - uy * 31
                canvas.create_line(sx, sy, ex, ey, fill="#475569", width=2, arrow=tk.LAST,
                                   arrowshape=(10, 12, 4), smooth=True)
                canvas.create_text((sx + ex) / 2, (sy + ey) / 2 - 9, text=title, fill="#0f172a")
        for state, (x, y) in coords.items():
            display = labels.get(state, state)
            width_oval = max(27, 11 * len(display))
            if state in automaton.finals:
                canvas.create_oval(x - width_oval - 5, y - 24, x + width_oval + 5, y + 24,
                                   outline="#2563eb", width=2)
            canvas.create_oval(x - width_oval, y - 19, x + width_oval, y + 19,
                               outline="#0f172a", width=2, fill="#f8fafc")
            canvas.create_text(x, y, text=display, fill="#0f172a")
            if state == automaton.initial:
                canvas.create_line(x - width_oval - 38, y, x - width_oval - 2, y,
                                   fill="#0f172a", width=2, arrow=tk.LAST)
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_resize(self, event):
        if self._automaton and event.width > 100 and event.height > 100:
            self.draw(self._automaton, self._labels)

    def _start_drag(self, event):
        if not self._automaton:
            return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        for state, (sx, sy) in self.node_positions.items():
            if abs(x - sx) <= 40 and abs(y - sy) <= 30:
                self._drag_state = state
                return
        self._drag_state = None

    def _drag(self, event):
        if self._drag_state:
            self.positions[self._drag_state] = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            self.draw(self._automaton, self._labels)


class Simulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador gráfico de autómatas")
        self.geometry("1120x780")
        self.minsize(900, 650)
        self.configure(background="#f1f5f9")
        self.automaton: Automaton | None = None
        self.dfa: Automaton | None = None
        self.dfa_labels: dict[str, str] = {}
        self.regex = None
        self.conversion_trace = []
        self.trace_index = 0
        self._build_ui()
        self.input_text.insert("1.0", json.dumps(SAMPLE, ensure_ascii=False, indent=2))
        self._validate(show_message=False)
        self.after(250, self._refresh_graph_layout)

    def _refresh_graph_layout(self):
        if self.automaton:
            self.input_graph.draw(self.automaton)

    def _build_ui(self):
        header = ttk.Frame(self, padding=(16, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Simulador de autómatas", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(header, text="Conversión AFND → AFD · Ecuaciones → ER · Verificación acotada",
                  foreground="#475569").pack(anchor="w", pady=(3, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.editor_tab = ttk.Frame(self.tabs, padding=12)
        self.dfa_tab = ttk.Frame(self.tabs, padding=12)
        self.regex_tab = ttk.Frame(self.tabs, padding=12)
        self.verify_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.editor_tab, text="1. Autómata")
        self.tabs.add(self.dfa_tab, text="2. AFND → AFD")
        self.tabs.add(self.regex_tab, text="3. AF → ER")
        self.tabs.add(self.verify_tab, text="4. Verificador")
        self._build_editor()
        self._build_conversion()
        self._build_regex()
        self._build_verifier()

    def _build_editor(self):
        toolbar = ttk.Frame(self.editor_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Validar entrada", command=self._validate).pack(side="left")
        ttk.Button(toolbar, text="Abrir JSON…", command=self._open_json).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Guardar JSON…", command=self._save_json).pack(side="left")
        ttk.Button(toolbar, text="Cargar ejemplo", command=self._load_sample).pack(side="left", padx=6)
        self.status = ttk.Label(toolbar, text="", foreground="#166534")
        self.status.pack(side="left", padx=12)
        body = ttk.Panedwindow(self.editor_tab, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=2)
        ttk.Label(left, text="Modelo JSON (UTF-8)").pack(anchor="w")
        self.input_text = ScrolledText(left, wrap="none", font=("Consolas", 10), undo=True)
        self.input_text.pack(fill="both", expand=True, pady=(5, 0))
        ttk.Label(right, text="Grafo del autómata de entrada").pack(anchor="w", pady=(0, 5))
        self.input_graph = Graph(right)
        self.input_graph.pack(fill="both", expand=True)
        ttk.Label(self.editor_tab, text="Formato: estados, alfabeto, inicial, finales y transiciones. Use ε como etiqueta solo para una transición vacía.",
                  foreground="#475569", wraplength=1020).pack(anchor="w", pady=(8, 0))

    def _build_conversion(self):
        toolbar = ttk.Frame(self.dfa_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Convertir por subconjuntos", command=self._convert).pack(side="left")
        ttk.Button(toolbar, text="Ver ecuaciones de este AFD", command=self._send_dfa_to_regex).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Exportar AFD…", command=self._save_dfa_json).pack(side="left")
        body = ttk.Panedwindow(self.dfa_tab, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=1)
        body.add(right, weight=2)
        ttk.Label(left, text="Tabla de conversión").pack(anchor="w")
        self.table = ttk.Treeview(left, show="headings", height=10)
        self.table.pack(fill="x", pady=5)
        ttk.Label(left, text="Traza paso a paso").pack(anchor="w", pady=(12, 2))
        controls = ttk.Frame(left)
        controls.pack(fill="x")
        ttk.Button(controls, text="◀ Anterior", command=self._previous_step).pack(side="left")
        ttk.Button(controls, text="Siguiente ▶", command=self._next_step).pack(side="left", padx=6)
        self.step_label = ttk.Label(left, text="Sin conversión", wraplength=400, justify="left")
        self.step_label.pack(fill="x", anchor="w", pady=8)
        ttk.Label(right, text="Grafo del AFD").pack(anchor="w", pady=(0, 5))
        self.dfa_graph = Graph(right)
        self.dfa_graph.pack(fill="both", expand=True)

    def _build_regex(self):
        ttk.Button(self.regex_tab, text="Construir sistema y resolver con Arden", command=self._make_regex).pack(anchor="w")
        self.regex_result = ttk.Label(self.regex_tab, text="Expresión regular: (sin calcular)",
                                      font=("Segoe UI", 13, "bold"), wraplength=1000)
        self.regex_result.pack(anchor="w", pady=10)
        ttk.Label(self.regex_tab, text="Ecuaciones, sustituciones y simplificaciones").pack(anchor="w")
        self.equations = ScrolledText(self.regex_tab, wrap="word", font=("Consolas", 10), state="disabled")
        self.equations.pack(fill="both", expand=True, pady=(5, 0))

    def _build_verifier(self):
        controls = ttk.Frame(self.verify_tab)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Label(controls, text="Longitud máxima n (mínimo 6):").pack(side="left")
        self.max_length = tk.StringVar(value="6")
        ttk.Spinbox(controls, from_=6, to=30, width=7, textvariable=self.max_length).pack(side="left", padx=8)
        ttk.Button(controls, text="Verificar AFND, AFD y ER", command=self._verify).pack(side="left")
        self.verify_status = ttk.Label(self.verify_tab, text="Convierta el AFND y genere la ER antes de verificar.",
                                       wraplength=1000)
        self.verify_status.pack(anchor="w", pady=8)
        ttk.Label(self.verify_tab, text="Cadenas que producen resultados distintos").pack(anchor="w")
        self.mismatch_table = ttk.Treeview(self.verify_tab, columns=("word", "nfa", "dfa", "regex"), show="headings")
        for column, title in (("word", "Cadena"), ("nfa", "AFND"), ("dfa", "AFD"), ("regex", "ER")):
            self.mismatch_table.heading(column, text=title)
        self.mismatch_table.pack(fill="both", expand=True, pady=5)
        ttk.Label(self.verify_tab, text="La coincidencia es exhaustiva hasta n; no constituye por sí sola una prueba para longitudes ilimitadas.",
                  foreground="#475569", wraplength=1000).pack(anchor="w", pady=(4, 0))

    def _read_automaton(self, show_message=True):
        try:
            data = json.loads(self.input_text.get("1.0", "end-1c"))
            self.automaton = Automaton.from_dict(data, allow_epsilon=True)
            self.dfa = None
            self.regex = None
            self.dfa_graph.draw(None)
            self.status.configure(text="Entrada válida", foreground="#166534")
            labels = {state: state for state in self.automaton.states}
            self.input_graph.draw(self.automaton, labels)
            if show_message:
                messagebox.showinfo("Validación", "El autómata es válido.")
            return self.automaton
        except (json.JSONDecodeError, ValueError, TypeError) as error:
            self.automaton = None
            self.status.configure(text="Entrada inválida", foreground="#b91c1c")
            if show_message:
                messagebox.showerror("No se pudo validar", str(error))
            return None

    def _validate(self, show_message=True):
        self._read_automaton(show_message)

    def _load_sample(self):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", json.dumps(SAMPLE, ensure_ascii=False, indent=2))
        self._validate(show_message=False)

    def _open_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            Automaton.from_dict(json.loads(content), allow_epsilon=True)
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", content)
            self._validate(show_message=False)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Error al abrir", str(error))

    def _save_json(self):
        automaton = self._read_automaton(show_message=False)
        if not automaton:
            messagebox.showerror("No se pudo guardar", "Corrija el autómata antes de exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(automaton.to_dict(), file, ensure_ascii=False, indent=2)

    def _save_dfa_json(self):
        if not self.dfa:
            messagebox.showerror("Exportar AFD", "Convierta primero un AFND.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        data = self.dfa.to_dict()
        data["etiquetas_estados"] = self.dfa_labels
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def _convert(self):
        automaton = self._read_automaton(show_message=False)
        if not automaton:
            messagebox.showerror("Conversión", "Valide primero el autómata de entrada.")
            return
        self.dfa, self.conversion_trace = subset_construction(automaton)
        self.dfa_labels = getattr(self.dfa, "_subset_labels", {})
        self.trace_index = 0
        columns = ["estado", *self.dfa.alphabet, "marcas"]
        self.table.configure(columns=columns)
        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=100, anchor="center")
        self.table.delete(*self.table.get_children())
        for state in self.dfa.states:
            row = [self.dfa_labels[state]]
            row.extend(self.dfa_labels.get(next(iter(self.dfa.transitions.get((state, symbol), {state}))), "∅")
                       for symbol in self.dfa.alphabet)
            marks = ("→ " if state == self.dfa.initial else "") + ("◎" if state in self.dfa.finals else "")
            row.append(marks)
            self.table.insert("", "end", values=row)
        self.dfa_graph.draw(self.dfa, self.dfa_labels)
        self._show_step()
        self.tabs.select(self.dfa_tab)

    def _show_step(self):
        if not self.conversion_trace:
            self.step_label.configure(text="Sin pasos disponibles.")
            return
        self.trace_index = max(0, min(self.trace_index, len(self.conversion_trace) - 1))
        step = self.conversion_trace[self.trace_index]
        text = (f"Paso {self.trace_index + 1} de {len(self.conversion_trace)}\n"
                f"Procesar {step['origen']} con {step['simbolo']}\n"
                f"{step['detalle']}\nUnión: {step['union']}\n"
                f"Destino: {step['destino']}" + (" (nuevo)" if step["nuevo"] else ""))
        self.step_label.configure(text=text)

    def _next_step(self):
        if self.conversion_trace:
            self.trace_index += 1
            self._show_step()

    def _previous_step(self):
        if self.conversion_trace:
            self.trace_index -= 1
            self._show_step()

    def _send_dfa_to_regex(self):
        if not self.dfa:
            self._convert()
        if self.dfa:
            self.tabs.select(self.regex_tab)
            self._make_regex(use_dfa=True)

    def _make_regex(self, use_dfa=False):
        if use_dfa and self.dfa:
            source = dfa_as_automaton(self.dfa)
        else:
            source = self._read_automaton(show_message=False)
        if not source:
            messagebox.showerror("Expresión regular", "Valide el autómata antes de resolver las ecuaciones.")
            return
        self.regex, steps = equations_to_regex(source)
        self.regex_result.configure(text="Expresión regular: " + regex_text(self.regex))
        self.equations.configure(state="normal")
        self.equations.delete("1.0", "end")
        self.equations.insert("1.0", "\n\n".join(steps))
        self.equations.configure(state="disabled")
        self.tabs.select(self.regex_tab)

    def _verify(self):
        if not self.automaton:
            self._read_automaton(show_message=False)
        if not self.dfa:
            try:
                if self.automaton:
                    self.dfa, self.conversion_trace = subset_construction(self.automaton)
                    self.dfa_labels = getattr(self.dfa, "_subset_labels", {})
            except Exception as error:
                messagebox.showerror("Verificador", str(error))
                return
        if self.regex is None and self.automaton:
            self.regex, _ = equations_to_regex(self.automaton)
        if not (self.automaton and self.dfa and self.regex is not None):
            messagebox.showerror("Verificador", "No están disponibles los tres modelos.")
            return
        try:
            n = int(self.max_length.get())
            count, mismatches, limit = verify_equivalence(self.automaton, self.dfa, self.regex, n)
            self.mismatch_table.delete(*self.mismatch_table.get_children())
            for item in mismatches:
                self.mismatch_table.insert("", "end", values=(item["cadena"], item["afnd"], item["afd"], item["er"]))
            if mismatches:
                self.verify_status.configure(text=f"Diferencias encontradas en {len(mismatches)} de {count:,} cadenas revisadas.", foreground="#b91c1c")
            else:
                self.verify_status.configure(text=f"Coincidencia en todas las {count:,} cadenas de longitud 0..{n}. Límite de trabajo: {limit:,}.", foreground="#166534")
        except (ValueError, OverflowError) as error:
            messagebox.showwarning("Verificador", str(error))


if __name__ == "__main__":
    Simulator().mainloop()
