# seleniumBsFolium - Extended

Follow along original YouTube series along with this code:
https://www.youtube.com/playlist?list=PL2UmzTIzxgL4GUqBPhGcpMe5BTOp0Ovqv

Follow along original Medium article along with this code:
https://medium.com/python-point/combining-web-scraping-api-requests-visualizations-6b7a4cfacdd2

This code has been modified to obtain a list of NHS trusts and for each trust the list of hospitals and clinics
to be able to show points on a map of all NHS hospital locations, using publicly available information
from www.nhs.com

Expects the following environment variables to be set:
MAPQUEST_API_KEY ::= 32 character key from mapquest.com (free for up to 15,000 requests per month)
Example values (note this is a made up key, so I don't expect it to work)
export MAPQUEST_API_KEY = "0dDhGdsZSE45tgbNJI(olp)9iw09e7D8"
export HOSPITALS_CSV = "NHSHospitals.csv"

crawl.py will generate the HOSPITALS_CSV will contain the hospital id, name, url, address, trustID, trust name, trust url
(Note this can take some time to crawl the NHS.com trusts and related hospitals)
getGeo.py will take the hospital data, extract the postcode and identify duplicates
where duplicates exist, the exiting lat/long will be used.
If lat/long data exists in the file, then this will also be tested to avoid excessive calls to mapquest.com.
