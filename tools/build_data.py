"""Convert mhdb-wilds-data merged JSON into a compact English dataset for the planner."""
import json, sys, os, re

SRC = sys.argv[1]
OUT = sys.argv[2]

def load(p):
    with open(os.path.join(SRC, p), encoding="utf-8") as f:
        return json.load(f)

def en(d):
    if not isinstance(d, dict):
        return d or ""
    t = d.get("en") or ""
    return re.sub(r"\s*\r?\n\s*", " ", t).strip()

# ---------- skills ----------
skills_raw = load("Skill.json")
skill_index = {}   # game_id -> compact index
skills = []
for s in skills_raw:
    name = en(s["names"])
    if not name:
        continue
    ranks = []
    for r in s["ranks"]:
        rk = {"l": r["level"], "d": en(r.get("descriptions"))}
        if r.get("names"):
            rk["n"] = en(r["names"])
        if r.get("set_pieces_required"):
            rk["p"] = r["set_pieces_required"]
        ranks.append(rk)
    ranks.sort(key=lambda x: x["l"])
    skill_index[s["game_id"]] = len(skills)
    skills.append({"n": name, "d": en(s.get("descriptions")), "k": s["kind"], "r": ranks})

def map_skills(d):
    out = {}
    for k, v in (d or {}).items():
        k = int(k)
        if k in skill_index and v:
            out[skill_index[k]] = out.get(skill_index[k], 0) + v
    return [[k, v] for k, v in sorted(out.items())]

ELEMS = ["fire", "water", "thunder", "ice", "dragon"]

# ---------- armor ----------
armor = []
sets_out = []
for a in load("Armor.json"):
    set_name = en(a["names"])
    set_idx = len(sets_out)
    sets_out.append({"n": set_name, "r": a["rarity"]})
    for p in a["pieces"]:
        nm = en(p["names"])
        if not nm:
            continue
        armor.append({
            "n": nm,
            "s": set_idx,
            "k": p["kind"],
            "r": a["rarity"],
            "b": p["defense"]["base"],
            "m": p["defense"]["max"],
            "e": [p["resistances"].get(e, 0) for e in ELEMS],
            "sl": p.get("slots") or [],
            "sk": map_skills(p.get("skills")),
        })

# ---------- decorations ----------
decos = []
for d in load("Accessory.json"):
    nm = en(d["names"])
    if not nm:
        continue
    decos.append({
        "n": nm, "lv": d["level"], "on": "w" if d["allowed_on"] == "weapon" else "a",
        "r": d["rarity"], "sk": map_skills(d.get("skills")),
    })

# ---------- talismans ----------
tals = []
for a in load("Amulet.json"):
    if a.get("is_random"):
        continue
    for r in a["ranks"]:
        nm = en(r["names"])
        if not nm:
            continue
        tals.append({"n": nm, "r": r["rarity"], "sk": map_skills(r.get("skills"))})

# ---------- weapons ----------
WTYPES = [
    ("GreatSword", "great-sword", "Great Sword"), ("LongSword", "long-sword", "Long Sword"),
    ("SwordShield", "sword-shield", "Sword & Shield"), ("DualBlades", "dual-blades", "Dual Blades"),
    ("Hammer", "hammer", "Hammer"), ("HuntingHorn", "hunting-horn", "Hunting Horn"),
    ("Lance", "lance", "Lance"), ("Gunlance", "gunlance", "Gunlance"),
    ("SwitchAxe", "switch-axe", "Switch Axe"), ("ChargeBlade", "charge-blade", "Charge Blade"),
    ("InsectGlaive", "insect-glaive", "Insect Glaive"), ("LightBowgun", "light-bowgun", "Light Bowgun"),
    ("HeavyBowgun", "heavy-bowgun", "Heavy Bowgun"), ("Bow", "bow", "Bow"),
]
SHARP = ["red", "orange", "yellow", "green", "blue", "white", "purple"]
wtypes = []
weapons = []
for fname, kind, label in WTYPES:
    ti = len(wtypes)
    wtypes.append(label)
    for w in load(f"weapons/{fname}.json"):
        nm = en(w.get("names"))
        if not nm:
            continue
        o = {"n": nm, "t": ti, "r": w["rarity"], "a": w["attack_raw"], "af": w["affinity"],
             "df": w.get("defense", 0), "sl": w.get("slots") or [], "sk": map_skills(w.get("skills"))}
        sp = []
        for s in w.get("specials") or []:
            typ = s.get("element") or s.get("status")
            sp.append([typ, s["raw"], 1 if s.get("hidden") else 0])
        if sp:
            o["sp"] = sp
        if w.get("sharpness"):
            o["sh"] = [w["sharpness"].get(c, 0) for c in SHARP]
            o["hc"] = w.get("handicraft") or []
        x = {}
        if w.get("phial"):
            ph = w["phial"]
            x["Phial"] = (ph if isinstance(ph, str) else (ph.get("kind", "") + (f" {ph['damage']}" if ph.get("damage") else ""))).replace("-", " ").title()
        if w.get("shell"):
            x["Shelling"] = f"{w['shell'].title()} Lv{w.get('shell_level', '')}"
        if w.get("kinsect_level") is not None:
            x["Kinsect Lv"] = str(w["kinsect_level"])
        if w.get("coatings"):
            x["Coatings"] = ", ".join(c.replace("-", " ").title() for c in w["coatings"])
        if w.get("ammo"):
            x["Ammo"] = ", ".join(f"{a['kind'].replace('-', ' ').title()} {a['level']} ({a['capacity']})" for a in w["ammo"] if a.get("capacity"))
        if x:
            o["x"] = x
        weapons.append(o)

# ---------- Artian / Gogma tagging ----------
ARTIAN_R8 = {"Varianza", "Dimensius", "Verdoloto", "Tiltkreise", "Moteurvankel", "Omiltika", "Skyscraper",
             "Argenesis", "Mundus Altus", "Chrono Gear", "Diprielcha", "Animilater", "Greifen", "Angelbein"}
GOGMA = {"Ostrak Oblivion", "Headsman's Hamus", "Kyrie Verd", "Eternal Cusp", "Bound Admonition", "Onyx Choros",
         "Aether Pike", "Auguring Omen", "Wicked Regnum", "Promised Abyss", "Limbo Llor", "Bethorned Agony",
         "Trembling Hels", "Calamitous Angel"}
FOCUS = {(200, -10): "A", (180, 15): "F", (190, 0): "E"}
FOCUS_LABEL = {"A": "Attack focus", "F": "Affinity focus", "E": "Element focus"}
found_gogma = set()
for w in weapons:
    if w["n"].startswith("Artian ") and w["r"] in (6, 7):
        w["art"] = 1
    elif w["n"] in ARTIAN_R8:
        w["art"] = 2
    elif w["n"] in GOGMA:
        f = FOCUS.get((w["a"], w["af"]))
        if not f:
            raise SystemExit(f"Unknown Gogma variant {w['n']} {w['a']} {w['af']}")
        w["art"] = 3
        w["fo"] = f
        w["n"] = f"{w['n']} ({FOCUS_LABEL[f]})"
        found_gogma.add(w["n"].split(" (")[0])
print("gogma lines:", sorted(found_gogma), "missing:", sorted(GOGMA - found_gogma))

kin = json.load(open(sys.argv[3], encoding="utf-8"))["list"]

data = {"skills": skills, "sets": sets_out, "armor": armor, "decos": decos,
        "tals": tals, "wtypes": wtypes, "weapons": weapons, "kinsects": kin}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
print({k: len(v) for k, v in data.items()}, os.path.getsize(OUT))
