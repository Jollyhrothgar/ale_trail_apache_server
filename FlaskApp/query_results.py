## Python packages - you may have to pip install sqlalchemy, sqlalchemy_utils, and psycopg2.
#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import re
from math import radians, cos, sin, asin, sqrt
from nltk.stem import PorterStemmer
ps = PorterStemmer()

# city structure = "{name":(lat,long)}"
# vista, escondido and san marcos are all the same region
# LA, Torrance, Anaheim are in same area

city = {
    'San Diego':(32.802840, -117.163859),
    'San Francisco':(37.762038, -122.435712),
    'Los Angeles':(34.096910, -118.211263),
    'Vista, Escondido, San Marcos':(33.137474, -117.175240),
    'Temecula':(33.510374, -117.151942),
    'Torrance':(33.846288, -118.331088),
}

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Returns miles
    
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 
    return c * r

def filter_results(query_results, distance_threshold,ref_city):
    beer_list = []
    for result in query_results:
        beer_dict = {}
        try:
            beer_dict['beer_key'] = str(result[0]).decode('utf-8')
            beer_dict['brewery_name'] = str(result[1]).decode('utf-8')
            beer_dict['beer_style'] = str(result[2]).decode('utf-8')
            beer_dict['beer_name'] = str(result[3]).decode('utf-8')
            beer_dict['city'] = str(result[4]).decode('utf-8')
            beer_dict['loc'] = str(result[5])+", "+str(result[6])
            beer_dict['avg_score'] = str(result[8])
            beer_dict['img'] =  "../static/img/beer/"+beer_dict['beer_key']+"_description.png"
        except:
            beer_dict['beer_key'] = result[0]
            beer_dict['brewery_name'] = result[1]
            beer_dict['beer_style'] = result[2]
            beer_dict['beer_name'] = result[3]
            beer_dict['city'] = result[4]
            beer_dict['loc'] = str(result[5])+", "+str(result[6])
            beer_dict['avg_score'] = str(result[8])
            beer_dict['img'] =  "../static/img/beer/"+beer_dict['beer_key']+"_description.png"
        if result[5] == None or result[6] == None:
            continue
        else:
            lat = float(result[5])
            lon = float(result[6])
            #print beer_dict['city']
            #print city['San Diego'][0]
            #print lat,lon,city[ref_city][0],city[ref_city][1]
            distance = haversine(city[ref_city][0],city[ref_city][1],lat,lon)
            if distance_threshold < distance:
                continue
        beer_list.append(beer_dict) 
    if len(beer_list) == 0:
        error_dict = {}
        error_dict['beer_key'] = 'No Results'
        error_dict['brewery_name'] = 'No Results'
        error_dict['beer_style'] = 'No Results'
        error_dict['beer_name'] = 'No Results'
        error_dict['city'] = 'No Results'
        error_dict['loc'] = 'No Results'
        error_dict['avg_score'] = 'No Results'
        error_dict['img'] =  " "
        beer_list.append(error_dict)
    return beer_list

def query_results(hop_range_min,hop_range_max,key_word_1,key_word_2,distance_threshold,ref_city):
    """
    given a range of hop-values, returns a dict of the form:
    dict[status_id]{beer_dictionary} where beer_dictionary populates an
    html table with suggested beers + images.

    the status is either 1, 2 or 3.

    1-> found a review with key_word_1 and key_word_2
    2-> found a review with key_word_1 or key_word_2
    3-> default, could not find any key-words requested.

    Status can be used to dynamically generate a message for the user 
    to perhaps rephrase their query.
    """
    dbname = 'beer_final'
    username = 'postgres'
    mypassword = 'simple'

    status = 1

    print "attempted keyword1:",key_word_1
    print "attempted keyword2:",key_word_2
    ## Sanitize input from nefarious actors...
    key_word_1 = re.sub(r'[^a-zA-Z]+', '', key_word_1)
    key_word_2 = re.sub(r'[^a-zA-Z]+', '', key_word_2)

    print 'hop_range_min:',hop_range_min
    print 'hop_range_max:',hop_range_max
    print 'key_word_1:',key_word_1
    print 'key_word_2:',key_word_2
    print 'city:',ref_city,city[ref_city]

    ## Here, we're using postgres, but sqlalchemy can connect to other things too.
    engine = create_engine('postgres://%s:%s@localhost/%s'%(username,mypassword,dbname))
    con = psycopg2.connect(database = dbname, user = username,host='/var/run/postgresql',password=mypassword)
    print "Connecting to",engine.url

    stem1 = ps.stem(key_word_1)
    stem2 = ps.stem(key_word_2)

    cur = con.cursor()
    # keyword 1 AND keyword 2
    beer_query_both = """
    SELECT 
        breweries.beer_name_key,
        breweries.brewery_name,
        breweries.style_name,
        breweries.beer_name,
        breweries.city,
        breweries.latittude,
        breweries.longitude,
        breweries.hop_mean,
        breweries.avg_score
    FROM 
        breweries
    WHERE
        breweries.hop_mean > %s and breweries.hop_mean < %s
    AND
        (breweries.review_stems like %s AND breweries.review_stems like %s)
    AND
        breweries.ratings_count > 5
    ORDER BY
        breweries.avg_score desc;
    """
    cur.execute(beer_query_both,(hop_range_min,hop_range_max,'%'+stem1+'%','%'+stem2+'%'))
    results_and = cur.fetchall()

    # keyword 1 OR keyword 2
    print "using 'or' query"
    beer_query_or = """
    SELECT 
        breweries.beer_name_key,
        breweries.brewery_name,
        breweries.style_name,
        breweries.beer_name,
        breweries.city,
        breweries.latittude,
        breweries.longitude,
        breweries.hop_mean,
        breweries.avg_score
    FROM 
        breweries
    WHERE
        breweries.hop_mean > %s and breweries.hop_mean < %s
    AND
        (breweries.review_stems like %s OR breweries.review_stems like %s)
    AND
        breweries.ratings_count > 5
    ORDER BY
        breweries.avg_score desc;
    """
    cur.execute(beer_query_or,(hop_range_min,hop_range_max,'%'+stem1+'%','%'+stem2+'%'))
    results_or = cur.fetchall()

    # No keywords actually used
    print  "using default query"
    standard_query = """
    SELECT 
        breweries.beer_name_key,
        breweries.brewery_name,
        breweries.style_name,
        breweries.beer_name,
        breweries.city,
        breweries.latittude,
        breweries.longitude,
        breweries.hop_mean,
        breweries.avg_score
    FROM 
        breweries
    WHERE
        breweries.hop_mean > %s and breweries.hop_mean < %s
    AND
        breweries.ratings_count > 5
    ORDER BY
        breweries.avg_score desc;
    """
    cur.execute(standard_query,(hop_range_min,hop_range_max))
    results_neither = cur.fetchall()
    # results has been filled with something by now
    print "both keywords:",len(results_and)
    print "either keyword:",len(results_or)
    print "no keywords:",len(results_neither)

    # Get beer lists based on query possibilities
    beer_list_and = filter_results(results_and,distance_threshold,ref_city)
    beer_list_or = filter_results(results_or,distance_threshold,ref_city)
    beer_list_neither = filter_results(results_neither,distance_threshold,ref_city)
   
    results_dict = {}
    results_dict['status'] = 0
    results_dict['beer_list'] = []
    status = 0
    if len(beer_list_and) > 4:
        status = 0
        results_dict['beer_list'] = beer_list_and[:5]
    elif len(beer_list_or) > 4:
        status = 1
        results_dict['beer_list'] = beer_list_or[:5]
    elif len(beer_list_neither) > 4:
        results_dict['beer_list'] = beer_list_neither[:5]
        status = 2
    elif len(beer_list_neither) == 1:
        results_dict['beer_list'] = beer_list_neither
        status = 3
    else:
        status = 4
        print "unhandled error, no results found, but dict did not return error handler from SQL query"
    cur.close()
    results_dict['status'] = status
    return results_dict
