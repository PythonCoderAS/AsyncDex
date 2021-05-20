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


Log in to your MangaDex account (see :ref:`authentication` for other authentication options):

.. code-block:: python

    client = MangadexClient(username="yourusername", password="yourpassword")
    await client.login()

View your manga follows list:

.. code-block:: python

    async for item in self.user.manga():
        print(item.titles.first().primary)
