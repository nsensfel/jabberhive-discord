## What is JabberHive?
JabberHive is a modular Reply Bot system. All "modules" are in fact separate
programs linked together using the JabberHive Protocol. Please refer to the
protocol for more information.

## Component Description
* Discord Gateway for a JabberHive network.

## JabberHive Protocol Compatibility
* **Protocol Version(s):** 1.
* **Inbound Connections:** None.
* **Outbound Connections:** Single.
* **Pipelining:** No.
* **Behavior:** Gateway.

## Dependencies
- Python 3.5+
- discord.py (https://github.com/Rapptz/discord.py)

## Example of Use
``./jh-discord -d /tmp/lc0 -t YOUR_TOKEN''
