import arcpy

domainEdges = r'D:\UpdatestoDomainEdgeScript\TestingDataset\TestingDataset.shp'

originalDomainsFolder = r'D:\UpdatestoDomainEdgeScript\TestingDataset\Domains'

outputDomainsFolder = r'D:\UpdatestoDomainEdgeScript\TestingDataset\OutputDomains'

originalNodesFolder = r'D:\UpdatestoDomainEdgeScript\TestingDataset\Nodes'

outputNodesFolder = r'D:\UpdatestoDomainEdgeScript\TestingDataset\OutputNodes'

bufferDistance = 1700 #this buffer is applied to the whole original domain

pointBufferDistance = 800 #this buffer is applied to the domain edge points

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#define the identified nodes, domains and domainEdges
cursor = arcpy.SearchCursor(domainEdges)
for row in cursor:
    x = row.getValue('Domain')
    originalDomain = str(originalDomainsFolder) + '\\' + x[8:] + '_Domain.shp'
    domainName = x[8:] + '_Domain'
    originalNode = str(originalNodesFolder) + '\\Nodes_' + x[8:] + '.shp'
    nodeName = 'Nodes_' + x[8:]
    
    
    domainEdgesFL = arcpy.MakeFeatureLayer_management(domainEdges,'in_memory\domainEdgesFL' + x)
    selectedDomainEdges = arcpy.SelectLayerByAttribute_management(domainEdgesFL,'NEW_SELECTION','"Domain" = ' + "'" + str(x) + "'")
    
    
    #complete the geoprocessing steps for the selected nodes and domains and copies the node
    bufferedSelectedDomainEdges = arcpy.Buffer_analysis(selectedDomainEdges,'in_memory\\bufferedSelectedDomainEdges' + x,str(pointBufferDistance) + ' METERS')
    bufferedDomain = arcpy.Buffer_analysis(originalDomain,'in_memory\\bufferedDomain' + x,str(bufferDistance) + ' METERS')
    bufferedDomainPoints = arcpy.GeneratePointsAlongLines_management(bufferedDomain,'in_memory\\bufferedDomainPoints' + x,'DISTANCE','30 METERS')
    domainPoints = arcpy.GeneratePointsAlongLines_management(originalDomain,'in_memory\\domainPoints' + x,'DISTANCE','30 METERS')
    fl1 = arcpy.MakeFeatureLayer_management(domainPoints,'in_memory\\fl1' + x)
    domainPointsSelected = arcpy.SelectLayerByLocation_management(fl1,'WITHIN_A_DISTANCE',selectedDomainEdges,'200 METERS')
    fl2 = arcpy.MakeFeatureLayer_management(bufferedDomainPoints,'in_memory\\fl2' + x)
    bufferedDomainPointsSelected = arcpy.SelectLayerByLocation_management(fl2,'WITHIN_A_DISTANCE',domainPointsSelected,str(bufferDistance + 1) + ' METERS')
    extendAreaPoints = arcpy.Merge_management([domainPointsSelected,bufferedDomainPointsSelected],'in_memory\\extendpoints' + x)
    extendAreaPoly = arcpy.MinimumBoundingGeometry_management(extendAreaPoints,'in_memory\\extendAreaPoly' + x,'CONVEX_HULL')
    domainshape = arcpy.Union_analysis([originalDomain, extendAreaPoly, bufferedSelectedDomainEdges],'in_memory\\shape' + x,'','',"NO_GAPS")
    arcpy.env.workspace = outputDomainsFolder
    arcpy.Dissolve_management(domainshape,domainName)
    arcpy.env.workspace = outputNodesFolder
    arcpy.CopyFeatures_management(originalNode,nodeName)
    arcpy.Delete_management('in_memory')
    
print('All Processes Complete')
print('Please Check Outputs')