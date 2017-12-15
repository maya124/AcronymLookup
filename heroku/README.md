## Heroku Hosting

The files in this folder were used to experiment with hosting the acronym look-up on Heroku to allow us to put the Chrome extension on the Chrome store. However, it turned out that the free tier was not sufficient for our purposes. One main reason for this is that Heroku is a "ephermal" memory hosting provider. This means that static files are meant to be hosted through other services. Since our pickle files are too large to put on GitHub, this meant that we needed to set up an Amazon S3 bucket to host the files, which would then be loaded when the Heroku instance first spun up. However, this process takes more than the 30 seconds per request provided by Heroku's free tier.  

These files are included so that if we (or anyone else) decides to host this code, they have a good starting point. Getting `scipy` and the like to work with Heroku took a fair amount of fiddling, so hopefully this will help someone.
