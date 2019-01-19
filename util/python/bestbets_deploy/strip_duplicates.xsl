<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <!-- *************************************************************************
         Solr falls over and dies if two identical queries are listed as boosted.
        
        
         Although 'identical' here means, 'identical after all Solr processing 
         applied', there is no way to check this without hitting the server.
         This file thus represents a slight optimisation, weeding out all strict
         duplicates (that is to say, strings that are identical even before Solr
         processing) prior to hitting the server.
        
         ************************************************************************* -->
    
    <xsl:variable name="deep-copy"><xsl:copy-of select="/"/></xsl:variable>
    
    <xsl:template match="/">
        <elevate>
            <xsl:for-each select="distinct-values(/elevate/query/@text)">
                <xsl:variable name="content" select="."/>
                <xsl:choose>
                    <xsl:when test="count($deep-copy/elevate/query[@text eq $content]) &gt; 1">
                        <xsl:comment>DUPLICATE ENTRIES FOR '<xsl:value-of select="$content"/>' FOUND</xsl:comment>
                        <xsl:copy-of select="($deep-copy/elevate/query[@text eq $content])[1]"></xsl:copy-of>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:copy-of select="$deep-copy/elevate/query[@text eq $content]"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </elevate>
    </xsl:template>
    
</xsl:stylesheet>