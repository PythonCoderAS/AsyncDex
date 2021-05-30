.. _permission:

MangaDex Permissions
====================

Several endpoints of the API require permissions. The MangaDex client checks the list of user permissions whenever any of these endpoints are called, and if the permission is not present, :class:`.PermissionMismatch` is raised.

Anonymous Permissions
+++++++++++++++++++++

By default, anonymous (logged out) users have this set of permissions:

* ``author.list``
* ``author.view``
* ``chapter.list``
* ``chapter.view``
* ``cover.list``
* ``cover.view``
* ``manga.list``
* ``manga.view``
* ``scanlation_group.list``
* ``scanlation_group.view``

This allows them to both view individual authors, chapters, mangas, and scanlation groups as well as use the listing endpoints. These permissions are checked by :meth:`.Author.fetch`, :meth:`.CoverArt.fetch`, :meth:`.Chapter.fetch`, :meth:`.Group.fetch` and :meth:`.Manga.fetch`, as well as :meth:`.get_authors`, :meth:`.get_covers`, :meth:`.get_chapters`, :meth:`.get_groups` and :meth:`.get_mangas`/:attr:`.search`.

Logged in Permissions
+++++++++++++++++++++

.. warning::
    The MangaDex API has changed the permission system and revoked these permissions for users.

When logged in as a normal user, these additional permissions are granted:

* ``author.create``
* ``cover.create``
* ``chapter.upload``
* ``manga.create``
* ``scanlation_group.create``
* ``user.list``


This allows the user to create new authors, chapters, mangas, and scanlation groups. These permissions are checked by :meth:`.create_author`, :meth:`.create_group`, and :meth:`.create_manga`.

Checking Permissions
++++++++++++++++++++

At any time, the client's permissions can be checked by :attr:`.ClientUser.permissions`:

.. code-block:: python

    print(client.user.permissions)
