#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Outil FDV by HARDCORE — v0.8 🔥
- Web UI locale moderne (single-file, offline, standard library only)
- API JSON pour calculs FDV
- Fallback CLI minimal via --cli
"""
from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import os
import re
import sys
import threading
import time
import unicodedata
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

TITLE = "🔥 Outil FDV by HARDCORE — v0.8 🔥"
VERSION = "0.8"

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
        "color": "#4f8cff",
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
        "color": "#3cd07b",
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
        "color": "#ffd24d",
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
        "color": "#d57dff",
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


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def slot_to_label(slot: int) -> str:
    return f"{(slot - 1) // 6 + 1}.{(slot - 1) % 6 + 1}"


def parse_slot(raw: str) -> int:
    txt = raw.strip().lower()
    if re.fullmatch(r"\d+", txt):
        v = int(txt)
        if 1 <= v <= 18:
            return v
    m = re.fullmatch(r"([1-3])\.([1-6])", txt)
    if m:
        return (int(m.group(1)) - 1) * 6 + int(m.group(2))
    raise ValueError("Slot invalide (1..18 ou 1.1..3.6)")


def normalize_race(raw: str) -> str:
    key = raw.strip().lower()
    if key in ALIAS_TO_RACE:
        return ALIAS_TO_RACE[key]
    if key in RACES:
        return key
    raise ValueError("Race invalide")


def self_test() -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if len(POP_THRESHOLDS) != 18:
        errors.append("POP_THRESHOLDS doit contenir 18 entrées")
    for race, cfg in RACES.items():
        levels = cfg["levels"]
        buildings = cfg["buildings"]
        if len(levels) != 18:
            errors.append(f"{race}: 18 slots attendus")
            continue
        for idx, row in enumerate(levels, start=1):
            if len(row) != len(buildings):
                errors.append(f"{race}: slot {idx} -> {len(buildings)} bâtiments attendus")
    return (len(errors) == 0, errors)


def required_levels(race: str, slot: int) -> List[int]:
    return list(RACES[race]["levels"][slot - 1])


def compute_priority(buildings: Sequence[Tuple[str, str]], missing: Sequence[int]) -> List[Dict[str, Any]]:
    items: List[Tuple[int, int, int]] = []
    for idx, (_, name) in enumerate(buildings):
        m = missing[idx]
        if m <= 0:
            continue
        lname = name.lower()
        if idx in (0, 1):
            cat = 0
        elif "t1→t2" in lname:
            cat = 1
        elif "t2→t3" in lname:
            cat = 2
        else:
            cat = 3
        items.append((cat, -m, idx))
    items.sort()
    return [
        {
            "index": idx,
            "building": buildings[idx][1],
            "missing": missing[idx],
            "category": cat,
        }
        for cat, _, idx in items
    ]


def compute_max_slot(race: str, current: Sequence[int]) -> int:
    max_slot = 0
    for s in range(1, 19):
        req = required_levels(race, s)
        if all((current[i] if i < len(current) else 0) >= req[i] for i in range(len(req))):
            max_slot = s
        else:
            break
    return max_slot


def build_slot_payload(race: str, slot: int) -> Dict[str, Any]:
    cfg = RACES[race]
    req = required_levels(race, slot)
    rows = []
    for i, ((emoji, b), lvl) in enumerate(zip(cfg["buildings"], req)):
        rows.append({"index": i, "emoji": emoji, "building": b, "required": lvl})
    return {
        "race": race,
        "display": cfg["display"],
        "slot": slot,
        "slot_label": slot_to_label(slot),
        "population": POP_THRESHOLDS[slot - 1],
        "requirements": rows,
    }


def build_delta_payload(race: str, slot: int, current: Sequence[int]) -> Dict[str, Any]:
    cfg = RACES[race]
    req = required_levels(race, slot)
    cur = [max(0, int(current[i] if i < len(current) else 0)) for i in range(len(req))]
    missing = [max(0, req[i] - cur[i]) for i in range(len(req))]
    reached = sum(1 for i in range(len(req)) if cur[i] >= req[i])
    progress = int(round((reached / len(req)) * 100)) if req else 0
    rows = []
    for i, (info, r, c, m) in enumerate(zip(cfg["buildings"], req, cur, missing)):
        rows.append(
            {
                "index": i,
                "emoji": info[0],
                "building": info[1],
                "required": r,
                "current": c,
                "missing": m,
                "ok": m == 0,
            }
        )
    maxslot = compute_max_slot(race, cur)
    next_slot = min(18, maxslot + 1) if maxslot < 18 else 18
    return {
        "race": race,
        "slot": slot,
        "slot_label": slot_to_label(slot),
        "population": POP_THRESHOLDS[slot - 1],
        "rows": rows,
        "priority": compute_priority(cfg["buildings"], missing),
        "progress": progress,
        "maxslot": maxslot,
        "nextslot": next_slot,
        "nextslot_label": slot_to_label(next_slot),
        "target_t25": build_slot_payload(race, 11),
    }


def build_full_payload(race: str, tier: int) -> Dict[str, Any]:
    if tier not in (1, 2, 3):
        raise ValueError("tier doit être 1..3")
    cfg = RACES[race]
    start = (tier - 1) * 6 + 1
    slots = list(range(start, start + 6))
    matrix = []
    for i, (emoji, bname) in enumerate(cfg["buildings"]):
        values = [cfg["levels"][s - 1][i] for s in slots]
        matrix.append({"index": i, "emoji": emoji, "building": bname, "values": values})
    return {
        "race": race,
        "tier": tier,
        "slots": [{"slot": s, "label": slot_to_label(s), "population": POP_THRESHOLDS[s - 1]} for s in slots],
        "matrix": matrix,
    }


def to_race_list() -> List[Dict[str, Any]]:
    out = []
    for key, cfg in RACES.items():
        out.append(
            {
                "key": key,
                "display": cfg["display"],
                "color": cfg["color"],
                "buildings": [{"emoji": e, "name": n} for e, n in cfg["buildings"]],
                "slots": [slot_to_label(i + 1) for i in range(18)],
            }
        )
    return out


HTML_PAGE = r"""
<!doctype html><html lang="fr"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>__TITLE__</title>
<style>
:root{--bg:#0f131a;--bg2:#141b25;--text:#eaf0ff;--muted:#93a3bf;--card:rgba(255,255,255,.05);--line:rgba(255,255,255,.12);--accent:#4f8cff;--ok:#3cd07b;--bad:#ff6d6d;--radius:14px;--pad:14px;--anim:.22s}
:root[data-theme="aurora"]{--bg:#0f1722;--bg2:#122032}
:root[data-theme="midnight"]{--bg:#0f131a;--bg2:#141b25}
:root[data-theme="paper"]{--bg:#f2f5fa;--bg2:#e9eef7;--text:#172031;--muted:#51627f;--card:rgba(255,255,255,.8);--line:rgba(20,33,56,.14)}
:root[data-density="compact"]{--pad:9px;--radius:10px}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:linear-gradient(140deg,var(--bg),var(--bg2));color:var(--text)}
.app{max-width:1200px;margin:0 auto;padding:18px}.glass{background:var(--card);backdrop-filter:blur(8px);border:1px solid var(--line);border-radius:var(--radius)}
.head{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:var(--pad);margin-bottom:12px}.title{font-weight:700}.sub{font-size:12px;color:var(--muted)}
.row{display:flex;gap:10px;flex-wrap:wrap}.btn{border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text);padding:8px 11px;border-radius:10px;cursor:pointer;transition:all var(--anim)}
.btn:hover{transform:translateY(-1px);border-color:var(--accent)} .btn.primary{background:color-mix(in srgb,var(--accent) 24%, transparent);border-color:color-mix(in srgb,var(--accent) 60%, white 10%)}
.tabs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;padding:8px}.tab{padding:10px;border-radius:10px;text-align:center;cursor:pointer;border:1px solid var(--line)}.tab.on{background:color-mix(in srgb,var(--accent) 16%, transparent);border-color:var(--accent)}
.panel{display:none;padding:var(--pad)}.panel.on{display:block;animation:in var(--anim) ease}@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.races{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.race{padding:10px;border:1px solid var(--line);border-radius:12px;cursor:pointer;transition:all var(--anim)}.race.on{outline:2px solid var(--accent);background:color-mix(in srgb,var(--accent) 16%, transparent)}
.stack{display:grid;gap:10px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.stat{padding:10px}.mono{font-family:ui-monospace,Consolas,monospace}
input,select,textarea{width:100%;padding:8px;border-radius:9px;border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text)}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}.ok{color:var(--ok)}.bad{color:var(--bad)}
.progress{height:10px;border-radius:999px;background:rgba(255,255,255,.11);overflow:hidden}.bar{height:100%;background:linear-gradient(90deg,var(--accent),#7bc5ff);width:0;transition:width .25s}
.palette{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;align-items:flex-start;justify-content:center;padding-top:10vh}.palette.on{display:flex}.palette .box{width:min(700px,92vw);padding:12px}
@media (max-width:900px){.races{grid-template-columns:repeat(2,minmax(0,1fr))}.grid2{grid-template-columns:1fr}.tabs{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media print{.noprint{display:none!important}body{background:white;color:#111}.glass{border:1px solid #ddd;background:#fff}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body>
<div class="app">
  <div class="head glass">
    <div><div class="title">🔥 Outil FDV by HARDCORE — v0.8 🔥</div><div class="sub">Offline · localhost · JSON API</div></div>
    <div class="row noprint"><button class="btn" id="cmd">Ctrl+K</button><button class="btn" id="share">Share link</button></div>
  </div>
  <div class="glass tabs noprint" id="tabs"></div>
  <div class="glass panel on" id="p-min"></div>
  <div class="glass panel" id="p-delta"></div>
  <div class="glass panel" id="p-full"></div>
  <div class="glass panel" id="p-auto"></div>
  <div class="glass panel" id="p-settings"></div>
</div>
<div class="palette" id="palette"><div class="box glass"><input id="k" placeholder="Commande: min, delta, full, auto, settings"/></div></div>
<script>
const TABS=[['min','Min requis'],['delta','DELTA'],['full','Tableau complet'],['auto','Auto-slot'],['settings','Settings']];
const state={race:'humains',slot:11,tier:2,races:[],current:[],emoji:true,anim:'normal',accentAuto:true,density:'comfortable',theme:'__DEFAULT_THEME__'};
const $=s=>document.querySelector(s);const esc=s=>String(s).replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
const save=()=>localStorage.setItem('fdv_v08',JSON.stringify({race:state.race,slot:state.slot,tier:state.tier,current:state.current,emoji:state.emoji,anim:state.anim,accentAuto:state.accentAuto,density:state.density,theme:state.theme}));
function load(){try{Object.assign(state,JSON.parse(localStorage.getItem('fdv_v08')||'{}'))}catch{};applyTheme();}
function applyTheme(){document.documentElement.dataset.theme=state.theme;document.documentElement.dataset.density=state.density;document.documentElement.style.setProperty('--anim',state.anim==='reduced'?'0s':'.22s');const race=state.races.find(r=>r.key===state.race);if(state.accentAuto && race)document.documentElement.style.setProperty('--accent',race.color);}
async function api(u,opt){const r=await fetch(u,opt);if(!r.ok)throw new Error(await r.text());return r.json()}
function slotLabel(s){return `${Math.floor((s-1)/6)+1}.${((s-1)%6)+1}`}
function normSlot(v){v=String(v).trim();if(/^\d+$/.test(v)){const n=+v;if(n>=1&&n<=18)return n}const m=v.match(/^([1-3])\.([1-6])$/);if(m)return (+m[1]-1)*6 + +m[2];return null}
function raceCards(){return `<div class="races">${state.races.map(r=>`<div class="race ${r.key===state.race?'on':''}" data-r="${r.key}"><div style="font-weight:600">${r.display}</div><div class="sub">${r.buildings.length} bâtiments</div></div>`).join('')}</div>`}
function setCurrentFromText(txt){const race=state.races.find(r=>r.key===state.race);if(!race)return;const map={};race.buildings.forEach((b,i)=>{map[b.name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')]=i;map[String(i+1)]=i;});
  txt.split(/\r?\n/).forEach(line=>{if(!line.trim())return;let [k,v]=line.split(/[:=;,\t]/);if(v===undefined)return;const kk=(k||'').trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');const idx=map[kk]??Object.keys(map).find(n=>kk.includes(n)&&!/^\d+$/.test(n))&&map[Object.keys(map).find(n=>kk.includes(n)&&!/^\d+$/.test(n))];const nv=Math.max(0,parseInt(v,10)||0);if(Number.isInteger(idx)){state.current[idx]=nv;}})
}
function importCsv(text){const rows=text.split(/\r?\n/).map(l=>l.split(','));if(!rows.length)return;for(const row of rows){if(row.length<2)continue;setCurrentFromText(`${row[0]}=${row[1]}`)} }
function renderTabs(active='min'){ $('#tabs').innerHTML=TABS.map(([k,l])=>`<div class="tab ${k===active?'on':''}" data-tab="${k}">${l}</div>`).join(''); document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on')); $(`#p-${active}`).classList.add('on'); document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>renderAll(t.dataset.tab)); }
function tableFilter(id,inputId){const q=$(inputId).value.toLowerCase();document.querySelectorAll(`#${id} tbody tr`).forEach(tr=>tr.style.display=tr.innerText.toLowerCase().includes(q)?'':'none');}
async function renderMin(){const d=await api(`/api/slot?r=${state.race}&slot=${state.slot}`);$('#p-min').innerHTML=`<div class="stack">
<div class="noprint">${raceCards()}</div><div class="grid2"><div class="stat glass"><div>Slot</div><div class="mono">${d.slot_label}</div><input id="slotRange" type="range" min="1" max="18" value="${state.slot}"><input id="slotText" value="${d.slot_label}"/></div><div class="stat glass"><div>Palier population</div><div class="mono">${d.population.toLocaleString('fr-FR')}</div></div></div>
<div class="row noprint"><input id="fmin" placeholder="Filtrer bâtiment..."/><button class="btn" id="copyMin">Copier</button><button class="btn" id="txtMin">Exporter .txt</button><button class="btn" id="jsonMin">Exporter JSON</button></div>
<div style="overflow:auto"><table id="tmin"><thead><tr><th>Bâtiment</th><th>Niveau min</th></tr></thead><tbody>${d.requirements.map(r=>`<tr><td>${state.emoji?r.emoji+' ':''}${esc(r.building)}</td><td class="mono">${r.required}</td></tr>`).join('')}</tbody></table></div></div>`;
 bindRaceCards();$('#slotRange').oninput=e=>{state.slot=+e.target.value;save();renderMin();};$('#slotText').onchange=e=>{const s=normSlot(e.target.value);if(s){state.slot=s;save();renderMin();}};$('#fmin').oninput=()=>tableFilter('tmin','#fmin');
 const txt=`[FDV] ${d.display} slot ${d.slot_label}\nPopulation: ${d.population}\n`+d.requirements.map(r=>`- ${r.building}: ${r.required}`).join('\n');$('#copyMin').onclick=()=>navigator.clipboard.writeText(txt);$('#txtMin').onclick=()=>download(`fdv_${state.race}_${d.slot_label}.txt`,txt);$('#jsonMin').onclick=()=>download(`fdv_${state.race}_${d.slot_label}.json`,JSON.stringify(d,null,2)); }
async function renderDelta(){const race=state.races.find(r=>r.key===state.race);if(state.current.length!==race.buildings.length)state.current=Array(race.buildings.length).fill(0);
 const d=await api('/api/delta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({race:state.race,slot:state.slot,current:state.current})});
 $('#p-delta').innerHTML=`<div class="stack"><div class="noprint">${raceCards()}</div><div class="grid2"><div class="glass stat"><div>Slot cible</div><input id="deltaSlot" value="${d.slot_label}"/><div class="progress" style="margin-top:10px"><div class="bar" style="width:${d.progress}%"></div></div><div class="sub">Progression ${d.progress}%</div></div>
 <div class="glass stat"><div>Top 3 suggestions</div>${d.priority.slice(0,3).map(x=>`<div class="mono">+${x.missing} ${esc(x.building)}</div>`).join('')||'<div class="sub">Rien à améliorer.</div>'}</div></div>
 <div class="glass stat"><div class="row"><input id="fdelta" placeholder="Filtrer..."/><button class="btn" id="exp">Mode Expé T2-5</button></div><div style="overflow:auto"><table id="tdelta"><thead><tr><th>Bâtiment</th><th>Actuel</th><th>Requis</th><th>Manque</th></tr></thead><tbody>${d.rows.map((r,i)=>`<tr><td>${state.emoji?r.emoji+' ':''}${esc(r.building)}</td><td><input data-i="${i}" class="cur" value="${r.current}"/></td><td class="mono">${r.required}</td><td class="mono ${r.ok?'ok':'bad'}">${r.missing}</td></tr>`).join('')}</tbody></table></div></div>
 <div class="glass stat"><div>Priorités</div><ol>${d.priority.map(p=>`<li>${esc(p.building)} <b class="mono">+${p.missing}</b></li>`).join('')||'<li>Tout est OK ✅</li>'}</ol></div>
 <div class="noprint row"><button class="btn" id="importText">Import texte</button><button class="btn" id="importCsv">Import CSV</button><button class="btn" id="saveProfile">Sauver profil</button></div></div>`;
 bindRaceCards();$('#deltaSlot').onchange=e=>{const s=normSlot(e.target.value);if(s){state.slot=s;save();renderDelta();}};document.querySelectorAll('.cur').forEach(inp=>inp.oninput=e=>{state.current[+e.target.dataset.i]=Math.max(0,parseInt(e.target.value||'0',10)||0);save();renderDelta();renderAuto();});
 $('#fdelta').oninput=()=>tableFilter('tdelta','#fdelta');$('#importText').onclick=()=>{const t=prompt('Coller lignes Nom=Valeur ou Nom:Valeur');if(t){setCurrentFromText(t);save();renderDelta();renderAuto();}};
 $('#importCsv').onclick=()=>{const t=prompt('Coller CSV (Nom, Valeur)');if(t){importCsv(t);save();renderDelta();renderAuto();}};
 $('#saveProfile').onclick=()=>{const name=prompt('Nom du profil ?','profil-'+Date.now());if(!name)return;const p=JSON.parse(localStorage.getItem('fdv_profiles')||'{}');p[name]={race:state.race,current:state.current};localStorage.setItem('fdv_profiles',JSON.stringify(p));alert('Profil sauvegardé');};
 $('#exp').onclick=async()=>{state.slot=11;save();alert('Objectif expérimental fixé sur T2-5 (slot 11).');renderDelta();}; }
async function renderFull(){const d=await api(`/api/full?r=${state.race}&tier=${state.tier}`);$('#p-full').innerHTML=`<div class="stack"><div class="row noprint"><select id="tierSel">${[1,2,3].map(t=>`<option ${t===state.tier?'selected':''}>${t}</option>`).join('')}</select><input id="ffull" placeholder="Filtrer"/></div><div style="overflow:auto"><table id="tfull"><thead><tr><th>Bâtiment</th>${d.slots.map(s=>`<th>${s.label}</th>`).join('')}</tr></thead><tbody>${d.matrix.map(r=>`<tr><td>${state.emoji?r.emoji+' ':''}${esc(r.building)}</td>${r.values.map(v=>`<td class="mono">${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div></div>`;
 $('#tierSel').onchange=e=>{state.tier=+e.target.value;save();renderFull();};$('#ffull').oninput=()=>tableFilter('tfull','#ffull'); }
async function renderAuto(){const race=state.races.find(r=>r.key===state.race);if(state.current.length!==race.buildings.length)state.current=Array(race.buildings.length).fill(0);const d=await api('/api/delta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({race:state.race,slot:18,current:state.current})});
 $('#p-auto').innerHTML=`<div class="stack"><div class="noprint">${raceCards()}</div><div class="grid2"><div class="glass stat"><div>Slot max atteignable</div><div class="mono">${slotLabel(d.maxslot||1)}</div></div><div class="glass stat"><div>Prochain slot conseillé</div><div class="mono">${d.nextslot_label}</div></div></div><div class="glass stat"><div>Delta auto vers ${d.nextslot_label}</div><ul>${(await api('/api/delta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({race:state.race,slot:d.nextslot,current:state.current})})).priority.slice(0,8).map(x=>`<li>${esc(x.building)} +${x.missing}</li>`).join('')||'<li>Aucun manque</li>'}</ul></div></div>`;
 bindRaceCards(); }
function renderSettings(){const prof=JSON.parse(localStorage.getItem('fdv_profiles')||'{}');$('#p-settings').innerHTML=`<div class="stack"><label><input type="checkbox" id="emoji" ${state.emoji?'checked':''}/> Emojis ON</label><label>Animations<select id="anim"><option value="normal" ${state.anim==='normal'?'selected':''}>normal</option><option value="reduced" ${state.anim==='reduced'?'selected':''}>reduced</option></select></label><label><input type="checkbox" id="accent" ${state.accentAuto?'checked':''}/> Accent auto selon race</label><label>Densité<select id="density"><option value="comfortable" ${state.density==='comfortable'?'selected':''}>confortable</option><option value="compact" ${state.density==='compact'?'selected':''}>compact</option></select></label><label>Thème<select id="theme"><option value="midnight" ${state.theme==='midnight'?'selected':''}>Midnight</option><option value="aurora" ${state.theme==='aurora'?'selected':''}>Aurora</option><option value="paper" ${state.theme==='paper'?'selected':''}>Paper</option></select></label><div><b>Profils</b>${Object.keys(prof).map(k=>`<div class="row"><button class="btn loadp" data-k="${k}">Charger ${esc(k)}</button><button class="btn delp" data-k="${k}">Suppr</button></div>`).join('')||'<div class="sub">Aucun profil</div>'}</div><div class="row"><button class="btn" onclick="window.print()">Imprimer</button></div></div>`;
 $('#emoji').onchange=e=>{state.emoji=e.target.checked;save();renderAll()};$('#anim').onchange=e=>{state.anim=e.target.value;applyTheme();save();};$('#accent').onchange=e=>{state.accentAuto=e.target.checked;applyTheme();save();};$('#density').onchange=e=>{state.density=e.target.value;applyTheme();save();};$('#theme').onchange=e=>{state.theme=e.target.value;applyTheme();save();};document.querySelectorAll('.loadp').forEach(b=>b.onclick=e=>{const p=prof[e.target.dataset.k];state.race=p.race;state.current=p.current;save();renderAll('delta')});document.querySelectorAll('.delp').forEach(b=>b.onclick=e=>{delete prof[e.target.dataset.k];localStorage.setItem('fdv_profiles',JSON.stringify(prof));renderSettings();}); }
function bindRaceCards(){document.querySelectorAll('.race').forEach(el=>el.onclick=()=>{state.race=el.dataset.r;applyTheme();save();renderAll();});}
function download(name,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));a.download=name;a.click();}
function share(){const data={r:state.race,s:state.slot,t:state.tier,c:state.current};const b64=btoa(unescape(encodeURIComponent(JSON.stringify(data)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');location.hash=b64;navigator.clipboard.writeText(location.href).catch(()=>{});}
function readShare(){if(!location.hash)return;try{const b=location.hash.slice(1).replace(/-/g,'+').replace(/_/g,'/');const pad='='.repeat((4-b.length%4)%4);const obj=JSON.parse(decodeURIComponent(escape(atob(b+pad))));Object.assign(state,{race:obj.r||state.race,slot:obj.s||state.slot,tier:obj.t||state.tier,current:obj.c||state.current});}catch{}}
async function renderAll(tab='min'){renderTabs(tab);await renderMin();await renderDelta();await renderFull();await renderAuto();renderSettings();}
async function boot(){load();const data=await api('/api/races');state.races=data.races;readShare();applyTheme();renderAll('min');$('#share').onclick=share;$('#cmd').onclick=()=>{$('#palette').classList.add('on');$('#k').focus();};
 document.addEventListener('keydown',e=>{if(e.ctrlKey&&e.key.toLowerCase()==='k'){e.preventDefault();$('#palette').classList.toggle('on');$('#k').focus();}if(['1','2','3','4'].includes(e.key)){state.race=['humains','rocktal','mecas','kaelesh'][+e.key-1];applyTheme();save();renderAll();}if(e.key==='ArrowLeft'){state.slot=Math.max(1,state.slot-1);save();renderAll();}if(e.key==='ArrowRight'){state.slot=Math.min(18,state.slot+1);save();renderAll();}});
 $('#k').onkeydown=e=>{if(e.key==='Enter'){const v=e.target.value.trim().toLowerCase();if(['min','delta','full','auto','settings'].includes(v))renderAll(v);$('#palette').classList.remove('on');e.target.value='';}};
 $('#palette').onclick=e=>{if(e.target.id==='palette')$('#palette').classList.remove('on');}; }
boot();
</script></body></html>
"""


class FdvHandler(BaseHTTPRequestHandler):
    server_version = "FDV/0.8"

    def _json(self, payload: Any, code: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _text(self, text: str, code: int = 200, ctype: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _parse_query(self) -> Dict[str, str]:
        q = parse_qs(urlparse(self.path).query)
        return {k: v[0] for k, v in q.items() if v}

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/":
                html = HTML_PAGE.replace("__TITLE__", TITLE).replace("__DEFAULT_THEME__", getattr(self.server, 'default_theme', 'midnight'))
                self._text(html, ctype="text/html; charset=utf-8")
                return
            if path == "/health":
                self._json({"ok": True, "version": VERSION, "time": int(time.time())})
                return
            if path == "/version":
                self._json({"title": TITLE, "version": VERSION})
                return
            if path == "/api/races":
                self._json({"races": to_race_list()})
                return
            if path == "/api/slot":
                q = self._parse_query()
                race = normalize_race(q.get("r", "humains"))
                slot = parse_slot(q.get("slot", "1"))
                self._json(build_slot_payload(race, slot))
                return
            if path == "/api/full":
                q = self._parse_query()
                race = normalize_race(q.get("r", "humains"))
                tier = int(q.get("tier", "1"))
                self._json(build_full_payload(race, tier))
                return
            self._json({"error": "Not found"}, 404)
        except Exception as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/delta":
            self._json({"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8") if raw else "{}")
            race = normalize_race(str(data.get("race", "humains")))
            slot = parse_slot(str(data.get("slot", "1")))
            current = data.get("current", [])
            if not isinstance(current, list):
                raise ValueError("current doit être une liste")
            self._json(build_delta_payload(race, slot, current))
        except Exception as exc:
            self._json({"error": str(exc)}, 400)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def run_web(host: str, port: int, open_browser: bool, theme: str) -> None:
    print(f"\n{TITLE}")
    print("Mode web local activé")
    print(f"Thème par défaut: {theme}")
    server = ThreadingHTTPServer((host, port), FdvHandler)
    server.default_theme = theme
    url = f"http://{host}:{port}"
    print(f"URL: {url}")
    if open_browser:
        threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nArrêt demandé (Ctrl+C)")
    finally:
        server.shutdown()
        server.server_close()
        print("Serveur arrêté proprement.")


def run_cli() -> int:
    print(TITLE)
    race = input("Race (1..4 ou nom) [humains]: ").strip() or "humains"
    try:
        r = normalize_race(race)
    except ValueError:
        print("Race invalide.")
        return 1
    slot_raw = input("Slot (1..18 ou 1.1..3.6) [11]: ").strip() or "11"
    try:
        slot = parse_slot(slot_raw)
    except ValueError as exc:
        print(exc)
        return 1
    payload = build_slot_payload(r, slot)
    print(f"\n{payload['display']} - slot {payload['slot_label']} - pop {fmt_int(payload['population'])}")
    for row in payload["requirements"]:
        print(f" - {row['building']}: {row['required']}")
    return 0


def ask_interactive(default_port: int = 8787) -> Tuple[int, bool, str]:
    print(TITLE)
    p = input(f"Port [{default_port}]: ").strip()
    port = int(p) if p.isdigit() else default_port
    o = input("Ouvrir le navigateur auto ? (O/n): ").strip().lower()
    open_browser = o not in {"n", "no", "non"}
    t = input("Thème par défaut (sombre/aurora/paper) [sombre]: ").strip().lower() or "sombre"
    theme = {"sombre": "midnight", "aurora": "aurora", "paper": "paper"}.get(t, "midnight")
    return port, open_browser, theme


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--cli", action="store_true", help="Force le mode texte")
    parser.add_argument("--port", type=int, default=None, help="Port HTTP (défaut: interactif -> 8787)")
    parser.add_argument("--host", default="127.0.0.1", help="Host bind (défaut 127.0.0.1)")
    parser.add_argument("--no-open", action="store_true", help="N'ouvre pas le navigateur")
    parser.add_argument("--self-test", action="store_true", help="Vérifie la cohérence des tables")
    args = parser.parse_args(argv)

    if args.self_test:
        ok, errors = self_test()
        if ok:
            print("SELF-TEST OK")
            return 0
        print("SELF-TEST KO")
        for e in errors:
            print(" -", e)
        return 1

    if args.cli:
        return run_cli()

    theme = "midnight"
    if args.port is None:
        port, open_browser, theme = ask_interactive(default_port=8787)
    else:
        port = args.port
        open_browser = not args.no_open
    if not (1 <= int(port) <= 65535):
        print("Port invalide")
        return 1
    run_web(args.host, int(port), open_browser, theme)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
