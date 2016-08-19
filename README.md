# flatdario
My flatsite generator - an aggregator of social activities from various services
This is an app that works scanning a number of social accounts related
 to his powerful master, save them in a local smallDB and
 generate a static website (that will be periodically updated) to
 show them to the world.
 
TODO Desiderata:
* Share a post to social networks, with a permanent link
* Be light, fast and save the planet


### Supported services

#### Youtube likes

Whatever you like in Youtube is saved.
How to use it:
It need Google API credentials:
 create an app that can access Youtube API save `client_secrets.json`
 then on the first run it will ask oauth2 authentication with your
 Youtube account (saved in `client-youtube-oauth2.json`).

