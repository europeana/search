<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <!-- *** just some sanity checks for schema.xml -->
    <!-- check 'where' and 'location' fields for contents -->
    <!-- what's going on with proxy_dcterms_alternative -->
    
    <!-- datatypes are correct? Eyeball it -->
    
    <xsl:template match="/">
        <report>
            <datatypes>
                <xsl:for-each select="/schema/types/fieldType">
                    <xsl:variable name="type-name" select="@name"/>
                    <xsl:element name="datatype">
                        <xsl:attribute name="name" select="$type-name"/>
                    <xsl:for-each select="parent::types/parent::schema/fields/field[@type eq $type-name]/@name">

                            <xsl:element name="field"><xsl:value-of select="."/></xsl:element>
                        
                    </xsl:for-each>
                        
                         
                    </xsl:element>     
                </xsl:for-each>
            </datatypes>
            
            
            
        </report>
    </xsl:template>
    
    <!-- TODO on schema.xml:
            - values for ts_skos_prefLabel(.*) - analysis type?
            - values for ts_skos_altLabel(.*) - analysis type?
            - provider_aggregation_edm_dataProvider - are we faceting on this? (string or proper_name?)
            - provider_aggregation_edm_provider - are we faceting on this? (string or proper_name?)
    -->
    
    
</xsl:stylesheet>