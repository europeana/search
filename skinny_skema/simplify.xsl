<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:variable name="retained-unchanged" as="xs:string*" select="('_version_','facet_tags', 'filter_tags', 'has_landingpage', 'has_media', 'has_thumbnails', 'is_fulltext', 'text', 'timestamp', 'europeana_id', 'europeana_collectionName', 'edm_datasetName', 'title', 'who', 'what', 'where', 'when', 'europeana_completeness', 'CREATOR', 'CONTRIBUTOR', 'UGC', 'LANGUAGE', 'TYPE', 'YEAR', 'PROVIDER', 'DATA_PROVIDER', 'COUNTRY', 'USERTAGS', 'RIGHTS', 'COMPLETENESS', 'edm_previewNoDistribute', 'subject')"/>
    <xsl:variable name="retain-changed" as="xs:string*" select="('provider_aggregation_dc_rights','provider_aggregation_edm_dataProvider','provider_aggregation_edm_hasView','provider_aggregation_edm_intermediateProvider','provider_aggregation_edm_isShownAt','provider_aggregation_edm_isShownBy','provider_aggregation_edm_object','provider_aggregation_edm_provider','provider_aggregation_edm_rights','Europeana agregation','europeana_aggregation_edm_country','europeana_aggregation_edm_language','europeana_aggregation_dc_creator','edm_webResource','wr_edm_rights','wr_dc_rights','wr_edm_isNextInSequence','wr_svcs_hasService','proxy_dc_contributor','proxy_dc_coverage','proxy_dc_creator','proxy_dc_date','proxy_dc_description','proxy_dc_format','proxy_dc_identifier','proxy_dc_language','proxy_dc_publisher','proxy_dc_rights','proxy_dc_source','proxy_dc_subject','proxy_dc_title','proxy_dc_type','proxy_dcterms_alternative','proxy_dcterms_created','proxy_dcterms_hasPart','proxy_dcterms_isPartOf','proxy_dcterms_issued','proxy_dcterms_medium','proxy_dcterms_provenance','proxy_dcterms_spatial','proxy_dcterms_temporal','proxy_edm_currentLocation','proxy_edm_hasMet','proxy_edm_isRelatedTo','proxy_edm_type','proxy_edm_year','edm_UGC','edm_agent','ag_skos_altLabel','ag_skos_prefLabel','ag_foaf_name','ag_rdagr2_dateOfBirth','ag_rdagr2_dateOfDeath','ag_rdagr2_professionOrOccupation','ag_rdagr2_placeOfBirth','ag_rdagr2_placeOfDeath','edm_timespan','ts_skos_altLabel','ts_skos_prefLabel','edm_place','pl_skos_altLabel','pl_skos_prefLabel','pl_wgs84_pos_alt','pl_wgs84_pos_lat','pl_wgs84_pos_long','skos_concept','cc_skos_altLabel','cc_skos_prefLabel','CC License','wr_cc_license','wr_cc_odrl_inherited_from','wr_cc_deprecated_on','provider_aggregation_odrl_inherited_from','provider_aggregation_cc_license','provider_agregation_cc_deprecated_on','foaf_organization','org_skos_altLabel','org_skos_prefLabel','svcs_service','sv_dcterms_conformsTo','proxy_dc_type_search')"/>
    <xsl:variable name="multilingual" as="xs:string*" select="('provider_aggregation_dc_rights', 'provider_aggregation_edm_dataProvider', 'provider_aggregation_edm_intermediateProvider', 'provider_aggregation_edm_provider', 'wr_dc_rights', 'proxy_dc_contributor', 'proxy_dc_coverage', 'proxy_dc_creator', 'proxy_dc_date', 'proxy_dc_description', 'proxy_dc_format', 'proxy_dc_identifier', 'proxy_dc_language', 'proxy_dc_publisher', 'proxy_dc_rights', 'proxy_dc_source', 'proxy_dc_subject', 'proxy_dc_title', 'proxy_dc_type', 'proxy_dcterms_alternative', 'proxy_dcterms_created', 'proxy_dcterms_hasPart', 'proxy_dcterms_isPartOf', 'proxy_dcterms_issued', 'proxy_dcterms_medium', 'proxy_dcterms_provenance', 'proxy_dcterms_spatial', 'proxy_dcterms_temporal', 'proxy_edm_currentLocation', 'proxy_edm_year', 'ag_skos_altLabel', 'ag_skos_prefLabel', 'ag_foaf_name', 'ag_rdagr2_dateOfBirth', 'ag_rdagr2_dateOfDeath', 'ag_rdagr2_professionOrOccupation', 'ag_rdagr2_placeOfBirth', 'ag_rdagr2_placeOfDeath', 'ts_skos_altLabel', 'ts_skos_prefLabel', 'pl_skos_altLabel', 'pl_skos_prefLabel', 'cc_skos_altLabel', 'cc_skos_prefLabel', 'org_skos_altLabel', 'org_skos_prefLabel', 'proxy_dc_type_search')"/>
    <xsl:variable name="as-proper-name" as="xs:string*" select="( 'proxy_dc_contributor',  'proxy_dc_creator',  'proxy_dc_publisher',  'ag_skos_altLabel',  'ag_skos_prefLabel',  'ag_rdagr2_placeOfBirth',  'ag_rdagr2_placeOfDeath',  'pl_skos_altLabel', 'pl_skos_prefLabel')"/>
    <xsl:variable name="as-text" as="xs:string*" select="('proxy_dc_description',  'proxy_dc_format',  'proxy_dc_subject',  'proxy_dc_title',  'proxy_dc_type',  'proxy_dcterms_medium',  'ag_rdagr2_professionOrOccupation', 'proxy_dc_type_search')"/>
    <xsl:variable name="to-text" as="xs:string*" select="('provider_aggregation_edm_dataProvider',  'provider_aggregation_edm_intermediateProvider',  'provider_aggregation_edm_provider',  'proxy_dc_contributor',  'proxy_dc_coverage',  'proxy_dc_creator',  'proxy_dc_date',  'proxy_dc_description',  'proxy_dc_format',  'proxy_dc_language',  'proxy_dc_publisher',  'proxy_dc_source',  'proxy_dc_subject',  'proxy_dc_title',  'proxy_dc_type',  'proxy_dcterms_alternative',  'proxy_dcterms_created',  'proxy_dcterms_issued',  'proxy_dcterms_medium',  'proxy_dcterms_provenance',  'proxy_dcterms_spatial',  'proxy_dcterms_temporal',  'proxy_edm_currentLocation',  'proxy_edm_isRelatedTo',  'proxy_edm_type',  'ag_skos_altLabel',  'ag_skos_prefLabel',  'ag_foaf_name',  'ts_skos_altLabel',  'ts_skos_prefLabel',  'pl_skos_altLabel',  'pl_skos_prefLabel',  'cc_skos_altLabel',  'cc_skos_prefLabel', 'proxy_dc_type_search')"/>
    <xsl:template match="/">'
        <xsl:apply-templates select="schema"/>
    </xsl:template>
    
    <xsl:template match="schema">
        <xsl:copy>
            <xsl:attribute name="name">europeana-simplified</xsl:attribute>
            <xsl:attribute name="version">0.1</xsl:attribute>
            <xsl:apply-templates/>
            <xsl:for-each select="$multilingual">
                <xsl:variable name="bucket-field" select="concat(., '.*')"/>
                <xsl:element name="copyField">
                    <xsl:attribute name="source" select="$bucket-field"/>
                    <xsl:attribute name="dest" select="."/> 
                </xsl:element>
                <xsl:if test=". = $to-text">
                    <xsl:element name="copyField">
                        <xsl:attribute name="source" select="$bucket-field"/>
                        <xsl:attribute name="dest" select="'text'"/>
                    </xsl:element>
                </xsl:if>
            </xsl:for-each>
            <xsl:for-each select="$to-text">
                <xsl:element name="copyField">
                    <xsl:attribute name="source" select="."/>
                    <xsl:attribute name="dest" select="'text'"/>
                </xsl:element>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="types">
        <xsl:copy-of select="."/>
    </xsl:template>
    
    <xsl:template match="fields">
        <xsl:copy>
            <xsl:for-each select="field">
                <xsl:choose>
                <xsl:when test="@name = $retained-unchanged">
                    <xsl:copy-of select="."/>
                    <xsl:call-template name="build-dynamic-field-definition">
                        <xsl:with-param name="field-name" select="@name"/>
                        <xsl:with-param name="field-type" select="@type"/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:when test="@name = $retain-changed">
                    <xsl:variable name="datatype">
                        <xsl:choose>
                            <xsl:when test="@name = $as-text"><xsl:value-of select="'text'"/></xsl:when>
                            <xsl:when test="@name = $as-proper-name"><xsl:value-of select="'proper_name'"/></xsl:when>
                            <xsl:otherwise><xsl:value-of select="'string'"/></xsl:otherwise>
                        </xsl:choose>
                    </xsl:variable>
                    <xsl:element name="field">
                        <xsl:attribute name="name" select="@name"/>
                        <xsl:attribute name="type" select="$datatype"/>
                        <xsl:attribute name="indexed" select="'true'"/>
                        <xsl:attribute name="stored" select="'true'"/>
                        <xsl:attribute name="multiValued" select="'true'"/>
                    </xsl:element>
                    <xsl:call-template name="build-dynamic-field-definition">
                        <xsl:with-param name="field-name" select="@name"/>
                        <xsl:with-param name="field-type" select="$datatype"/>
                    </xsl:call-template>
                </xsl:when>
                    <xsl:otherwise/>
                </xsl:choose>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template name="build-dynamic-field-definition">
        <xsl:param name="field-name" as="xs:string"/>
        <xsl:param name="field-type" as="xs:string"/>
        <xsl:if test="$field-name = $multilingual">
            <xsl:variable name="dynamic-field-name" select="concat($field-name, '.*')"/>
            <xsl:element name="dynamicField">
                <xsl:attribute name="name" select="$dynamic-field-name"/>
                <xsl:attribute name="type" select="$field-type"/>
                <xsl:attribute name="indexed" select="'true'"/>
                <xsl:attribute name="stored" select="'true'"/>
                <xsl:attribute name="multiValued" select="'true'"/>
            </xsl:element>   
        </xsl:if>
    </xsl:template>
    
    <xsl:template match="uniqueKey">
        <xsl:copy-of select="."/>
    </xsl:template>
    
    <xsl:template match="defaultSearchField">
        <xsl:copy-of select="."/>
    </xsl:template>
    
    <xsl:template match="copyField">
        <xsl:variable name="raw-source" select="substring-before(@source, '.*')"/>
        <xsl:if test="(@dest = $retain-changed or @dest = $retained-unchanged) and @dest ne 'text' and (@source = $retained-unchanged or @source = $retain-changed or $raw-source = $retain-changed or $raw-source = $retained-unchanged) and @dest ne $raw-source">
            <xsl:copy-of select="."/>   
        </xsl:if>
    </xsl:template>
    
</xsl:stylesheet>