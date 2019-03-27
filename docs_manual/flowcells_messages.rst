.. _flowcells_messages:

==================
Flow Cell Messages
==================

The "Messages" tab contains the user interface for posting messages, optionally with attachments.

On the top, you see a list of all messages.
Messages can either consist of unformatted text (line breaks are interpreted) or Markdown.
Markdown allows the embedding of links and highlighting of text.
Each message can have a list of attachments.

The message system can be used for various functions.

1. The Digestiflow Demux tool will add a message to the flow cell with its results.
   In case of success, log files are attached as well as archives of the MultiQC report.
   In case of failure, only log files are attached.

2. You can use this for persisting the wet-lab Excel sheets that you base your Digestiflow sample sheets on.

3. Machine and demultiplexing operators can use this for persisting information and discussion results.
   E.g., in case of issues it can be useful to leave small notes that explain the issue.
   This can be followed by documenting the resolution.
   As you can find text in the message subjects and bodies, a site's messages quickly become a useful resource for issue root cause analysis.
   Instead of discussions disappearing in individual user's mailboxes, they are visible for all members of a site.

You can use the form at the bottom for writing messages.
You can upload up to three attachments in one go.
If you want to upload more attachments, click "save as draft".
Afterwards, you will be able to more attachments (and also remove existing ones an modify the message subject or body).
Each user can have at most one active draft for each flow cell.

Do not forget to finally send the message (or publish the draft) by clicking "Send".
