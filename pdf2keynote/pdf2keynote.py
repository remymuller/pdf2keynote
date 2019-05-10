"""
"""

import os  
import re
import sys 
import string
import argparse
import pdf2keynote
import shutil
import tempfile 

from collections import defaultdict

# import OSX stuff
from objc import nil, NO, YES
from Foundation import NSURL, NSString

if sys.version_info[0] == 3:
    _s = NSString.stringWithString_
else:
    _s = NSString.stringWithUTF8String_

from Quartz import (
    PDFDocument, PDFAnnotationText, PDFAnnotationLink,
    PDFActionNamed,
    kPDFActionNamedNextPage, kPDFActionNamedPreviousPage,
    kPDFActionNamedFirstPage, kPDFActionNamedLastPage,
    kPDFActionNamedGoBack, kPDFActionNamedGoForward,
    kPDFDisplayBoxMediaBox, kPDFDisplayBoxCropBox,
)


def escape(notes):
    return '"{}"'.format(notes)

# Keynote applescript wrappers
def insert_note(slide, notes):
    print("with notes:", notes)
    # TODO use a RTF file for each notes
    do_apple_script('insert_note', slide, escape(notes))


def insert_image(slide, image):
    print("add image {}".format(image))
    do_apple_script('insert_image', slide, image)


def create_empty_slide():
    do_apple_script('create_empty_slide')


def delete_slide(index):
    do_apple_script('delete_slide', index)


# TODO: add w,h
def create_keynote_document():
    do_apple_script('create_keynote_document')


def save_keynote_document(path):
    print("saving to {}".format(path))
    do_apple_script('save_keynote_document', path)


def apple_script_path(command):
    return os.path.abspath(pdf2keynote.__path__[0] + "/applescripts/{}.scpt".format(command))


def do_apple_script(command, *args):
    path = apple_script_path(command)
    args = " ".join([str(arg) for arg in args])
    os.system("osascript {} {}".format(path, args))

def natural_sort(list, key=lambda s:s):
    """
    Sort the list into natural alphanumeric order.
    """
    def get_alphanum_key_func(key):
        convert = lambda text: int(text) if text.isdigit() else text 
        return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]
    sort_key = get_alphanum_key_func(key)
    list.sort(key=sort_key)


# def get_pages(path_to_pdf):
#     """
#     split pdf into pages and notes
#     """
#     base,_ = os.path.split(path_to_pdf)
#     temp_dir = base + "/.pdf_pages"
#     if not os.path.exists(temp_dir):
#         print("mkdir", temp_dir)
#         os.mkdir(temp_dir)

#     os.system("gs -sDEVICE=pdfwrite -dNOPAUSE -dQUIET -dBATCH -sOutputFile={}/%d.pdf {}".format(temp_dir, path_to_pdf))

#     files = os.listdir(temp_dir)
#     natural_sort(files)

#     pages = [(temp_dir+'/'+file, "notes place holder") for file in files]
#     return pages

def lines(selection):
    return [line.string() for line in selection.selectionsByLine() or []]

# def get_beamer_notes(pdf):
#     beamer_notes = defaultdict(list)
#     title_page = pdf.pageAtIndex_(0)
#     (x, y), (w, h) = title_page.boundsForBox_(kPDFDisplayBoxMediaBox)

#     if w/h > 7/3: # likely to be a two screens pdf
#         # heuristic to guess template of note slide
#         w /= 2
#         title = lines(title_page.selectionForRect_(((x, y), (w, h))))
#         miniature = lines(title_page.selectionForRect_(((x+w+3*w/4, y+3*h/4), (w/4, h/4))))
#         header = miniature and all( # miniature do not have navigation
#             line in title
#             for line in miniature
#         )
    
#         page_count = pdf.pageCount()
#         for page_number in range(page_count):
#             page = pdf.pageAtIndex_(page_number)
#             (x, y), (w, h) = page.boundsForBox_(kPDFDisplayBoxMediaBox)
#             w /= 2
#             page.setBounds_forBox_(((x, y), (w, h)), kPDFDisplayBoxCropBox)
#             selection = page.selectionForRect_(((x+w, y), (w, 3*h/4 if header else h)))
#             beamer_notes[page_number].append('\n'.join(lines(selection)))
#     return beamer_notes


def get_beamer_notes_for_page(pdf, page_number):
    title_page = pdf.pageAtIndex_(0)
    (x, y), (w, h) = title_page.boundsForBox_(kPDFDisplayBoxMediaBox)

    notes = ""
    if w/h > 7/3: # likely to be a two screens pdf
        # heuristic to guess template of note slide
        w /= 2
        title = lines(title_page.selectionForRect_(((x, y), (w, h))))
        miniature = lines(title_page.selectionForRect_(((x+w+3*w/4, y+3*h/4), (w/4, h/4))))
        header = miniature and all( # miniature do not have navigation
            line in title
            for line in miniature
        )
    
        page = pdf.pageAtIndex_(page_number)
        (x, y), (w, h) = page.boundsForBox_(kPDFDisplayBoxMediaBox)
        w /= 2
        page.setBounds_forBox_(((x, y), (w, h)), kPDFDisplayBoxCropBox)
        selection = page.selectionForRect_(((x+w, y), (w, 3*h/4 if header else h)))
        notes = '\n'.join(lines(selection))
    return notes


def create_pdf_for_page(pdf, page_number):
    page_pdf = PDFDocument.alloc().init()    
    page_pdf.insertPage_atIndex_(pdf.pageAtIndex_(page_number), 0)

    f,pdf_path = tempfile.mkstemp(prefix="pdf2keynote", suffix=".pdf")
    page_pdf.writeToFile_(pdf_path)

    return pdf_path


def get_pages(path_to_pdf):
    """
    split pdf into pages and notes
    """

    url = NSURL.fileURLWithPath_(_s(path_to_pdf))
    pdf = PDFDocument.alloc().initWithURL_(url)
    if not pdf:
        exit_usage("'%s' does not seem to be a pdf." % url.path(), 1)

    pages = []
    print("Slides:")
    for page_number in range(pdf.pageCount()):
        notes = get_beamer_notes_for_page(pdf, page_number)
        pdf_path = create_pdf_for_page(pdf, page_number)
        print((page_number, notes, pdf_path))
        pages.append((pdf_path, notes))

    return pages


def pdf_to_keynote(path_to_pdf, path_to_keynote=None):
    """
    """
    path_to_pdf = os.path.abspath(path_to_pdf)
    print("reading", path_to_pdf)
    if path_to_keynote is None:
        root,ext = os.path.splitext(path_to_pdf)
        path_to_keynote = root + ".key"

    pages = get_pages(path_to_pdf)
    if pages:
        create_keynote_document()

        slide = 1
        for (pdf_path,notes) in pages:
            if slide > 1:
                create_empty_slide()
            insert_image(slide, pdf_path)
            insert_note(slide, notes)
            os.remove(pdf_path)
            slide += 1

        # TODO select first slide

        save_keynote_document(path_to_keynote)


def main():
    """
    """

    parser = argparse.ArgumentParser(description='Converts PDF to Keynote.')
    parser.add_argument('pdf', 
                        metavar="pdf_path", 
                        type=str, 
                        help='path to PDF file')
    parser.add_argument('-o', '--output', 
                        metavar="output_path", 
                        type=str, 
                        help='path to Keynote file', 
                        nargs=1)
    args = parser.parse_args(sys.argv[1:])

    path_to_pdf = args.pdf
    path_to_keynote = args.output
    pdf_to_keynote(path_to_pdf, path_to_keynote)


# if __name__ == "__main__":
#     pdf_to_keynote(pdf2keynote.__path__[0] + '../test/dafx19-opa-presentation.pdf')

