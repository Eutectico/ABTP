# Markdown zu PDF Konverter (`md2pdf.py`)

Dieses Skript ist Teil der ABTP-Sammlung und konvertiert Markdown-Dateien (`.md`) in PDF-Dokumente. Es versucht zunächst, das Rendering mit **WeasyPrint** (HTML/CSS-Engine) durchzuführen. Falls WeasyPrint nicht verfügbar ist, fällt es automatisch auf **xhtml2pdf** zurück, das komplett in Python implementiert ist.

## Features
- Einzelne Dateien oder ganze Verzeichnisse konvertieren  
- Optional rekursiv durch Unterordner navigieren  
- Anpassbare CSS-Stylesheets  
- Sicheres Überschreiben vorhandener PDFs (`--overwrite`)  
- Detaillierte Fehlermeldungen, wenn Konvertierungen scheitern

## Voraussetzungen
Installiere die Abhängigkeiten aus `requirements.txt`:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Hinweis für Windows: WeasyPrint benötigt zusätzliche Systembibliotheken (GTK/Pango). Alternativ kannst du nur mit `xhtml2pdf` arbeiten, indem du WeasyPrint nicht installierst.

## Nutzung

### Einzelne Datei
```powershell
python md2pdf.py path\to\file.md
```
Ergebnis: `path\to\file.pdf`.

### Ausgabepfad festlegen
```powershell
python md2pdf.py path\to\file.md --output path\to\custom.pdf
```

### Verzeichnis konvertieren
```powershell
python md2pdf.py path\to\markdown-folder --out-dir path\to\pdf-folder
```
Mit `--recursive` werden Unterordner berücksichtigt.

### Eigenes Stylesheet verwenden
```powershell
python md2pdf.py README.md --css custom.css
```
Das CSS wird entweder direkt als Inline-Style eingebettet (xhtml2pdf) oder als externes Stylesheet eingebunden (WeasyPrint).

### Überschreiben erzwingen
```powershell
python md2pdf.py docs --out-dir output --overwrite
```

## Fehlersuche
- **"Missing dependency: markdown"** – Installiere `markdown` mit `pip install markdown`.
- **WeasyPrint ImportError/OSError** – Überprüfe Installationsvoraussetzungen laut WeasyPrint-Dokumentation.
- **xhtml2pdf fehlgeschlagen** – Prüfe Fehlermeldungen im Terminal und stelle sicher, dass `reportlab` installiert ist.
- **"No Markdown files found"** – Prüfe Pfad und Dateiendungen; `--recursive` aktivieren, falls Unterordner durchsucht werden sollen.

## Weiterentwicklung
- Ergänze Beispielkonfigurationen (`.css`, Templates) im Ordner.
- Schreibe Unit-Tests für kritische Pfade wie CSS-Laden oder Pfadberechnung.
- Dokumentiere neue Optionen im Skript und ergänze sie in diesem README.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
