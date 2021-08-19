Slack Printer
=============

A silly little project that prints new messages to a USB lp printer under 
Linux (`/dev/usb/lp0`).

Requires a Slack Bot with a user Oauth scope token that can read messages and
setup for event subscription. The server this runs runs on port 8774.

I personally have Slack reach this server via SSH port forwarding: 
`ssh -N -R 8774:localhost:8774 server`.

Config
------
Environment variables:

- SLACK_SIGNING_SECRET: Signing secret of your app
- SLACK_BOT_TOKEN: Slack user scope oauth token
- USER_ID: Your User ID. Will print when you are mentioned.
- GROUP_IDS: Groups you are in. Will print when a group is mentioned. Comma-seperated.
