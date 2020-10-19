# Automodel
A service for connecting to databases and then dimensionally modelling data...

## Prerequisites
python3, vue.js

## API Capabilities
to come...

## How to:

*Run program in development*

This repo uses the file ```package.json``` and [yarn](https://yarnpkg.com/lang/en/) to run the required commands.

1. Make sure you have installed yarn.
2. Create a file called ```helpers.json``` and set username and password in the following format:
```
{
    "username": "some username",
    "password": "some password"
}
```
3. run:
    ```
        yarn install
    ```
4. execute to run the script:
    ```
        yarn swagger
    ```

*Run program in production*

Make sure the required env variables are defined.

*Use program as a SESAM connector*

#### System config :

```
    {
    "_id": "ecovadis",
    "type": "system:microservice",
    "docker": {
        "environment": {
        "password": "$SECRET(ecovadis-password)",
        "username": "$ENV(ecovadis-username)"
        },
        "image": "sesamcommunity/ecovadis:latest",
        "port": 5000
    },
    "verify_ssl": true
    }
```

#### Example Pipe config :

```
    {
    "_id": "ecovadis-evdata",
    "type": "pipe",
    "source": {
        "type": "json",
        "system": "ecovadis",
        "url": "/entities/get/EVData"
    },
    "transform": {
        "type": "dtl",
        "rules": {
        "default": [
            ["copy", "*"],
            ["add", "_id",
            ["string", "_S.evid"]
            ]
        ]
        }
    }
    }
```

## Routes

```
    /
```