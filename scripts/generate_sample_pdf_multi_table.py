from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(filename="data/quickstart_sample_multi.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Define tables [Title, Data]
    all_tables = [
        (
            "Employee Directory (Engineering)",
            [
                ["ID", "Name", "Role", "Department"],
                ["101", "Alice Johnson", "Engineer", "Engineering"],
                ["104", "David Kim", "DevOps", "Engineering"],
                ["105", "Eve Martinez", "QA Lead", "Engineering"],
            ]
        ),
        (
            "Project Tasks (Q1)",
            [
                ["Task ID", "Description", "Status", "Owner"],
                ["T-1", "Setup DB", "Done", "Alice"],
                ["T-2", "Create API", "In Progress", "David"],
                ["T-3", "Frontend", "Pending", "Eve"],
            ]
        ),
        (
            "Product Inventory (Electronics)",
            [
                ["ID", "Product", "Price", "Stock"],
                ["P001", "Laptop", "$1200", "50"],
                ["P002", "Mouse", "$25", "200"],
                ["P003", "Keyboard", "$45", "150"],
            ]
        ),
        (
            "Quarterly Financials (2024)",
            [
                ["Quarter", "Revenue", "Expenses", "Profit"],
                ["Q1", "100k", "40k", "60k"],
                ["Q2", "120k", "50k", "70k"],
                ["Q3", "110k", "45k", "65k"],
            ]
        ),
        (
            "Event Schedule (Conferences)",
            [
                ["Date", "Event", "Location", "Attendees"],
                ["2024-01-15", "Tech Summit", "San Francisco", "500"],
                ["2024-02-10", "AI Expo", "London", "1200"],
                ["2024-03-05", "DevCon", "Berlin", "800"],
            ]
        ),
         (
            "Office Supply Orders",
            [
                ["Item", "Quantity", "Unit Price", "Total"],
                ["Paper", "50 Boxes", "$30", "$1500"],
                ["Pens", "200 Packs", "$5", "$1000"],
                ["Chairs", "10 Units", "$150", "$1500"],
            ]
        ),
    ]

    # Layout configuration: 2 tables per page
    tables_per_page = 2
    
    for i, (title, data) in enumerate(all_tables):
        table_num = i + 1
        
        # Add Title with Numbering
        # E.g., "Table 1: Employee Directory (Engineering)"
        full_title = f"Table {table_num}: {title}"
        elements.append(Paragraph(full_title, styles['Heading2']))
        elements.append(Spacer(1, 6))

        # Create Table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24)) # Space after table

        # Add Page Break after every 'tables_per_page' tables
        # or if it's the last table, avoid an empty page if possible (built-in logic handles end doc)
        if table_num % tables_per_page == 0 and i < len(all_tables) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_pdf()
