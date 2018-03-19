import requests
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import os
import time
from random import randint
from bs4 import BeautifulSoup

headers= {
    'User-Agent': 'Mozilla/5.0'
}

def writeBasicData(vehicleid, make, model, year, numberplate, engine, mileage, transmission, currentregistration, price, yearfrom, yearto):
    with open('nettiauto_vehicles.csv', 'a') as f:
        csvRow=vehicleid+","+make+","+model+","+year+","+numberplate+","+engine+","+mileage+","+transmission+","+currentregistration+","+price+","+yearfrom+","+yearto+"\n"
        f.write(csvRow)        
    return;

def downloadImage(url, vehicleId):   
    if not os.path.exists(vehicleId):
        os.makedirs(vehicleId)
    path=vehicleId+'/'+vehicleId+'-'+url.split('/')[5]
    if not os.path.exists(path):
        r = requests.get(url, stream=True, headers=headers)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    return;

def processVehicle(vehicleId, make, model, price):
    vehiclePage=requests.get("http://www.nettiauto.fi/"+str(vehicleId))
    vehicleSoup=BeautifulSoup(vehiclePage.content, 'html.parser')

    yearfrom, yearto='',''
    #Parse model years (from - to) from the similar vehicle search
    similarity_tag=vehicleSoup.select('a.gray_btn_nl')
    if similarity_tag:
        similarity_url=similarity_tag[0].get('href')
#<a class="gray_btn_nl" href="https://www.nettiauto.com/fiat/brava?id_car=9433949&amp;id_vehicle_type=1&amp;yfrom=1999&amp;yto=2001&amp;engine_size=1.2&amp;id_fuel_type=1&amp;id_four_wheel=1&amp;id_gear_type=2&amp;id_car_type=3&amp;road_permit=N&amp;vsv=1&amp;PN[0]=car_info&amp;PL[0]=fiat/brava/9433949" title="Huomioi erot mallitarkennuksessa ja vuosimallissa">Samanlaisia</a>
        if len(similarity_url.split('yfrom='))>1:
            yearfrom=similarity_url.split('yfrom=')[1][:4]
        if len(similarity_url.split('yto='))>1: 
            yearto=similarity_url.split('yto=')[1][:4]

    currenregistration="valid"
    currentregistration_tag=vehicleSoup.find('span', text='Ei tieliikennekelpoinen')
    if currentregistration_tag:
        currenregistration="invalid"
    
    #make, model, year, numberplate, engine, mileage, transmission, currentregistration
    vehicle_data_table=vehicleSoup.select('table.data_table')
    if vehicle_data_table:
        year, engine, licenseplate, mileage, transmission='', '', '', '', ''
        
        tag_year=vehicle_data_table[0].find('td', text="Vuosimalli ")      
        if tag_year:
            year=tag_year.findNext('td').string
        
        tag_engine=vehicle_data_table[0].find('td', text="Moottori")
        if tag_engine:    
            engine=tag_engine.findNext('td').string      
        
        tag_licenseplate=vehicle_data_table[0].find('td', text="Rek.nro")
        if tag_licenseplate:
            licenseplate=tag_licenseplate.findNext('td').string
        
        tag_mileage=vehicle_data_table[0].find('td', text="Mittarilukema")
        if tag_mileage:        
            mileage=tag_mileage.findNext('td').string
        
        tag_transmission=vehicle_data_table[0].find('td', text="Vaihteisto")
        if tag_transmission:        
            transmission=tag_transmission.findNext('td').string
        
        writeBasicData(vehicleId, make, model, year, engine, licenseplate, mileage, transmission, currenregistration, price, yearfrom, yearto)

    for link in vehicleSoup.find_all('div'):
        if link.get('data-ipath') != None:
            img_link=link.get('data-ipath')        
            downloadImage(img_link, vehicleId)
         
            random_delay_between_dls=randint(1,18)
            print("Sleeping between image DLs for ",random_delay_between_dls, " secs")
            time.sleep(random_delay_between_dls)            
    return;

def iterateAllPages(numberOfPages):
    #https://www.nettiauto.com/vaihtoautot?page=1
    #for i in range(1, numberOfPages):
    numberOfPages=int(numberOfPages)+1
    for i in range(1, numberOfPages):
        #Fetch page
        currentPage=requests.get("http://www.nettiauto.com/vaihtoautot?page="+str(i))
        currentSoup = BeautifulSoup(currentPage.content, 'html.parser')
        print("------------------ Processing page ",i)		
        for link in currentSoup.find_all('a'):
            if link.get('data-make') != None:
#<a href="https://www.nettiauto.com/nissan/note/8760131" class="childVifUrl tricky_link"  data-make="Nissan" data-model="Note" data-id="8760131" data-vtype="Pakettiauto" data-postedby="Automyynti Pirinen" data-year="2011" data-mileage="99000" data-price="8899">Nissan Note</a>                
                print("Vehicle ",link.get('data-id'))
                #Check if the vehicle information already exists
                if vehicleExists(link.get('data-id')):
                    break;
                processVehicle(link.get('data-id'), link.get('data-make'),link.get('data-model'), link.get('data-price'))
                random_delay_between_vehicles=randint(4,90)
                print("Sleeping between vehicles for ",random_delay_between_vehicles, " secs")
                time.sleep(random_delay_between_vehicles)
        random_delay_between_pages=randint(5,30)
        print("Sleeping between pages for ",random_delay_between_pages, " secs")
        time.sleep(random_delay_between_pages)
    return;

def buildExistingVehicleArray():   
    with open('nettiauto_vehicles.csv') as f:
        for line in f:
            vehicleid = line.split(',')[0]
            existingVehicles[vehicleid]=line.split(',')[1]
    print("We have ", len(existingVehicles), " vehicles so far")
    return;

def vehicleExists(vehicleId):
    if vehicleId in existingVehicles:
        return True
    else:
        return False



while True:
    try:
        page=requests.get("http://www.nettiauto.com/vaihtoautot", headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        total_results=soup.find(id="tot_result")
        total_value_string=total_results.select('input')[0].get('value')
        total_value=total_value_string.split('(')[1].split(')')[0]

        total_pages=soup.find(id="stickyListHeader")
        total_pages_string=total_pages.select('span.totPage')
        total_pages_value=total_pages_string[0].string

        existingVehicles={}
        buildExistingVehicleArray()
        iterateAllPages(total_pages_value)
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        time.sleep(randint(100,200))
        print("Tilt!", time.ctime(), page)
        continue


