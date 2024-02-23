#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
for path in [os.getcwd(),"software/Util","software/scripts","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource
from sdoterm import *
from buildtermlist import buildlist

def fileName(fn):
    name = OUTPUTDIR + "/" +fn
    checkFilePath(os.path.dirname(name))
    return name

def docsTemplateRender(template,extra_vars=None):
    tvars = {
        'BUILDOPTS': BUILDOPTS,
        'docsdir': DOCSDOCSDIR
    }
    if extra_vars:
        tvars.update(extra_vars)
    return templateRender(template,tvars)

def singleHome(page):
    global listings
    if not listings:
        listings = []
        listings.append(listingNode("Thing",title="Types:"))
        listings.append(listingNode("DataType",title="DataTypes:"))
    extra_vars = {
        'home_page': "True",
        'title': SITENAME,
        'termcounts': SdoTermSource.termCounts(),
        'listings': listings
    }
    return docsTemplateRender("docs/Home.j2",extra_vars)

def schemasPage(page):
    extra_vars = {
        'home_page': "False",
        'title': SITENAME + ' - Schemas',
        'termcounts': SdoTermSource.termCounts()
    }
    return docsTemplateRender("docs/Schemas.j2",extra_vars)

def buildTermCatList(terms,checkCat=False):
    first = True
    cat = None
    termcat = {}
    termcount = 0
    for t in terms:
        if checkCat:
            tcat = t.cat
        else:
            tcat = ""
        if first or tcat != cat:
            first = False
            cat = tcat
            ttypes = {}
            termcat[cat] = ttypes
            ttypes[SdoTerm.TYPE] = []
            ttypes[SdoTerm.PROPERTY] = []
            ttypes[SdoTerm.DATATYPE] = []
            ttypes[SdoTerm.ENUMERATION] = []
            ttypes[SdoTerm.ENUMERATIONVALUE] = []
        if t.termType == SdoTerm.REFERENCE:
            continue
        ttypes[t.termType].append(t)
        termcount += 1

    termcat = dict(sorted(termcat.items()))
    return termcat, termcount


VISITLIST=[]
class listingNode():

    def __init__(self,term,depth=0,title="",parent=None):
        global VISITLIST
        termdesc = SdoTermSource.getTerm(term)
        if termdesc is None:  # Check if term description is not available
            print("No term found for:", term)
            return
        if parent == None:
            VISITLIST=[]
        self.repeat = False
        self.subs = []
        self.parent = parent
        self.title = title
        self.id = termdesc.label
        self.termType = termdesc.termType
        self.depth = depth
        self.retired = termdesc.retired
        self.pending = termdesc.pending
        if not self.id in VISITLIST:
            VISITLIST.append(self.id)
            if termdesc.termType == SdoTerm.ENUMERATION:
                for enum in sorted(termdesc.enumerationMembers):
                    self.subs.append(listingNode(enum,depth=depth+1,parent=self))
            for sub in sorted(termdesc.subs):
                self.subs.append(listingNode(sub,depth=depth+1,parent=self))

        else: #Visited this node before so don't parse children
            self.repeat = True
        #log.info("%s %s %s"%("  "*depth,term,len(self.subs)))


import json
def jsonldtree(page):
    global VISITLIST
    VISITLIST=[]

    term = {}
    context = {}
    context['rdfs'] = "http://www.w3.org/2000/01/rdf-schema#"
    context['schema'] = "https://schema.org"
    context['rdfs:subClassOf'] = { "@type": "@id" }
    context['description'] = "rdfs:comment"
    context['children'] = { "@reverse": "rdfs:subClassOf" }
    term['@context'] = context
    data = _jsonldtree("Thing",term)
    return json.dumps(data,indent=3)

def _jsonldtree(tid,term=None):
    termdesc = SdoTermSource.getTerm(tid)
    if not term:
        term = {}
    term['@type'] = "rdfs:Class"
    term['@id'] = "schema:" + termdesc.id
    term['name'] = termdesc.label
    if termdesc.supers:
        sups = []
        for sup in termdesc.supers:
            sups.append("schema:" + sup)
        if len(sups) == 1:
            term['rdfs:subClassOf'] = sups[0]
        else:
            term['rdfs:subClassOf'] = sups
    term['description'] = textutils.ShortenOnSentence(
        textutils.StripHtmlTags(termdesc.comment))
    if termdesc.pending:
        term['pending'] = True
    if termdesc.retired:
        term['attic'] = True
    if tid not in VISITLIST:
        VISITLIST.append(tid)
        if termdesc.subs:
            subs = []
            for sub in termdesc.subs:
                subs.append(_jsonldtree(sub))
            term['children'] = subs
    return term

listings = None

def fullReleasePage(page):
    listings = []
    listings.append(listingNode("Thing",title="Type hierarchy"))
    types = SdoTermSource.getAllEnumerationvalues(expanded=True)
    types.extend(SdoTermSource.getAllTypes(expanded=True))
    types = SdoTermSource.expandTerms(types)
    types = sorted(types, key=lambda t: t.id)
    extra_vars = {
        'home_page': "False",
        'title': "Full Release Summary",
        'version': getVersion(),
        'date': getCurrentVersionDate(),
        'listings': listings,
        'types': types,
        'properties': SdoTermSource.getAllProperties(expanded=True)
    }
    return docsTemplateRender("docs/FullRelease.j2",extra_vars)

def aboutPage(page):
    extra_vars = {
        'home_page': "False",
        'title': "About",
        'version': getVersion(),
        'date': getCurrentVersionDate()
    }
    return docsTemplateRender("docs/About.j2",extra_vars)

def termfind(file):
    if not hasOpt("notermfinder"):
        print("Building term list")
        return buildlist(True)
    return ""

PAGELIST = {"Home": (singleHome,["docs/home.html"]),
             "FullRelease": (fullReleasePage,["docs/fullrelease.html","releases/%s/schema-all.html" % getVersion()]),
             "TermFind": (termfind,["docs/termfind/termlist.txt"]),
             "About": (aboutPage,["docs/about.html","releases/%s/schema-all.html" % getVersion()]),
             "Tree": (jsonldtree,["docs/tree.jsonld"])
         }

def buildDocs(pages):
    all = ["ALL","All","all"]
    for a in all:
        if a in pages:
            pages = sorted(PAGELIST.keys())
            break


    for p in pages:
        print("%s:"%p)
        if p in PAGELIST.keys():
            func, filenames = PAGELIST.get(p,None)
            if func:
                content = func(p)
                for filename in filenames:
                    fn = fileName(filename)
                    f = open(fn,"w", encoding='utf8')
                    f.write(content)
                    f.close()
                    print("Created %s" % fn)
        else:
            print("Unknown page name: %s" % p)
