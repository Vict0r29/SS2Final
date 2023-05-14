import urllib
from flask import Flask, session, abort, redirect, request, render_template, jsonify, make_response

url = "https://www.sciencedirect.com/science/article/pii/S1364815215000811"
file = urllib.request.urlopen(url)

for line in file:
	decoded_line = line.decode("utf-8")
	print(decoded_line)