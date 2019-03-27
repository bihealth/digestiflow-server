.. _projects_permissions:

===========
Permissions
===========

Clicking the little "Members" icon in the left bar gives access to the Site member management area.

.. note::

    When using LDAP authentication, users are only created in the Digestiflow database after the first login.
    That is, any user from your LDAP directory will be able to login and then has to be given access to a site as described here.
    This is a two step process and the user can only be added **after** logging in for the first time.
    Alternative, you can use the "invite user" feature described below to invite users that are not part of the project yet and select a role they should be given.
    After logging in for the first time, they will be granted site membership with the role that you selected.
    When using local users, you can add users through the Django administration interface.

------------
Member Roles
------------

Site members can have one of three roles.

Site Owner
    There can be one site owner that is able to modify all aspects of the site and the contained objects.
    Further, only the owner can assign the delegate role.

Delegates
    Users with this role also are able to modify all aspects of the site except for assigning delegate roles.
    They can add users with the contributor and guest role, though.

Contributor
    Contributor users are able to create and edit sequencing machines and barcode sets as well as flow cells.

Guests
    Site guests have read-only access to a site.

Further, standard Django user management allows to assign another important flags to a user (see below for details).

Superuser
    A user that is automatically granted all permissions within the full Digestiflow installation.

-----------
Member List
-----------

On this page you can see the list of users that have access to the site and their role within the project.
User the blue "Member Operations" button to access the functionality to add or invite members, and view the invites.
Next to each entry, the little gray button gives access to updating or deleting users.
Of course, a confirmation dialogue will be display before removing a user from a project.

--------------------
Managing Memberships
--------------------

Managing site memberships should be self-explanatory.

---------------
Sending Invites
---------------

The main limitation that is faced when using LDAP authentication is the fact that users have to log in first in order to create a user record in the Digestiflow Server database.
The onboarding process of users can be simplified by the invite feature.
Here, you send an invitation email to a users with a link for logging into a given Digestiflow site.
When sending the invite you also define a role for the user.
Upon accepting the invitation by clicking on the link and following the instructions, the user will be automatically granted the appropriate role on the project (this does not work for project owners yet).

.. _django_admin:

------------
Django Admin
------------

Super users can also access the Django administration interface.
Django is the web application framework used for developing Digestiflow.
You can access is through the User menu.

.. note::

    Note that using the admin interface beyond managing users can damage the data in your Digestiflow installation.

After opening, scroll down to the "Users" section and click the little "Users" link within for managing users.
The interface is self-explanatory.
The relevant features are:

Create Local Users
    Even when using LDPAP authentication, you can create local users in the databse.
    This is useful for creating single-purpose users, e.g., for isolating the import/demux process for each machine or site and decoupling it from personal accounts.

Reset Password
    You can update the password of a user in the Digestiflow database.
    Note that this only applies to local users.

Disabling Users
    Uncheck the ``Active`` box in the "Permissions" section of a user to disable users (they will not be able to login any more).

Superuser
    Check the ``Active`` box in the "Permissions" section of a user to give all permissions to this user.

Don't forget to apply the changes made to users by clicking "Save".

.. note::

    The Django group and permission system is not used for Digestiflow.
