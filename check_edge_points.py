# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 11:39:02 2024

@author: ae133
"""

import geopandas as gpd
import numpy as np
from shapely.strtree import STRtree
from shapely.geometry import Polygon

def distance(point1, point2):
    d = ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)**0.5
    return d

def avg(points):
    avg_x = 0
    avg_y = 0
    avg_z = 0
    for point in points:
        avg_x += point[0]
        avg_y += point[1]
        avg_z += point[2]
    avg_x = avg_x / len(points)
    avg_y = avg_y / len(points)
    avg_z = avg_z / len(points)
    return [avg_x, avg_y, avg_z]

# 讀取 shapefiles 基礎測試用 會換
shapefile = r"P:\13018-113年及114年三維道路模型建置案\04_Python\One_Workflow_113\1130822_SEC3\CHK_接邊點\AREA.shp"
output_file_path = r"P:\13018-113年及114年三維道路模型建置案\04_Python\One_Workflow_113\1130822_SEC3\CHK_接邊點\AREA_123.shp"
THRESHOLD = 0.00001

polygon = gpd.read_file(shapefile)
tree = STRtree(polygon['geometry'])

output_dict = {}
count = 0



# 遍歷所有的面
for idx, row in polygon.iterrows():
    # 查詢與當前面相交的所有面
    intersect = tree.query(row['geometry'].buffer(0.1))
    # 過濾掉與自身相交的面
    intersect = [g for g in intersect if g != idx]

    for intersect_i in intersect:
        intersect_p_points = []
        # 收集相交面所有的節點
        polygon_geom = polygon['geometry'][intersect_i]
        for coords in polygon_geom.exterior.coords:
            intersect_p_points.append(coords)
        
    # 該面節點找過近距離的點
    new_polygon = []
    for point in polygon['geometry'][idx].exterior.coords:
        near_point = []
        for i in range(len(intersect_p_points)):
            if distance(point, intersect_p_points[i]) < THRESHOLD:
                near_point.append(intersect_p_points[i])                 
        if near_point:
            near_point.append(point)
            avg_point = avg(near_point)
            # print("avg =", avg_point)
            new_polygon.append(avg_point)
        else:
            new_polygon.append(point)
            
    
    new_row = row.copy()
    new_row['geometry'] = Polygon(shell = new_polygon,
                                  holes = new_row['geometry'].interiors)
    output_dict[count] = new_row
    count += 1
    

output_polygons = gpd.GeoDataFrame.from_dict(output_dict, orient = 'index')
output_polygons = output_polygons.reset_index(drop = True)
output_polygons.to_file(filename = output_file_path,
                        driver = 'ESRI Shapefile', 
                        encoding = 'utf-8',
                        engine = 'pyogrio')            
                

