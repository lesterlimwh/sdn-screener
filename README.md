# SDN Screener Backend Service
A Python FastAPI application that screens a person against the publicly available OFAC Specially Designated Nationals (SDN) [list](https://sanctionslist.ofac.treas.gov/Home/SdnList).
## Instructions to run the service locally
**Clone the repository**
```
git clone https://github.com/lesterlimwh/sdn-screener.git
```
**Set environment variables**

Modify the following variables in the .env file
```
MONGO_INITDB_ROOT_USERNAME
MONGO_INITDB_ROOT_PASSWORD
OFAC_API_KEY
```
Sign up [here](https://www.ofac-api.com/account/sign-up) (free trial is ok) for the OFAC API key.

**Start the Docker container**
```
docker-compose up --build
```

## Endpoints
http://localhost:8000/api/v1/screen

API request format
```
[
    {
        "id": int,
        "name": string,
        "dob": string (YYYY-MM-DD),
        "country": string
    }
]
```

API response format
```
[
    {
        "id": int,
        "name_match": bool,
        "dob_match": bool,
        "country_match": bool
    }
]
```

**Sample POST request body**
```
[
    {
        "id": 1,
        "name": "Ubaidullah Akhund Sher Mohammed",
        "dob": "1950-01-01",
        "country": "Afghanistan"
    },
    {
        "id": 2,
        "name": "Abu Abbas",
        "dob": "1948-12-10",
        "country": "Yemen"
    }
]
```

## Modifications / Improvements
- Requires *full date of birth* instead of just the birth year
    - This is due to OFAC API constraints (it seems to use strict matching for dob)
    - Supplying just the birth year with dummy month and day will always result in non-match if we keep the minimum score above the recommended 80
- API is able to bulk process a list of people instead of a single person
    - The UI does not use this functionality, as this is more suitable for scripting purposes
- Redis Caching
    - Uses name-dob-country as a key to store previous screening results
    - Minimizes repeated calls to OFAC API

## TODO: Further Optimizations
- Authentication
    - Add an authentication layer to this service so API calls require a token
- Message Broker
    - Use a message broker like RabbitMQ/Kafka to process bulk requests
