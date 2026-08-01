from pathlib import Path
from urllib.parse import urlparse
import re
from invoice_service import analyze_invoice_from_url, extract_invoice_data
from json_writer import save_json


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-\.]+", "_", name.strip(), flags=re.UNICODE)
    return name or "invoice"


def get_name_from_url(url: str) -> str:
    parsed = urlparse(url)
    stem = Path(parsed.path).stem

    if stem:
        return sanitize_filename(stem)

    return "invoice"


def load_urls_from_txt(txt_file: str) -> list[str]:
    urls = []

    with open(txt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and line.startswith(("http://", "https://")):
                urls.append(line)

    return urls


def process_urls(urls: list[str], output_dir: str = "output") -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not urls:
        print("No URLs found in input file.")
        return

    for i, url in enumerate(urls, start=1):
        try:
            result = analyze_invoice_from_url(url)
            invoice_data = extract_invoice_data(result)

            base_name = get_name_from_url(url)
            output_file = output_path / f"{base_name}_result.json"

            if output_file.exists():
                output_file = output_path / f"{base_name}_{i}_result.json"

            save_json(invoice_data, str(output_file))
            print(f"Invoice data saved to: {output_file}")

        except Exception as e:
            print(f"Error processing {url}: {e}")


def main():
    txt_file = "urls.txt"

    if not Path(txt_file).exists():
        print(f"File not found: {txt_file}")
        return

    urls = load_urls_from_txt(txt_file)
    process_urls(urls)


if __name__ == "__main__":
    main()