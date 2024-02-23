#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import argparse
for path in [os.getcwd(),"software/util"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from flask import Flask, render_template,after_this_request, request, Response
from rdflib import Graph, Namespace, RDF
import re
from colorama import Fore, Back, Style
from schemaversion import getVersion

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
parser.add_argument("--port", default=8080, help="Port (default: 8080")
parser.add_argument("--production", default=False, action='store_true', help="Production settings")
args = parser.parse_args()

# create the application object
app = Flask(__name__, static_folder='site', static_url_path='')

g = Graph()
g.parse("data/schema.ttl", format="ttl")

# Define namespaces
schema = Namespace("https://schema.org/")
VOCAB_URI = Namespace("https://schema.learndata.info/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

@app.route('/')
def serve_home():
    @after_this_request
    def add_headers(response):
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Accept'
        response.headers['Access-Control-Allow-Origin'] = '"*"'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Expose-Headers'] = 'Link'
        response.headers['link'] = '</docs/jsonldcontext.jsonld>; rel="alternate"; type="application/ld+json"'
        return response
    path = 'docs/home.html'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/favicon.ico')
def serve_favicon():
    path = 'docs/favicon.ico'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/robots.txt')
def serve_robots():
    path = 'docs/robots-blockall.txt'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/docs/devnote.css')
def serve_devnote():
    if args.production:
        path = 'docs/devnotehide.css'
    else:
        path = 'docs/devnoteshow.css'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/sitemap.xml')
@app.route('/docs/sitemap.xml')
def serve_sitemap():
    if args.production:
        path = 'docs/sitemap.xml'
    else:
        path = 'docs/sitemap.xml_no_serve'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/docs/collab/<path>')
def serve_colls(path):
    if not path.endswith(".html"):
        path = "docs/collab/" +path+".html"

    print("Serving file: " + path)

    return app.send_static_file(path)

@app.route('/<path>')
@app.route('/<path>')
def serve_terms(path):
    # Get Accept header
    accept_header = request.headers.get('Accept')

    term_uri = VOCAB_URI[path]
    term_graph = Graph()
    term_graph.bind("schema", schema)
    term_graph.bind("base", VOCAB_URI)

    # Check if the requested term is a class
    class_triples = list(g.triples((term_uri, rdf.type, rdfs.Class)))

    if class_triples:
        # The requested term is a class, find all properties with schema:domainIncludes of the class
        #properties = [obj for s, p, obj in g.triples((None, schema.domainIncludes, term_uri))]
        # Add the class to the graph
        term_graph.add((term_uri, rdf.type, rdfs.Class))

        term_triples = g.triples((term_uri, None, None))
        for triple in term_triples:
            term_graph.add(triple)

        # Add properties with their metadata to the graph
        properties = list(g.triples((None, schema.domainIncludes, term_uri)))
        for prop, _, _ in properties:
            term_graph.add((term_uri, schema.hasProperty, prop))

    else:
        term_triples = g.triples((term_uri, None, None))
        for triple in term_triples:
            term_graph.add(triple)

    # If Accept header is not specified or supported, default to HTML format
    if accept_header is None or not any(accept_type in accept_header for accept_type in ['text/turtle', 'application/ld+json', 'application/rdf+xml']):
        accept_header = 'text/html'

    # Handle content negotiation
    if 'text/turtle' in accept_header:
        # Convert requested term to Turtle format
        turtle_data = term_graph.serialize(format='turtle')
        return Response(turtle_data, mimetype='text/turtle')
    elif 'application/ld+json' in accept_header:
        # Convert requested term to JSON-LD format
        jsonld_data = term_graph.serialize(format='json-ld')
        return Response(jsonld_data, mimetype='application/ld+json')
    elif 'application/rdf+xml' in accept_header:
        # Convert requested term to RDF/XML format
        rdf_data = term_graph.serialize(format='xml')
        return Response(rdf_data, mimetype='application/rdf+xml')
     # Check if the path does not end with ".html" or content negotiation is specified
    elif 'text/html' in accept_header:
        m = re.match("^([a-z])(.*)$", path)
        if m:
            path = "terms/properties/%s/%s%s.html" % (m.group(1), m.group(1), m.group(2))
        else:
            m = re.match("^([0-9A-Z])(.*)$", path)
            if m:
                path = "terms/types/%s/%s%s.html" % (m.group(1), m.group(1), m.group(2))

        return app.send_static_file(path)

    else:
        # Default to HTML format if no matching Accept header found
        return app.send_static_file(path)

@app.route('/version/<ver>')
@app.route('/version/<ver>/')
@app.route('/version/<ver>/<path>')
def serve_downloads(ver,path=""):
    if ver == "latest":
        ver = getVersion()
    if not len(path):
        path="schema-all.html"
    path = "releases/%s/%s" % (ver,path)
    print("Serving file: " + path)
    return app.send_static_file(path)

# start the server with the 'run()' method
if __name__ == '__main__':
    print("Local dev server for version: %s" % getVersion())
    if args.production:
        print(Fore.RED + "Runing with Production settings" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "Running with Development settings" + Style.RESET_ALL)

    app.run(host=args.host, port=args.port,debug=False)