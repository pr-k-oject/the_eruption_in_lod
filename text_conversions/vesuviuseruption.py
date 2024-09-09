from lxml import etree
import os

print(os.getcwd())
# Carica XML e XSLT
xml_file = etree.parse("/Users/alicep/Downloads/TOMASI Vesuvius Eruption/vesuvius_eruption.xml")
xslt_file = etree.parse("/Users/alicep/Downloads/TOMASI Vesuvius Eruption/vesuvius_eruption_fromxml.xslt")

# Applica la trasformazione XSLT
transform = etree.XSLT(xslt_file)
result = transform(xml_file)

with open("vesuviuseruption.html", "wb") as f:
    f.write(etree.tostring(result, pretty_print=True))
print(str(result))