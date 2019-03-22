.. _misc_api_tokens:

==========
API Tokens
==========

In your "user menu", you will find a menu entry "API Tokens" that takes you to the site-wide API token management.
An API token is a unique identifier for your account that consists of 64 randomly randomly characters and is thus infeasible to guess.
You can use it for authenticating requests to the Digestiflow REST API in a secure manner that is independent of your password.
Thus, you can store it in properly secured locations such as files that Digestiflow CLI and Demux can read.

.. note::
    The major advantage of using tokens in APIs is that you don't have to store your password in plain-text files.
    Also, you can create an arbitrary number of tokens.
    Thus, in case a token is compromised, it can be exchanged easily (the same is true if you lose your token).

.. note::
    For Digestiflow Cli and Demux, it also makes sense to create dedicated "machine" users in the Digestiflow Web database as described in the section :ref:`django_admin`.

------------------
Listing API Tokens
------------------

Using the "API Tokens" in your "user menu", you will be directed to the "Tokens" list.
Here, you can see the list of currently active tokens.
For each token, the table lists the creation time, expiry date, and a token "key" for identifying your token.
On the right hand side of each token entry there is a little gray button that allows for the deletion of a token.

Use the blue button "API Tokens" on the top right to access the token creation functions.

-------------------
Creating API Tokens
-------------------

When creating a token, the only thing that you can add is a "time to live."
That is, tokens expire after a defined number of hours.
Specifying ``0`` here makes the token live forever.

After the token has been created you will be able to see it only once, so copy it into another file.
In case you forget to copy the token don't worry as you can just create a new one.
