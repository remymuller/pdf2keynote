pdf2keynote
===========

automate the conversion from PDF to Apple's Keynote

Install 
-------

install for development mode::

	git clone https://github.com/remymuller/pdf2keynote.git
	pip install -e pdf2keynote/

install directly from git::

	pip install git+https://github.com/remymuller/pdf2keynote.git


Usage
-----

example::

	pdf2keynote [-o path_to_keynote] path_to_pdf


If the presentation is generated using Beamer with::

	\setbeameroption{show notes on second screen=right}

then Beamer notes commands::

	\note{comments}

are extracted as Keynote's presenter notes
