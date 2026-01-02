from pathlib import Path

def main():
    source_file = Path("messy_code.js")

    if not source_file.exists():
        print("Fine not found!")
        return
    
    print(f"__Reading {source_file.name}")
    code = source_file.read_text(encoding="utf-8")

    print(code)

    copy_file = Path("messy_code_copy.js")
    copy_file.write_text(code)
    print("\n COpied to messy_code_copy.js")

if __name__ == "__main__":
    main()