<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#" exclude-result-prefixes="xs" version="2.0">

    <!-- ************************************************************************
         Takes files returned as XML from Solr and adds Fashion-specific path
         prefixing where appropriate, retransforming into XML ready for 
         reingest.
         
         @author: thill
         
         ************************************************************************ -->

    <xsl:variable name="copyfields" select="('text','spell','date','source','identifier','location','subject','TYPE','LANGUAGE','COUNTRY','YEAR','DATA_PROVIDER','CONTRIBUTOR','PROVIDER','RIGHTS','COMPLETENESS','UGC', 'what', 'whatSpell', 'when','whenSpell','titleSpell','where','whereSpell','who','whoSpell')"/>
    <!-- utility variables -->
    <xsl:variable name="field-separator">¦</xsl:variable>
    <xsl:variable name="cv-ns">http://thesaurus.europeanafashion.eu/thesaurus/</xsl:variable>
    <xsl:variable name="colors"
        select="distinct-values(doc('fash_thesaurus.rdf.xml')/rdf:RDF/rdf:Description/skos:inScheme[@rdf:resource eq 'http://thesaurus.europeanafashion.eu/thesaurus/Colours']/parent::rdf:Description/@rdf:about)"
        as="xs:string*"/>
    <xsl:variable name="materials"
        select="distinct-values(doc('fash_thesaurus.rdf.xml')/rdf:RDF/rdf:Description/skos:inScheme[@rdf:resource eq 'http://thesaurus.europeanafashion.eu/thesaurus/Materials']/parent::rdf:Description/@rdf:about)"
        as="xs:string*"/>
    <xsl:variable name="techniques"
        select="distinct-values(doc('fash_thesaurus.rdf.xml')/rdf:RDF/rdf:Description/skos:inScheme[@rdf:resource eq 'http://thesaurus.europeanafashion.eu/thesaurus/Techniques']/parent::rdf:Description/@rdf:about)"
        as="xs:string*"/>
    <xsl:template match="/">
        <add>
            <xsl:for-each select="//doc">
                <doc>
                    <xsl:variable name="is-fash-doc"
                        select="exists(arr[@name eq 'provider_aggregation_edm_provider']/str[text() eq 'Europeana Fashion'])"
                        as="xs:boolean"/>
                    <xsl:for-each select="element()">
                        <xsl:variable name="name" select="@name"/>
                        <xsl:choose>
                            <xsl:when test="$name eq '_version_'"/>
                            <!-- designers mapped to CREATOR -->
                            <xsl:when test="$name eq 'CREATOR'">
                                <xsl:for-each select="str">
                                    <xsl:variable name="prefixed-creator">
                                        <xsl:choose>
                                            <xsl:when test="$is-fash-doc eq true()">
                                                <xsl:value-of select="concat('¦fashion¦designer¦', text())"
                                                />
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:value-of select="text()"/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:variable>
                                    <field name="CREATOR">
                                        <xsl:value-of select="$prefixed-creator"/>
                                    </field>
                                </xsl:for-each>
                            </xsl:when>
                            <!-- object types mapped to SUBJECT-->
                            <xsl:when test="$name eq 'skos_concept'">
                                <xsl:for-each select="str">
                                    <xsl:if test="matches(text(), concat($cv-ns, '[\d]+')) and $is-fash-doc eq true()">
                                        <xsl:variable name="prefixed-concept">
                                            <xsl:value-of
                                                select="concat('¦fashion¦object_type¦', text())"/>
                                        </xsl:variable>
                                        <field name="SUBJECT">
                                            <xsl:value-of select="$prefixed-concept"/>
                                        </field>
                                    </xsl:if>
                                    <field name="{$name}">
                                        <xsl:value-of select="text()"/>
                                    </field>
                                </xsl:for-each>
                            </xsl:when>
                            <!-- Various Fashion profile fields are mapped to format. Note that they 
                                 can't be disambiguated by data present in the Solr documents, as this
                                 is unreliable - so we need to refer back to the Fashion CVs to determine
                                 the original fields -->
                            <xsl:when test="$name eq 'proxy_dc_format.def' and $is-fash-doc eq true()">
                                <!-- first we output the CV urls -->
                                <xsl:for-each select="str">
                                    <xsl:variable name="format-prefix">
                                        <xsl:choose>
                                            <xsl:when test="text() = $colors">
                                                <xsl:value-of select="'¦fashion¦color¦'"/>
                                            </xsl:when>
                                            <xsl:when test="text() = $materials">
                                                <xsl:value-of select="'¦fashion¦material¦'"/>
                                            </xsl:when>
                                            <xsl:when test="text() = $techniques">
                                                <xsl:value-of select="'¦fashion¦technique¦'"/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:value-of select="''"/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:variable>
                                    <field name="TYPE">
                                        <xsl:value-of select="concat($format-prefix, text())"/>
                                    </field>
                                    <field name="proxy_dc_format.def">
                                        <xsl:value-of select="text()"/>
                                    </field>
                                    <!-- now let's correct the original fields -->
                                    <xsl:variable name="label-prefix">
                                        <xsl:choose>
                                            <xsl:when test="text() = $colors">
                                                <xsl:value-of select="'Color: '"/>
                                            </xsl:when>
                                            <xsl:when test="text() = $materials">
                                                <xsl:value-of select="'Material: '"/>
                                            </xsl:when>
                                            <xsl:when test="text() = $techniques">
                                                <xsl:value-of select="'Technique: '"/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:value-of select="''"/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:variable>
                                    <xsl:variable name="url" select="text()"/>
                                    <xsl:variable name="en-translation">
                                        <xsl:value-of
                                            select="doc('fash_thesaurus.rdf.xml')/rdf:RDF/rdf:Description[@rdf:about eq $url]/skos:prefLabel[@xml:lang eq 'en']/text()"
                                        />
                                    </xsl:variable>
                                    <field name="proxy_dc_format.en">
                                        <xsl:value-of
                                            select="concat($label-prefix, $en-translation)"/>
                                    </field>
                                </xsl:for-each>
                            </xsl:when>
                            <xsl:when
                                test="$name eq 'proxy_dc_format.en' and $is-fash-doc eq true()">
                                <!-- dealt with in the previous 'when' clause -->
                            </xsl:when>
                            <xsl:when test="substring-before($name, '.') = $copyfields or $name = $copyfields">
                                <!-- need to eliminate copyfields from output -->
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:choose>
                                    <xsl:when test="count(child::element()) eq 0">
                                        <field name="{$name}">
                                            <xsl:value-of select="text()"/>
                                        </field>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:for-each select="child::element()">
                                            <field name="{$name}">
                                                <xsl:value-of select="text()"/>
                                            </field>
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
