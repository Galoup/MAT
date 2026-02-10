#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Outil FDV by HARDCORE — v0.6 🔥
- Standard library only
- Données min-cost fixes (lookup) pour 4 races
- Rendu ASCII box-drawing aligné (largeur affichée, ANSI-safe)
"""
from __future__ import annotations

import argparse
import ctypes
import os
import re
import shutil
import sys
import unicodedata
from typing import Dict, List, Sequence, Tuple

TITLE = "🔥 Outil FDV by HARDCORE — v0.6 🔥"

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_CYAN = "\033[36m"
ANSI_BLUE = "\033[34m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_MAGENTA = "\033[35m"
ANSI_RED = "\033[31m"

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

POP_THRESHOLDS = [
    200000,
    300000,
    400000,
    500000,
    750000,
    1000000,
    1200000,
    3000000,
    5000000,
    7000000,
    9000000,
    11000000,
    13000000,
    26000000,
    56000000,
    112000000,
    224000000,
    448000000,
]

RACES = {
    "humains": {
        "display": "Humains",
        "color": ANSI_BLUE,
        "aliases": ["1", "humains", "humain", "human"],
        "buildings": [
            ("🏘️", "Secteur résidentiel"),
            ("🌿", "Ferme biosphérique"),
            ("🎓", "Académie des sciences (T1→T2)"),
            ("🧠", "Centre de neurocalibrage (T2→T3)"),
            ("🥫", "Silo alimentaire"),
            ("🏢", "Gratte-ciel"),
            ("🧬", "Laboratoire de biotechnologie"),
        ],
        "levels": [
            [22, 20, 0, 0, 0, 0, 0],
            [23, 22, 0, 0, 0, 0, 0],
            [23, 24, 0, 0, 0, 0, 0],
            [24, 25, 0, 0, 0, 0, 0],
            [27, 26, 0, 0, 0, 0, 0],
            [27, 28, 0, 0, 0, 0, 0],
            [43, 43, 4, 0, 2, 0, 3],
            [46, 44, 7, 0, 4, 2, 3],
            [46, 46, 8, 0, 4, 4, 4],
            [48, 47, 8, 0, 8, 4, 5],
            [49, 48, 8, 0, 9, 4, 6],
            [50, 49, 8, 0, 9, 4, 6],
            [61, 59, 11, 7, 17, 11, 14],
            [63, 60, 12, 8, 25, 16, 16],
            [66, 62, 13, 9, 26, 19, 19],
            [69, 65, 13, 9, 31, 19, 20],
            [71, 66, 14, 10, 38, 27, 23],
            [74, 68, 15, 10, 42, 29, 27],
        ],
    },
    "rocktal": {
        "display": "Rock’tal",
        "color": ANSI_GREEN,
        "aliases": ["2", "rocktal", "rock'tal", "rock’tal", "rock"],
        "buildings": [
            ("🪨", "Enclave stoïque"),
            ("💎", "Culture du cristal"),
            ("🧿", "Forge runique (T1→T2)"),
            ("🗿", "Orictorium (T2→T3)"),
            ("🧱", "Monolithe"),
            ("🧪", "Centre de recherche sur les minéraux"),
        ],
        "levels": [
            [21, 21, 0, 0, 0, 0],
            [23, 23, 0, 0, 0, 0],
            [24, 25, 0, 0, 0, 0],
            [25, 26, 0, 0, 0, 0],
            [27, 27, 0, 0, 0, 0],
            [28, 29, 0, 0, 0, 0],
            [43, 44, 5, 0, 0, 0],
            [45, 46, 7, 0, 1, 0],
            [47, 48, 8, 0, 1, 0],
            [48, 50, 8, 0, 2, 0],
            [50, 51, 8, 0, 2, 0],
            [51, 52, 8, 0, 2, 0],
            [62, 64, 10, 8, 6, 2],
            [64, 66, 12, 9, 7, 2],
            [67, 69, 14, 9, 8, 3],
            [70, 72, 14, 10, 9, 3],
            [72, 75, 15, 11, 10, 4],
            [75, 78, 16, 11, 10, 5],
        ],
    },
    "mecas": {
        "display": "Mécas",
        "color": ANSI_YELLOW,
        "aliases": ["3", "mecas", "mécas", "mecas", "mecha"],
        "buildings": [
            ("🏭", "Chaîne de production"),
            ("⚗️", "Usine de fusion de cellules"),
            ("📡", "Réseau d’actualisation (T1→T2)"),
            ("🧮", "Centre d’informatique quantique (T2→T3)"),
            ("💾", "Chaîne de production de micropuces"),
            ("🦾", "Centre d’assemblage automatisé"),
        ],
        "levels": [
            [17, 20, 0, 0, 0, 0],
            [19, 21, 0, 0, 0, 0],
            [20, 23, 0, 0, 0, 0],
            [21, 24, 0, 0, 0, 0],
            [23, 26, 0, 0, 0, 0],
            [24, 28, 0, 0, 0, 0],
            [41, 49, 3, 0, 0, 1],
            [43, 50, 5, 0, 1, 2],
            [44, 52, 6, 0, 2, 2],
            [45, 53, 7, 0, 2, 2],
            [46, 54, 7, 0, 4, 4],
            [47, 55, 7, 0, 4, 5],
            [59, 69, 10, 6, 12, 11],
            [61, 71, 11, 7, 16, 13],
            [64, 74, 11, 8, 21, 16],
            [67, 77, 12, 8, 25, 18],
            [69, 80, 13, 9, 25, 21],
            [72, 83, 14, 9, 30, 22],
        ],
    },
    "kaelesh": {
        "display": "Kaelesh",
        "color": ANSI_MAGENTA,
        "aliases": ["4", "kaelesh", "kae"],
        "buildings": [
            ("🛖", "Refugium"),
            ("⚛️", "Condensateur d’antimatière"),
            ("🧿", "Salles de réalisation (T1→T2)"),
            ("🌌", "Forum de la transcendance (T2→T3)"),
            ("🧲", "Convecteur d’antimatière"),
            ("🪺", "Accélérateur par chrysalide"),
            ("🔮", "Modulateur psionique"),
        ],
        "levels": [
            [20, 20, 0, 0, 0, 0, 0],
            [21, 22, 0, 0, 0, 0, 0],
            [23, 23, 0, 0, 0, 0, 0],
            [24, 24, 0, 0, 0, 0, 0],
            [25, 26, 0, 0, 0, 0, 0],
            [27, 27, 0, 0, 0, 0, 0],
            [43, 45, 3, 0, 0, 1, 0],
            [44, 46, 6, 0, 0, 1, 0],
            [46, 48, 6, 0, 2, 3, 2],
            [47, 49, 7, 0, 2, 3, 2],
            [48, 50, 7, 0, 3, 4, 2],
            [49, 51, 7, 0, 3, 4, 2],
            [60, 62, 10, 6, 13, 18, 6],
            [62, 64, 11, 7, 15, 18, 7],
            [65, 67, 11, 8, 15, 21, 7],
            [67, 69, 12, 8, 19, 30, 9],
            [69, 71, 13, 9, 19, 34, 11],
            [72, 74, 13, 9, 22, 40, 11],
        ],
    },
}

ALIAS_TO_RACE = {alias.lower(): key for key, cfg in RACES.items() for alias in cfg["aliases"]}


def setup_console() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if os.name == "nt":
        try:
            kernel32 = ctypes.windll.kernel32
            h_out = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
                kernel32.SetConsoleMode(h_out, mode.value | 0x0004)
        except Exception:
            pass


def format_int(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def level_label_from_slot(slot: int) -> str:
    tier = (slot - 1) // 6 + 1
    sub = (slot - 1) % 6 + 1
    return f"{tier}.{sub}"


def slot_from_input(value: str) -> int:
    s = value.strip().lower()
    if s in {"q", "quit", "exit"}:
        raise KeyboardInterrupt
    if re.fullmatch(r"\d+", s):
        slot = int(s)
        if 1 <= slot <= 18:
            return slot
        raise ValueError("Le slot doit être entre 1 et 18")
    m = re.fullmatch(r"([1-3])\.([1-6])", s)
    if m:
        return (int(m.group(1)) - 1) * 6 + int(m.group(2))
    raise ValueError("Format invalide. Utilise 1..18 ou 1.1..3.6")


def normalize_race(value: str) -> str:
    key = value.strip().lower()
    if key in ALIAS_TO_RACE:
        return ALIAS_TO_RACE[key]
    raise ValueError("Race invalide (1..4 ou nom)")


def required_levels(race_key: str, slot: int) -> List[int]:
    return RACES[race_key]["levels"][slot - 1]


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def display_width(s: str) -> int:
    plain = strip_ansi(s)
    w = 0
    for ch in plain:
        if unicodedata.combining(ch):
            continue
        if unicodedata.east_asian_width(ch) in {"W", "F"}:
            w += 2
        else:
            w += 1
    return w


def pad_right(s: str, width: int) -> str:
    d = width - display_width(s)
    if d > 0:
        return s + (" " * d)
    return s


def pad_left(s: str, width: int) -> str:
    d = width - display_width(s)
    if d > 0:
        return (" " * d) + s
    return s


def build_box_table(headers: Sequence[str], rows: Sequence[Sequence[str]], aligns: Sequence[str] | None = None) -> str:
    if not rows:
        rows = []
    n = len(headers)
    if aligns is None:
        aligns = ["left"] * n
    widths = [display_width(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], display_width(str(c)))

    def fmt_row(cells: Sequence[str]) -> str:
        out = []
        for i, c in enumerate(cells):
            txt = str(c)
            out.append(pad_left(txt, widths[i]) if aligns[i] == "right" else pad_right(txt, widths[i]))
        return "│ " + " │ ".join(out) + " │"

    top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"

    lines = [top, fmt_row(headers), mid]
    for r in rows:
        lines.append(fmt_row(r))
    lines.append(bot)

    # Vérif: toutes les lignes ont exactement la même largeur affichée
    expected = display_width(lines[0])
    normalized = []
    for line in lines:
        if display_width(line) != expected:
            line = pad_right(line, expected)
        normalized.append(line)
    return "\n".join(normalized)


def colored_race_name(race_key: str) -> str:
    cfg = RACES[race_key]
    return f"{cfg['color']}{cfg['display']}{ANSI_RESET}"


def render_header() -> str:
    inside = f" {ANSI_BOLD}{ANSI_CYAN}{TITLE}{ANSI_RESET} "
    width = max(52, display_width(strip_ansi(inside)))
    top = "╔" + "═" * (width + 2) + "╗"
    mid = "║ " + pad_right(inside, width) + " ║"
    bot = "╚" + "═" * (width + 2) + "╝"
    tip = f"{ANSI_DIM}Astuce: tape q pour quitter.{ANSI_RESET}"
    return "\n".join([top, mid, bot, tip])


def render_min_levels(race_key: str, slot: int) -> str:
    cfg = RACES[race_key]
    req = required_levels(race_key, slot)
    pop_req = POP_THRESHOLDS[slot - 1]

    title_line = (
        f"Race: {colored_race_name(race_key)}  |  Slot: {ANSI_BOLD}{slot}{ANSI_RESET} "
        f"({level_label_from_slot(slot)})  |  Palier population: {ANSI_BOLD}{format_int(pop_req)}{ANSI_RESET}"
    )

    rows = []
    for (icon, name), lvl in zip(cfg["buildings"], req):
        rows.append([icon, name, str(lvl)])

    table = build_box_table(
        headers=["Icône", "Bâtiment", "Niveau min"],
        rows=rows,
        aligns=["left", "left", "right"],
    )
    return f"{title_line}\n{table}"


def compute_delta(req: Sequence[int], cur: Sequence[int]) -> List[int]:
    return [max(0, r - c) for r, c in zip(req, cur)]


def render_delta_table(race_key: str, slot: int, current: Sequence[int]) -> str:
    cfg = RACES[race_key]
    req = required_levels(race_key, slot)
    delta = compute_delta(req, current)

    rows = []
    for (icon, name), c, r, d in zip(cfg["buildings"], current, req, delta):
        rows.append([icon, name, str(c), str(r), str(d)])

    table = build_box_table(
        ["Icône", "Bâtiment", "Actuel", "Requis", "Manque"],
        rows,
        aligns=["left", "left", "right", "right", "right"],
    )

    prio = sorted(
        [(name, d) for (_, name), d in zip(cfg["buildings"], delta) if d > 0],
        key=lambda x: (-x[1], x[0]),
    )
    lines = [f"{ANSI_BOLD}Comparaison DELTA{ANSI_RESET}", table, "Priorité (plus gros manque d’abord):"]
    if not prio:
        lines.append("✅ Aucun manque, objectif atteint.")
    else:
        for i, (name, d) in enumerate(prio, 1):
            lines.append(f"{i:>2}. {name} (+{d})")
    return "\n".join(lines)


def render_full_level_block(race_key: str, tier: int) -> str:
    cfg = RACES[race_key]
    start = (tier - 1) * 6
    slots = list(range(start + 1, start + 7))
    labels = [f"{tier}.{i}" for i in range(1, 7)]

    width = shutil.get_terminal_size((120, 30)).columns
    estimated = 12 + 28 + 7 * 8

    if width >= estimated:
        headers = ["Icône", "Bâtiment"] + labels
        rows = []
        for bidx, (icon, name) in enumerate(cfg["buildings"]):
            vals = [str(cfg["levels"][s - 1][bidx]) for s in slots]
            rows.append([icon, name] + vals)
        lines = [
            f"{ANSI_BOLD}Tableau complet {tier}.x — {colored_race_name(race_key)}{ANSI_RESET}",
            "Paliers pop: " + " | ".join(f"{lab}:{format_int(POP_THRESHOLDS[s-1])}" for lab, s in zip(labels, slots)),
            build_box_table(headers, rows, aligns=["left", "left"] + ["right"] * 6),
        ]
        return "\n".join(lines)

    # Vue verticale stable si terminal étroit
    rows = []
    for i, s in enumerate(slots):
        rows.append([labels[i], format_int(POP_THRESHOLDS[s - 1])])
    head = build_box_table(["Slot", "Palier population"], rows, ["left", "right"])

    lines = [f"{ANSI_BOLD}Tableau complet {tier}.x — vue compacte (terminal étroit){ANSI_RESET}", head]
    for i, s in enumerate(slots):
        req = cfg["levels"][s - 1]
        r_rows = []
        for (icon, name), lv in zip(cfg["buildings"], req):
            r_rows.append([icon, name, str(lv)])
        lines.append(f"\n{ANSI_BOLD}Slot {labels[i]}{ANSI_RESET}")
        lines.append(build_box_table(["Icône", "Bâtiment", "Niv"], r_rows, ["left", "left", "right"]))
    return "\n".join(lines)


def ask(prompt: str) -> str:
    v = input(prompt).strip()
    if v.lower() in {"q", "quit", "exit"}:
        raise KeyboardInterrupt
    return v


def interactive_flow() -> int:
    print(render_header())
    print("Choix race: 1) Humains  2) Rock’tal  3) Mécas  4) Kaelesh")
    race_key = normalize_race(ask("Race (1..4 ou texte): "))
    slot = slot_from_input(ask("Slot cible (1..18 ou 1.1..3.6): "))

    print()
    print(render_min_levels(race_key, slot))

    compare = ask("\nComparer avec mes niveaux actuels ? (o/N): ").lower()
    if compare in {"o", "oui", "y", "yes"}:
        cfg = RACES[race_key]
        current = []
        print("Entre tes niveaux actuels:")
        for _, name in cfg["buildings"]:
            while True:
                try:
                    x = ask(f" - {name}: ")
                    val = int(x)
                    if val < 0:
                        raise ValueError
                    current.append(val)
                    break
                except ValueError:
                    print("Valeur invalide, entier >= 0 attendu.")
        print()
        print(render_delta_table(race_key, slot, current))

    full = ask("\nVoir un niveau complet ? (1 / 2 / 3 / non): ").lower()
    if full in {"1", "2", "3"}:
        print()
        print(render_full_level_block(race_key, int(full)))

    return 0


def parse_current_arg(raw: str, n: int) -> List[int]:
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) != n:
        raise ValueError(f"--current doit contenir {n} valeurs séparées par des virgules")
    out = []
    for p in parts:
        out.append(int(p))
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Outil FDV by HARDCORE — v0.6")
    p.add_argument("--race", help="Race: humains|rocktal|mecas|kaelesh ou 1..4")
    p.add_argument("--slot", help="Slot cible 1..18 ou 1.1..3.6")
    p.add_argument("--delta", action="store_true", help="Afficher tableau delta")
    p.add_argument("--current", default="", help="Niveaux actuels CSV: ex 10,12,3,0,4,2")
    p.add_argument("--full-level", choices=["1", "2", "3"], help="Affiche le tableau complet 1.x/2.x/3.x")
    return p


def main() -> int:
    setup_console()
    parser = build_parser()
    args = parser.parse_args()

    try:
        if len(sys.argv) == 1:
            return interactive_flow()

        if not args.race or not args.slot:
            parser.error("En mode CLI, --race et --slot sont obligatoires.")

        race_key = normalize_race(args.race)
        slot = slot_from_input(args.slot)

        print(render_header())
        print()
        print(render_min_levels(race_key, slot))

        if args.delta:
            req_n = len(RACES[race_key]["buildings"])
            current = parse_current_arg(args.current, req_n)
            print()
            print(render_delta_table(race_key, slot, current))

        if args.full_level:
            print()
            print(render_full_level_block(race_key, int(args.full_level)))

        return 0
    except KeyboardInterrupt:
        print("\n👋 Fermeture de l’outil.")
        return 0
    except Exception as exc:
        print(f"{ANSI_RED}❌ Erreur: {exc}{ANSI_RESET}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
