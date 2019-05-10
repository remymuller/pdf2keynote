# Generates Keynote presentation 

all: keynote 
	echo "building all..."

pdf:
	echo "building pdf..."
	pdflatex pdf2keynote.tex
	rm *.aux *.log *.nav *.out *.snm *.toc *.vrb

keynote: pdf	
	echo "building keynote..."
	pdf2keynote pdf2keynote.pdf




