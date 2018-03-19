# Nettiauto Scraper
Nettiauto web scraper based on the Beautiful Soup 4. Python script to scrape used vehicles/vaihtoautot listing with images. Saves the vehicle information in the CSV file and images of the vehicles into the respective folders named after the classified used vehicle ID given by the Nettiauto. Has random lenght pauses between the scraping and downloads to not overburden the nice service of Nettiauto.
CSV file contains vehicleId, make, model, year, engine, licenseplate, mileage, transmission, currenregistration, price, yearfrom, yearto. Yearfrom and yearto denote the years the current model has been available. The currentregistration indicates the registration status as understood by the Finnish road legislation.

