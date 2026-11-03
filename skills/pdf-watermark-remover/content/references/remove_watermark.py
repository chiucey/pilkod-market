from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, NameObject
import re


def remove_watermark(input_path, output_path):
    """Remove watermark from PDF by removing watermark XObject rendering code."""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    watermark_patterns = [
        rb"/Artifact\s*<</Subtype\s*/Watermark.*?>>\s*BDC.*?EMC",
        rb"Watermark\s*/Type\s*/Pagination\s*>>\s*BDC.*?EMC",
    ]

    for page_num, page in enumerate(reader.pages):
        if "/Contents" not in page:
            writer.add_page(page)
            continue

        contents = page["/Contents"]
        if isinstance(contents, ArrayObject):
            new_array = ArrayObject()
            for c in contents:
                c = c.get_object()
                if hasattr(c, "get_data"):
                    data = c.get_data()
                    for pattern in watermark_patterns:
                        new_data = re.sub(
                            pattern, b"", data, flags=re.IGNORECASE | re.DOTALL
                        )
                        if new_data != data:
                            data = new_data
                            break
                    c.set_data(data)
                new_array.append(c)
            page[NameObject("/Contents")] = new_array
        else:
            contents = contents.get_object()
            if hasattr(contents, "get_data"):
                data = contents.get_data()
                for pattern in watermark_patterns:
                    new_data = re.sub(
                        pattern, b"", data, flags=re.IGNORECASE | re.DOTALL
                    )
                    if new_data != data:
                        data = new_data
                        break
                contents.set_data(data)

        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


if __name__ == "__main__":
    import sys

    input_file = sys.argv[1] if len(sys.argv) > 1 else "1.pdf"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "1_no_watermark.pdf"

    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

    reader = PdfReader(input_file)
    print(f"Pages: {len(reader.pages)}")

    remove_watermark(input_file, output_file)
    print(f"Done! Watermark removed and saved to {output_file}")
