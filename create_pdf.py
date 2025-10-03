from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas('test_claim.pdf', pagesize=letter)
c.drawString(100, 750, 'CLAIMS DOCUMENT')
c.drawString(100, 700, 'Policy Number: POL-12345')
c.drawString(100, 650, 'Claim Number: CLM-67890')
c.drawString(100, 600, 'Date of Loss: 2025-01-15')
c.drawString(100, 550, 'Description: Vehicle accident with property damage')
c.drawString(100, 500, 'Estimated Loss: $15,000')
c.drawString(100, 450, 'This is a test claims document for the Claims Triage Agent.')
c.save()
print('PDF created successfully')
