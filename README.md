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
Apps keys are in `appkeys/` user kets in `userkeys/`.

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
