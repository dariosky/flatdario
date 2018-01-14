# flatdario
My flatsite generator - an aggregator of social activities 
from various services.

This is an app that works scanning a number of social accounts related
 to his powerful master, save them in a local smallDB and
 generate a static website (that will be periodically updated) to
 show them to the world.

Services may require an API key to access the various API
and a user authorization to access the data for read access
 (check the services documentation down here).
Apps keys are in `appkeys/` user keys in `userkeys/`.

TODO Desiderata:
* Share a post to social networks, with a permanent link
* Be light, fast and save the planet


### Supported services

#### Youtube likes

Whatever you like in Youtube is saved.
How to use it:
It need Google API credentials:
 create an app that can access Youtube API, and save its secrets as
 `appkeys/google.json`  then on the first run it will ask
 oauth2 authentication with your
 Youtube account (saved in `userkeys/google.json`).

#### Pocket

What you archive in Pocket is saved.
You need pocket credentials, [get them here](https://getpocket.com/developer/docs/authentication)
and put the consumer_key in a json file in `appkeys/pocket.json` 


# How to use it

Collect all your data, scraping the supported services, and update the DB:
	
	flat.py collect

This will update the DB, that by default is stored as `db.json`.

The generated static site is stored in the `build` subfolder.

Initialize the build subfolder typing

	flat.py init --template empty
	
You can create a new template, for your site: check the `/flatbuilder/empty` folder
and create a new template if you like.

Now you can create the static site with the collected data:

	flat.py build
	
The static file is ready to be served and deployed.

If you want to check it out locally, you can run:

	flat.py preview
	
And then point your browser to http://localhost:7747
