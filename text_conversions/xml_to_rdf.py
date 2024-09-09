import xml.etree.ElementTree as ET
import rdflib
from rdflib import URIRef, Literal, Namespace
from rdflib import RDF, RDFS, XSD, OWL
import re

tree = ET.parse("vesuvius eruption 7 xml.unknown")
root = tree.getroot()
print("tree parsed")

ns = {"": "http://www.tei-c.org/ns/1.0"}

schema = Namespace("http://www.schema.org/")
fabio = Namespace("http://purl.org/spar/fabio/")
rel = Namespace("http://purl.org/vocab/relationship")

title = tree.find("teiHeader/fileDesc/sourceDesc/biblStruct/monogr/title", ns).text
split_title = title.split("/")
title = split_title[0]
print(title)
slug = title.lower().split()
title_uri = "http://www.w3id.org/book/"+"-".join(slug)
print(title_uri)

author = tree.find("teiHeader/fileDesc/sourceDesc/biblStruct/monogr/author", ns).text
author_ctrl = tree.find("teiHeader/fileDesc/titleStmt/author", ns).attrib["sameAs"]
split_author = author.split(",")
author = split_author[0]
slug = author.lower().split()
author_uri = "http://www.w3id.org/book/"+"-".join(slug)
print(author_uri)

pub_date = tree.find("teiHeader/fileDesc/sourceDesc/biblStruct/monogr/imprint/date", ns).text
setting_place = tree.find("teiHeader/profileDesc/settingDesc/setting/name", ns).text
setting_place = setting_place.split(",")
setting_date = tree.find("teiHeader/profileDesc/settingDesc/setting/time", ns).text

characters = {}
for person in tree.findall("teiHeader/profileDesc/particDesc/listPerson/person/persName/forename", ns):
    character_name = person.text
    characters[character_name] = "http://www.w3id.org/character/"+character_name.lower()
    print(characters)

characters_nicknames = []
for nickname in tree.findall("teiHeader/profileDesc/particDesc/listPerson/person/persName/addName", ns):
    if nickname.text:
        character_nickname = nickname.text
        characters_nicknames.append(character_nickname)

places = {}
for place in tree.findall(".//p/placeName", ns):
    if place is not None and place.text:
        place_name = place.text
        place_geo = place.attrib.get("sameAs")
        places[place_name] = place_geo
for place in tree.findall(".//p//placeName", ns):
    if place is not None and place.text:
        place_name = place.text
        place_geo = place.attrib.get("sameAs")
        places[place_name] = place_geo

del places["temple"]

places_uri = []
for key in places.keys():
    if " " in key:
        slug = key.lower().split()
        place_uri = "http://www.w3id.org/place/"+"-".join(slug)
        places_uri.append(place_uri)
    else:
        place_uri = "http://www.w3id.org/place/"+key.lower()
        places_uri.append(place_uri)

print(places)

direct_speech = {}
count = 0
for speech in tree.findall(".//p/said", ns):
    count += 1
    speech_cont = "".join(speech.itertext())
    direct_speech[speech_cont] = ""
    #print(direct_speech)
    spoken_by = speech.attrib["who"]
    spoken_by = re.sub(r'[^\w]', "", spoken_by)
    direct_speech[speech_cont] = {"send": spoken_by}
    spoken_to = speech.attrib["toWhom"]
    spoken_to = re.sub(r'[^\w]', "", spoken_to)
    direct_speech[speech_cont] = {"send": characters[spoken_by], "rec": characters[spoken_to]}
    speech_uri = "http://w3id.org/quotation/"+"quot"+str(count)
    direct_speech[speech_cont] = {"send": characters[spoken_by], "rec": characters[spoken_to], "uri": speech_uri}
   
print(direct_speech)

g = rdflib.Graph()

g.bind("schema", schema)
g.bind("fabio", fabio)
g.bind("arco", rel)

# book
g.add((URIRef(title_uri), RDF.type, URIRef(fabio.book)))
g.add((URIRef(title_uri), RDFS.label, Literal(title, datatype=XSD.string)))
g.add((URIRef(title_uri), fabio.hasCreator, URIRef(author_uri)))
    #who
g.add((URIRef(author_uri), RDF.type, URIRef(schema.Person)))
g.add((URIRef(author_uri), RDFS.label, Literal(author, datatype=XSD.string)))
g.add((URIRef(author_uri), OWL.sameAs, URIRef(author_ctrl)))
    #when
g.add((URIRef(title_uri), schema.dateCreated, Literal(pub_date, datatype=XSD.gYear)))
    #where
g.add((URIRef(title_uri), schema.contentLocation, Literal(setting_place[0], datatype=XSD.string)))
g.add((URIRef(title_uri), schema.contentLocation, Literal(setting_place[1], datatype=XSD.string)))
g.add((URIRef(title_uri), schema.contentLocation, URIRef(places_uri[0])))
g.add((URIRef(title_uri), schema.contentLocation, URIRef(places_uri[1])))

#characters
for key, value in characters.items():
    g.add((URIRef(title_uri), schema.character, URIRef(value)))
    g.add((URIRef(value), RDFS.label, Literal(key, datatype=XSD.string)))
    if key == "Ione":
        g.add((URIRef(value), rel.engagedTo, URIRef(characters["Glaucus"])))
    if key == "Glaucus":
        g.add((URIRef(value), schema.additionalName, Literal(characters_nicknames[0], datatype=XSD.string)))
    if key == "Nydia":
        g.add((URIRef(value), schema.additionalName, Literal(characters_nicknames[1], datatype=XSD.string)))

#places
for key, value in places.items():
    g.add((URIRef(places_uri[0]), OWL.sameAs, URIRef(value)))
    g.add((URIRef(places_uri[1]), OWL.sameAs, URIRef(value)))
    g.add((URIRef(places_uri[0]), RDFS.label, Literal(key, datatype=XSD.string)))
    g.add((URIRef(places_uri[1]), RDFS.label, Literal(key, datatype=XSD.string)))

# quotations
for speech, attr_dict in direct_speech.items():
   for key, value in attr_dict.items():
        if key == "uri":
            g.add((URIRef(value), RDF.type, URIRef(schema.quotation)))
            g.add((URIRef(value), RDFS.label, Literal(speech, datatype=XSD.string)))
            g.add((URIRef(value), schema.spokenByCharacter, URIRef(attr_dict["send"])))
        if key == "send":
            g.add((URIRef(value), schema.knows, URIRef(attr_dict["rec"])))


for s, p, o in g.triples((None, None, None)):
    print(s, p, o)

# turtle serialization
g.serialize(destination="novel_chapters_dataset.ttl", format="turtle")

