pdf2keynote
===========

automate the conversion from PDF to Apple's Keynote

Install 
-------

.. install from pip::
..
..	pip install pdf2keynote

install from git::

	pip install git+https://github.com/remymuller/pdf2keynote.git

.. install for development::
..
..	git clone https://github.com/remymuller/pdf2keynote.git
..	pip install -e pdf2keynote/


Usage
-----

example::

	pdf2keynote [-o path_to_keynote_presentation] path_to_pdf


If the presentation is generated using Beamer with::

	\setbeameroption{show notes on second screen=right}

then Beamer notes commands like::

	\note 
	{
        	\begin{itemize}
            		\item dont forget to say this 
            		\item and this
            		\item and that!
        	\end{itemize}
    	}	

are extracted as Keynote's presenter notes. 

and media references like ::

	\href{path/to/audio/or/movie}{ Alternate Text to be displayed. }
	
are extracted as playable sounds or movies

See the `Demo example <https://github.com/remymuller/pdf2keynote/blob/master/test/pdf2keynote.pdf>`_ and its `source <https://github.com/remymuller/pdf2keynote/blob/master/test/pdf2keynote.tex>`_


Credits
-------
Thanks to the following projects to get me started
	
- `Presentation App <http://iihm.imag.fr/blanch/software/osx-presentation/>`_
- `md2key <https://github.com/k0kubun/md2key>`_
- `PDF to Keynote <https://www.cs.hmc.edu/~oneill/freesoftware/pdftokeynote.html>`_
- `iWork Automation <http://iworkautomation.com>`_
