#!/bin/bash

# Script zum Löschen aller Confluence-Result-Ordner,
# die NICHT über Symlinks verlinkt sind und NICHT von heute sind

RESULTS_DIR="/home/anton/DCPT/dc-app-performance-toolkit/app/results/confluence"

cd "$RESULTS_DIR" || exit 1

# Alle Symlink-Ziele sammeln
echo "=== Sammle Symlink-Ziele ==="
linked_dirs=$(find . -maxdepth 1 -type l -exec readlink {} \; | sort -u)
echo "$linked_dirs"
echo ""

# Heutiges Datum im Format YYYY-MM-DD
today=$(date +%Y-%m-%d)
echo "=== Heutiges Datum: $today ==="
echo ""

# Counter
deleted=0
kept_linked=0
kept_today=0

echo "=== Verarbeite Ordner ==="
# Alle Ordner durchgehen die mit 20 beginnen (Datum-Pattern)
for dir in 20*/; do
    [ -d "$dir" ] || continue  # Skip wenn nicht existiert
    dir_name=${dir%/}

    # Prüfe ob heute
    if [[ $dir_name == ${today}* ]]; then
        echo "BEHALTEN (heute): $dir_name"
        ((kept_today++))
        continue
    fi

    # Prüfe ob über Symlink verlinkt
    if echo "$linked_dirs" | grep -q "^${dir_name}$"; then
        echo "BEHALTEN (linked): $dir_name"
        ((kept_linked++))
        continue
    fi

    # Ordner löschen
    echo "LÖSCHE: $dir_name"
    rm -rf "$dir_name"
    if [ $? -eq 0 ]; then
        ((deleted++))
    else
        echo "  FEHLER beim Löschen von $dir_name"
    fi
done

echo ""
echo "=== ZUSAMMENFASSUNG ==="
echo "Gelöscht: $deleted Ordner"
echo "Behalten (via Symlinks): $kept_linked Ordner"
echo "Behalten (von heute): $kept_today Ordner"
echo ""
echo "=== Verbleibende Struktur ==="
ls -lh | head -20
