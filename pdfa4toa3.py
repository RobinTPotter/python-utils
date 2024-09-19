from fpdf import FPDF
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import os
import sys

import fpdf

pdf = fpdf.FPDF()

# function to create a generator of page pairs, accepts a number of pages 
# which translates to 1,2,3,4,5..N if a list (of page numbers) is supplied
# this maps to the input pdf, it is the only way to supply a range not starting
# at 1

def page_pairs(pages):
    if isinstance(pages, list):
        pagelist = pages
        pages = len(pagelist)
    else:
        pagelist = list(range(1, pages + 1))
    if pages % 4 != 0:
        pages += 4 - (pages % 4)
    if pages>len(pagelist):
        pagelist.extend([-1] * (pages - len(pagelist)))
    start = 1
    # flip is needed because the even pages are printed on the back of the previous odd
    flip = False
    while pages>start:
        startpage = pagelist[start-1]
        endpage = pagelist[pages-1]
        if flip:
            yield (startpage,endpage)
            #print (start)
            #print (pages)
        else:
            yield (endpage,startpage)
            #print (pages)
            #print (start)
        pages-=1
        start+=1
        flip = not flip

# Paths to input and output PDFs

num_pages = None


# github copilot prompted some of this but should argparse at some point
# it did get it slightly wrong though so be careful what you wish for

if len(sys.argv)==1:
    print("Usage: python3 booklet.py <input_pdf_path>")
    sys.exit(1)
elif len(sys.argv)==2:
    input_pdf_path = sys.argv[1]
elif len(sys.argv)==3:
    input_pdf_path = sys.argv[1]
    num_pages = sys.argv[2]
    if num_pages.isdigit():
        num_pages = int(num_pages)
    else:
        num_pages = [int(n) for n in num_pages.split(",")]



# generate the output file from the input 

filename = input_pdf_path.split("/")[-1]
path ="/".join(input_pdf_path.split("/")[:-1])
output_pdf_path = f'{path}/A3-Booklet-{filename}'

# github copilot helped with this, it did some of the basic work , I didn't have the first clue about
# pdf choppering, it didn't know the python version and messed it up a few times, so it wasn't plain sailing
# any alterations to the flow were mine, also corrections - it didn't seem to understand list indexes

# Read the input PDF
reader = PdfReader(input_pdf_path)

if num_pages is None: num_pages = len(reader.pages)
print(f"num_pages {num_pages}")

# Convert PDF pages to images
images = convert_from_path(input_pdf_path)

# Create an A3 PDF
pdf = FPDF('L', 'mm', 'A3')

# Calculate the dimensions for A4 pages on an A3 sheet
a4_width = pdf.w / 2
a4_height = pdf.h

# Add pages from the original PDF to the new A3 PDF
for i,j in page_pairs(num_pages):
    print(f"page pairs {i} and {j}")
    # Add a new page to the output PDF every two pages
    pdf.add_page()
    
    # Save the first page as an image
    if i>=0:
        image1_path = f'page_{i}.png'
        print(f"image1_path {image1_path}")
        images[i-1].save(image1_path, 'PNG')
        pdf.image(image1_path, x=0, y=0, w=a4_width, h=a4_height)
        os.remove(image1_path)  # Remove the temporary image file
    
    # Check if there is a second page
    if j>=0:
        # Save the second page as an image
        image2_path = f'page_{j}.png'
        print(f"image2_path {image2_path}")
        images[j-1].save(image2_path, 'PNG')
        pdf.image(image2_path, x=a4_width, y=0, w=a4_width, h=a4_height)
        os.remove(image2_path)  # Remove the temporary image file

# Save the new PDF
pdf.output(output_pdf_path)
