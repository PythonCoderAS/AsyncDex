.. _authentication:

Authenticating to the MangaDex API
==================================

While most of the critical features such as finding manga and downloading chapters are open to everyone, many endpoints require authentication.

The client will automatically renew the session and refresh tokens if possible.

Methods that require authentication will check if the client is authenticated. If the client is unauthorized, an :class:`.Unauthorized` will be raised with the method and the relative path taken.

There are two ways to authenticate: via refresh token and via username/password.

Refresh Token
+++++++++++++

Refresh tokens are the preferred way to authenticate to the API. They do not require the storage of sensitive data and can easily be revoked should there be a need to do so. To use a refresh token, initialize the client with the ``refresh_token`` parameter (see :ref:`Obtaining a Refresh Token <obtain>` to get a refresh token):

.. code-block:: python

    client = MangadexClient(refresh_token="my refresh token here")

Pros:

* No need to store username/password
* Can be easily revoked

Cons:

* Need to be renewed every so often (currently lasts for one month)

Username/Password
+++++++++++++++++

The username and password pair is the common way to log into MangaDex, as they are more memorable than long refresh token strings. They are recommended for one-off client sessions and for local testing/development. There are two ways of entering the username and password: either through the Client initializor or through the :meth:`.login` method.

Pros:

* Do not need to be renewed (allows the client to self authenticate without never needing outside intervention such as supplying a new refresh token)

Cons:

* Login credentials have to be stored in order to be supplied to the client if the client is used in a script
* Login information needs to be prompted for if it is not stored

Utilizing Both Refresh Tokens and Username/Password
+++++++++++++++++++++++++++++++++++++++++++++++++++

When a new session token is obtained, the library will also check if the token is valid. If the token is invalid, the client will logout (without calling the logout endpoint) and be set to anonymous mode. If you want to check without fetching a new session token, use :meth:`.ClientUser.fetch` (which is implicitly called by :meth:`.get_session_token`), which will do the same thing.

Initializing Via Constructor
............................

.. code-block:: python

    client = MangadexClient(username="your username", password="your password")

Initializing Via Login Method
.............................

.. code-block:: python

    client = MangadexClient()
    await client.login(username="your username", password="your password")


.. _obtain:

Obtaining a Refresh Token
+++++++++++++++++++++++++

When you log in via the username and password, a refresh token is generated, which is then used to obtain the session token that is actually used in authentication. The refresh token is available via the :attr:`.MangadexClient.refresh_token` attribute.

.. code-block:: python

    client = MangadexClient(username="your username", password="your password")
    await client.login()
    print(client.refresh_token)
