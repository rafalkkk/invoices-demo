from pathlib import Path
from invoice_service import analyze_invoice_from_file, extract_invoice_data
from json_writer import save_json


def main():
    input_dir = Path("sample_docs")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    invoice_files = list(input_dir.glob("*.pdf"))

    if not invoice_files:
        print(f"No invoice files found in: {input_dir}")
        return

    for input_file in invoice_files:
        try:
            result = analyze_invoice_from_file(str(input_file))
            invoice_data = extract_invoice_data(result)

            output_file = output_dir / f"{input_file.stem}_result.json"
            save_json(invoice_data, str(output_file))

            print(f"Invoice data saved to: {output_file}")

        except Exception as e:
            print(f"Error processing {input_file.name}: {e}")


if __name__ == "__main__":
    main()