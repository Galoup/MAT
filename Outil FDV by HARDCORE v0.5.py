#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 Outil FDV by HARDCORE — v0.4 🔥
- Interactif : race + slot à débloquer
- Sortie : tableau ASCII bien aligné (même avec emojis) grâce à une colonne Icône séparée
- Noms FR corrigés (bâtiments clés du chemin "min-cost" slots élevés)
- 100% standard library
"""

from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ---------------------------
# Couleurs ANSI (ON)
# ---------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

def col(s: str, *codes: str) -> str:
    return "".join(codes) + s + C.RESET

# ---------------------------
# Largeur "visuelle" (évite les décalages Windows Terminal)
# On enlève les variation selectors (le fameux "️") + ZWJ.
# ---------------------------
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)

def strip_vs_zwj(s: str) -> str:
    # VS (FE00..FE0F) + ZWJ (200D) + skin tones (1F3FB..1F3FF)
    out = []
    for ch in s:
        o = ord(ch)
        if 0xFE00 <= o <= 0xFE0F:
            continue
        if o == 0x200D:
            continue
        if 0x1F3FB <= o <= 0x1F3FF:
            continue
        out.append(ch)
    return "".join(out)

def _char_width(ch: str) -> int:
    o = ord(ch)
    if unicodedata.combining(ch):
        return 0
    # Emojis/pictos -> 2 (heuristique robuste)
    if (0x1F300 <= o <= 0x1FAFF) or (0x2600 <= o <= 0x27BF):
        return 2
    eaw = unicodedata.east_asian_width(ch)
    if eaw in ("W", "F"):
        return 2
    return 1

def vwidth(s: str) -> int:
    s = strip_vs_zwj(strip_ansi(s))
    return sum(_char_width(ch) for ch in s)

def rpad(s: str, width: int) -> str:
    pad = width - vwidth(s)
    return s + (" " * max(0, pad))

def lpad(s: str, width: int) -> str:
    pad = width - vwidth(s)
    return (" " * max(0, pad)) + s

def fmt_int_fr(n: int) -> str:
    return f"{n:,}".replace(",", " ")

# ---------------------------
# Paliers population (slots 1..18)
# ---------------------------
POP_THRESHOLDS = [
    200_000, 300_000, 400_000, 500_000, 750_000, 1_000_000,
    1_200_000, 3_000_000, 5_000_000, 7_000_000, 9_000_000, 11_000_000,
    13_000_000, 26_000_000, 56_000_000, 112_000_000, 224_000_000, 448_000_000
]

@dataclass(frozen=True)
class BuildingLabel:
    icon: str
    name: str

@dataclass(frozen=True)
class RaceData:
    key: str
    name: str
    color: str
    order: List[str]                      # ordre affichage
    labels: Dict[str, BuildingLabel]      # key -> (icon, nom FR)
    slots: List[Dict[str, int]]           # 18 slots

def make_data() -> Dict[str, RaceData]:
    # --- HUMAIN ---
    hum_order = ["HAB","FOOD","T2","T3","SILO","SKY","BIO"]
    hum_labels = {
        "HAB":  BuildingLabel("🏠", "Secteur résidentiel"),
        "FOOD": BuildingLabel("🍽", "Ferme biosphérique"),
        "T2":   BuildingLabel("🎓", "Académie des sciences (T1→T2)"),
        "T3":   BuildingLabel("🧠", "Centre de neurocalibrage (T2→T3)"),
        "SILO": BuildingLabel("🥫", "Silo alimentaire"),
        "SKY":  BuildingLabel("🏙", "Gratte-ciel"),
        "BIO":  BuildingLabel("🧬", "Laboratoire biotech"),
    }
    hum_slots = [
        {"HAB":22, "FOOD":20},
        {"HAB":23, "FOOD":22},
        {"HAB":23, "FOOD":24},
        {"HAB":24, "FOOD":25},
        {"HAB":27, "FOOD":26},
        {"HAB":27, "FOOD":28},
        {"HAB":43, "FOOD":43, "T2":4, "SILO":2, "BIO":3},
        {"HAB":46, "FOOD":44, "T2":7, "SILO":4, "SKY":2, "BIO":3},
        {"HAB":46, "FOOD":46, "T2":8, "SILO":4, "SKY":4, "BIO":4},
        {"HAB":48, "FOOD":47, "T2":8, "SILO":8, "SKY":4, "BIO":5},
        {"HAB":49, "FOOD":48, "T2":8, "SILO":9, "SKY":4, "BIO":6},
        {"HAB":50, "FOOD":49, "T2":8, "SILO":9, "SKY":4, "BIO":6},
        {"HAB":61, "FOOD":59, "T2":11, "T3":7, "SILO":17, "SKY":11, "BIO":14},
        {"HAB":63, "FOOD":60, "T2":12, "T3":8, "SILO":25, "SKY":16, "BIO":16},
        {"HAB":66, "FOOD":62, "T2":13, "T3":9, "SILO":26, "SKY":19, "BIO":19},
        {"HAB":69, "FOOD":65, "T2":13, "T3":9, "SILO":31, "SKY":19, "BIO":20},
        {"HAB":71, "FOOD":66, "T2":14, "T3":10, "SILO":38, "SKY":27, "BIO":23},
        {"HAB":74, "FOOD":68, "T2":15, "T3":10, "SILO":42, "SKY":29, "BIO":27},
    ]

    # --- ROCK'TAL ---
    roc_order = ["HAB","FOOD","T2","T3","MEGA","MRC"]
    roc_labels = {
        "HAB":  BuildingLabel("🏠", "Enclave stoïque"),
        "FOOD": BuildingLabel("🍽", "Culture du cristal"),
        "T2":   BuildingLabel("🎓", "Centre technologique runique (T1→T2)"),
        "T3":   BuildingLabel("🧠", "Oriktorium (T2→T3)"),
        "MEGA": BuildingLabel("🗿", "Mégalithe"),
        "MRC":  BuildingLabel("⛏", "Centre de recherche minérale"),
    }
    roc_slots = [
        {"HAB":21, "FOOD":21},
        {"HAB":23, "FOOD":23},
        {"HAB":24, "FOOD":25},
        {"HAB":25, "FOOD":26},
        {"HAB":27, "FOOD":27},
        {"HAB":28, "FOOD":29},
        {"HAB":43, "FOOD":44, "T2":5},
        {"HAB":45, "FOOD":46, "T2":7, "MEGA":1},
        {"HAB":47, "FOOD":48, "T2":8, "MEGA":1},
        {"HAB":48, "FOOD":50, "T2":8, "MEGA":2},
        {"HAB":50, "FOOD":51, "T2":8, "MEGA":2},
        {"HAB":51, "FOOD":52, "T2":8, "MEGA":2},
        {"HAB":62, "FOOD":64, "T2":10, "T3":8, "MEGA":6, "MRC":2},
        {"HAB":64, "FOOD":66, "T2":12, "T3":9, "MEGA":7, "MRC":2},
        {"HAB":67, "FOOD":69, "T2":14, "T3":9, "MEGA":8, "MRC":3},
        {"HAB":70, "FOOD":72, "T2":14, "T3":10, "MEGA":9, "MRC":3},
        {"HAB":72, "FOOD":75, "T2":15, "T3":11, "MEGA":10, "MRC":4},
        {"HAB":75, "FOOD":78, "T2":16, "T3":11, "MEGA":10, "MRC":5},
    ]

    # --- MÉCAS ---
    mec_order = ["HAB","FOOD","T2","T3","CHIP","ASSEMBLY"]
    mec_labels = {
        "HAB":      BuildingLabel("🏠", "Chaîne de production"),
        "FOOD":     BuildingLabel("🍽", "Usine de fusion de cellules"),
        "T2":       BuildingLabel("🎓", "Réseau de mise à jour (T1→T2)"),
        "T3":       BuildingLabel("🧠", "Centre informatique quantique (T2→T3)"),
        "CHIP":     BuildingLabel("🧩", "Chaîne de production de micropuces"),
        "ASSEMBLY": BuildingLabel("🏭", "Centre d’assemblage automatisé"),
    }
    mec_slots = [
        {"HAB":17, "FOOD":20},
        {"HAB":19, "FOOD":21},
        {"HAB":20, "FOOD":23},
        {"HAB":21, "FOOD":24},
        {"HAB":23, "FOOD":26},
        {"HAB":24, "FOOD":28},
        {"HAB":41, "FOOD":49, "T2":3, "ASSEMBLY":1},
        {"HAB":43, "FOOD":50, "T2":5, "CHIP":1, "ASSEMBLY":2},
        {"HAB":44, "FOOD":52, "T2":6, "CHIP":2, "ASSEMBLY":2},
        {"HAB":45, "FOOD":53, "T2":7, "CHIP":2, "ASSEMBLY":2},
        {"HAB":46, "FOOD":54, "T2":7, "CHIP":4, "ASSEMBLY":4},
        {"HAB":47, "FOOD":55, "T2":7, "CHIP":4, "ASSEMBLY":5},
        {"HAB":59, "FOOD":69, "T2":10, "T3":6, "CHIP":12, "ASSEMBLY":11},
        {"HAB":61, "FOOD":71, "T2":11, "T3":7, "CHIP":16, "ASSEMBLY":13},
        {"HAB":64, "FOOD":74, "T2":11, "T3":8, "CHIP":21, "ASSEMBLY":16},
        {"HAB":67, "FOOD":77, "T2":12, "T3":8, "CHIP":25, "ASSEMBLY":18},
        {"HAB":69, "FOOD":80, "T2":13, "T3":9, "CHIP":25, "ASSEMBLY":21},
        {"HAB":72, "FOOD":83, "T2":14, "T3":9, "CHIP":30, "ASSEMBLY":22},
    ]

    # --- KAELESH ---
    kae_order = ["HAB","FOOD","T2","T3","CONV","CHRYS","PSI"]
    kae_labels = {
        "HAB":   BuildingLabel("🏠", "Refugium"),
        "FOOD":  BuildingLabel("🍽", "Condensateur d’antimatière"),
        "T2":    BuildingLabel("🎓", "Salles de réalisation (T1→T2)"),
        "T3":    BuildingLabel("🧠", "Forum de transcendance (T2→T3)"),
        "CONV":  BuildingLabel("⚛", "Convecteur d’antimatière"),
        "CHRYS": BuildingLabel("🐛", "Accélérateur chrysalide"),
        "PSI":   BuildingLabel("🌀", "Modulateur psionique"),
    }
    kae_slots = [
        {"HAB":20, "FOOD":20},
        {"HAB":21, "FOOD":22},
        {"HAB":23, "FOOD":23},
        {"HAB":24, "FOOD":24},
        {"HAB":25, "FOOD":26},
        {"HAB":27, "FOOD":27},
        {"HAB":43, "FOOD":45, "T2":3, "CHRYS":1},
        {"HAB":44, "FOOD":46, "T2":6, "CHRYS":1},
        {"HAB":46, "FOOD":48, "T2":6, "CONV":2, "CHRYS":3, "PSI":2},
        {"HAB":47, "FOOD":49, "T2":7, "CONV":2, "CHRYS":3, "PSI":2},
        {"HAB":48, "FOOD":50, "T2":7, "CONV":3, "CHRYS":4, "PSI":2},
        {"HAB":49, "FOOD":51, "T2":7, "CONV":3, "CHRYS":4, "PSI":2},
        {"HAB":60, "FOOD":62, "T2":10, "T3":6, "CONV":13, "CHRYS":18, "PSI":6},
        {"HAB":62, "FOOD":64, "T2":11, "T3":7, "CONV":15, "CHRYS":18, "PSI":7},
        {"HAB":65, "FOOD":67, "T2":11, "T3":8, "CONV":15, "CHRYS":21, "PSI":7},
        {"HAB":67, "FOOD":69, "T2":12, "T3":8, "CONV":19, "CHRYS":30, "PSI":9},
        {"HAB":69, "FOOD":71, "T2":13, "T3":9, "CONV":19, "CHRYS":34, "PSI":11},
        {"HAB":72, "FOOD":74, "T2":13, "T3":9, "CONV":22, "CHRYS":40, "PSI":11},
    ]

    races = {
        "humains": RaceData("humains", "Humains", C.BLUE, hum_order, hum_labels, hum_slots),
        "rocktal": RaceData("rocktal", "Rock’tal", C.GREEN, roc_order, roc_labels, roc_slots),
        "mecas":   RaceData("mecas", "Mécas", C.YELLOW, mec_order, mec_labels, mec_slots),
        "kaelesh": RaceData("kaelesh", "Kaelesh", C.MAGENTA, kae_order, kae_labels, kae_slots),
    }

    for k, rd in races.items():
        if len(rd.slots) != 18:
            raise ValueError(f"{k}: 18 slots attendus, trouvé {len(rd.slots)}")
    return races

RACES = make_data()

# ---------------------------
# Slot parsing
# ---------------------------
def parse_slot(s: str) -> Optional[Tuple[int, int, int]]:
    s = s.strip().lower()
    s = s.replace(",", ".").replace(":", ".").replace("-", ".")
    s = re.sub(r"\s+", "", s)

    if re.fullmatch(r"\d{1,2}", s):
        n = int(s)
        if 1 <= n <= 18:
            niveau = (n - 1) // 6 + 1
            idx = (n - 1) % 6 + 1
            return (n, niveau, idx)
        return None

    m = re.fullmatch(r"([123])\.(\d)", s)
    if m:
        niveau = int(m.group(1))
        idx = int(m.group(2))
        if 1 <= idx <= 6:
            n = (niveau - 1) * 6 + idx
            return (n, niveau, idx)

    return None

# ---------------------------
# UI helpers
# ---------------------------
def ask(prompt: str) -> str:
    return input(prompt).strip()

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    d = "O/n" if default else "o/N"
    while True:
        r = ask(f"{prompt} [{d}] : ").lower()
        if not r:
            return default
        if r in ("o", "oui", "y", "yes"):
            return True
        if r in ("n", "non", "no"):
            return False
        print("Réponse attendue: o / n")

def banner():
    t = "🔥  Outil FDV by HARDCORE  —  v0.4  🔥"
    line = "=" * max(52, vwidth(t) + 10)
    print(col(line, C.DIM))
    print(col(t.center(vwidth(line)), C.BOLD, C.WHITE))
    print(col(line, C.DIM))
    print(col("Astuce : tape 'q' pour quitter.\n", C.DIM))

def pick_race() -> str:
    options = [
        ("humains", "Humains", C.BLUE),
        ("rocktal", "Rock’tal", C.GREEN),
        ("mecas", "Mécas", C.YELLOW),
        ("kaelesh", "Kaelesh", C.MAGENTA),
    ]
    print(col("Choisis ta race :", C.BOLD))
    for i, (_, label, color) in enumerate(options, 1):
        print(f"  {i}) {col(label, C.BOLD, color)}")

    while True:
        r = ask("Tape 1/2/3/4 (ou le nom) : ").lower().replace("’", "'")
        if r in ("q", "quit", "exit"):
            raise SystemExit
        if r in ("1","2","3","4"):
            return options[int(r)-1][0]
        if r in RACES:
            return r
        if r in ("rock", "roctal", "r"):
            return "rocktal"
        if r in ("mecha", "meca", "m"):
            return "mecas"
        if r in ("kae", "k"):
            return "kaelesh"
        if r in ("humain", "h"):
            return "humains"
        print("Race invalide. Exemple: 2 ou rocktal")

def render_table(rows: List[Tuple[str, str, str]]) -> str:
    # rows = (icon, name, lvl)
    icon_w = max([vwidth("Icône")] + [vwidth(r[0]) for r in rows])
    name_w = max([vwidth("Bâtiment")] + [vwidth(r[1]) for r in rows])
    lvl_w  = max([vwidth("Niveau")] + [vwidth(r[2]) for r in rows])

    # respirations
    icon_w = max(icon_w, 2)
    name_w += 2
    lvl_w  += 2

    def hline(ch="-") -> str:
        return "+" + (ch * (icon_w + 2)) + "+" + (ch * (name_w + 2)) + "+" + (ch * (lvl_w + 2)) + "+"

    out = []
    out.append(hline("="))
    out.append("| " + rpad("Icône", icon_w) + " | " + rpad("Bâtiment", name_w) + " | " + rpad("Niveau", lvl_w) + " |")
    out.append(hline("="))
    for ic, nm, lv in rows:
        out.append("| " + rpad(ic, icon_w) + " | " + rpad(nm, name_w) + " | " + lpad(lv, lvl_w) + " |")
    out.append(hline("="))
    return "\n".join(out)

def print_result(race_key: str, slot_global: int, show_zeros: bool):
    rd = RACES[race_key]
    levels = rd.slots[slot_global - 1]
    pop = POP_THRESHOLDS[slot_global - 1]
    niveau = (slot_global - 1) // 6 + 1
    idx = (slot_global - 1) % 6 + 1

    print()
    print(col(f"{rd.name}  •  Slot {niveau}.{idx}  (#{slot_global})", C.BOLD, rd.color))
    print(col(f"Population minimum : {fmt_int_fr(pop)}", C.CYAN, C.BOLD))
    print()

    rows: List[Tuple[str, str, str]] = []
    for key in rd.order:
        val = levels.get(key, 0)
        if show_zeros or val > 0:
            lab = rd.labels[key]
            # On force le nettoyage VS/ZWJ sur l’icône (évite le '️' parasite)
            icon = strip_vs_zwj(lab.icon)
            name = lab.name
            rows.append((icon, name, str(val)))

    print(col("Niveaux minimum des bâtiments :", C.BOLD))
    print(render_table(rows))
    print(col("Note : paliers basés sur un chemin optimisé « min-cost » (objectif slots élevés).", C.DIM))

def main():
    banner()
    while True:
        try:
            race_key = pick_race()
        except SystemExit:
            return

        print()
        print(col("Quel slot veux-tu débloquer ?", C.BOLD))
        print("  Exemples: 1.3  |  2.6  |  3.2  |  ou un numéro global 1..18 (ex: 18)")
        slot = None
        while slot is None:
            s = ask("Slot : ")
            if s.lower() in ("q","quit","exit"):
                return
            slot = parse_slot(s)
            if slot is None:
                print("Format invalide. Essaye: 2.4 ou 10")

        slot_global, _, _ = slot
        show_zeros = ask_yes_no("Afficher aussi les bâtiments à 0 (non requis) ?", default=False)
        print_result(race_key, slot_global, show_zeros)

        if not ask_yes_no("\nTu veux tester un autre slot ?", default=True):
            break

    print(col("\nFin.", C.DIM))

if __name__ == "__main__":
    main()
