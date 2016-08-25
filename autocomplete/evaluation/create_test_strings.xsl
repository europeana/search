<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://exslt.org/math"
    extension-element-prefixes="math"
    exclude-result-prefixes="xs"
    version="2.0">
    
        
    <xsl:template match="/">
        <xsl:for-each select="/root/query">
            <xsl:variable name="strlen" select="((count(./preceding-sibling::query)) mod 3) + 3" />
            <xsl:variable name="startstr" select="substring(@text, 1, $strlen)"/>
            <text><xsl:value-of select="@text"/><xsl:value-of select="'  '"></xsl:value-of><xsl:value-of select="$startstr"/></text>
        </xsl:for-each>
        
        
    </xsl:template>
    
    
</xsl:stylesheet>