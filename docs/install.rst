
Installation and Usage
===========================

This module is installing and configuring Oracle Instant Client

The module can be used on a new or existing Webmin installation

Installation
------------

Step 1: Get the repo from Github::

    git clone https://github.com/cited/Oracle-Instant-Client.git

Step 2: Change name::

    mv webmin_oci-master oci

Step 4 Create the Webmin tar.gz file::

    tar -cvzf oci.wbm.gz oci/

Step 5: Install the module::

    /usr/share/webmin/install.pl oci.wbm.gz

Wizard
-------   

Once the module is installed, go to Servers >> Oracle Instant Client and click through the Wizard

.. image:: _static/5.png

Select the packages to install

.. image:: _static/6.png

Once completed, the panel should look like below:

.. image:: _static/7.png


SQL Plus
-----------------

If you selected SQLPlus, you can test functionality via the Webmin terminal app:

.. image:: _static/8.png

Start SQL Plus

.. image:: _static/9.png

Contribute
----------

- Issue Tracker: github.com/cited/Oracle-Instant-Client/issues
- Source Code: github.com/AcuGIS/Oracle-Instant-Client

Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@google-groups.com

License
-------

The project is licensed under the BSD license.