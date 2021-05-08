Quickstart
##########

.. warning::
    All AsyncDex operations have to be done inside of an async context.

Create an instance of MangadexClient:

.. code-block:: python

    from asyncdex import MangadexClient

    async def main():
        client = MangadexClient()

Make a request for a random manga and print the authors of the manga:

.. code-block:: python

    manga = await client.random_manga()
    print(f"{manga.id}: {manga.titles.en.primary}")
    await manga.load_authors()
    print(f"Author of {manga.titles.en.primary}: {manga.authors[0].name}")


Log in to your MangaDex account:

.. code-block:: python

    await client.login(username="yourusername", password="yourpassword")
    # alternate method
    client = MangadexClient(username="yourusername", password="yourpassword")
    await client.login()

View your manga follows list:

.. code-block:: python

    response = await client.request("GET", "/user/follows/manga")
    json = await response.json()
    [print(item["data"]["id"]) for item in json["results"]]
