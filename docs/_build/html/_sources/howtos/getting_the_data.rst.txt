Getting the data
================

I used the following workflow to access all papers of S. Shelah listed on
'MathSciNet'

First I retrieve the MR-numbers. I use the ``mrnumbers`` command from
``mrtools.py``. The option ``--url`` should point to a search result from
'MathSciNet'. The option ``--crawl`` specifies, that I want the results from
all pages and finally I specify where I want to dump the list of MR-numbers.

.. code-block:: bash

    $ mrtools.py mrnumbers --crawl --dump files/mrnumbers.yaml --url \ 
    > "http://tinyurl.com/shelahmsn"

Next I will access the bib-files associated to these numbers. For this purpose
I am using the ``bib`` command.


.. code-block:: bash

    $ mrtools.py bib --load files/mrnumbers.yaml --dump files/msn.bib

Now that I have the bibliographic data from 'MathSciNet', I am going to create
the merge keys. This can be done using ``pybibtools.py`` with the ``make-key``
command. The option ``-k`` tells the script which fields should be used for the
key creation. There are to special values for ``-k``, namely ``normauthor`` and
``normtitle``. They call :func:`listb.normalizetex.norm_author` or
:func:`listb.normalizetex.norm_title` resp. and add these fields to the
bibliography.

.. code-block:: bash

    $ pybibtools.py make-key -k normauthor -k year -k normtitle \ 
    > -o files/norm_msn.bib files/msn.bib

Now let's do the same for 'listb'.

.. code-block:: bash

    $ pybibtools.py make-key -k normauthor -k year -k normtitle \ 
    > -o files/norm_listb.bib files/listb.bib

This raises a ``RuntimeError`` if the generated keys are not unique. If so a
note is taken in the respective 'info' file.

Finally, we are able to merge the datasets.

.. code-block:: bash

    $ pybibtools.py merge --left -o files/merged.bib \ 
    > files/norm_listb.bib files/norm_msn.bib

Note that the ``merge`` command is *not* commutative.

Here is some data of the first trial run. The last column indicates that 842
entries could be matched.

  ====== ======= ======== ===========
  #      entries with URL with MR-no.
  ====== ======= ======== ===========
  listb     1144        0           0
  ------ ------- -------- -----------
  msn       1019      889        1019
  ------ ------- -------- -----------
  merged    1144      752         842
  ====== ======= ======== ===========

