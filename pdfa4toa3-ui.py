# docker run -it --rm -v %cd%:/hello -w /hello python:3.11 bash
# apt update && apt upgrade && apt install libpoppler-cpp-dev
# pip install fpdf PyPDF2 pdf2image pillow tk python-poppler --trusted-host=pypi.org --trusted-host=files.pythonhosted.org
# WORK IN PROGRESS

from fpdf import FPDF
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import argparse

def page_pairs(pages):
    if isinstance(pages, list):
        pagelist = pages
        pages = len(pagelist)
    else:
        pagelist = list(range(1, pages + 1))
    if pages % 4 != 0:
        pages += 4 - (pages % 4)
    if pages > len(pagelist):
        pagelist.extend([-1] * (pages - len(pagelist)))
    start = 1
    flip = False
    while pages > start:
        startpage = pagelist[start - 1]
        endpage = pagelist[pages - 1]
        if flip:
            yield (startpage, endpage)
        else:
            yield (endpage, startpage)
        pages -= 1
        start += 1
        flip = not flip

def generate_pdf(input_pdf_path, selected_pages):
    filename = input_pdf_path.split("/")[-1]
    path = "/".join(input_pdf_path.split("/")[:-1])
    output_pdf_path = f'{path}/A3-Booklet-{filename}'

    reader = PdfReader(input_pdf_path)
    num_pages = len(selected_pages)
    images = convert_from_path(input_pdf_path)
    pdf = FPDF('L', 'mm', 'A3')
    a4_width = pdf.w / 2
    a4_height = pdf.h

    for i, j in page_pairs(selected_pages):
        pdf.add_page()
        if i >= 0:
            image1_path = f'page_{i}.png'
            images[i - 1].save(image1_path, 'PNG')
            pdf.image(image1_path, x=0, y=0, w=a4_width, h=a4_height)
            os.remove(image1_path)
        if j >= 0:
            image2_path = f'page_{j}.png'
            images[j - 1].save(image2_path, 'PNG')
            pdf.image(image2_path, x=a4_width, y=0, w=a4_width, h=a4_height)
            os.remove(image2_path)

    pdf.output(output_pdf_path)
    print(f"Output PDF saved to {output_pdf_path}")

def on_generate():
    selected_pages = [i + 1 for i, var in enumerate(page_vars) if var.get() == 1]
    generate_pdf(input_pdf_path, selected_pages)

def create_gui(input_pdf_path):
    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)
    images = convert_from_path(input_pdf_path)

    root = tk.Tk()
    root.title("PDF Page Selector")

    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    global page_vars
    page_vars = []

    for i, image in enumerate(images):
        img = ImageTk.PhotoImage(image.resize((400, 300)))
        label = ttk.Label(scrollable_frame, image=img)
        label.image = img
        label.pack()

        var = tk.IntVar(value=1)
        page_vars.append(var)
        radio_button = ttk.Checkbutton(scrollable_frame, text=f"Page {i + 1}", variable=var)
        radio_button.pack()

    generate_button = ttk.Button(root, text="Generate A3 PDF", command=on_generate)
    generate_button.pack()

    root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert A4 PDF to A3 booklet format.")
    parser.add_argument("input_pdf_path", type=str, help="Path to the input PDF file.")
    args = parser.parse_args()

    input_pdf_path = args.input_pdf_path
    create_gui(input_pdf_path)