#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Outil FDV by HARDCORE — v0.9 🔥
Single-file local web app (offline, stdlib-only) + minimal CLI fallback.
"""
from __future__ import annotations

import argparse
import base64
import errno
import json
import re
import socket
import threading
import time
import unicodedata
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Sequence, Tuple
from urllib.parse import parse_qs, quote, unquote, urlparse

TITLE = "🔥 Outil FDV by HARDCORE — v0.9 🔥"
VERSION = "0.9"
DEFAULT_THEME = "neon"

POP_THRESHOLDS = [
    200000,
    320000,
    512000,
    819200,
    1310720,
    2097152,
    3355443,
    5368709,
    8589934,
    13743894,
    21990230,
    35184368,
    56294989,
    90071982,
    144115171,
    230584274,
    368934838,
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
            ("🥫", "Réserve alimentaire"),
            ("🏙️", "Tour d’habitation"),
            ("🧬", "Laboratoire de biotechnologie"),
        ],
        "levels": [
            [22, 20, 0, 0, 0, 0, 0], [23, 22, 0, 0, 0, 0, 0], [23, 24, 0, 0, 0, 0, 0],
            [24, 25, 0, 0, 0, 0, 0], [27, 26, 0, 0, 0, 0, 0], [27, 28, 0, 0, 0, 0, 0],
            [43, 43, 4, 0, 2, 0, 3], [46, 44, 7, 0, 4, 2, 3], [46, 46, 8, 0, 4, 4, 4],
            [48, 47, 8, 0, 8, 4, 5], [49, 48, 8, 0, 9, 4, 6], [50, 49, 8, 0, 9, 4, 6],
            [61, 59, 11, 7, 17, 11, 14], [63, 60, 12, 8, 25, 16, 16], [66, 62, 13, 9, 26, 19, 19],
            [69, 65, 13, 9, 31, 19, 20], [71, 66, 14, 10, 38, 27, 23], [74, 68, 15, 10, 42, 29, 27],
        ],
    },
    "rocktal": {
        "display": "Rock’tal",
        "color": "#38c876",
        "aliases": ["2", "rocktal", "rock'tal", "rock’tal", "rock"],
        "buildings": [
            ("🪨", "Enclave stoïque"),
            ("💎", "Culture du cristal"),
            ("🧿", "Forge runique (T1→T2)"),
            ("🗿", "Orictorium (T2→T3)"),
            ("🧱", "Monolithe"),
            ("⚗️", "Centre de recherche sur les minéraux"),
        ],
        "levels": [
            [21, 21, 0, 0, 0, 0], [23, 23, 0, 0, 0, 0], [24, 25, 0, 0, 0, 0],
            [25, 26, 0, 0, 0, 0], [27, 27, 0, 0, 0, 0], [28, 29, 0, 0, 0, 0],
            [43, 44, 5, 0, 0, 0], [45, 46, 7, 0, 1, 0], [47, 48, 8, 0, 1, 0],
            [48, 50, 8, 0, 2, 0], [50, 51, 8, 0, 2, 0], [51, 52, 8, 0, 2, 0],
            [62, 64, 10, 8, 6, 2], [64, 66, 12, 9, 7, 2], [67, 69, 14, 9, 8, 3],
            [70, 72, 14, 10, 9, 3], [72, 75, 15, 11, 10, 4], [75, 78, 16, 11, 10, 5],
        ],
    },
    "mecas": {
        "display": "Mécas",
        "color": "#ffd24d",
        "aliases": ["3", "mecas", "mécas", "mecha"],
        "buildings": [
            ("🏭", "Chaîne de production"),
            ("⚗️", "Usine de fusion de cellules"),
            ("📡", "Réseau d’actualisation (T1→T2)"),
            ("🧮", "Centre d’informatique quantique (T2→T3)"),
            ("💾", "Chaîne de production de micropuces"),
            ("🦾", "Centre d’assemblage automatisé"),
        ],
        "levels": [
            [17, 20, 0, 0, 0, 0], [19, 21, 0, 0, 0, 0], [20, 23, 0, 0, 0, 0],
            [21, 24, 0, 0, 0, 0], [23, 26, 0, 0, 0, 0], [24, 28, 0, 0, 0, 0],
            [41, 49, 3, 0, 0, 1], [43, 50, 5, 0, 1, 2], [44, 52, 6, 0, 2, 2],
            [45, 53, 7, 0, 2, 2], [46, 54, 7, 0, 4, 4], [47, 55, 7, 0, 4, 5],
            [59, 69, 10, 6, 12, 11], [61, 71, 11, 7, 16, 13], [64, 74, 11, 8, 21, 16],
            [67, 77, 12, 8, 25, 18], [69, 80, 13, 9, 25, 21], [72, 83, 14, 9, 30, 22],
        ],
    },
    "kaelesh": {
        "display": "Kaelesh",
        "color": "#d57dff",
        "aliases": ["4", "kaelesh", "kae"],
        "buildings": [
            ("🛖", "Refugium"),
            ("⚛️", "Condensateur d’antimatière"),
            ("🔭", "Salles de réalisation (T1→T2)"),
            ("🌌", "Forum de la transcendance (T2→T3)"),
            ("🧲", "Convecteur d’antimatière"),
            ("🪺", "Accélérateur par chrysalide"),
            ("🔮", "Modulateur psionique"),
        ],
        "levels": [
            [20, 20, 0, 0, 0, 0, 0], [21, 22, 0, 0, 0, 0, 0], [23, 23, 0, 0, 0, 0, 0],
            [24, 24, 0, 0, 0, 0, 0], [25, 26, 0, 0, 0, 0, 0], [27, 27, 0, 0, 0, 0, 0],
            [43, 45, 3, 0, 0, 1, 0], [44, 46, 6, 0, 0, 1, 0], [46, 48, 6, 0, 2, 3, 2],
            [47, 49, 7, 0, 2, 3, 2], [48, 50, 7, 0, 3, 4, 2], [49, 51, 7, 0, 3, 4, 2],
            [60, 62, 10, 6, 13, 18, 6], [62, 64, 11, 7, 15, 18, 7], [65, 67, 11, 8, 15, 21, 7],
            [67, 69, 12, 8, 19, 30, 9], [69, 71, 13, 9, 19, 34, 11], [72, 74, 13, 9, 22, 40, 11],
        ],
    },
}

ALIAS_TO_RACE = {a.lower(): k for k, v in RACES.items() for a in v["aliases"]}


def slot_to_label(slot: int) -> str:
    return f"{(slot - 1) // 6 + 1}.{(slot - 1) % 6 + 1}"


def parse_slot(raw: str) -> int:
    s = str(raw).strip().lower()
    if re.fullmatch(r"\d+", s):
        n = int(s)
        if 1 <= n <= 18:
            return n
    m = re.fullmatch(r"([1-3])\.([1-6])", s)
    if m:
        return (int(m.group(1)) - 1) * 6 + int(m.group(2))
    raise ValueError("Slot invalide (1..18 ou 1.1..3.6)")


def normalize_race(raw: str) -> str:
    s = str(raw).strip().lower()
    if s in RACES:
        return s
    if s in ALIAS_TO_RACE:
        return ALIAS_TO_RACE[s]
    raise ValueError("Race invalide")


def canon(s: str) -> str:
    t = unicodedata.normalize("NFKD", s.lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", t)


def required_levels(race: str, slot: int) -> List[int]:
    return list(RACES[race]["levels"][slot - 1])


def parse_levels_text(race: str, text: str) -> List[int]:
    b = RACES[race]["buildings"]
    out = [0] * len(b)
    raw = (text or "").strip()
    if not raw:
        return out

    nums = [int(x) for x in re.findall(r"\d+", raw)]
    if "," in raw and "=" not in raw and ":" not in raw and len(nums) >= 2:
        for i, v in enumerate(nums[: len(out)]):
            out[i] = max(0, v)
        return out

    name_map = {canon(name): i for i, (_, name) in enumerate(b)}
    for i, (_, name) in enumerate(b):
        name_map[str(i + 1)] = i
        name_map[canon(name[:24])] = i

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"[:=;\t,]", line, maxsplit=1)
        if len(parts) == 1:
            continue
        k, v = parts[0].strip(), parts[1].strip()
        m = re.search(r"\d+", v)
        if not m:
            continue
        idx = name_map.get(canon(k))
        if idx is None:
            ck = canon(k)
            for nk, ni in name_map.items():
                if nk and nk in ck:
                    idx = ni
                    break
        if idx is not None:
            out[idx] = max(0, int(m.group(0)))

    if not any(out) and nums:
        for i, v in enumerate(nums[: len(out)]):
            out[i] = max(0, v)
    return out


def compute_priority(buildings: Sequence[Tuple[str, str]], missing: Sequence[int]) -> List[Dict[str, Any]]:
    ranked: List[Tuple[int, int, int]] = []
    for i, (_, name) in enumerate(buildings):
        miss = missing[i]
        if miss <= 0:
            continue
        n = name.lower()
        if i in (0, 1):
            cat = 0
        elif "t1→t2" in n:
            cat = 1
        elif "t2→t3" in n:
            cat = 2
        else:
            cat = 3
        ranked.append((cat, -miss, i))
    ranked.sort()
    return [{"index": i, "building": buildings[i][1], "missing": missing[i], "category": c} for c, _, i in ranked]


def compute_max_slot(race: str, current: Sequence[int]) -> int:
    mx = 0
    for slot in range(1, 19):
        req = required_levels(race, slot)
        if all((current[i] if i < len(current) else 0) >= req[i] for i in range(len(req))):
            mx = slot
        else:
            break
    return mx


def build_slot_payload(race: str, slot: int) -> Dict[str, Any]:
    cfg = RACES[race]
    req = required_levels(race, slot)
    return {
        "race": race,
        "display": cfg["display"],
        "slot": slot,
        "slot_label": slot_to_label(slot),
        "population": POP_THRESHOLDS[slot - 1],
        "requirements": [
            {"index": i, "emoji": em, "building": name, "required": req[i]}
            for i, (em, name) in enumerate(cfg["buildings"])
        ],
    }


def build_delta_payload(race: str, slot: int, current: Sequence[int]) -> Dict[str, Any]:
    cfg = RACES[race]
    req = required_levels(race, slot)
    cur = [max(0, int(current[i] if i < len(current) else 0)) for i in range(len(req))]
    miss = [max(0, req[i] - cur[i]) for i in range(len(req))]
    ok_count = sum(1 for i in range(len(req)) if miss[i] == 0)
    progress = int((ok_count / len(req)) * 100) if req else 0
    maxslot = compute_max_slot(race, cur)
    nextslot = min(18, maxslot + 1) if maxslot < 18 else 18
    return {
        "race": race,
        "slot": slot,
        "slot_label": slot_to_label(slot),
        "population": POP_THRESHOLDS[slot - 1],
        "rows": [
            {
                "index": i,
                "emoji": cfg["buildings"][i][0],
                "building": cfg["buildings"][i][1],
                "current": cur[i],
                "required": req[i],
                "missing": miss[i],
                "ok": miss[i] == 0,
            }
            for i in range(len(req))
        ],
        "priority": compute_priority(cfg["buildings"], miss),
        "progress": progress,
        "maxslot": maxslot,
        "nextslot": nextslot,
        "nextslot_label": slot_to_label(nextslot),
    }


def build_autoslot_payload(race: str, current: Sequence[int]) -> Dict[str, Any]:
    maxslot = compute_max_slot(race, current)
    nextslot = min(18, maxslot + 1) if maxslot < 18 else 18
    delta = build_delta_payload(race, nextslot, current)
    return {"race": race, "maxslot": maxslot, "nextslot": nextslot, "deltaNext": delta}


def build_full_payload(race: str, tier: int) -> Dict[str, Any]:
    if tier not in (1, 2, 3):
        raise ValueError("tier doit être 1|2|3")
    cfg = RACES[race]
    start = (tier - 1) * 6 + 1
    slots = list(range(start, start + 6))
    return {
        "race": race,
        "tier": tier,
        "slots": [{"slot": s, "label": slot_to_label(s), "population": POP_THRESHOLDS[s - 1]} for s in slots],
        "matrix": [
            {
                "index": i,
                "emoji": em,
                "building": name,
                "values": [cfg["levels"][s - 1][i] for s in slots],
            }
            for i, (em, name) in enumerate(cfg["buildings"])
        ],
    }


def races_payload() -> Dict[str, Any]:
    return {
        "races": [
            {
                "key": k,
                "display": v["display"],
                "color": v["color"],
                "buildings": [{"emoji": em, "name": n} for em, n in v["buildings"]],
                "slots": [slot_to_label(i) for i in range(1, 19)],
            }
            for k, v in RACES.items()
        ]
    }


def self_test() -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if len(POP_THRESHOLDS) != 18:
        errors.append("POP_THRESHOLDS doit avoir 18 valeurs")
    expected_last_mecas = [72, 83, 14, 9, 30, 22]
    if RACES["mecas"]["levels"][17] != expected_last_mecas:
        errors.append("Mécas slot 18 invalide")
    for race, cfg in RACES.items():
        if len(cfg["levels"]) != 18:
            errors.append(f"{race}: 18 slots requis")
            continue
        if any(not em for em, _ in cfg["buildings"]):
            errors.append(f"{race}: emoji manquant")
        for s, row in enumerate(cfg["levels"], 1):
            if len(row) != len(cfg["buildings"]):
                errors.append(f"{race}: slot {s} incohérent")
    return len(errors) == 0, errors


HTML_PAGE = r"""<!doctype html>
<html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>__TITLE__</title>
<style>
:root{--bg:#090d16;--bg2:#0f1422;--txt:#e9f0ff;--mut:#8ea1c2;--line:rgba(255,255,255,.14);--card:rgba(255,255,255,.04);--accent:#4f8cff;--ok:#3bd179;--bad:#ff7070;--dur:.18s;--fs:100%;--pad:12px}
:root[data-theme='minimal']{--bg:#101214;--bg2:#171a1e;--txt:#f2f4f7;--mut:#a3acba;--card:rgba(255,255,255,.03)}
:root[data-theme='contrast']{--bg:#000;--bg2:#0b0b0b;--txt:#fff;--mut:#d0d0d0;--line:#ffffff55;--card:#111}
:root[data-density='compact']{--pad:8px}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,sans-serif;font-size:var(--fs);background:linear-gradient(155deg,var(--bg),var(--bg2));color:var(--txt)}
.layout{display:grid;grid-template-columns:320px 1fr;min-height:100vh}.side{border-right:1px solid var(--line);padding:14px;position:sticky;top:0;height:100vh;overflow:auto}.main{padding:14px;overflow:auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:var(--pad);backdrop-filter:blur(8px)} .stack{display:grid;gap:10px}.row{display:flex;gap:8px;flex-wrap:wrap}
.race{padding:10px;border:1px solid var(--line);border-radius:10px;cursor:pointer;transition:all var(--dur)}.race.on{outline:2px solid var(--accent);background:color-mix(in srgb,var(--accent) 12%, transparent)}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}.tab{padding:8px 12px;border:1px solid var(--line);border-radius:10px;cursor:pointer;position:relative}.tab.on{border-color:var(--accent)}.tab.on:after{content:'';position:absolute;left:10px;right:10px;bottom:3px;height:2px;background:var(--accent);animation:sl var(--dur)}
@keyframes sl{from{transform:scaleX(.3);opacity:.4}to{transform:scaleX(1);opacity:1}}
.panel{display:none;animation:in var(--dur)}.panel.on{display:block}@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
input,select,textarea,button{width:100%;padding:8px;border-radius:10px;border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--txt)}button{cursor:pointer;width:auto}.btn{padding:8px 12px}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left}tbody tr{transition:all var(--dur)}tbody tr:hover{background:rgba(255,255,255,.04);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--accent) 35%, transparent)}
.progress{height:10px;background:rgba(255,255,255,.12);border-radius:999px;overflow:hidden}.bar{height:100%;background:linear-gradient(90deg,var(--accent),#73c4ff)}
.k{position:fixed;inset:0;display:none;background:#0007;align-items:flex-start;justify-content:center;padding-top:10vh}.k.on{display:flex}.kbox{width:min(760px,95vw)}
.sub{color:var(--mut);font-size:12px}.mono{font-family:ui-monospace,Consolas,monospace}.noprint{}
@media (max-width:980px){.layout{grid-template-columns:1fr}.side{position:relative;height:auto}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media print{.noprint,.side{display:none!important}.layout{grid-template-columns:1fr}.main{padding:0}body{background:#fff;color:#000}}
</style></head>
<body>
<div class='layout'>
<aside class='side'>
  <div class='stack'>
    <div class='card'><div style='font-weight:700'>🔥 Outil FDV by HARDCORE — v0.9 🔥</div><div class='sub'>Offline · localhost</div></div>
    <div class='card'><div class='sub'>Race</div><div id='raceCards' class='stack'></div></div>
    <div class='card stack'>
      <div class='sub'>Slot cible</div>
      <input id='slotText' value='2.5'>
      <input id='slotRange' type='range' min='1' max='18' value='11'>
      <div class='sub' id='slotPop'></div>
    </div>
    <div class='card stack'>
      <div class='sub'>Import niveaux</div>
      <textarea id='importBox' rows='6' placeholder='CSV: 10,12,0,3\nou\nNom=12'></textarea>
      <div class='row'><button class='btn' id='importApply'>Appliquer</button><button class='btn' id='clearLv'>Reset</button></div>
    </div>
    <div class='card row noprint'>
      <button class='btn' id='copyLink'>Copier le lien</button>
      <button class='btn' id='openCmd'>Ctrl+K</button>
    </div>
  </div>
</aside>
<main class='main'>
  <div class='tabs noprint' id='tabs'></div>
  <section id='p-min' class='panel on'></section>
  <section id='p-delta' class='panel'></section>
  <section id='p-full' class='panel'></section>
  <section id='p-auto' class='panel'></section>
  <section id='p-settings' class='panel'></section>
  <section id='p-help' class='panel'></section>
</main>
</div>
<div id='k' class='k'><div class='kbox card'><input id='kInput' placeholder='slot 18 | race mecas | theme minimal | export txt | toggle emoji'></div></div>
<script>
const TABS=[['min','MIN'],['delta','DELTA'],['full','FULL'],['auto','AUTO-SLOT'],['settings','SETTINGS'],['help','HELP']];
const state={race:'humains',slot:11,tier:2,current:[],races:[],tab:'min',emoji:true,anim:true,theme:'__DEFAULT_THEME__',density:'comfortable',fontScale:100,accentAuto:true,lastProfile:''};
const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const esc=s=>String(s).replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
async function api(u,o){const r=await fetch(u,o);if(!r.ok) throw new Error(await r.text()); return r.json();}
const slotLabel=s=>`${Math.floor((s-1)/6)+1}.${((s-1)%6)+1}`;
function parseSlot(v){v=String(v).trim();if(/^\d+$/.test(v)){const n=+v; if(n>=1&&n<=18)return n;} const m=v.match(/^([1-3])\.([1-6])$/); if(m)return (+m[1]-1)*6+(+m[2]); return null;}
function save(){localStorage.setItem('fdv_v09',JSON.stringify(state));}
function load(){try{Object.assign(state,JSON.parse(localStorage.getItem('fdv_v09')||'{}'));}catch{} }
function applyTheme(){
  document.documentElement.dataset.theme = state.theme==='neon'?'':(state.theme==='minimal'?'minimal':'contrast');
  document.documentElement.dataset.density = state.density;
  document.documentElement.style.setProperty('--fs', state.fontScale+'%');
  document.documentElement.style.setProperty('--dur', state.anim?'.18s':'0s');
  const r=state.races.find(x=>x.key===state.race); if(state.accentAuto && r) document.documentElement.style.setProperty('--accent',r.color);
}
function hashState(){
  const payload={r:state.race,s:state.slot,t:state.tier,c:state.current,e:state.emoji,th:state.theme,d:state.density,f:state.fontScale};
  const b=btoa(unescape(encodeURIComponent(JSON.stringify(payload)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  location.hash=b;
}
function restoreHash(){
  const h=location.hash.slice(1); if(!h)return;
  try{const b=h.replace(/-/g,'+').replace(/_/g,'/');const pad='='.repeat((4-b.length%4)%4);const o=JSON.parse(decodeURIComponent(escape(atob(b+pad))));
    Object.assign(state,{race:o.r||state.race,slot:o.s||state.slot,tier:o.t||state.tier,current:o.c||state.current,emoji:o.e??state.emoji,theme:o.th||state.theme,density:o.d||state.density,fontScale:o.f||state.fontScale});
  }catch{}
}
function raceCards(){
  $('#raceCards').innerHTML=state.races.map(r=>`<div class='race ${r.key===state.race?'on':''}' data-r='${r.key}'><b>${esc(r.display)}</b><div class='sub'>${r.buildings.length} bâtiments</div></div>`).join('');
  $$('.race').forEach(c=>c.onclick=()=>{state.race=c.dataset.r;ensureCurrentLen();applyTheme();save();renderAll();});
}
function ensureCurrentLen(){const race=state.races.find(r=>r.key===state.race); if(!race)return; if(!Array.isArray(state.current)||state.current.length!==race.buildings.length) state.current=Array(race.buildings.length).fill(0);}
function renderTabs(){ $('#tabs').innerHTML=TABS.map(t=>`<button class='tab ${state.tab===t[0]?'on':''}' data-tab='${t[0]}'>${t[1]}</button>`).join(''); $$('.tab').forEach(b=>b.onclick=()=>{state.tab=b.dataset.tab;save();renderPanels();}); }
function renderPanels(){ $$('.panel').forEach(p=>p.classList.remove('on')); $(`#p-${state.tab}`).classList.add('on'); }
function filterTable(id,q){q=q.toLowerCase(); $$(id+' tbody tr').forEach(tr=>tr.style.display=tr.innerText.toLowerCase().includes(q)?'':'none');}
function dl(name,txt,typ='text/plain;charset=utf-8'){const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([txt],{type:typ})); a.download=name; a.click();}

async function renderMin(){
  const d=await api(`/api/slot?r=${state.race}&slot=${state.slot}`);
  $('#slotPop').textContent='Population: '+new Intl.NumberFormat('fr-FR').format(d.population);
  $('#p-min').innerHTML=`<div class='card stack'><div class='row noprint'><input id='fmin' placeholder='Filtrer bâtiment'><button class='btn' id='copyMin'>Copier</button><button class='btn' id='txtMin'>TXT</button><button class='btn' id='jsonMin'>JSON</button></div><table id='tmin'><thead><tr><th>Bâtiment</th><th>Niveau</th></tr></thead><tbody>${d.requirements.map(r=>`<tr><td>${state.emoji?r.emoji+' ':''}${esc(r.building)}</td><td class='mono'>${r.required}</td></tr>`).join('')}</tbody></table></div>`;
  $('#fmin').oninput=e=>filterTable('#tmin',e.target.value);
  const txt=`[FDV] ${d.display} slot ${d.slot_label}\nPopulation: ${d.population}\n`+d.requirements.map(r=>`- ${r.building}: ${r.required}`).join('\n');
  $('#copyMin').onclick=()=>navigator.clipboard.writeText(txt);
  $('#txtMin').onclick=()=>dl(`fdv_${state.race}_${d.slot_label}.txt`,txt);
  $('#jsonMin').onclick=()=>dl(`fdv_${state.race}_${d.slot_label}.json`,JSON.stringify(d,null,2),'application/json');
}

async function renderDelta(){
  ensureCurrentLen();
  const d=await api('/api/delta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({race:state.race,slot:state.slot,current:state.current})});
  $('#p-delta').innerHTML=`<div class='stack'><div class='card'><div class='sub'>Progression slot ${d.slot_label}</div><div class='progress'><div class='bar' style='width:${d.progress}%'></div></div><div class='sub'>${d.progress}% · max ${slotLabel(d.maxslot||1)} · next ${d.nextslot_label}</div></div><div class='card'><div class='row noprint'><input id='fdelta' placeholder='Filtrer'><button class='btn' id='saveProfile'>Sauver profil</button></div><table id='tdelta'><thead><tr><th>Bâtiment</th><th>Actuel</th><th>Requis</th><th>Manque</th></tr></thead><tbody>${d.rows.map((r,i)=>`<tr><td>${state.emoji?r.emoji+' ':''}${esc(r.building)}</td><td><input class='lv' data-i='${i}' value='${r.current}'></td><td class='mono'>${r.required}</td><td class='mono' style='color:${r.ok?'var(--ok)':'var(--bad)'}'>${r.missing}</td></tr>`).join('')}</tbody></table></div><div class='card'><b>Top suggestions</b><ol>${d.priority.slice(0,8).map(p=>`<li>${esc(p.building)} +${p.missing}</li>`).join('')||'<li>Tout est OK</li>'}</ol></div></div>`;
  $('#fdelta').oninput=e=>filterTable('#tdelta',e.target.value);
  $$('.lv').forEach(i=>i.oninput=e=>{state.current[+e.target.dataset.i]=Math.max(0,parseInt(e.target.value||'0',10)||0);save();hashState();renderDelta();renderAuto();});
  $('#saveProfile').onclick=()=>{
    const name=prompt('Nom du profil?','profil-'+new Date().toISOString().slice(0,16).replace('T',' ')); if(!name)return;
    const p=JSON.parse(localStorage.getItem('fdv_profiles')||'{}'); p[name]={race:state.race,current:state.current,savedAt:new Date().toISOString()};
    localStorage.setItem('fdv_profiles',JSON.stringify(p)); state.lastProfile=name; save(); alert('Profil sauvegardé'); renderSettings();
  };
}

async function renderFull(){
  const d=await api(`/api/full?r=${state.race}&tier=${state.tier}`);
  $('#p-full').innerHTML=`<div class='card stack'><div class='row noprint'><select id='tierSel'><option ${state.tier===1?'selected':''}>1</option><option ${state.tier===2?'selected':''}>2</option><option ${state.tier===3?'selected':''}>3</option></select><input id='ffull' placeholder='Filtrer'></div><table id='tfull'><thead><tr><th>Bâtiment</th>${d.slots.map(s=>`<th>${s.label}</th>`).join('')}</tr></thead><tbody>${d.matrix.map(r=>`<tr><td>${state.emoji?r.emoji+' ':''}${esc(r.building)}</td>${r.values.map(v=>`<td class='mono'>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  $('#tierSel').onchange=e=>{state.tier=+e.target.value; save(); hashState(); renderFull();};
  $('#ffull').oninput=e=>filterTable('#tfull',e.target.value);
}

async function renderAuto(){
  ensureCurrentLen();
  const d=await api('/api/autoslot',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({race:state.race,current:state.current})});
  $('#p-auto').innerHTML=`<div class='stack'><div class='card'><div class='sub'>Slot max atteignable</div><div class='mono' style='font-size:22px'>${slotLabel(d.maxslot||1)}</div><div class='sub'>Prochain conseillé: ${slotLabel(d.nextslot)}</div></div><div class='card'><b>Delta auto vers ${slotLabel(d.nextslot)}</b><ul>${d.deltaNext.priority.slice(0,10).map(x=>`<li>${esc(x.building)} +${x.missing}</li>`).join('')||'<li>Aucun manque</li>'}</ul></div></div>`;
}

function renderSettings(){
  const profiles=JSON.parse(localStorage.getItem('fdv_profiles')||'{}');
  $('#p-settings').innerHTML=`<div class='stack'><div class='card stack'><label><input id='emoji' type='checkbox' ${state.emoji?'checked':''}> Emojis ON</label><label><input id='anim' type='checkbox' ${state.anim?'checked':''}> Animations ON</label><label>Theme<select id='theme'><option value='neon' ${state.theme==='neon'?'selected':''}>Neon HUD</option><option value='minimal' ${state.theme==='minimal'?'selected':''}>Minimal</option><option value='contrast' ${state.theme==='contrast'?'selected':''}>High Contrast</option></select></label><label>Font scale<input id='fs' type='range' min='90' max='120' value='${state.fontScale}'></label><label>Density<select id='density'><option value='comfortable' ${state.density==='comfortable'?'selected':''}>comfortable</option><option value='compact' ${state.density==='compact'?'selected':''}>compact</option></select></label><label><input id='accentAuto' type='checkbox' ${state.accentAuto?'checked':''}> Accent auto par race</label></div><div class='card'><b>Profils</b><div class='sub'>Auto-restore: ${state.lastProfile||'aucun'}</div>${Object.keys(profiles).map(k=>`<div class='row'><button class='btn lp' data-k='${esc(k)}'>Charger ${esc(k)}</button><button class='btn dp' data-k='${esc(k)}'>Suppr</button></div>`).join('')||'<div class="sub">Aucun profil</div>'}</div></div>`;
  $('#emoji').onchange=e=>{state.emoji=e.target.checked;save();renderAll();};
  $('#anim').onchange=e=>{state.anim=e.target.checked;applyTheme();save();};
  $('#theme').onchange=e=>{state.theme=e.target.value;applyTheme();save();};
  $('#fs').oninput=e=>{state.fontScale=+e.target.value;applyTheme();save();};
  $('#density').onchange=e=>{state.density=e.target.value;applyTheme();save();};
  $('#accentAuto').onchange=e=>{state.accentAuto=e.target.checked;applyTheme();save();};
  $$('.lp').forEach(b=>b.onclick=()=>{const p=profiles[b.dataset.k]; state.race=p.race; state.current=p.current; state.lastProfile=b.dataset.k; save(); applyTheme(); renderAll();});
  $$('.dp').forEach(b=>b.onclick=()=>{delete profiles[b.dataset.k]; localStorage.setItem('fdv_profiles',JSON.stringify(profiles)); renderSettings();});
}

function renderHelp(){
  $('#p-help').innerHTML=`<div class='card stack'><b>Raccourcis</b><ul><li>1..4: race</li><li>←/→: slot -/+</li><li>Ctrl+K: command palette</li></ul><b>Commandes palette</b><ul><li>slot 18</li><li>race mecas</li><li>theme minimal</li><li>export txt / export json</li><li>toggle emoji</li></ul></div>`;
}

async function applyImport(){
  const text=$('#importBox').value||'';
  const d=await api('/api/parse-levels',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({race:state.race,text})});
  state.current=d.current; save(); hashState(); renderDelta(); renderAuto();
}

function openPalette(){ $('#k').classList.add('on'); $('#kInput').focus(); }
function closePalette(){ $('#k').classList.remove('on'); $('#kInput').value=''; }
async function runCmd(cmd){
  const c=cmd.trim().toLowerCase();
  if(!c)return;
  if(c.startsWith('slot ')){const s=parseSlot(c.slice(5)); if(s){state.slot=s;save();hashState();renderAll();}}
  else if(c.startsWith('race ')){const r=c.slice(5).trim(); state.race=r==='1'?'humains':r==='2'?'rocktal':r==='3'?'mecas':r==='4'?'kaelesh':r; save(); applyTheme(); renderAll();}
  else if(c.startsWith('theme ')){state.theme=c.slice(6).trim(); applyTheme(); save();}
  else if(c==='toggle emoji'){state.emoji=!state.emoji; save(); renderAll();}
  else if(c==='export txt'){const d=await api(`/api/export?format=txt&race=${encodeURIComponent(state.race)}&slot=${state.slot}&current=${encodeURIComponent(state.current.join(','))}`); dl('fdv_export.txt',d.text);}
  else if(c==='export json'){const d=await api(`/api/export?format=json&race=${encodeURIComponent(state.race)}&slot=${state.slot}&current=${encodeURIComponent(state.current.join(','))}`); dl('fdv_export.json',JSON.stringify(d,null,2),'application/json');}
  else if(c==='help'){state.tab='help'; renderTabs(); renderPanels();}
}

async function renderAll(){
  ensureCurrentLen();
  raceCards(); renderTabs(); renderPanels(); applyTheme();
  await renderMin(); await renderDelta(); await renderFull(); await renderAuto(); renderSettings(); renderHelp();
  $('#slotText').value=slotLabel(state.slot); $('#slotRange').value=String(state.slot);
}

async function boot(){
  load(); const r=await api('/api/races'); state.races=r.races; restoreHash(); ensureCurrentLen();
  const profiles=JSON.parse(localStorage.getItem('fdv_profiles')||'{}'); if(state.lastProfile && profiles[state.lastProfile]){state.race=profiles[state.lastProfile].race;state.current=profiles[state.lastProfile].current||state.current;}
  applyTheme();
  $('#slotRange').oninput=e=>{state.slot=+e.target.value; $('#slotText').value=slotLabel(state.slot); save(); hashState(); renderMin(); renderDelta();};
  $('#slotText').onchange=e=>{const s=parseSlot(e.target.value); if(s){state.slot=s; $('#slotRange').value=String(s); save(); hashState(); renderMin(); renderDelta();}};
  $('#importApply').onclick=applyImport;
  $('#clearLv').onclick=()=>{ensureCurrentLen(); state.current=state.current.map(()=>0); save(); hashState(); renderDelta(); renderAuto();};
  $('#copyLink').onclick=()=>{hashState(); navigator.clipboard.writeText(location.href).then(()=>alert('Lien copié'));};
  $('#openCmd').onclick=openPalette;
  $('#k').onclick=e=>{if(e.target.id==='k')closePalette();};
  $('#kInput').onkeydown=e=>{if(e.key==='Enter'){runCmd(e.target.value);closePalette();} if(e.key==='Escape')closePalette();};
  document.addEventListener('keydown',e=>{
    if(e.ctrlKey&&e.key.toLowerCase()==='k'){e.preventDefault();openPalette();}
    if(['1','2','3','4'].includes(e.key)){state.race=['humains','rocktal','mecas','kaelesh'][+e.key-1]; applyTheme(); save(); renderAll();}
    if(e.key==='ArrowLeft'){state.slot=Math.max(1,state.slot-1); save(); hashState(); renderMin(); renderDelta();}
    if(e.key==='ArrowRight'){state.slot=Math.min(18,state.slot+1); save(); hashState(); renderMin(); renderDelta();}
  });
  await renderAll();
}
boot();
</script>
</body></html>"""


class FdvHandler(BaseHTTPRequestHandler):
    server_version = "FDV/0.9"

    def _json(self, payload: Any, code: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str, code: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _query(self) -> Dict[str, str]:
        q = parse_qs(urlparse(self.path).query)
        return {k: v[0] for k, v in q.items() if v}

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/":
                self._html(HTML_PAGE.replace("__TITLE__", TITLE).replace("__DEFAULT_THEME__", DEFAULT_THEME))
            elif path == "/health":
                self._json({"ok": True, "version": VERSION, "time": int(time.time())})
            elif path == "/version":
                self._json({"title": TITLE, "version": VERSION})
            elif path == "/api/races":
                self._json(races_payload())
            elif path == "/api/slot":
                q = self._query()
                self._json(build_slot_payload(normalize_race(q.get("r", "humains")), parse_slot(q.get("slot", "1"))))
            elif path == "/api/full":
                q = self._query()
                self._json(build_full_payload(normalize_race(q.get("r", "humains")), int(q.get("tier", "1"))))
            elif path == "/api/export":
                q = self._query()
                race = normalize_race(q.get("race", "humains"))
                slot = parse_slot(q.get("slot", "11"))
                fmt = q.get("format", "txt").lower()
                current = [int(x) for x in re.findall(r"\d+", q.get("current", ""))]
                payload = build_delta_payload(race, slot, current)
                if fmt == "json":
                    self._json(payload)
                else:
                    text = [f"[FDV] {RACES[race]['display']} slot {payload['slot_label']}"]
                    text.append(f"Population: {payload['population']}")
                    text.extend([f"- {r['building']}: actuel {r['current']} / requis {r['required']} / manque {r['missing']}" for r in payload["rows"]])
                    self._json({"format": "txt", "text": "\n".join(text)})
            else:
                self._json({"error": "Not found"}, 404)
        except Exception as exc:
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            ln = int(self.headers.get("Content-Length", "0"))
            data = json.loads((self.rfile.read(ln) or b"{}").decode("utf-8"))
            if path == "/api/delta":
                race = normalize_race(data.get("race", "humains"))
                slot = parse_slot(str(data.get("slot", "1")))
                current = data.get("current", [])
                if not isinstance(current, list):
                    raise ValueError("current doit être une liste")
                self._json(build_delta_payload(race, slot, current))
            elif path == "/api/autoslot":
                race = normalize_race(data.get("race", "humains"))
                current = data.get("current", [])
                if not isinstance(current, list):
                    raise ValueError("current doit être une liste")
                self._json(build_autoslot_payload(race, current))
            elif path == "/api/parse-levels":
                race = normalize_race(data.get("race", "humains"))
                text = str(data.get("text", ""))
                parsed = parse_levels_text(race, text)
                self._json({"race": race, "current": parsed, "buildings": [b for _, b in RACES[race]["buildings"]]})
            else:
                self._json({"error": "Not found"}, 404)
        except Exception as exc:
            self._json({"error": str(exc)}, 400)

    def log_message(self, *_: Any) -> None:
        return


def run_cli() -> int:
    print(TITLE)
    race = input("Race [humains]: ").strip() or "humains"
    slot = input("Slot [11]: ").strip() or "11"
    try:
        payload = build_slot_payload(normalize_race(race), parse_slot(slot))
    except ValueError as exc:
        print(exc)
        return 1
    print(f"\n{payload['display']} | slot {payload['slot_label']} | pop {payload['population']}")
    for r in payload["requirements"]:
        print(f"- {r['building']}: {r['required']}")
    return 0


def ask_start(default_port: int) -> Tuple[int, bool, str]:
    print(TITLE)
    p = input(f"Port [{default_port}]: ").strip()
    port = int(p) if p.isdigit() else default_port
    auto = input("Ouvrir navigateur auto ? (O/n): ").strip().lower() not in {"n", "no", "non"}
    theme = input("Thème (neon/minimal/contrast) [neon]: ").strip().lower() or "neon"
    return port, auto, theme


def bind_server(host: str, wanted_port: int, tries: int = 50) -> Tuple[ThreadingHTTPServer, int]:
    last_error: Exception | None = None
    for p in range(wanted_port, wanted_port + tries + 1):
        try:
            return ThreadingHTTPServer((host, p), FdvHandler), p
        except OSError as exc:
            last_error = exc
            if exc.errno != errno.EADDRINUSE:
                raise
    raise RuntimeError(f"Aucun port libre entre {wanted_port} et {wanted_port + tries}: {last_error}")


def run_web(host: str, port: int, no_open: bool) -> int:
    server, final_port = bind_server(host, port, tries=50)
    url = f"http://{host}:{final_port}"
    print(f"\n{TITLE}\nMode web local\nURL: {url}")
    if final_port != port:
        print(f"Port {port} occupé, bascule automatique vers {final_port}.")
    if not no_open:
        threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nArrêt demandé.")
    finally:
        server.shutdown()
        server.server_close()
        print("Serveur arrêté.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    global DEFAULT_THEME

    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--cli", action="store_true", help="Mode texte minimal")
    parser.add_argument("--port", type=int, default=None, help="Port HTTP")
    parser.add_argument("--host", default="127.0.0.1", help="Host bind")
    parser.add_argument("--no-open", action="store_true", help="Ne pas ouvrir le navigateur")
    parser.add_argument("--self-test", action="store_true", help="Tests de cohérence tables")
    args = parser.parse_args(argv)

    if args.self_test:
        ok, errors = self_test()
        if ok:
            print("SELF-TEST OK")
            return 0
        print("SELF-TEST KO")
        for e in errors:
            print("-", e)
        return 1
    run_web(args.host, int(port), open_browser, theme)
    return 0

    if args.cli:
        return run_cli()

    if args.port is None:
        port, auto_open, _ = ask_start(8787)
        return run_web(args.host, port, not auto_open)
    return run_web(args.host, args.port, args.no_open)

    if args.cli:
        return run_cli()

    if args.port is None:
        port, auto_open, theme = ask_start(8787)
        DEFAULT_THEME = theme
        return run_web(args.host, port, not auto_open)

    DEFAULT_THEME = "neon"
    return run_web(args.host, args.port, args.no_open)


if __name__ == "__main__":
    raise SystemExit(main())
