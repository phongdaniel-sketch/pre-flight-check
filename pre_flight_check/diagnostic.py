import sys
import os

print("--- DIAGNOSTIC START ---")
print(f"Python path: {sys.executable}")
print(f"Working directory: {os.getcwd()}")

try:
    print("Attempting to import crewai...")
    import crewai
    print(f"CrewAI imported successfully. Version: {getattr(crewai, '__version__', 'unknown')}")
except Exception as e:
    print(f"FAILED to import crewai: {e}")
    sys.exit(1)

try:
    print("Attempting to import AntigravityCrew from crew.py...")
    # Add src to path
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from crew import AntigravityCrew
    print("AntigravityCrew imported successfully.")
except Exception as e:
    print(f"FAILED to import AntigravityCrew: {e}")
    sys.exit(1)

print("--- DIAGNOSTIC END ---")
