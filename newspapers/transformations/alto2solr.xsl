<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
    xmlns:alto="http://www.loc.gov/standards/alto/ns-v2#"
    exclude-result-prefixes="xs xd" version="2.0">
    <xd:doc scope="stylesheet">
        <xd:desc>
            <xd:p><xd:b>Created on:</xd:b> Feb 12, 2018</xd:p>
            <xd:p><xd:b>Author:</xd:b>Timothy Hill</xd:p>
            <xd:p/>
        </xd:desc>
    </xd:doc>
    <xsl:param name="language" as="xs:string"/>
    <xsl:template match="/">
        <add>
            <doc>
                <field name="doc_type">Newspaper</field><!-- TODO: Get URI for this -->
                <field name="language"><xsl:value-of select="$language"/></field>
                <field name="body.{$language}">
                    <xsl:for-each select="//alto:Page">
                        <xsl:variable name="pageno">
                            <xsl:value-of select="count(preceding-sibling::Page) + 1"/>
                        </xsl:variable>
                        <xsl:for-each select="//alto:String">
                            <xsl:variable name="content" select="@CONTENT"/>
                            <xsl:variable name="xpos" select="@HPOS"/>
                            <xsl:variable name="ypos" select="@VPOS"/>
                            <xsl:variable name="width" select="@WIDTH"/>
                            <xsl:variable name="height" select="@HEIGHT"/>
                            <xsl:variable name="posinfo"
                                select="concat($pageno, ',', $xpos, ',', $ypos, ',', $width, ',', $height)"/>
                            <xsl:variable name="token" select="concat($content, '|', $posinfo)"/>
                            <xsl:value-of select="$token"/>
                            <xsl:value-of select="' '"/>
                        </xsl:for-each>
                    </xsl:for-each>
                </field>
            </doc>
        </add>
    </xsl:template>
</xsl:stylesheet>
