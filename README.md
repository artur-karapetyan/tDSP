# Toy Demand-Side Platform

This project is made by the team The Interns as a final project of IPONWEB internship.

## Description

Demand-Side Platform (DSP) is a software platform used in programmatic advertising that allows advertisers and agencies
to purchase digital ad inventory from multiple ad exchanges and ad networks through a single interface. DSPs automate
the process of bidding on ad inventory in real-time, using data and algorithms to optimize the buying process.

## API Endpoints

> _Note that all endpoints are protected with JWT authentication. To send requests to endpoints You need to be logged in to User account and use the given token in Authorization Header._

| API URL                            | Request Method    | Description                                                                                              |
|------------------------------------|-------------------|----------------------------------------------------------------------------------------------------------|
| `/rtb/bid/`                        | `POST`            | To send bid request and get response with bid price and creative image url                               |
| `/rtb/notify/`                     | `POST`            | To send `win` or `lose` notification. Response type is `text/plain;charset=UTF-8` with status code `200` |
| `/game/configure/`                 | `POST`            | To send configuration of the game                                                                        |
| `api/creatives/`                   | `POST`            | To create a new creative                                                                                 |
| `api/creatives/<str:creative_id>`  | `GET`             | To get the image of the creative                                                                         |
| `api/creatives/<int:page>/`        | `GET`             | To get creatives using paginator                                                                         |
| `api/campaigns/`                   | `POST` or `PATCH` | To create a new campaign or edit `min_bid` of all campaigns                                              |
| `api/campaigns/<int:campaign_id>/` | `PATCH`           | To edit `min_bid` or `is_enabled` fields of a specific campaign                                          |
| `api/bid_request/<int:page>/`      | `GET`             | To get bid requests using paginator                                                                      |
| `api/bid_response/<int:page>/`     | `GET`             | To get bid responses using paginator                                                                     |
| `api/categories/`                  | `GET`             | To get all categories' id-s                                                                              |
| `api/categories/<int:page>/`       | `GET`             | To get categories using paginator                                                                        |
| `api/notify/<int:page>/`           | `GET`             | To get notifications using paginator                                                                     |
| `login/`                           | `POST`            | To login into User account                                                                               |
| `logout/`                          | `POST`            | To logout from logged in User account                                                                    |

## Installation

To start, clone the repo to your local computer and change into the proper directory.

```
$ git clone https://github.com/artur-karapetyan/tDSP.git
$ cd src/tdsp/
```

> _Note that you need to have installed Django version 4 or above and Python version 3 or above to run the project._

To use the project with PostgreSQL as the database create `.env` file in `tdsp` directory to reflect the following:

```
DATABASE_NAME=YOUR_DATABASE_NAME
USER_NAME=YOUR_USER_NAME
PASSWORD=YOUR_PASSWORD
HOST=localhost
PORT=5432
```

After configuring database run these commands:

```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
# Load the site at http://127.0.0.1:8000
```

## Contributing

Contributions, issues and feature requests are welcome!

## Support

Give a ⭐️ if this project helped you!

## License

[GNU GENERAL PUBLIC LICENSE](LICENSE)