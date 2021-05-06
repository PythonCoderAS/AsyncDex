Quickstart
##########

.. warning::
    All AsyncDex operations have to be done inside of an async context.

Create an instance of MangadexClient:

.. code-block:: python

    from asyncdex import MangadexClient

    async def main():
        client = MangadexClient()

Make a request for a random manga:

.. code-block:: python

    response = await client.request("GET", "/manga/random")
    json = await response.json()
    print(json["data"]["id"])

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
