import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

INPUT_FILE = "quotes.csv"
OUTPUT_FILE = "quotes_report.xlsx"

# ---------- 1. Load ----------
df = pd.read_csv(INPUT_FILE, encoding="utf-8")
print(f"Rows loaded: {len(df)}")

# ---------- 2. Clean ----------
df = df.drop_duplicates()                              # remove duplicate rows
df = df.dropna(subset=["text", "author"])              # drop rows missing key fields

df["text"] = df["text"].str.strip().str.strip("“”\"")  # trim spaces and surrounding quote marks
df["author"] = df["author"].str.strip()
df["tags"] = df["tags"].fillna("").str.strip()
df["tags"] = df["tags"].replace("", "none")            # label empty tags

df = df.sort_values("author").reset_index(drop=True)
df = df.rename(columns={"text": "Quote", "author": "Author", "tags": "Tags"})
df.insert(0, "No.", df.index + 1)                      # add a serial number column

print(f"Rows after cleaning: {len(df)}")

# ---------- 3. Summary sheet ----------
summary = df["Author"].value_counts().reset_index()
summary.columns = ["Author", "Number of Quotes"]

# ---------- 4. Styling ----------
header_fill = PatternFill("solid", start_color="1F4E78")
header_font = Font(bold=True, color="FFFFFF")
thin = Side(style="thin", color="CCCCCC")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def format_sheet(ws, widths):
    for i, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    for cell in ws[1]:                                  # header row
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    for row in ws.iter_rows(min_row=2):                 # data rows
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = border

    ws.freeze_panes = "A2"                              # keep header visible when scrolling
    ws.auto_filter.ref = ws.dimensions                  # add filter dropdowns


# ---------- 5. Save to Excel ----------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Quotes", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)

    format_sheet(writer.sheets["Quotes"], widths=[6, 80, 25, 35])
    format_sheet(writer.sheets["Summary"], widths=[30, 18])

print(f"Saved to {OUTPUT_FILE}")