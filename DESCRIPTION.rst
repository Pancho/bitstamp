Bistamp Python API
==================

This is an official API library for accessing Bitstamp's REST API.

Sample Usage
------------

Usage

In the root folder of this package you can find the file example.py which contains an
example of how to instantiate the class (with python file format for config) and how to
call the ticker method.

Configuration

To configure your API key and secret this library requires for you to use an external file
where you store those two values. To make your life easier, we've made it possible for you
to use one of three file types: json, ini or plain python. To see examples, browse the
examples folder.
Worth mentioning: python config format will work up until Python 3.4 as the importing
procedure is not defined for later versions (expect na update for that case).