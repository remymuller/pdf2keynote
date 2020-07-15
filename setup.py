"""
inspired from 
https://python-packaging.readthedocs.io/en/latest/

we use find_packages because of this:
https://stackoverflow.com/questions/43253701/python-packaging-subdirectories-not-installed
"""

from setuptools import setup, find_packages

setup(name='pdf2keynote', # pyton module name
      version='1.0',
      description='python module for converting PDF files to Apple Keynote',
      url='https://github.com/remymuller/pdf2keynote',
      author='Remy Muller',
      author_email='muller.remy@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
        # 'applescript',
        'pyobjc' # to handle PDF
      ],
      setup_requires=['setuptools_scm'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'pdf2keynote = pdf2keynote.pdf2keynote:main', 
          ]
      },
      zip_safe=False)
