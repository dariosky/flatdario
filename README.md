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

# How to use it

### collect

Collect all your data, scraping the supported services, and update the DB:
	
	flat.py collect

This will update the DB, that by default is stored as `db.json`.

### build

The generated static site is stored in the `build` subfolder.

Initialize the build subfolder typing

	flat.py init --template empty
	
You can create a new template, for your site: check the `/flatbuilder/empty` folder
and create a new template if you like.

Now you can create the static site with the collected data:

	flat.py build
	
The static file is ready to be served and deployed.

### serve static

If you want to check it out locally, you can run:

	flat.py preview
	
And then point your browser to [http://localhost:7747](http://localhost:7747)

### Supported services

#### Youtube likes

Collect videos you like in Youtube.

How to use it:

*	It needs Google API credentials:
 	create an app that can access Youtube API, and save its secrets as
 	`appkeys/google.json`
 
 		then on the first run it will ask oauth2 authentication with your
 		Youtube account (saved in `userkeys/google.json`).

#### Pocket

What you archive in Pocket is saved.

You need pocket credentials, [get them here](https://getpocket.com/developer/docs/authentication)
and put the consumer_key in a json file in `appkeys/pocket.json` 

#### Vimeo

Collect videos you like in Vimeo.

You have to create an app [here](https://developer.vimeo.com/apps/new)
 and put their credentials in `appkeys/vimeo.json`

### RSS

Collect entries from any RSS feed (or Atom or CDF).
Just provide the feed url.

### Serve dynamically

There is an additional mode to serve the generated site,
that allows to serve the site dynamically, allowing search and (soon),
autentication and updates the DB.

You'll need to run an API server that is done in Python (Flask and GraphQL)
to serve a React web application.

* Start the API server

		flat.py runapi
		
* Build the UI machinery using WebPack:
  
```bash
    cd api/ui
    # install the dependencies 
    yarn
    # yarn run watch
```
		
* Connect to [http://localhost:3001/](http://localhost:3001/)


# TODO - Desiderata:

* Be light, fast and save the planet
* Full-text search for content
* Login and update content
* Share a post to social networks, with a permanent link
* Instagram collector

Done:

* <del> Support for generic RSS feeds, in particular: TinyTinyRSS </del>
* <del> Tumblr specific reader (supporting pagination)</del>
