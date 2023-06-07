from osgeo import gdal,ogr,osr
import json


dataSourceRead = ogr.Open('AFG_adm2.shp',0)
dataSourceWrite = ogr.Open('AFG_adm2.shp',1)

myShapeFile=ogr.Open('line.shp',0)
myShapeFileWrite=ogr.Open('line.shp',1)


def area_big_than_one():
    layer = dataSourceRead.GetLayer()
    i=1
    for feature in layer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea() 
        if(area>1):
            create_line_strings(geom,i)
            i+=1
            print (area,feature.GetFID(),feature['NAME_2'],feature.GetField('NAME_1'),json.loads(feature.ExportToJson())["geometry"]["coordinates"] )


def distance():
    layer = dataSourceWrite.GetLayer()
    new_field = ogr.FieldDefn("DISTANCE", ogr.OFTInteger)
    layer.CreateField(new_field)
    new_field_neighbors = ogr.FieldDefn("NEIGHBORS", ogr.OFTInteger)
    layer.CreateField(new_field_neighbors)

    myObj = list(filter(lambda x: x['NAME_2'] == 'Char Burjak', layer))
    for feature in layer:
        count= add_num_of_neighbors(feature.geometry())
        print(count)
        feature.SetField("NEIGHBORS",count)
        if (myObj[0].GetGeometryRef().Distance(feature.GetGeometryRef()) < 1):
            feature.SetField("DISTANCE", 1)
        else:
            feature.SetField("DISTANCE", 0)
        layer.SetFeature(feature)
        print('The Distance Updated',feature.GetField('NEIGHBORS'))


def add_num_of_neighbors(feature):
    layer = dataSourceRead.GetLayer()
    counter=0
    for neighbor in layer:
        n1=neighbor.geometry()
        if (feature.Touches(n1)):
            counter+=1
    return(counter)
        
   
def create_shapfile():
    driver=ogr.GetDriverByName("ESRI Shapefile")
    ds=driver.CreateDataSource("line.shp")
    srs =  osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer = ds.CreateLayer("line", srs, ogr.wkbLineString)
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(idField)
    ds = None
    
    
def create_line_strings(feat=None,i=None,ls=None,ls2=None):
    layer=myShapeFileWrite.GetLayer()
    linegeo = ogr.Geometry(ogr.wkbLineString)
    if(feat!=None and i!=None):
        myGeom = feat.GetGeometryRef(0)
        for j in range(myGeom.GetPointCount()):
            linegeo.AddPoint(myGeom.GetX(j),myGeom.GetY(j))
    else:
        linegeo.AddPoint(ls[0],ls[1])
        linegeo.AddPoint(ls2[0],ls2[1])
        print(linegeo)
       
        
    featureDefn = layer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(linegeo)
    feature.SetField("id", i)
    layer.CreateFeature(feature)
    feature = None
    

def add_line_string():
    layer=myShapeFile.GetLayer()
    layer2=dataSourceRead.GetLayer()
    maxArea=max(layer ,key=lambda feature:feature.GetGeometryRef().GetArea())
    maxNeighbor=max(layer2,key=lambda feat:feat["NEIGHBORS"])
    x1=maxArea.GetGeometryRef().Centroid().GetX()
    y1=maxArea.GetGeometryRef().Centroid().GetY()
    x2=maxNeighbor.GetGeometryRef().Centroid().GetX()
    y2=maxNeighbor.GetGeometryRef().Centroid().GetY()
    create_line_strings(None, len(layer),[x1,y1],[x2,y2])
    
      
print('hello')
