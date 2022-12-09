import pandas as pd
import requests
import json
import os
from time import sleep

# loop around the file 100 lines at a time, incrementing by 100*x
# x = 0 - rows 0 to 99 (0 * x + row)
# x = 1 - rows 100 to 199 (1 * x + row)

# addrs_df = pd.read_csv("NHSHospitals.csv", encoding="utf-8",
#       skiprows=lambda x:x in range(1,100], nrows=100, names=('id','Hospital','URL','Address'))
# pd.set_option('display.max_rows', None)


def get_file_data(filename):
    dataframe = pd.read_csv(filename, encoding="utf-8")
    pd.set_option('display.max_rows', None)
    return dataframe


def postcode_to_geo(addrs_df, mq_key):
    postcode_dict = {}
    call_count = 0
    for i, row in addrs_df.iterrows():
        print("i = ", i)
        assert 'Address' in row.keys(), \
            f"Expected data heading 'Address' missing, got: {row.keys()}"
        assert 'Latitude' and 'Longitude' in row.keys(), \
            f"Extra data headings 'Latitude' and 'Longitude' found"

        try:
            print('Address', row['Address'])
            api_address = row['Address']
            postcode = api_address.split(',')[-1]
        except KeyError:
            print('Expected data heading "Address" missing')
            raise

        # Extract postcode from the end of the address
        # use the postcode as a key value to a dict
        # if the lat, long is in the dict, use that, rather than looking it up.

        try:
            # test for NaN value for Latitude
            # assume if one not set then neither is the other
            if pd.isna(row["Latitude"]):
                print(f'no geo location for {i}, {row["Address"]}')
            else:
                print(f'Geo Location is {row["Latitude"]}, {row["Longitude"]}')
                # lat = (postcode_dict[postcode][0]['locations'][0]
                #               ['latLng']['lat'])
                postcode_dict[postcode] = [{'locations': [
                                            {'latLng': {
                                                'lat': row["Latitude"],
                                                'lng': row["Longitude"]}}]}]

        except KeyError:
            print(f'no geo location for {i}, {row["Address"]}')

        if postcode not in postcode_dict.keys():
            print("New Postcode", postcode)
            parameters = {
                "key": mq_key,
                "location": api_address
            }

            response = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params=parameters)
            if response.status_code == 200:
                print('postcode ', postcode, ' response ', response)
                call_count += 1
                data = response.text
                postcode_dict[postcode] = json.loads(data)['results']
            else:
                print("response not OK:", response.status_code, postcode)
                sleep(10)   # pause the requests for 10 seconds
                continue
        else:
            print('Existing postcode ', postcode, " for ", api_address)

        lat = (postcode_dict[postcode][0]['locations'][0]['latLng']['lat'])
        lng = (postcode_dict[postcode][0]['locations'][0]['latLng']['lng'])

        addrs_df.at[i, 'Latitude'] = lat
        addrs_df.at[i, 'Longitude'] = lng

    print("Calls to mapquest ", call_count)
    addrs_df.to_csv('NHSHospitals_Geo_2.csv')


if __name__ == '__main__':
    data_file_name = os.getenv('HOSPITALS_CSV', '')
    api_key = os.getenv('MAPQUEST_API_KEY', '')
    assert len(data_file_name) > 3, \
        f"Expected filename with more the three characters, got: {len(data_file_name)}"
    assert len(api_key) == 32, \
        f"Expected api key to be 32 characters long - please check.  Key lenget: {len(api_key)}"
    hospital_addrs = get_file_data(data_file_name)
    # TOTread parameters from config
    postcode_to_geo(hospital_addrs, api_key)
