import math
import ezdxf
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Attempt to import shapely for true outline extraction
try:
    from shapely.geometry import LineString
    from shapely.ops import unary_union, polygonize
    _shapely_ok = True
except ImportError:
    _shapely_ok = False

#############################
# Geometry and Processing Functions
#############################

def compute_updated_drawing(L, W):
    # Compute core dimensions
    A = L
    B = W + 9
    C = W + 12
    D = W + 13
    E = (B - 5) / math.pi
    G = W
    H = G + 1
    I = E + 2
    S = 1.5
    Mid1 = B / 2 + 2
    Mid2 = G / 2
    V_GAP = 3

    # Leg length and vertical height for group2
    F = math.hypot(B / 2, E)
    height_G = math.sqrt(max(F**2 - (G / 2)**2, 0))

    # Sheet dimensions and centering
    sheet_W, sheet_L = 48, 120
    sheet_cx = sheet_W / 2

    # Text summary for UI
    calc_text = (
        f"A (Length)            = {A}\n"
        f"B (Width + 9)         = {B}\n"
        f"C (Width +12)         = {C}\n"
        f"D (Width +13)         = {D}\n"
        f"E ((B–5)/π)           = {E:.3f}\n"
        f"F (leg length)        = √[(B/2)²+E²] = {F:.3f}\n"
        f"G (Width)             = {G}\n"
        f"H (G+1)               = {H}\n"
        f"I (E+2)               = {I:.3f}\n"
        f"height_G (from F & G) = {height_G:.3f}\n"
    )

    # Define group1 segments
    group1 = [
        [(0, 0), (2, 0)], [(2, 0), (Mid1, E)], [(Mid1, E), (D - 2, 0)], [(D - 2, 0), (D, 0)],
        [(D, 0), (D, L)], [(D - 2, L), (D, L)], [(D - 2, L), (Mid1, L - E)], [(Mid1, L - E), (2, L)],
        [(2, L), (0, L)], [(0, L), (0, 0)],
    ]
    x = float(0.5)
    # Define group2 base segments
    group2 = [
        [(x, 0), (x, x)],
        [(0,x),(x,x)],
        [(0, x), (0, S)], 
        [(0, S), (x, S)], 
        # [(0, S), (S, S)], 
         [(G - x, S), (G, S)], 
         [(G, S), (G, x)], 
         [(G, x), (G-x, x)],
         [(G-x, x), (G-x, 0)],
         
    ]

    # Rectangle builder
    def make_rect(p1, p2, h):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        Lseg = math.hypot(dx, dy)
        if Lseg == 0: return []
        ux, uy = -dy / Lseg, dx / Lseg
        ox, oy = ux * h, uy * h
        return [(p1[0], p1[1]), (p2[0], p2[1]), (p2[0] + ox, p2[1] + oy), (p1[0] + ox, p1[1] + oy)]

    rects2 = [
        make_rect((x, S), (Mid2, height_G), S - 1),
        make_rect((Mid2, height_G), (G - x, S), S - 1),
        make_rect((x, -S + 1.5), (G - x, -S + 1.5), S - 1.5), 
    ]

    # helpers
    def shift(segs, dx, dy): return [[(x + dx, y + dy) for x, y in seg] for seg in segs]
    def rotate180(segs, center):
        cx, cy = center
        return [[(2 * cx - x, 2 * cy - y) for x, y in seg] for seg in segs]

    # positions
    y2 = 5
    y1 = y2 + height_G + V_GAP
    y2r = y1 + L + V_GAP

    # initial shifts
    g2 = shift(group2, sheet_cx - Mid2, y2)
    r2 = shift(rects2, sheet_cx - Mid2, y2)
    g1 = shift(group1, sheet_cx - D / 2, y1)

    # rotation + shift
    rot_center = (sheet_cx, y2 + height_G / 2)
    g2r = shift(rotate180(g2, rot_center), 0, y2r - y2)
    r2r = shift(rotate180(r2, rot_center), 0, y2r - y2)

    return {
        "sheet": {"W": sheet_W, "L": sheet_L},
        "group1": {"segs": g1},
        "group2": {"segs": g2, "rects": r2},
        "group2_rot": {"segs": g2r, "rects": r2r},
        "calc_text": calc_text
    }

#############################
# Outline Extraction Utility
#############################

def uniq_segments(all_segs):
    seen = {}
    for p1, p2 in all_segs:
        key = tuple(sorted((tuple(p1), tuple(p2))))
        seen[key] = (p1, p2)
    return list(seen.values())

def get_outline_segments(segments):
    """
    Returns only the outermost outline from a set of segments.
    Uses shapely if available, otherwise exact dedupe.
    """
    if _shapely_ok:
        lines = [LineString(seg) for seg in segments]
        merged = unary_union(lines)
        polys = polygonize(merged)
        outline = []
        for poly in polys:
            coords = list(poly.exterior.coords)
            outline += [(coords[i], coords[i+1]) for i in range(len(coords)-1)]
        return outline
    else:
        return uniq_segments(segments)

#############################
# DXF Saving Function
#############################

def save_dxf(drawing_data, filename="output.dxf"):
    doc = ezdxf.new()
    msp = doc.modelspace()

    sw, sh = drawing_data["sheet"]["W"], drawing_data["sheet"]["L"]
    border = [(0,0), (sw,0), (sw,sh), (0,sh), (0,0)]

    segments = []
    segments += list(zip(border, border[1:]))
    segments += drawing_data["group1"]["segs"]
    segments += drawing_data["group2"]["segs"]
    segments += drawing_data["group2_rot"]["segs"]
    # only keep the 3 non-base edges of each rect
    for grp in ("group2", "group2_rot"):
        for rect in drawing_data[grp]["rects"]:
            p1, p2, p3, p4 = rect
            segments += [(p2, p3), (p3, p4), (p4, p1)]

    clean = get_outline_segments(segments)
    for a, b in clean:
        msp.add_line(a, b)
    doc.saveas(filename)

#############################
# Matplotlib Preview
#############################

def plot_drawing(drawing_data, canvas=None):
    # if using an existing canvas, reuse its figure and axis
    if canvas:
        fig = canvas.figure
        ax = fig.axes[0] if fig.axes else fig.add_subplot(111, aspect='equal')
        ax.clear()
    else:
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111, aspect='equal')

    sw, sh = drawing_data["sheet"]["W"], drawing_data["sheet"]["L"]
    ax.plot([0, sw, sw, 0, 0], [0, 0, sh, sh, 0], linestyle='--', linewidth=1)

    segments = []
    segments += drawing_data["group1"]["segs"]
    segments += drawing_data["group2"]["segs"]
    segments += drawing_data["group2_rot"]["segs"]
    # only include 3 edges of rectangles (no base)
    for grp in ("group2", "group2_rot"):
        for rect in drawing_data[grp]["rects"]:
            p1, p2, p3, p4 = rect
            segments += [(p2, p3), (p3, p4), (p4, p1)]

    clean = get_outline_segments(segments)
    for a, b in clean:
        ax.plot([a[0], b[0]], [a[1], b[1]], color='black')

    ax.invert_yaxis()
    ax.grid(True)
    ax.set_title("Triangle Layout (outline + 3 rectangle edges)")

    if canvas:
        canvas.draw()
    else:
        return fig

#############################
# Tkinter Application
#############################

class DXFApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DXF Triangle Generator")
        self.geometry("900x700")
        self.drawing_data = None
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frm, text="Width (W):").grid(row=0, column=0)
        self.w_var = tk.StringVar(value="30")
        ttk.Entry(frm, textvariable=self.w_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(frm, text="Height (L):").grid(row=0, column=2)
        self.l_var = tk.StringVar(value="50")
        ttk.Entry(frm, textvariable=self.l_var, width=10).grid(row=0, column=3, padx=5)

        ttk.Button(frm, text="Generate", command=self.on_generate).grid(row=0, column=4, padx=10)
        ttk.Button(frm, text="Save as DXF", command=self.on_save).grid(row=0, column=5, padx=10)

        self.calc_text = tk.Text(self, height=10)
        self.calc_text.pack(fill=tk.X, padx=10)

        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_generate(self):
        try:
            W = float(self.w_var.get())
            L = float(self.l_var.get())
        except ValueError:
            messagebox.showerror("Error", "Enter numeric W & L.")
            return
        self.drawing_data = compute_updated_drawing(L, W)
        self.calc_text.delete(1.0, tk.END)
        self.calc_text.insert(tk.END, self.drawing_data["calc_text"])
        plot_drawing(self.drawing_data, canvas=self.canvas)

    def on_save(self):
        if not self.drawing_data:
            messagebox.showinfo("Info", "Generate first.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".dxf",
                                          filetypes=[("DXF", "*.dxf")])
        if fn:
            try:
                save_dxf(self.drawing_data, fn)
                messagebox.showinfo("Success", f"Saved to {fn}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save: {e}")

if __name__ == "__main__":
    DXFApp().mainloop()
