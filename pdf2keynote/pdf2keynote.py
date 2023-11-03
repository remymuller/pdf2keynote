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
    PDFDocument,
    PDFPage,
    PDFSelection,
    PDFAnnotationText,
    PDFAnnotationLink,
    PDFActionNamed,
    kPDFActionNamedNextPage,
    kPDFActionNamedPreviousPage,
    kPDFActionNamedFirstPage,
    kPDFActionNamedLastPage,
    kPDFActionNamedGoBack,
    kPDFActionNamedGoForward,
    kPDFDisplayBoxMediaBox,
    kPDFDisplayBoxCropBox,
)


def escape(notes):
    return '"{}"'.format(notes)


# Keynote applescript wrappers
def insert_note(slide, notes):
    print("with notes:", notes)
    # TODO use a RTF file for each notes
    do_apple_script("insert_note", slide, escape(notes))


def insert_image(slide, image):
    print("add image {}".format(image))
    do_apple_script("insert_image", slide, image)


def insert_sound(slide, sound, x, y):
    print("add sound {} at ({},{})".format(sound, x, y))
    do_apple_script("insert_sound", slide, sound, int(x), int(y))


def insert_movie(slide, movie, x, y):
    print("add movie {} at ({},{})".format(movie, x, y))
    do_apple_script("insert_movie", slide, movie, int(x), int(y))


def create_empty_slide():
    do_apple_script("create_empty_slide")


# def delete_slide(index):
#     do_apple_script("delete_slide", index)


def create_keynote_document(width=1024, height=768):
    do_apple_script("create_keynote_document", width, height)


def save_keynote_document(path):
    print("saving to {}".format(path))
    do_apple_script("save_keynote_document", path)


def apple_script_path(command):
    return os.path.abspath(
        pdf2keynote.__path__[0] + "/applescripts/{}.scpt".format(command)
    )


def do_apple_script(command, *args):
    path = apple_script_path(command)
    args = " ".join([str(arg) for arg in args])
    cmdline = "osascript {} {}".format(path, args)
    # print(cmdline)
    os.system(cmdline)


def lines(selection):
    return [line.string() for line in selection.selectionsByLine() or []]

def has_notes(page: PDFPage) -> bool:
    """
     Checks if the PDF is likely to include a note slide. 
     Only works between 21:18 and 21:9 format slides. So does not work for 1:1 or portait mode slides!
    """
    _, (w, h) = page.boundsForBox_(kPDFDisplayBoxMediaBox)

    return w / h > 21/9 # = 7/3 # Usual aspect ratios are 4/3 or 16/9, therefore 2 * 4/3 = 8/3 and 32/9 are the ratios for double-slides.

def exclude_notes(page: PDFPage, origin=(0,0)):
    "Crops page to exclude notes. `origin` is the origin of the slide."
    _, (w, h) = page.boundsForBox_(kPDFDisplayBoxMediaBox)
    page.setBounds_forBox_((origin, (w/2, h)), kPDFDisplayBoxCropBox)

def get_beamer_notes_for_page(page: PDFPage):
    (x, y), (w, h) = page.boundsForBox_(kPDFDisplayBoxMediaBox)
    
    # heuristic to guess template of note slide
    w /= 2
    title = lines(page.selectionForRect_(((x, y), (w, h))))
    miniature = lines(
        page.selectionForRect_(
            ((x + w + 3 * w / 4, y + 3 * h / 4), (w / 4, h / 4))
        )
    )
    header = miniature and all(  # miniature do not have navigation
        line in title for line in miniature
    )

    selection = page.selectionForRect_(
        ((x + w, y), (w, 3 * h / 4 if header else h))
    )
    return "\n".join(lines(selection))


def create_pdf_for_page(page: PDFPage):
    page_pdf = PDFDocument.alloc().init()
    page_pdf.insertPage_atIndex_(page, 0)

    f, pdf_path = tempfile.mkstemp(prefix="pdf2keynote", suffix=".pdf")
    page_pdf.writeToFile_(pdf_path)

    return pdf_path


def get_pdf_scale(pdf):
    title_page = pdf.pageAtIndex_(0)
    (x, y), (w, h) = title_page.boundsForBox_(kPDFDisplayBoxMediaBox)
    return 768 / h


def get_pdf_dimensions(pdf):
    """"""
    title_page = pdf.pageAtIndex_(0)
    (x, y), (w, h) = title_page.boundsForBox_(kPDFDisplayBoxMediaBox)
    if w / h > 7 / 3:  # likely to be a two screens pdf
        w = w // 2

    # rescale to normalize height to 768px
    w = (w / h) * 768
    h = (h / h) * 768
    return (w, h)
    # return (1024,768)


def is_audio(path):
    _, ext = os.path.splitext(path)
    return ext in [".wav", ".aif", ".aiff", ".mp3", ".flac"]


def is_video(path):
    _, ext = os.path.splitext(path)
    return ext in [".mov", ".mpg", ".mpeg", ".m4v", ".mp4", ".gif"]


def process_annotations_for_page(pdf, page_number):
    scale = get_pdf_scale(pdf)

    page = pdf.pageAtIndex_(page_number)
    annotations = page.annotations() or []
    for annotation in annotations:
        annotation_type = type(annotation)
        if annotation_type == PDFAnnotationText:
            print("PDFAnnotationText at page %d" % page_number, annotation.contents())
            # annotation.setShouldDisplay_(False)
            # pdf_notes[page_number].append(annotation.contents().replace('\r', '\n'))
        elif annotation_type == PDFAnnotationLink:
            print("PDFAnnotationLink at page %d:" % page_number, annotation.URL())
            url = annotation.URL()
            if url:
                bounds = annotation.bounds()
                print(bounds)
                P = bounds.origin
                slide = page_number + 1
                path = os.path.abspath(url.path())
                # TODO: test if annotation is on second screen and duplicates...
                if is_audio(path):
                    insert_sound(slide, path, P.x * scale, P.y * scale)
                elif is_video(path):
                    insert_movie(slide, path, P.x * scale, P.y * scale)
        # elif annotation_type == PDFAnnotationMovie:
        # elif annotation_type == PDFAnnotationWidget:
    return []


def pdf_to_keynote(path_to_pdf, path_to_keynote=None):
    """"""
    path_to_pdf = os.path.abspath(path_to_pdf)
    print("reading", path_to_pdf)
    if path_to_keynote is None:
        root, ext = os.path.splitext(path_to_pdf)
        path_to_keynote = root + ".key"

    url = NSURL.fileURLWithPath_(_s(path_to_pdf))
    pdf = PDFDocument.alloc().initWithURL_(url)
    if not pdf:
        exit_usage("'%s' does not seem to be a pdf." % url.path(), 1)

    if pdf.pageCount() <= 0:
        exit_usage("'{url.path()}' has no pages.", 1)

    w, h = get_pdf_dimensions(pdf)
    print(w, h)

    create_keynote_document(w, h)

    for page_number in range(pdf.pageCount()):
        slide = page_number + 1
        if slide > 1:
            create_empty_slide()

        page = pdf.pageAtIndex_(page_number)

        pdf_path = create_pdf_for_page(page)
        insert_image(slide, pdf_path)
        os.remove(pdf_path)

        if has_notes(page):
            notes = get_beamer_notes_for_page(page)
            exclude_notes(page)
            insert_note(slide, notes)

        process_annotations_for_page(pdf, page_number)

        print((slide, notes, pdf_path))

        # TODO select first slide

        save_keynote_document(path_to_keynote)


def main():
    """"""

    parser = argparse.ArgumentParser(description="Converts PDF to Keynote.")
    parser.add_argument("pdf", metavar="pdf_path", type=str, help="path to PDF file")
    parser.add_argument(
        "-o",
        "--output",
        metavar="output_path",
        type=str,
        help="path to Keynote file",
        nargs=1,
    )
    args = parser.parse_args(sys.argv[1:])

    path_to_pdf = args.pdf
    path_to_keynote = args.output
    pdf_to_keynote(path_to_pdf, path_to_keynote)
