# Wilds Build Forge

A build planner for **Monster Hunter Wilds**. Equip any weapon, armor, decorations and talisman and see:

- every skill with its level, max level and the effect at each rank
- set and group bonuses, with how many pieces you have and need
- defense at max upgrade and elemental resistances, including skill bonuses
- weapon attack, affinity, element or status, and sharpness with Handicraft
- Artian and Gogma Artian forging (parts, element matching, reinforcements, Gogma skills)
- kinsects for the Insect Glaive, with stats at the glaive's kinsect level
- appraised (random) talismans with your own skills and slots

Builds save in your browser and can be shared as a build code.

The whole site is one file, `index.html`, with no server or database.

## Running it

Open `index.html` in a browser, or serve the repository with GitHub Pages
(Settings → Pages → Deploy from a branch → `main`, root folder).

## Updating the game data

Game data comes from [mhdb-wilds-data](https://github.com/LartTyler/mhdb-wilds-data).
When it updates, rebuild the page:

```sh
git clone --depth 1 https://github.com/LartTyler/mhdb-wilds-data
python tools/build.py mhdb-wilds-data/output/merged "Month YYYY"
```

That regenerates `index.html` from `src/template.html` (the page's code) and the new data.

## Project layout

| Path | What it is |
|---|---|
| `index.html` | The built site. This is what GitHub Pages serves. |
| `src/template.html` | Page code and styles, with placeholders for the data. |
| `tools/build_data.py` | Converts mhdb-wilds-data into the compact dataset the page uses. |
| `tools/build.py` | Runs the conversion and writes `index.html`. |
| `data/kinsects.json` | Kinsect stats, from [Kiranico](https://mhwilds.kiranico.com/data/kinsects). |

## Data sources and accuracy

- Equipment, skills and decorations: mhdb-wilds-data (game extraction).
- Artian Rarity 8 element and status values: GameWith's Artian weapon pages.
- Artian Rarity 6–7 values and Gogma reinforcement tiers are community estimates.

## License

GPL-3.0, matching the mhdb-wilds-data project this is built on. See `LICENSE`.

This is an unofficial fan project and is not affiliated with Capcom.
Monster Hunter is a trademark of Capcom.
