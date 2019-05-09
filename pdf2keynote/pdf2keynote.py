"""
"""

import os  
import sys 
import string
import argparse

def main():
    import pdf2keynote
    modulepath = pdf2keynote.__path__[0]

    parser = argparse.ArgumentParser(description='.')
    parser.add_argument('pdf', metavar="PDF", required=True, type=string, help='path to PDF file', nargs=1)
    args = parser.parse_args(sys.argv[1:])

    path_to_pdf = args.pdf

    # os.system("pdflatex {}".format(output_filename))
