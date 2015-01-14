Setup
-----

First install the requests package by running:

    pip install requests

Ensure your ~/.zendesk.cfg is already configured.
You can use your API token information as found at https://support.datastax.com/settings/api.
(You will need ZenDesk admin access to view this page.)
This is mine:

    [ZenDesk]
    domain = support.datastax.com
    email = stephen@<domain>.com/token
    pass = TOKEN

    [Downloader]
    download_directory = /home/icc/Downloads/support
    run_open = True
    open_program = vi

Then perhaps something simple like:

    sudo ln -s ~/repos/zendesk_downloader/download /usr/local/bin/download

Usage
-----
    download

This will download all tickets with a status of solved

    download 1828

This will download ticket 1828

After that, all attachments are downloaded into the folder

    <download_directory>/<assigned_user_name>/<ticket_subject>/

where:

* `.tar.gz` and `.zip` files are extracted into their proper folders
* file creation and modified dates are set to the original upload date
* files with no extensions are automatically fixed with at .txt 

Purpose
-------

* Download attachments for solved tickets for archiving or exporting to document management system
* Have all organization files ready to easily be grepped
* Create a summary of the request details for archiving and 3rd party systems
* Automatically extract compressed information
