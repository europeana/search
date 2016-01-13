<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:template match="/">
        <add>
        <xsl:for-each select="/rdf:RDF/skos:Concept">
            <doc>
                <field name="europeana_id"><xsl:value-of select="@rdf:about"/></field>
                <field name="edm_conceptualClass">Concept</field>
                <xsl:apply-templates/>
            </doc>
        </xsl:for-each>
        </add>
    </xsl:template>
    
    <xsl:template match="skos:prefLabel">
        <xsl:variable name="lang" select="@xml:lang"/>
        <field name="skos_prefLabel.{$lang}"><xsl:value-of select="text()"/></field>
    </xsl:template>
    
    <xsl:template match="skos:altLabel">
        <xsl:variable name="lang" select="@xml:lang"/>
        <field name="skos_altLabel.{$lang}"><xsl:value-of select="text()"/></field>
    </xsl:template>
    
    <xsl:template match="skos:definition">
        <field name="skos_note"><xsl:value-of select="normalize-space(text())"/></field>
    </xsl:template>
    
    <xsl:template match="skos:exactMatch">
        <field name="skos_exactMatch"><xsl:value-of select="text()"/></field>
    </xsl:template>
    
    <xsl:template match="element()">
        <xsl:variable name="name" select="concat('skos_', local-name())"></xsl:variable>
        <xsl:variable name="identifier" select="@rdf:resource"/>
        <field name="{$name}"><xsl:value-of select="$identifier"/></field>
    </xsl:template>
</xsl:stylesheet>