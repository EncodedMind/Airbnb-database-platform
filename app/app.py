# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import pymysql
import json
from collections import defaultdict

# Example usage:
db_config = {
    'host': 'localhost',
    'user': 'root', ##your user name here, usually root
    'password': 'root', ##your password here
    'database': 'new_airbnb', ## the name of your database
    # 'charset': 'utf8mb4', #optional
    # 'cursorclass': pymysql.cursors.DictCursor #optional
}

""" By default, pymysql cursors return results as tuples. Each tuple represents a row from the database, 
    and you access the columns by their numerical index (e.g., row[0], row[1]).
    pymysql.cursors.DictCursor changes this behavior. Instead of tuples, it returns results as dictionaries.
"""

def checkIfPropertyExists(location_a, property_type_a):
    connection = pymysql.connect(**db_config)
    try:
        cursor = connection.cursor()
        sql = """
            SELECT COUNT(*) > 0 AS answer
            FROM PROPERTY pr, PROPERTYTYPE t, PROPERTY_HAS_TYPE h
            WHERE
                pr.location = %s AND t.type_name = %s AND
                pr.property_id = h.property_id AND t.type_id = h.type_id;
        """
        cursor.execute(sql, (location_a, property_type_a))
        result = cursor.fetchone()
        answer = "yes" if result[0] else "no"
        return [(), (answer,)]
    finally:
        connection.close()


def selectTopNhosts(N):

    # Check if N is a non-negative integer
    try:
        N = int(N)
    except ValueError:
        raise ValueError("N must be a non-negative integer.")
    if N < 0:
        raise ValueError("N must be a non-negative integer.")
    
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    sql = """
        SELECT 
            T.type_name, 
            H.host_id, 
            COUNT(*) AS property_count
        FROM 
            property P, 
            host H, 
            property_has_type PHT, 
            propertytype T
        WHERE 
            P.property_id = PHT.property_id
            AND T.type_id = PHT.type_id
            AND P.host_id = H.host_id
        GROUP BY 
            T.type_name, H.host_id
        ORDER BY 
            property_count DESC;
    """

    results = [("Property Type", "Host ID", "Property Count",),]

    try:        
        # Execute the SQL command
        cursor.execute(sql)
        
        # Fetch all the rows in a list of lists
        rows = cursor.fetchall()
        
        top_hosts = defaultdict(list)

        # Iterate through the rows in descending order of `total_properties`
        # and store the top N hosts for each property type 
        for type_name, host_id, total_properties in rows:
            if len(top_hosts[type_name]) < int(N):
                top_hosts[type_name].append((host_id, total_properties))

        for type_name in top_hosts.items():
            for host_id, count in type_name[1]:
                # Append to results
                results.append((type_name[0], host_id, count))

    except Exception as e:
        print(f"Error: unable to fetch data. Details: {e}")
    
    connection.close()
     
    return results
     
def findMatchingProperties(guest_id):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    sql_get_amenities_in_wishlist = f"""
        SELECT 
            PHA.amenity_id
        FROM 
            wishlist_has_property WHP, 
            wishlist W, 
            property_has_amenity PHA
        WHERE 
            WHP.property_id = PHA.property_id 
            AND WHP.wishlist_id = W.wishlist_id 
            AND W.guest_id = {guest_id}
    """

    sql_get_rules_in_bookings = f"""
        SELECT 
            PHR.rule_id
        FROM 
            booking B, 
            property_has_rule PHR
        WHERE 
            B.property_id = PHR.property_id 
            AND B.guest_id = {guest_id}
    """

    sql_get_hosts_in_bookings = f"""
        SELECT 
            P.host_id
        FROM 
            property P, 
            booking B
        WHERE 
            B.guest_id = {guest_id}
            AND B.property_id = P.property_id
    """

    sql = f"""
        SELECT 
            P.property_id, 
            GROUP_CONCAT(DISTINCT A.amenity_name) AS amenities,
            GROUP_CONCAT(DISTINCT R.rule_name) AS house_rules
        FROM 
            property P, 
            property_has_amenity PHA, 
            amenity A, 
            property_has_rule PHR, 
            houserule R
        WHERE 
            P.property_id = PHA.property_id
            AND PHA.amenity_id = A.amenity_id
            AND P.property_id = PHR.property_id
            AND PHR.rule_id = R.rule_id
            AND EXISTS (
                SELECT 1
                FROM property_has_amenity PHA
                WHERE PHA.property_id = P.property_id
                      AND PHA.amenity_id IN ({sql_get_amenities_in_wishlist})
                )
            AND EXISTS (
                SELECT 1
                FROM property_has_rule PHR
                WHERE PHR.property_id = P.property_id
                      AND PHR.rule_id IN ({sql_get_rules_in_bookings})
                )
            AND P.host_id NOT IN ({sql_get_hosts_in_bookings})
        GROUP BY P.property_id
    """

    results = [("Property ID", "Amenities", "House Rules",),]

    try:        
        # Execute the SQL command to fetch qualifying properties
        cursor.execute(sql)
        
        # Fetch all the rows in a list of lists
        properties = cursor.fetchall()

        results.extend(properties)
    
    except Exception as e:
        print(f"Error: unable to fetch data. Details: {e}")

    connection.close()
    
    return results

def countWordsForProperties(N, M):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    sql_get_properties = f"""
        SELECT 
            P.property_id, 
            P.name, 
            P.location, 
            COUNT(DISTINCT B.guest_id) AS num_guests, 
            GROUP_CONCAT(DISTINCT A.amenity_name) AS amenities
        FROM 
            property P, 
            property_has_amenity PHA, 
            amenity A, 
            booking B
        WHERE 
            P.property_id = B.property_id
            AND P.property_id = PHA.property_id
            AND PHA.amenity_id = A.amenity_id
            AND P.property_id NOT IN (
                SELECT property_id FROM wishlist_has_property -- not in any wishlist
            )
            AND EXISTS (    -- at least one review from a guest who booked the property
                SELECT 1
                FROM review R1
                WHERE R1.property_id = P.property_id
                AND R1.guest_id IN (
                    SELECT guest_id 
                    FROM booking B1
                    WHERE B1.property_id = P.property_id
                )
            )
        GROUP BY 
            P.property_id, P.name, P.location
        HAVING 
            COUNT(DISTINCT B.guest_id) >= {int(N)}  --  at least N unique guests
            AND COUNT(DISTINCT PHA.amenity_id) >= 2;    -- at least 2 amenities
        """
    
    sql_get_reviews = """
        SELECT
            GROUP_CONCAT(R.comment SEPARATOR ',') AS reviews
        FROM
            review R
        WHERE
            R.property_id = %s 
            AND R.guest_id IN (     -- only guests who booked the property     
                SELECT guest_id 
                FROM booking B
                WHERE B.property_id = %s
            )
    """

    results = [("Property ID", "Name", "Location", "Amenities", "Unique guests", "Top Words",),]

    stop_words = {
        'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
        'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before',
        'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot',
        'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing',
        "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
        "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll",
        "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his',
        'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is',
        "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most',
        "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once',
        'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over',
        'own', 'same', 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so',
        'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them',
        'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll",
        "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under',
        'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're",
        "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where',
        "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with',
        "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've",
        'your', 'yours', 'yourself', 'yourselves'
    }

    try:        
        # Execute the SQL command to fetch qualifying properties
        cursor.execute(sql_get_properties)
        
        # Fetch all the rows in a list of lists
        properties = cursor.fetchall()

        print(f"Number of properties: {len(properties)}")      

        for [property_id, name, location, number_of_guests, amenities] in properties:

            cursor.execute(sql_get_reviews, (property_id,))
            reviews = cursor.fetchone()[0]

            # Split reviews into words
            words = reviews.split()
            # Count occurrences of each word
            word_count = defaultdict(int)

            for word in words:
                # Remove punctuation and convert to lowercase
                word = ''.join(filter(str.isalnum, word)).lower()
                # Ignore stop words
                if word not in stop_words:
                    word_count[word] += 1
            # Sort words by frequency
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            # Get the top M words
            top_words = [word for word, count in sorted_words[:int(M)]]
            # Join top words into a string
            top_words_str = ', '.join(top_words)

            # Append to results
            results.append((property_id, name, location, amenities, number_of_guests, top_words_str))

    except Exception as e:
        print(f"Error: unable to fetch data. Details: {e}")
    
    return results

def findCommonPropertiesAndGuests(guest_id_a, guest_id_b):
    connection = pymysql.connect(**db_config)
    try:
        cursor = connection.cursor()
        sql = """
            SELECT DISTINCT pr.name, c.guest_id, d.guest_id
            FROM PROPERTY pr, GUEST c, GUEST d, BOOKING bc, BOOKING bd
            WHERE 
                bc.property_id = pr.property_id
                AND bd.property_id = pr.property_id
                AND bc.guest_id = c.guest_id
                AND bd.guest_id = d.guest_id
                AND c.guest_id <> d.guest_id
                AND EXISTS (
                    SELECT *
                    FROM BOOKING b1, BOOKING b2
                    WHERE b1.guest_id = c.guest_id
                      AND b2.guest_id = %s
                      AND b1.property_id = b2.property_id
                )
                AND EXISTS (
                    SELECT *
                    FROM BOOKING b3, BOOKING b4
                    WHERE b3.guest_id = d.guest_id
                      AND b4.guest_id = %s
                      AND b3.property_id = b4.property_id
                );
        """
        cursor.execute(sql, (guest_id_a, guest_id_b))
        results = cursor.fetchall()
        
        # Format: [("Property Name", "Guest C", "Guest D", "Guest A", "Guest B")]
        formatted = [(row[0], row[1], row[2], guest_id_a, guest_id_b) for row in results]
        return [("Property Name", "Guest C", "Guest D", "Guest A", "Guest B")] + formatted

    finally:
        connection.close()  

def highValueHost(min_price_booking, min_rating_review, min_avg_price_host, min_avg_rating_host):
    connection = pymysql.connect(**db_config)
    try:
        cursor = connection.cursor()
        sql = """
            SELECT am.amenity_name, COUNT(*) AS frequency 
            FROM PROPERTY pr, AMENITY am, PROPERTY_HAS_AMENITY h 
            WHERE pr.property_id = h.property_id
              AND am.amenity_id = h.amenity_id
              AND pr.property_id IN (
                SELECT pr.property_id
                FROM PROPERTY pr, HOST h
                WHERE pr.host_id = h.host_id
                  AND (
                    SELECT AVG(p1.price)
                    FROM PROPERTY p1
                    WHERE p1.host_id = h.host_id
                  ) >= %s
                  AND (
                    SELECT AVG(p2.rating)
                    FROM PROPERTY p2
                    WHERE p2.host_id = h.host_id
                  ) >= %s
                  AND pr.property_id IN (
                    SELECT pr2.property_id
                    FROM PROPERTY pr2, BOOKING b, GUEST g
                    WHERE pr2.property_id = b.property_id
                      AND b.guest_id = g.guest_id
                      AND (
                        SELECT MIN(pr1.price)
                        FROM BOOKING b1, PROPERTY pr1
                        WHERE b1.guest_id = g.guest_id
                          AND pr1.property_id = b1.property_id
                      ) >= %s
                      AND (
                        SELECT MIN(r.rating)
                        FROM REVIEW r
                        WHERE r.guest_id = g.guest_id
                      ) >= %s
                  )
              )
            GROUP BY am.amenity_name
            ORDER BY frequency DESC;
        """
        cursor.execute(sql, (
            min_avg_price_host,
            min_avg_rating_host,
            min_price_booking,
            min_rating_review
        ))
        results = cursor.fetchall()

        formatted = [(row[0], row[1]) for row in results]
        return [("Amenity", "Frequency")] + formatted

    finally:
        connection.close()

def recommendProperty(guest_id, desired_city, desired_amenities, max_price, min_rating):
    try:
        # Convert JSON string of desired amenities into a dictionary
        desired_amenities = json.loads(desired_amenities)
        if not isinstance(desired_amenities, dict):
            raise ValueError("desired_amenities must be a JSON dictionary.")
        
        # Ensure numeric values are floats
        max_price = float(max_price)
        min_rating = float(min_rating)

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Input error: {e}")
        return [()]

    best_property = None
    max_score = 0

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # Query to retrieve properties in the desired city within price and rating range, along with their amenities
    sql_fetch_properties = f"""
    SELECT 
        P.property_id, 
        P.name, 
        P.rating, 
        P.price,
        GROUP_CONCAT(DISTINCT A.amenity_name) AS amenities
    FROM 
        property P, 
        property_has_amenity PHA, 
        amenity A
    WHERE 
        P.property_id = PHA.property_id
        AND PHA.amenity_id = A.amenity_id
        AND P.location = "{desired_city}"
        AND P.price <= {max_price}
        AND P.rating >= {min_rating}
    GROUP BY 
        P.property_id, P.name, P.rating
    """

    cursor.execute(sql_fetch_properties)
    rows = cursor.fetchall()

    # Score each property and find the one with the highest combined score
    for row in rows:
        property_id, property_name, property_rating, property_price, amenities_str = row
        amenities = [a.strip() for a in amenities_str.split(',')] if amenities_str else []

        max_weight = max(desired_amenities.values()) if len(desired_amenities) > 0 else 1
        min_weight = min(desired_amenities.values()) if len(desired_amenities) > 0 else 0

        # Min-max normalization of weights
        amenity_weights = {
            amenity: (weight - min_weight) / (max_weight - min_weight)
            for amenity, weight in desired_amenities.items()
        }

        # If property has amenity, add amenity weight to amenity_score
        amenity_score = sum(
            weight for amenity, weight in amenity_weights.items()
            if amenity in amenities
        )

        property_rating = float(property_rating)
        property_price = float(property_price)

        # Scoring weights
        w_amenity = 2
        w_rating = 1
        w_price = 1.5 # Positive price weight -> lower price is better

        # Exponential scoring
        combined_score = amenity_score ** w_amenity * property_rating ** w_rating / property_price ** w_price

        if combined_score >= max_score:
            max_score = combined_score
            best_property = (property_id, property_name)

    # If a best match was found, create a wishlist and add the property
    if best_property:

        sql_check_if_wishlist_exists = """
        SELECT 
            COUNT(*)
        FROM 
            wishlist_has_property WHP,
            wishlist W
        WHERE 
            WHP.property_id = %s
            AND W.guest_id = %s
            AND WHP.wishlist_id = W.wishlist_id
        """
        
        sql_create_wishlist = """
        INSERT INTO 
            wishlist (guest_id, name, privacy)
        VALUES 
            (%s, "WISHLIST", "Public")
        """

        sql_create_wishlist_property = """
        INSERT INTO 
            wishlist_has_property (wishlist_id, property_id)
        VALUES 
            (%s, %s)
        """

        try:
            # Check if the wishlist already exists
            cursor.execute(sql_check_if_wishlist_exists, (best_property[0], guest_id))
            wishlist_exists = cursor.fetchone()[0]

            if wishlist_exists:
                print("Wishlist already exists.")

                connection.close()
                return [best_property]    
            
        except Exception as e:
            # Query failed
            print(f"Error while checking if wishlist exists: {e}")
            connection.close()
            
            return [()]
        
        try:
            # Create one wishlist
            cursor.execute(sql_create_wishlist, (guest_id,))
            wishlist_id = cursor.lastrowid

            # Add the best property to the wishlist
            cursor.execute(sql_create_wishlist_property, (wishlist_id, best_property[0]))
            connection.commit()

            print(f"Wishlist created with ID {wishlist_id} and property {best_property[0]} added.")

        except Exception as e:
            # Insertion failed
            connection.rollback()
            print(f"Error while inserting wishlist: {e}")

            return [()]
    else:
        connection.close()
        raise ValueError("No properties found that match the criteria.")

    connection.close()
    return [best_property]
 
