#!/usr/bin/env python3

import subprocess
import os
import sys
import re
from collections import defaultdict

# Couleurs ANSI
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

BANNER = f"""{GREEN}
            ##                       ###                          ##
            ##                        ##                          ##
 ######    #####    #####   ######    ##      ##  ##   #####     #####    ####    ######
  ##  ##    ##     ##        ##  ##   #####   ##  ##   ##  ##     ##     ##  ##    ##  ##
  ##        ##      #####    ##  ##   ##  ##  ##  ##   ##  ##     ##     ######    ##
  ##        ## ##       ##   #####    ##  ##  ##  ##   ##  ##     ## ##  ##        ##
 ####        ###   ######    ##      ###  ##   ######  ##  ##      ###    #####   ####
                            ####

                ----------- BY MISTERFOUGERE01 -----------
{RESET}"""

def load_paths(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{RED}Erreur : le fichier '{filename}' est introuvable.{RESET}")
        sys.exit(1)

def extract_error(stderr):
    if "401" in stderr:
        return "401 Unauthorized"
    elif "403" in stderr:
        return "403 Forbidden"
    elif "404" in stderr:
        return "404 Not Found"
    elif "400" in stderr:
        return "400 Bad Request"
    elif "Connection refused" in stderr:
        return "Connection refused"
    else:
        match = re.search(r'\b\d{3}\b.*', stderr)
        if match:
            return match.group(0).strip()
        return "Erreur inconnue"

def main():
    os.system("clear")
    print(BANNER)

    ip = input("Adresse IP de la cible         : ").strip()
    port = input("Port RTSP (défaut = 554)      : ").strip()
    auth = input("Authentification (user:pass)  : ").strip()

    if not port:
        port = "554"

    base = f"rtsp://{auth + '@' if auth else ''}{ip}:{port}"
    paths = load_paths("paths.txt")

    error_stats = defaultdict(int)
    valid_urls = []

    print(f"\nLancement du scan sur {base}\n")

    for path in paths:
        url = f"{base}{path}"
        print(f"Test: {url} ... ", end="")
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-timeout", "5000000", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                print(f"{GREEN}OK{RESET} ➤ {url}")
                valid_urls.append(url)
            else:
                error = extract_error(result.stderr)
                error_stats[error] += 1
                print(f"{RED}FAIL{RESET} ({error})")
        except Exception as e:
            error_stats["Erreur d'exécution"] += 1
            print(f"{RED}Erreur : {e}{RESET}")

    print(f"\n{CYAN}=== RÉCAPITULATIF DES ERREURS ==={RESET}")
    if error_stats:
        for err, count in error_stats.items():
            print(f"{RED}- {err}: {count}{RESET}")
    else:
        print(f"{GREEN}Aucune erreur détectée !{RESET}")

    print(f"\n{CYAN}=== URL(S) VALIDE(S) DÉTECTÉE(S) ==={RESET}")
    if valid_urls:
        for url in valid_urls:
            print(f"{GREEN}- {url}{RESET}")
    else:
        print(f"{RED}Aucune URL valide trouvée.{RESET}")

    print(f"\n{GREEN}Scan terminé.{RESET}")

if __name__ == "__main__":
    main()
