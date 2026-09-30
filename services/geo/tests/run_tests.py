"""Runner for all VAYU-RAKSHA test modules."""
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "tests")

import test_cascade
import test_counterfactual
import test_mosdac
import test_climada_curves
import test_agents

modules = [
    ("test_cascade", test_cascade),
    ("test_counterfactual", test_counterfactual),
    ("test_mosdac", test_mosdac),
    ("test_climada_curves", test_climada_curves),
    ("test_agents", test_agents),
]

total = 0
for name, mod in modules:
    test_funcs = [f for f in dir(mod) if f.startswith("test_")]
    for tf in test_funcs:
        fn = getattr(mod, tf)
        fn()
        total += 1
    print(f"PASS: {name} ({len(test_funcs)} tests)")

print(f"\nSUCCESS: All {total} tests passed cleanly!")
