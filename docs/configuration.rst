.. _configuration:

=============
Configuration
=============
Location
--------

``kibitzr`` reads configuration from ``kibitzr.yml`` file.
It tries to find it in following places:

1. ``./kibitzr.yml`` - current working directory.
2. ``~/.config/kibitzr/kibitzr.yml``
3. ``~/kibitzr.yml``

``kibitzr-creds.yml`` can be used to store credentials,
it must be placed in the same directory as ``kibitzr.yml``.

Format
------

``kibitzr`` serves list of ``checks``.

Each check must have a **unique** ``name``.
The name is used in notifications and internally as a check identifier.

Next, check may have ``url``. If it is provided, it will be used to fetch data.
Another option is ``script``, which is arbitrary bash script.

Check will be executed every ``period`` seconds.

Fetched data from ``url`` (or ``script`` output) is passed
to a pipeline of transformations defined under ``transform`` key.
See :ref:`Transforms documentation <transforms>` for a complete list of
supported transformations.

Finally transformed data is passed to a list of notifiers
defined under ``notify`` key.
See :ref:`Notifier documentation <transforms>` for a complete list of
supported notifiers.

Kibitzr supports browser interactions. They can be activated by using any of keys:

   1. ``delay`` - number of seconds to wait after page loaded in browser to process Javascipt.
   2. ``scenario`` - python scenario acting on selenium_ driver after page load.

Simple example
--------------

Let's start with something simple. It's not very useful check, but it'll show the basics.

.. code-block:: yaml

    checks:
      - name: Current Time
        url: https://www.timeanddate.com/worldclock/usa/new-york
        transform:
            - css: "#qlook > div"
            - text
        notify:
            - python: print(text)
        period: 15

Copy paste it to your ``kibitzr.yml`` and launch ``kibitzr``.
You will see something like this:

.. code-block:: bash

	$ kibitzr
	2017-03-28 22:02:39,465 [INFO] kibitzr.checker: Fetching 'Current Time' at 'https://www.timeanddate.com/worldclock/usa/new-york'
	2017-03-28 22:02:39,687 [INFO] kibitzr.notifier.custom: Executing custom notifier
	10:02:39 pm
	EDT
	2017-03-28 22:02:39,687 [INFO] kibitzr.main: Scheduling checks for 'Current Time' every 15 seconds
	2017-03-28 22:02:39,688 [INFO] kibitzr.main: Starting infinite loop
	2017-03-28 22:02:54,705 [INFO] schedule: Running job Every 15 seconds do check() (last run: [never], next run: 2017-03-28 22:02:54)
	2017-03-28 22:02:54,705 [INFO] kibitzr.checker: Fetching 'Current Time' at 'https://www.timeanddate.com/worldclock/usa/new-york'
	2017-03-28 22:02:54,823 [INFO] kibitzr.notifier.custom: Executing custom notifier
	10:02:54 pm
	EDT

Let's follow the configuration file line-by-line to see how it works.

On the first line we define a dictionary key ``checks``:

.. code-block:: yaml
    checks:

Then, starting with indentation and dash goes the name of the first check:

.. code-block:: yaml

      - name: Current Time

It's an arbitrary string, the only constraint is that it must be **unique** within the ``checks`` list.

Right after name, we define URL:

.. code-block:: yaml

        url: https://www.timeanddate.com/worldclock/usa/new-york

Please note, that all keys are in lower case.

So far so good, we came to transformations:

.. code-block:: yaml

        transform:
          - css: "#qlook > div"
          - text

``transform`` value must be a list (as denoted by dashes).
Please note how list items indentation is deeper, than of ``transform``.

Each ``transform`` item can be a simple ``transform`` name (like ``text``, which extracts text from HTML),
or a ``name: argument`` pair (like ``css: "#qlook > div"`` which crops HTML using CSS selector ``"#qlook > div"``)

As you can see, we first crop whole page to a single HTML tag and then extract plain text from it.

Having all the hard job behind, we came to notification settings.
``kibitzr`` supports :ref:`many different notifiers <notifiers>`,
but here we are using the one, that does not require credentials management - arbitrary Python script.

.. code-block:: yaml

        notify:
            - python: print(text)

It is exactly the code, that produced

.. code-block:: bash

	10:02:39 pm
	EDT

in the ``kibitzr`` output.

Last line of configuration file is the ``period``:

.. code-block:: yaml

        period: 15

The number of seconds to wait between (*start of*) checks.

And here is the more complex example:

.. code-block:: yaml

    pages:
    
      - name: NASA awards on preview
        url: http://preview.ncbi.nlm.nih.gov/pmc/utils/granthub/award/?authority.code=nasa&format=json
        transform:
          - json
          - changes
        period: 30
        notify:
          - mailgun
    
      - name: Rocket launches
        url: http://www.nasa.gov/centers/kennedy/launchingrockets/index.html
        transform: changes
        period: 600
        notify:
          - mailgun
    
    notifiers:
    
        # This can be moved to kibitzr-creds.yml:
        mailgun:
            key: <mailgun api key>
            domain: <your domain>
            to: <your email>

This configuration tells kibitzr to check URL at http://preview... every 5 minutes (300 seconds),
prettify JSON and compare against previously saved result. git diff output is sent through mailgun.


.. _requests: http://docs.python-requests.org/
.. _BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
.. _mailgun: https://mailgun.com/
.. _slack: https://slack.com/
.. _selenium: https://selenium-python.readthedocs.io/api.html