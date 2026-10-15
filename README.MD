# Mini Social

This is a mock social media platform created for the Social Computing course at the University of Oulu by Dr. Aku Visuri and Daniel Szabo.

The codebase contains three missing implementations at the end of `app.py` for coding assignments #2 (moderation) and #3 (recommendation).

## Coding Assignment 1

This fork implements **Needs a reply**, **Your weekly goal**, and **Support you received** on the signed-in home feed, supporting Chapter 2 Claims 1 and 15 and Chapter 3 Claim 30.

See the [Assignment 1 guide](docs/assignment-1-guide.md) for setup, behavior, tests, and a two-account demonstration with a separate dataset.

The repository contains a ready database, you do not have to create your own data.

## Usage (for students)

1. Create a [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) of this repository
2. Clone your forked repository onto your computer
3. Make sure you have Python 3.11 installed
4. Install dependencies by running `pip install -r requirements.txt`
5. Start the server by running `python ./app.py`
6. The web application will be available at http://127.0.0.1:8080. 
7. The admin interface is at http://127.0.0.1:8080/admin, available only to the Admin user (username: admin, pw: admin)
8. Make sure your fork is public, and add its URL to your coursework assignments.

### Docker

If you prefer to run Mini-Social as a docker container, you can build the image and run it as follows:

1. Build image with `docker build --tag mini-social .`
2. Run image with the following command, where 8000 is the port you will access the application at `http://127.0.0.1:8000`

```
docker run -d -p 8000:5000 \
    --restart always \
    -v $(pwd)/database.sqlite:/python-docker/database.sqlite \
    mini-social
```
 
