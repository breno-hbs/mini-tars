#!/usr/bin/env python3
"""Gancho de parada: roda os testes antes de o agente encerrar.

Se falharem, devolve código 2 e a mensagem, e o agente continua para corrigir.
Se o gancho já bloqueou uma vez neste turno (stop_hook_active), deixa parar para não entrar em laço.
"""
import json, subprocess, sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
if payload.get("stop_hook_active"):
    sys.exit(0)
if not __import__("os").path.isdir("tests"):
    sys.exit(0)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], capture_output=True, text=True)
if r.returncode not in (0, 5):  # 5 = nenhum teste coletado
    sys.stderr.write("Testes falharam; corrija antes de encerrar:\n" + (r.stdout + r.stderr)[-1500:])
    sys.exit(2)
sys.exit(0)
