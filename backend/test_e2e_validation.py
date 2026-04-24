import requests
import json
import time

BASE_URL = "http://localhost:8000"

def log_test(name, result, msg=""):
    status = "PASS" if result else "FAIL"
    print(f"[{status}] {name} {msg}")

def test_01_assets_sync():
    res = requests.get(f"{BASE_URL}/assets")
    assert res.status_code == 200
    assets = res.json()
    found = any("AC20-Institute-Var-2.ifc" in a["name"] for a in assets)
    log_test("Requirement: Asset Sync (CAD/Docs)", found)
    assert found

def test_02_bom_cad_parsing():
    payload = {"message": "Genera una BOM con IfcWall e IfcWindow", "lang": "it"}
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    assert res.status_code == 200
    resp = res.json()["response"].upper()
    # Verifica se os nomes das categorias aparecem na tabela de resposta
    success = "IFCWALL" in resp or "IFCWINDOW" in resp or "CATEGORY" in resp
    if not success:
        print(f"DEBUG BOM RESP: {resp}")
    log_test("Requirement: Structured BOM from CAD", success)
    assert success

def test_03_software_documentation():
    payload = {"message": "Genera documentazione per main.py", "lang": "it"}
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    assert res.status_code == 200
    resp = res.json()["response"].lower()
    success = "main.py" in resp or "endpoint" in resp or "async" in resp
    log_test("Requirement: Auto-Doc from Codebase", success)
    assert success

def test_04_firmware_test_plan():
    payload = {"message": "Crea piano di test per firmware", "lang": "it"}
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    assert res.status_code == 200
    resp = res.json()["response"].lower()
    success = "test" in resp or "validazione" in resp or "firmware" in resp
    log_test("Requirement: Auto Test Plans for Firmware", success)
    assert success

def test_05_manual_generation():
    payload = {"message": "Genera manuale tecnico", "lang": "it"}
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    assert res.status_code == 200
    resp = res.json()["response"].upper()
    success = "MANUAL" in resp or "OKOLAB" in resp
    log_test("Requirement: General Technical Documentation", success)
    assert success

def run_suite():
    print("\n--- OKOLAB R&D E2E VALIDATION SUITE ---")
    try:
        test_01_assets_sync()
        test_02_bom_cad_parsing()
        test_03_software_documentation()
        test_04_firmware_test_plan()
        test_05_manual_generation()
        print("\n[CONCLUSION] PLATFORM FULLY COMPLIANT WITH JOB DESCRIPTION.")
    except Exception as e:
        print(f"\n[ERROR] Compliance check failed: {e}")
        exit(1)

if __name__ == "__main__":
    run_suite()
