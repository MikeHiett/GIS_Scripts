import arcpy

#DEFINE THE INPUTS 

flowObs = r'C:\Users\Michael-H\Desktop\FlowObsScriptTESTING\AUSTRALIA\FlowObs\FlowObs.shp' 
DTM = r'C:\Users\Michael-H\Desktop\FlowObsScriptTESTING\AUSTRALIA\DTM\TAS_LiDAR_SRTM_AGG_FUSED_MGA53_30m_v1.tif' 
patchOutputFolder = r'C:\Users\Michael-H\Desktop\FlowObsScriptTESTING\AUSTRALIA\OutputPatches' 
scratchFolder = r'C:\Users\Michael-H\Desktop\FlowObsScriptTESTING\AUSTRALIA\Scratch' 

#define script variables
bufferedFlowObs = 'in_memory\\bufferedFlowObs'
lines = 'in_memory\\lines'
splitlines = 'in_memory\\splitlines'
FLsplitlines = 'in_memory\\FLsplitlines'
endLines = 'in_memory\\endLines'
endPoints = 'in_memory\\endPoints'
endPointsLyr = patchOutputFolder

#define the environment variables
description = arcpy.Describe(DTM)
cellsize = description.children[0].meanCellHeight
buffDist = cellsize*2
pointDistance = str(cellsize) + ' Meters'
arcpy.env.snapRaster = DTM
arcpy.env.outputCoordinateSystem = arcpy.Describe (DTM).spatialReference

#complete all the geoprocessing steps up to iterator
arcpy.Buffer_analysis(flowObs,bufferedFlowObs,buffDist,'FULL','FLAT','','','')
arcpy.PolygonToLine_management(bufferedFlowObs,lines,'')
arcpy.SplitLine_management(lines,splitlines)
arcpy.MakeFeatureLayer_management(splitlines,FLsplitlines,'','','')
arcpy.SelectLayerByLocation_management(FLsplitlines,'INTERSECT',flowObs,'','NEW_SELECTION','INVERT')
arcpy.DeleteRows_management(FLsplitlines)
arcpy.CopyFeatures_management(FLsplitlines,endLines,'','','','')
arcpy.GeneratePointsAlongLines_management(endLines,endPoints,'DISTANCE',pointDistance,'','END_POINTS')
arcpy.gp.ExtractMultiValuesToPoints_sa(endPoints, str(DTM) + ' Heights', 'None')
arcpy.MakeFeatureLayer_management(endPoints,endPointsLyr)

IDs = []
with arcpy.da.SearchCursor(endPointsLyr, ('RIGHT_FID',)) as cursor:
    for row in cursor:
        if row not in IDs:
            IDs.append(row)
IDlist = []
for values in IDs:
    for x in values:
        IDlist.append(x)
     
for patchID in IDlist:
    selection = arcpy.SelectLayerByAttribute_management(endPointsLyr,"ADD_TO_SELECTION",'RIGHT_FID = ' + str(patchID))
    outTIN = scratchFolder + '\TIN_' + str(patchID) 
    depthfield = ' Heights'
    mp = ' Mass_Points'
    none = ' <None>'
    inFeatures = str(selection) + depthfield + mp + none
    arcpy.CreateTin_3d(outTIN,'',inFeatures,"DELAUNAY")
    arcpy.TinRaster_3d(outTIN,patchOutputFolder + '\Patch_' + str(patchID) + '.tif',"FLOAT",'',"CELLSIZE " + str(cellsize),)
    arcpy.SelectLayerByAttribute_management(endPointsLyr,"CLEAR_SELECTION")
    
print('All processes complete')