from fpdf import FPDF
import os  # Add this import

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Association Rules Report', 0, 1, 'C')
        self.ln(5)  # Add some space after the header

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def table(self, data):
        self.set_font('Arial', 'B', 12)
        col_widths = [40, 30, 30, 90]  # Adjust column widths as needed
        headers = ['Item', 'Support', 'Confidence', 'Explanation']
        
        # Print header
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()

        # Print rows
        self.set_font('Arial', '', 12)
        for index, row in data.iterrows():
            # Calculate the height of the row
            explanation_lines = self.multi_cell(col_widths[3], 10, row['Penjelasan'], 0, split_only=True)
            row_height = max(10, len(explanation_lines) * 10)

            self.cell(col_widths[0], row_height, row['Item'], 1)
            self.cell(col_widths[1], row_height, str(row['Support']), 1)
            self.cell(col_widths[2], row_height, str(row['Confidence']), 1)
            x, y = self.get_x(), self.get_y()
            self.multi_cell(col_widths[3], 10, row['Penjelasan'], 1)
            self.set_xy(x + col_widths[3], y)
            self.ln(row_height)

def create_pdf(report_data, file_path, uploaded_filename):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.set_font('Arial', '', 12)
    # Remove file extension
    filename_without_ext = os.path.splitext(uploaded_filename)[0]
    pdf.cell(0, 10, filename_without_ext, 0, 1, 'C')
    pdf.ln(10)  # Add some space after the filename
    pdf.table(report_data)
    pdf.output(file_path)