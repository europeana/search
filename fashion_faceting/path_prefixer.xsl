<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <!-- ************************************************************************
         Takes files returned as XML from Solr and adds Fashion-specific path
         prefixing where appropriate, retransforming into XML ready for 
         reingest.
         
         @author: thill
         
         ************************************************************************ -->
    <xsl:variable name="copyfields" select="distinct-values(doc('schema.xml')//copyField/@dest)"/>
    
    <xsl:template match="/">
        <add>
            <xsl:for-each select="//doc">
                <doc>
                    <xsl:variable name="is-fash-doc" select="exists(field[@name eq 'provider_aggregation_edm_provider'][text() eq 'Europeana Fashion'])" as="xs:boolean"/>
                    <xsl:for-each select="element()">
                        <xsl:variable name="name" select="@name"/>
                        <xsl:choose>
                            <xsl:when test="$name eq '_version_'"/>
                            <xsl:when test="$name eq 'CREATOR'">
                                <xsl:for-each select="str">
                                <xsl:variable name="prefixed-creator"><xsl:value-of select="concat('/fasion/designer/', text())"/></xsl:variable>
                                <field name="CREATOR"><xsl:value-of select="$prefixed-creator"/></field>
                                </xsl:for-each>
                            </xsl:when>
                            <!--
                                ...
                            -->
                            <xsl:when test="$name = $copyfields">
                                <!-- need to eliminate copyfields from output -->
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:choose>
                                    <xsl:when test="count(child::element()) eq 0">
                                        <field name="{$name}"><xsl:value-of select="text()"/></field>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:for-each select="child::element()">
                                            <field name="{$name}"><xsl:value-of select="text()"/></field>
                                        </xsl:for-each>
                                    </xsl:otherwise>
                                </xsl:choose>
                                
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </doc>
            </xsl:for-each>
        </add>
    </xsl:template>
    
    
</xsl:stylesheet>