<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:tei="http://www.tei-c.org/ns/1.0"  
    version="1.0">

<xsl:output method="html" indent="yes"/> 

    <xsl:template match="/">
        <html>
            <head>
                <title><xsl:value-of select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/></title>
                <style>
                    body {
                            font-family: 'Palatino', Garamond, sans-serif;
                            margin: 70px;
                            background-color: #c6c6c6; 
                            text-align:justify;
                        }
                    .h1 { 
                            color: #6d0900
                        }
                    .metadata {
                            padding-bottom: 15px;
                            margin-bottom: 20px;
                            text-align: center;
                        }
                </style>
            </head>
            <body>
                <div class="metadata">
                    <h1><xsl:value-of select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/></h1>
                    <h2>By <xsl:value-of select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author"/></h2>
                    <h3>Publication Details</h3>
                    <p>Publisher: <xsl:value-of select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:publisher"/></p>
                    <p>Date: <xsl:value-of select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date"/></p>
                    <p>Id: <xsl:value-of select="tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:idno"/></p>
                </div>
                <div>
                    <h3>Characters</h3>
                    <ul> <!-- unordered list-->
                        <xsl:for-each select="tei:TEI/tei:teiHeader/tei:profileDesc/tei:particDesc/tei:listPerson/tei:person/tei:persName">
                            <li> <!--list element-->
                                <xsl:value-of select="tei:forename"/> 
                                <xsl:value-of select="tei:surname"/>
                                <xsl:if test="tei:addName">
                                    (<xsl:value-of select="tei:addName"/>)
                                </xsl:if>
                            </li>
                        </xsl:for-each>
                    </ul>
                </div>
                <!-- Testo principale -->
                <xsl:for-each select="tei:TEI/tei:text/tei:body/tei:div">
                    <div>
                        <h3>Chapter <xsl:value-of select="@n"/>: <xsl:value-of select="head"/></h3>
                        <xsl:for-each select="tei:div[@type='paragraph']">
                            <p>
                                <xsl:value-of select="tei:p"/>
                            </p>
                        </xsl:for-each>
                    </div>
                </xsl:for-each>                
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
            