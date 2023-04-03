# Toy Demand-Side Platform
This project is made by the team The Interns as a final project of IPONWEB internship.

## Description
Demand-Side Platform (DSP) is a software platform used in programmatic advertising that allows advertisers and agencies to purchase digital ad inventory from multiple ad exchanges and ad networks through a single interface. DSPs automate the process of bidding on ad inventory in real-time, using data and algorithms to optimize the buying process.

## Installation
To start, clone the repo to your local computer and change into the proper directory.

```
$ git clone https://github.com/artur-karapetyan/tDSP.git
$ cd src/tdsp/
```

>_Note that you need to have installed Django version 4 or above and Python version 3 or above to run the project._

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

Give a ⭐️  if this project helped you!

## License

[GNU GENERAL PUBLIC LICENSE](LICENSE)