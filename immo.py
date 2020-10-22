from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
import pandas as pd
import random
import time
from IPython.display import clear_output
import math
from tqdm import tqdm
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from ipywidgets import *
from ipyleaflet import *
from tqdm import tqdm
import asyncio
import sqlite3


def plot_real(number, r):
    x = 30
    y = 30
    img = Image.new('RGBA', (60,60), (250,250,250,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('Immo/Arial.ttf',18)
    leftUpPoint = (x-r, y-r)
    rightDownPoint = (x+r, y+r)
    twoPointList = [leftUpPoint, rightDownPoint]
    draw.ellipse(twoPointList, fill=(0,255,0,255), outline =(0,200,0,255))
    draw.text((18, 18),number,(0,0,0), font = font)
    return img

def Immo_map(df_filter):
    m = Map(
    basemap=basemaps.OpenStreetMap.Mapnik,
    center = (52.57005, 13.39995),
    zoom=12
    )
    locations = []
    for index in tqdm(df_filter.index):
        if df_filter['lon'][index] != 0 or df_filter['lat'][index] != 0:
            popup = HTML()
            price_by_m = str('%.2f' % float(df_filter['Price'][index]/df_filter['Area'][index]))
            year = str(df_filter['Construction_Year'][index])
            popup.value = '<a href="'+df_filter['url'][index] +'"target="_blank">Price/m2: '+ price_by_m + ' Area:'+str(df_filter['Area'][index])+ ' Year:'+year+' </a>'
            lat = df_filter['lat'][index]
            lon = df_filter['lon'][index]
            #if df_filter['Precision'][index] == 0:
            icon = Icon(icon_url='https://raw.githubusercontent.com/MuriloAndre2000/imgs/main/'+df_filter['url'][index].split('/')[-1]+'.png', icon_size=[30, 30])
            #else:
                #icon = Icon(icon_url='fileb.png', icon_size=[60, 60])
            while (lat,lon) in locations:
                lat += 0.0001*random.randint(-10, 10)
                lon += 0.0001*random.randint(-10, 10)
            point = (lat, lon)
            m.add_layer(Marker(location=point,icon = icon,name = year,popup = popup, draggable=False))
            locations.append(point)
    print(len(locations), " Real_States")
    #control = LayersControl(position='topright')
    #m.add_control(control)
    return m

def wait_for_change(widget, value):
    future = asyncio.Future()
    def getvalue(change):
        # make the new value available
        future.set_result(change.new)
        widget.unobserve(getvalue, value)
    widget.observe(getvalue, value)
    return future

async def f(slide,list_of_slides):
    while 1:
        x = await wait_for_change(slide, 'value')
        clear_output()
        for slid in list_of_slides:
            display(slid)
        conn = sqlite3.connect('Immo.db')
        df_filter = pd.read_sql_query(
        '''select * from Real_State
        where Area >= '''+str(list_of_slides[0].value)+'''
        and Area <=   '''+str(list_of_slides[1].value)+'''
        and Pricem2 >= '''+str(list_of_slides[2].value)+'''
        and Pricem2 <='''+str(list_of_slides[3].value)+'''
        and Construction_Year >= '''+str(list_of_slides[4].value)+'''
        and Construction_Year <='''+str(list_of_slides[5].value)+'''
        ''', conn)
        conn.close()
        display(Immo_map(df_filter))


def plot():
    area_min = IntSlider(description='Area_Min:', min=0, max=50, value=0)
    area_max = IntSlider(description='Area_Max:', min=0, max=401, value=400)
    price_min = IntSlider(description='Price_Min:', min=0, max=20, value=0)
    price_max = IntSlider(description='Price_Max:', min=0, max=20, value=20)
    year_min = IntSlider(description='Year_Min:', min=1870, max=2020, value=1950)
    year_max = IntSlider(description='Year_Max:', min=1900, max=2020, value=2020)
    display(area_min,area_max,price_min,price_max,year_min,year_max)
    list_of_slides = [area_min,area_max,price_min,price_max,year_min,year_max]
    out = Output()
    asyncio.ensure_future(f(area_min, list_of_slides))
    asyncio.ensure_future(f(area_max, list_of_slides))
    asyncio.ensure_future(f(price_min, list_of_slides))
    asyncio.ensure_future(f(price_max, list_of_slides))
    asyncio.ensure_future(f(year_min, list_of_slides))
    asyncio.ensure_future(f(year_max, list_of_slides))
    display(out)