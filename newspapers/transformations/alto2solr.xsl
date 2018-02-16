<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
    xmlns:alto="http://www.loc.gov/standards/alto/ns-v2#" exclude-result-prefixes="xs xd alto"
    version="2.0">
    <xd:doc scope="stylesheet">
        <xd:desc>
            <xd:p><xd:b>Created on:</xd:b> Feb 12, 2018</xd:p>
            <xd:p><xd:b>Author:</xd:b>Timothy Hill</xd:p>
            <xd:p/>
        </xd:desc>
    </xd:doc>
    <xsl:param name="doc-language" as="xs:string"/>

    <xsl:template match="/">
        <xsl:variable name="whole-doc">
            <xsl:copy-of select="."/>
        </xsl:variable>
        <add>
            <doc>
                <xsl:variable name="languages" as="xs:string*" select="distinct-values(//@language)"/>
                <field name="doc_type">Newspaper</field>
                <!-- TODO: Get URI for this -->
                <field name="language">
                    <xsl:value-of select="$doc-language"/>
                </field>
                <xsl:variable name="all-langs" as="xs:string*"
                    select="distinct-values((//node()/@language, $doc-language))"/>
                <xsl:for-each select="$all-langs">
                    <xsl:variable name="now-lang">
                        <xsl:value-of select="."/>
                    </xsl:variable>
                    <xsl:variable name="raw-text-tokens" as="xs:string*">
                        <xsl:for-each select="$whole-doc//alto:String">
                            <xsl:variable name="content">
                                <xsl:choose>
                                    <xsl:when test="./@SUBS_TYPE eq 'HypPart1'">
                                        <xsl:value-of select="concat(./@CONTENT, '☞')"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="./@CONTENT"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="langcheck"
                                select="ancestor-or-self::node()/@language"/>
                            <xsl:variable name="string-lang" as="xs:string">
                                <xsl:choose>
                                    <xsl:when test="string-length($langcheck) != 2">
                                        <xsl:value-of select="$doc-language"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="$langcheck"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="filtered-output">
                                <xsl:choose>
                                    <xsl:when test="$string-lang eq $now-lang">
                                        <xsl:value-of select="$content"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="'☃'"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:value-of select="$filtered-output"/>
                        </xsl:for-each>
                    </xsl:variable>
                    <xsl:variable name="annotated-text-tokens" as="xs:string*">
                        <xsl:for-each select="$whole-doc//alto:String">
                            <xsl:variable name="content" select="replace(@CONTENT, '\n', '')"/>
                            <xsl:variable name="xpos" select="@HPOS"/>
                            <xsl:variable name="ypos" select="@VPOS"/>
                            <xsl:variable name="width" select="@WIDTH"/>
                            <xsl:variable name="height" select="@HEIGHT"/>
                            <xsl:variable name="posinfo"
                                select="concat($xpos, ',', $ypos, ',', $width, ',', $height)"/>
                            <xsl:variable name="langcheck"
                                select="ancestor-or-self::node()/@language"/>
                            <xsl:variable name="string-lang" as="xs:string">
                                <xsl:choose>
                                    <xsl:when test="string-length($langcheck) != 2">
                                        <xsl:value-of select="$doc-language"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="$langcheck"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="filtered-output">
                                <xsl:choose>
                                    <xsl:when test="$string-lang eq $now-lang">
                                        <xsl:value-of select="concat($content, '|', $posinfo)"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="'☃'"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:value-of select="$filtered-output"/>
                        </xsl:for-each>
                    </xsl:variable>
                    <xsl:variable name="raw-text-as-string">
                        <xsl:value-of select="$raw-text-tokens"/>
                    </xsl:variable>
                    <xsl:variable name="raw-filtered-text">
                        <xsl:value-of
                            select="normalize-space(replace(replace($raw-text-as-string, '( ☃ )', '☃'), '(☃)+', '☃'))"
                        />
                    </xsl:variable>
                    <xsl:variable name="unhyphenated-filtered-text">
                        <xsl:value-of select="replace($raw-filtered-text, '☞\s*', '')"/>
                    </xsl:variable>
                    <xsl:for-each select="tokenize($unhyphenated-filtered-text, '☃')">
                        <xsl:if test="string-length(.) > 0">
                            <xsl:variable name="fieldname" select="concat('fulltext.', $now-lang)"/>
                            <field name="{$fieldname}">
                                <xsl:value-of select="."/>
                            </field>
                        </xsl:if>
                    </xsl:for-each>
                    <xsl:variable name="annotated-text-as-string">
                        <xsl:value-of select="$annotated-text-tokens"/>
                    </xsl:variable>
                    <xsl:variable name="annotated-filtered-text">
                        <xsl:value-of
                            select="normalize-space(replace(replace($annotated-text-as-string, '( ☃ )', '☃'), '(☃)+', '☃'))"
                        />
                    </xsl:variable>
                    <xsl:for-each select="tokenize($annotated-filtered-text, '☃')">
                        <xsl:if test="string-length(.) > 0">
                            <xsl:variable name="annotated-fieldname"
                                select="concat('fulltext.annotated.', $now-lang)"/>
                            <field name="{$annotated-fieldname}">
                                <xsl:value-of select="."/>
                            </field>
                        </xsl:if>
                    </xsl:for-each>
                </xsl:for-each>
            </doc>
        </add>
    </xsl:template>


</xsl:stylesheet>
