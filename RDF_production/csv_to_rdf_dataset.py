import csv
import rdflib
from rdflib.namespace import XSD, RDF, RDFS, OWL, SKOS
from rdflib import URIRef, Literal, Namespace

schema = Namespace("http://schema.org/")
dcterms = Namespace("http://purl.org/dc/terms/")
crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
time = Namespace("http://www.w3.org/2006/time#")
dbo = Namespace("http://dbpedia.org/ontology/")
frbroo = Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
fabio = Namespace("http://purl.org/spar/fabio/")
arco = Namespace("https://w3id.org/arco/ontology/")
co = Namespace("https://w3id.org/arco/ontology/context-description/")
loc = Namespace("https://w3id.org/arco/ontology/location/")
lode = Namespace("http://linkedevents.org/ontology/")

namespaces = {
    "schema": schema,
    "dcterms": dcterms,
    "crm": crm,
    "dbo": dbo,
    "frbroo": frbroo,
    "fabio": fabio,
    "arco": arco,
    "co": co,
    "loc": loc,
    "lode": lode,
    "time": time
}

subjects_uri = {}

people = set()
places = set()
institutions = set()
arc_sites = set()
arc_buldings = set()
events = set()
activities = set()
items = set()
dates = set()
subject = set()
t_spans = set()

data = {}



with open("data_representation - complete_dataset.csv", mode="r", encoding="utf-8") as f:
    csv_reader = csv.DictReader(f)
    # casting csv_reader into a list
    csv_reader_list = list(csv_reader)
    #print(csv_reader_list)

    for row in csv_reader_list:
        # extracting people
        if "birthDate" in row["predicate"]:
            people.add(row["subject"])
        # extracting places
        for place in ["stabiae", "herculaneum", "naples", "pompeii"]:
            if row["object"].lower() == place:
                places.add(row["object"])
        # extracting institutions
        if "coverage" in row["predicate"]:
            institutions.add(row["object"])
        # extracting sites
        if "site" in row["subject"].lower():
            arc_sites.add(row["subject"])
        # extracting buildings 
        if "temple" in row["object"].lower() or "sanctuary" in row["object"].lower():
            arc_buldings.add(row["object"])
        # extracting events
        if "death" in row["subject"].lower() or "eruption" in row["subject"].lower():
            events.add(row["subject"])
        # extracting activities
        if row["subject"].lower() == "excavation":
            activities.add(row["subject"])
        # extracting dates
        if row["subject"] == "79":
            dates.add(row["subject"])
        # extracting subjects
        if row["object"] == "Demetra":
            subject.add(row["object"])
        # extracting time spans
        if "century" in row["subject"] or " AD" in row["subject"] or " BC" in row["subject"] or "1924" in row["subject"]:
            t_spans.add(row["subject"])
        # extracting items
        if "created" in row["predicate"] or "frbroo" in row["predicate"]:
            items.add(row["subject"])

    
    # assigning URIs and associating strings to them in a dictionary
    for x in people:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/person/"+"-".join(slug)
    for x in places:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/place/"+"-".join(slug)
    for x in institutions:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/institution/"+"-".join(slug)
    for x in arc_sites:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/archaeological-site/"+"-".join(slug)
    for x in arc_buldings:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/archaeological-building/"+"-".join(slug)
    for x in events:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/event/"+"-".join(slug)
    for x in activities:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/activity/"+"-".join(slug)  
    for x in dates:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/date/"+"-".join(slug)
    for x in subject:
        slug = x.lower()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/subject/"+slug
    for x in t_spans:
        slug = x.lower().split()
        slug = [s for s in slug if s != '-']
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/time-span/"+"-".join(slug)
    for x in items:
        slug = x.lower().split()
        subjects_uri[x] = "http://w3id.org/the-eruption-in-lod/item/"+"-".join(slug)
    

    for key, val in subjects_uri.items():
        for row in csv_reader_list:
            # Checking if the subject in the csv matches the current key in subjects_uri
            if row["subject"] == key:
                # checking for inclusion of the URI in the dictionary
                if val not in data:
                    # populate the dictionary with URIs as keys and initialize empty list as value
                    data[val] = []
            
            # Check if the object should be treated as a URI
                if row["object"] in subjects_uri:
                    object_uri = subjects_uri[row["object"]]
                # Append predicate with the URI object
                    data[val].append({row["predicate"]: object_uri})
                else:
                # If the object is not in subjects_uri, treat it as a literal
                    data[val].append({row["predicate"]: row["object"]})

    #print(data)

    # populate graph
    g = rdflib.Graph()

    g.bind("schema", schema)
    g.bind("dcterms", dcterms)
    g.bind("crm", crm)
    g.bind("time", time)
    g.bind("dbo", dbo)
    g.bind("frbroo", frbroo)
    g.bind("fabio", fabio)
    g.bind("arco", arco)
    g.bind("co", co)
    g.bind("loc", loc)
    g.bind("lode", lode)

    def populate_graph(my_graph, outer_dict, ns_dict):
        for key, value_list in outer_dict.items():
            for inner_dict in value_list:
                for pred, obj in inner_dict.items():
                    pred = pred.strip()
                    #print(pred)
                    pref, prop = pred.split(":")
                    for ns in ns_dict.keys():
                        if ns == pref and "http" in obj:
                            my_graph.add((URIRef(key), URIRef(ns_dict[ns]+prop), URIRef(obj))) 
                        elif ns == pref and "http" not in obj:
                            my_graph.add((URIRef(key), URIRef(ns_dict[ns]+prop), Literal(obj)))
                            
        
        # assigning datatypes to literals
        for s, p, o in list(my_graph.triples((None, None, None))):
            if isinstance(o, Literal):
                if o.value.isdigit() and len(o.value) == 4:
                    my_graph.remove((s, p, o))
                    my_graph.add((s, p, Literal(o.value, datatype=XSD.gYear)))
                elif o.value.startswith("-") and len(o.value) == 5:
                    my_graph.remove((s, p, o))
                    my_graph.add((s, p, Literal(o.value, datatype=XSD.gYear)))
                elif "-" in o.value and len(o.value) == 10:
                    if not any(char.isalpha() for char in o.value):
                        my_graph.remove((s, p, o))
                        my_graph.add((s, p, Literal(o.value, datatype=XSD.date)))
                else:
                    my_graph.remove((s, p, o))
                    my_graph.add((s, p, Literal(o.value, datatype=XSD.string)))

        # check datatype assignment            
        #for s, p, o, in g.triples((None, None, None)):
        #    if isinstance(o, Literal):
        #         print(f"Subject: {s}, Predicate: {p}, Object: {o}, Datatype: {o.datatype}")
        
        return my_graph
    
    populate_graph(g, data, namespaces)

    # associate RDF type and RDFS label
    for entity, uri in subjects_uri.items():
        if "person" in uri and "pliny-the-elder" not in uri:
            g.add((URIRef(uri), RDF.type, URIRef(schema.Person)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if entity == "Pliny the Elder":
            g.add((URIRef(uri), RDF.type, URIRef(crm.E39)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "vesuvius-eruption" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(lode.event)))
        if "death" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(crm.E5)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "place" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(crm.E53)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "subject" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(crm.E55)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "archaeological-site" in uri or "archaeological-building" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(arco.archaeological_property)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "institution" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(crm.E74)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "time-span" in uri or "date" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(crm.E52)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "activity" in uri:
            g.add((URIRef(uri), RDF.type, URIRef(crm.E7)))
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        if "item" in uri:
            g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
        for subj, dict_list in data.items():
            if subj == uri:
                if "vettii" in uri:
                    g.add((URIRef(uri), RDF.type, URIRef(arco.archaeological_property)))
                    g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
                if "destruction" in uri:
                    g.add((URIRef(uri), RDF.type, URIRef(crm.E22)))
                    g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
                if "documentary" in uri:
                    g.add((URIRef(uri), RDF.type, URIRef(fabio.moving_image)))
                    g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
                if "photo" in uri or "poster" in uri:
                    g.add((URIRef(uri), RDF.type, URIRef(fabio.still_image)))
                    g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
                if "novel" in uri:
                    g.add((URIRef(uri), RDF.type, URIRef(fabio.book)))
                    g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
                if "map" in uri:
                    g.add((URIRef(uri), RDF.type, URIRef(loc.map)))
                    g.add((URIRef(uri), RDFS.label, Literal(entity, datatype=XSD.string)))
                if "vesuvius-eruption" in uri:
                    for inner_dict in dict_list:
                        for k, v in inner_dict.items():
                            #print(k, v)
                            if "involved" in k and "vettii" not in v: 
                                g.add((URIRef(v), RDF.type, URIRef(crm.E22)))
        
    # associate authorities
    for entity, uri in subjects_uri.items():
        if entity in places:
            if entity == "Pompeii":
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q36471")))
            if entity == "Stabiae":
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.geonames.org/3179661")))
            if entity == "Herculaneum":
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q72111")))
        if entity in arc_sites:
            if "Stabiae" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q547910")))
            if "Herculaneum" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.geonames.org/3177364")))
            if "Pompeii" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.geonames.org/3170336")))
        if entity in people:
            if "Martin" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("http://vocab.getty.edu/page/ulan/500023063")))
            if "Elder" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://viaf.org/viaf/100219162/#Pliny,_the_Elder")))
            if "Younger" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://viaf.org/viaf/10638270/#Pliny,_the_Younger")))
            if "Reeves" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://viaf.org/viaf/8607800/#Reeves,_Steve")))
            if "Lytton" in entity:
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://viaf.org/viaf/99871326/#Lytton,_Edward_Bulwer_Lytton,_Baron,_1803-1873.")))
        if entity in activities:
            g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q959782")))
        if entity in items:
            if "destruction" in entity.lower():
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q16934315")))
            if "last" in entity.lower():
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q1218985")))
            if "giorni" in entity.lower():
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q1218993")))
            if "vettii" in entity.lower():
                g.add((URIRef(uri), OWL.sameAs, URIRef("https://www.wikidata.org/wiki/Q1590855")))
    
    # associations
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/activity/excavation"), SKOS.broader, URIRef("https://www.wikidata.org/wiki/Q23498")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/activity/excavation"), OWL.differentFrom, URIRef("https://www.wikidata.org/wiki/Q839954")))    
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/place/pompeii"), crm.P122, URIRef("http://w3id.org/the-eruption-in-lod/place/stabiae")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/place/pompeii"), crm.P89, URIRef("http://w3id.org/the-eruption-in-lod/place/naples")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/place/stabiae"), crm.P89, URIRef("http://w3id.org/the-eruption-in-lod/place/naples")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/place/herculaneum"), crm.P89, URIRef("http://w3id.org/the-eruption-in-lod/place/naples")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/place/naples"), crm.P89, URIRef("http://www.geonames.org/3181042")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/subject/demetra"), SKOS.broader, URIRef("http://www.wikidata.org/wiki/Q22989102")))
    g.add((URIRef("http://w3id.org/the-eruption-in-lod/subject/demetra"), schema.sameAs, URIRef("http://www.wikidata.org/wiki/Q32102")))
    g.add((URIRef("http://www.wikidata.org/wiki/Q22989102"), SKOS.related, URIRef("http://www.wikidata.org/wiki/Q34726")))
    
    # turtle serialization
    g.serialize(destination="complete_dataset.ttl", format="turtle")

    