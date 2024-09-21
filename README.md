# What is this website?

This is a project I threw together in roughly two weeks that tracks the results of my family's football pool.
The football pool is fairly simple in its rules; members of our family each "own" an NFL football team, and the winners are determined based on how the teams play.
I threw the site together so that there could be a tracker for the results of the football pool, as well as the results of the current NFL week's scores.

# How did I put this all together?

## Project Structure

I used this [`flask-empty`](https://github.com/italomaia/flask-empty) repository (which itself is powered by [`cookiecutter`](https://github.com/cookiecutter/cookiecutter)) to create the initial skeleton for this project.
I chose Flask because:
1. I have previous experience with Flask applications in a work environment.
2. This project is extremely lightweight and doesn't need a lot of the included batteries that Django offers.
3. Both Django and Flask are the only two frameworks I had any experience in, and I wanted the website available by the start of the season.

I'm a big fan of [devcontainers](https://code.visualstudio.com/docs/devcontainers/containers) (especially in VSCode), so I spent the first day making a devcontainer from scratch.
It's not super powerful or re-usable, but it fits the needs of the project pretty well so I like it a lot.
With respect to my devcontainer "build plans", I generally combine a Docker Compose file, a Dockerfile, and a `devcontainer.json` file within the `.devcontainer` directory to make productionizing a bit easier.

## Development

For the front-end, I leveraged [`tailwindcss`](https://tailwindcss.com/), which I've come to really enjoy for how simple it can make front-end design.
Here's a free secret: if you're not skilled with front-end and you *aren't* using a component library, you're only hurting yourself.
My component library of choice is [DaisyUI](https://daisyui.com/).
And having a 🤖 like ChatGPT available to help with the templating, styling, etc. definitely doesn't hurt. 😉

The back-end was a lot easier, it combines the power of [`pydantic`](https://docs.pydantic.dev/latest/) with your general web-app capabilities, like database integration.
The `pydantic` comes into play when reading the live game results from ESPN's API.

## Productionizing

As mentioned above, the fact that I used a devcontainer made making the production container much easier.
Much of the work was already in place, it just took a few modifications to ensure that the production container would be a bit smaller and more secure.
I also had to change some aspects of the implementation so that it fits the need of my production environment.
I'm being intentionally vague here, but just know it took a few tries to get it right!

After I got it running, it was the simple matter of initializing the database, running the migrations to get everything created, then seeding the database.
There have definitely been bugs, but `flask shell` is a really awesome command that allows me to do things within the database (or otherwise) that utilizes the currently running app.

# What did I learn?

That I love development, dude.
It isn't often that I get a sudden strike of inspiration like this, but I absolutely could not put this idea away once it came to me.
It was *really* cool to see this come together over the course of two weeks or so.
I also learned a ton about the history of the football pool and my family -- I'm so lucky to have such an amazing family that can support and enjoy a project like this one!
