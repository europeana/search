<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
 
    
    <xsl:template match="/">
        <root>
            <searchComponent class="solr.SuggestComponent" name="suggestConcept">
                <lst name="suggester">
                    <str name="name">suggestConcept</str>
                    <str name="lookupImpl">FuzzyLookupFactory</str>
                    <str name="storeDir">suggester_fuzzy_dir</str>   
                    <str name="dictionaryImpl">DocumentDictionaryFactory</str>
                    <str name="field">skos_prefLabel</str>
                    <str name="suggestAnalyzerFieldType">suggestType</str>
                    <str name="buildOnStartup">true</str>
                    <str name="buildOnCommit">false</str>
                    <str name="weightField">derived_score</str>
                </lst>
            </searchComponent>
            <requestHandler class="org.apache.solr.handler.component.SearchHandler" name="/suggestConcept" startup="lazy">
                <lst name="defaults">
                    <str name="suggest">true</str>
                    <str name="suggest.count">10</str>
                    <str name="suggest.dictionary">suggestConcept</str>
                </lst>
                <arr name="components">
                    <str>suggestConcept</str>
                </arr>
            </requestHandler>
        <xsl:for-each select="//lang">
            <xsl:variable name="lang" select="text()"/>
            
            <searchComponent class="solr.SuggestComponent" name="suggestConcept_{$lang}">
                <lst name="suggester">
                    <str name="name">suggestConcept_<xsl:value-of select="$lang"/></str>
                    <str name="lookupImpl">FuzzyLookupFactory</str>
                    <str name="storeDir">suggester_fuzzy_dir</str>   
                    <str name="dictionaryImpl">DocumentDictionaryFactory</str>
                    <str name="field">skos_prefLabel.<xsl:value-of select="$lang"/></str>
                    <str name="suggestAnalyzerFieldType">suggestType</str>
                    <str name="buildOnStartup">true</str>
                    <str name="buildOnCommit">false</str>
                    <str name="weightField">derived_score</str>
                </lst>
            </searchComponent>
            <requestHandler class="org.apache.solr.handler.component.SearchHandler" name="/suggestConcept/{$lang}" startup="lazy">
                <lst name="defaults">
                    <str name="suggest">true</str>
                    <str name="suggest.count">10</str>
                    <str name="suggest.dictionary">suggestConcept_<xsl:value-of select="$lang"/></str>
                </lst>
                <arr name="components">
                    <str>suggestConcept_<xsl:value-of select="$lang"/></str>
                </arr>
            </requestHandler>
            
        </xsl:for-each>
        </root>
    </xsl:template>
    
    
</xsl:stylesheet>