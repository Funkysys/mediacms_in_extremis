#!/usr/bin/env python3
"""
Script de vérification de santé pour le service de traitement vidéo.
Vérifie que le service est opérationnel et peut accéder aux dossiers nécessaires.
"""
import os
import sys
from pathlib import Path

# Dossiers à vérifier
REQUIRED_DIRS = [
    '/videos/originals',
    '/videos/encoded',
    '/videos/thumbnails'
]

def check_directories():
    """Vérifie que les dossiers requis existent et sont accessibles en écriture."""
    missing = []
    not_writable = []
    
    for dir_path in REQUIRED_DIRS:
        path = Path(dir_path)
        if not path.exists():
            missing.append(str(path))
            continue
            
        if not os.access(dir_path, os.W_OK):
            not_writable.append(str(path))
    
    return missing, not_writable

def main():
    """Fonction principale."""
    # Vérifier les dossiers
    missing, not_writable = check_directories()
    
    if missing or not_writable:
        if missing:
            print(f"ERREUR: Dossiers manquants: {', '.join(missing)}")
        if not_writable:
            print(f"ERREUR: Dossiers sans accès en écriture: {', '.join(not_writable)}")
        sys.exit(1)
    
    # Si on arrive ici, tout va bien
    print("OK: Tous les contrôles de santé sont passés avec succès")
    sys.exit(0)

if __name__ == "__main__":
    main()
