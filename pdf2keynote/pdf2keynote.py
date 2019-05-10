"""
"""

import os  
import re
import sys 
import string
import argparse
import pdf2keynote


def escape(notes):
    return '"{}"'.format(notes)

# Keynote applescript wrappers
def insert_note(slide, notes):
    print("with notes:", notes)
    # TODO use a RTF file for each notes
    do_apple_script('insert_note', slide, escape(notes))


def insert_image(slide, image):
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


def get_pages(path_to_pdf):
    """
    split pdf into pages and notes
    """
    base,_ = os.path.split(path_to_pdf)
    temp_dir = base + "/.pdf_pages"
    if not os.path.exists(temp_dir):
        print("mkdir", temp_dir)
        os.mkdir(temp_dir)

    os.system("gs -sDEVICE=pdfwrite -dNOPAUSE -dQUIET -dBATCH -sOutputFile={}/%d.pdf {}".format(temp_dir, path_to_pdf))

    files = os.listdir(temp_dir)
    natural_sort(files)

    pages = [(temp_dir+'/'+file, "notes place holder") for file in files]
    return pages


def clean_pages():
    pass


def pdf_to_keynote(path_to_pdf, path_to_keynote=None):
    """
    """
    path_to_pdf = os.path.abspath(path_to_pdf)
    print("reading", path_to_pdf)
    if path_to_keynote is None:
        root,ext = os.path.splitext(path_to_pdf)
        path_to_keynote = root + ".key"

    pages = get_pages(path_to_pdf)
    # assert(len(pages) > 0)

    create_keynote_document()

    if pages:
        slide = 1
        for (pdf,notes) in pages:
            create_empty_slide()
            insert_image(slide, os.path.abspath(pdf))
            insert_note(slide, notes)
            slide += 1

    save_keynote_document(path_to_keynote)

    clean_pages()


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

