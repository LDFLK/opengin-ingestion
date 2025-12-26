from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(filename="data/quickstart_sample.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Data for 5 pages
    # Each page will have a table with a title
    table_data_list = [
        [
            ["ID", "Name", "Role", "Department"],
            ["101", "Alice Johnson", "Engineer", "Engineering"],
            ["102", "Bob Smith", "Manager", "Sales"],
            ["103", "Charlie Brown", "Analyst", "Marketing"],
        ],
        [
            ["ID", "Product", "Price", "Stock"],
            ["P001", "Laptop", "$1200", "50"],
            ["P002", "Mouse", "$25", "200"],
            ["P003", "Keyboard", "$45", "150"],
        ],
        [
            ["Date", "Event", "Location", "Attendees"],
            ["2024-01-15", "Kickoff", "Room A", "20"],
            ["2024-02-10", "Review", "Room B", "15"],
            ["2024-03-05", "Launch", "Main Hall", "100"],
        ],
        [
            ["Quarter", "Revenue", "Expenses", "Profit"],
            ["Q1", "100k", "40k", "60k"],
            ["Q2", "120k", "50k", "70k"],
            ["Q3", "110k", "45k", "65k"],
        ],
        [
            ["Task ID", "Description", "Status", "Owner"],
            ["T-1", "Setup DB", "Done", "Alice"],
            ["T-2", "Create API", "In Progress", "Bob"],
            ["T-3", "Frontend", "Pending", "Charlie"],
        ],
    ]

    titles = [
        "Employee Directory",
        "Product Inventory",
        "Event Schedule",
        "Quarterly Financials",
        "Project Tasks"
    ]

    for i, data in enumerate(table_data_list):
        # Add Title
        title_text = titles[i] if i < len(titles) else f"Page {i+1} Table"
        elements.append(Paragraph(title_text, styles['Heading1']))
        elements.append(Spacer(1, 12))

        # Create Table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.cyan),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
        # Add Page Break unless it's the last page
        if i < len(table_data_list) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_pdf()
