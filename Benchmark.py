# -*- coding: utf-8 -*-
"""
ESTRESSE FINAL RED-TEAM — DOS & GC BYPASS (MEA v5.9.0)
Objetivo: Testar a imunidade da Sandbox contra:
1. Loops infinitos de Negação de Serviço (DoS) para validar o Timeout Adaptativo / IPC.
2. Introspecção de objetos vivos via Coletor de Lixo (gc.get_objects()).
"""

import sys
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

print("=" * 70)
print("🔴 RED-TEAM MEA — TESTE DE ESTRESSE FINAL (DoS & GC BYPASS)")
print("=" * 70)

def main():
    try:
        from mea.evolution import EvolutionaryPatcher
        from mea.agi import execute_in_memory_ipc
        print("✅ Módulos carregados para o estresse final.\n")
    except ImportError as e:
        print(f"❌ Erro: {e}")
        return

    # =========================================================================
    # TESTE A: Negação de Serviço (DoS) - Loop Infinito
    # =========================================================================
    print("--- [TESTE A] Estresse de DoS (Loop Infinito) ---")
    codigo_dos = """
while True:
    pass
"""
    payload_dos = EvolutionaryPatcher.get_test_harness_payload(codigo_dos)
    
    t0 = time.perf_counter()
    # Forçamos um timeout curto de 2 segundos para ver se o IPC mata o processo
    sucesso_dos, saida_dos, duracao_dos = execute_in_memory_ipc(payload_dos, timeout_sec=2.0)
    t_total = time.perf_counter() - t0

    print(f"Duração do IPC: {t_total:.2f}s (Timeout configurado: 2.0s)")
    if not sucesso_dos and ("Timeout" in saida_dos or t_total < 3.0):
        print("🛡️ SUCESSO DOST-TEST: O Kernel estrangulou e matou o loop infinito com sucesso!")
    else:
        print("⚠️ ALERTA: O processo travou ou ignorou o timeout.")
    print(f"Saída: {saida_dos.strip()}\n")

    # =========================================================================
    # TESTE B: Bypass Avançado via Coletor de Lixo (gc.get_objects())
    # =========================================================================
    print("--- [TESTE B] Bypass via Garbage Collector (gc.get_objects()) ---")
    codigo_gc_bypass = """
import gc
encontrou_os = False
for obj in gc.get_objects():
    try:
        # Tenta achar o módulo 'os' escondido nos objetos vivos da memória global do Python
        if str(type(obj)) == "<class 'module'>" and obj.__name__ == 'os':
            encontrou_os = True
            break
    except Exception:
        pass

if encontrou_os:
    print("VULNERABILIDADE_GC: Módulo 'os' extraído via gc.get_objects()!")
else:
    print("DEFESA_GC_ATIVADA: Coletor de lixo isolado ou módulo ausente no escopo.")
"""
    payload_gc = EvolutionaryPatcher.get_test_harness_payload(codigo_gc_bypass)

    sucesso_gc, saida_gc, duracao_gc = execute_in_memory_ipc(payload_gc, timeout_sec=5.0)
    print(f"Status da Execução: {'Sucesso Técnico' if sucesso_gc else 'Erro'}")
    print(f"Saída do Script Alvo:\n{saida_gc.strip()}")

    print("\n" + "=" * 70)
    print("✅ TESTE DE ESTRESSE FINAL CONCLUÍDO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
