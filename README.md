# ABTP – Automate Boring Tasks with Python

Willkommen zurück im aufgefrischten ABTP-Repository! Hier sammelst du Skripte und Workflows, die wiederkehrende Aufgaben automatisieren – egal ob es um Dateiverarbeitung, Web-Scraping oder kleine Helferlein für den Alltag geht.

## Ziele des Projekts
- **Produktivität steigern:** Spare dir manuelle Klickarbeit durch kleine, fokussierte Automationsskripte.
- **Wissen teilen:** Zeige, wie du typische „Automate the Boring Stuff with Python“-Ideen in der Praxis umsetzt.
- **Wiederverwendbarkeit fördern:** Jede Aufgabe ist so strukturiert, dass andere sie nachvollziehen, anpassen und erweitern können.

## Projektstruktur
```
Priv-Projects/ABTP/
├─ README.md              ← Dieses Dokument
├─ tasks/
│  ├─ <task-name>/        ← Einzelne Automationsaufgaben
│  │  ├─ main.py          ← Einstiegspunkt pro Aufgabe
│  │  ├─ config/          ← Optional: Einstellungen, Templates
│  │  └─ docs.md          ← Kurze Erklärung & Beispiele
└─ utils/                 ← Helferfunktionen, die mehrere Tasks verwenden
```
> Passe die Struktur gerne an deine tatsächlichen Verzeichnisse an. Wichtig ist, dass jedes Skript schnell verständlich bleibt.

## Loslegen
1. **Repository aktualisieren**
   ```powershell
   git pull
   ```
2. **Python-Umgebung vorbereiten**  
   Installiere Abhängigkeiten oder lege eine virtuelle Umgebung an:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt   # falls vorhanden
   ```
3. **Eine Aufgabe starten**  
   ```powershell
   python tasks/<task-name>/main.py
   ```
   Ergänze Parameter oder Konfigurationsdateien nach Bedarf – idealerweise dokumentiert in `docs.md`.

## Eigene Aufgaben hinzufügen
1. Erstelle im `tasks/`-Ordner einen neuen Unterordner.
2. Implementiere dein Skript in `main.py` und beschreibe Nutzung & Stolperfallen in einer kurzen `docs.md`.
3. Falls du wiederkehrende Hilfsfunktionen baust, lege sie in `utils/` ab, damit andere Tasks davon profitieren.
4. Ergänze Beispieleingaben, Dateitemplates oder Konfigurationsdateien, damit Nutzer sofort loslegen können.

## Best Practices
- Halte deine Skripte modular und nutze Funktionen oder Klassen für klare Schnittstellen.
- Dokumentiere Eingaben, Ausgaben und erwartete Umgebung (z. B. API-Keys, Ordnerstruktur).
- Füge Tests oder einfache Checks hinzu, wenn eine Aufgabe komplexer wird.
- Verweise in diesem README auf neue Aufgaben, sobald du sie hinzufügst.

## Nächste Schritte
- Liste in diesem README die vorhandenen Automationsaufgaben samt Kurzbeschreibung.
- Ergänze Badges, GIFs oder Screenshots, um die Ergebnisse anschaulich zu machen.
- Überlege, ob du ein kleines CLI-Menü oder ein Launch-Skript bereitstellst, das alle Tasks auffindbar macht.



