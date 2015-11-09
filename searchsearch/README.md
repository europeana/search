# Django installation for search applications

This django installation is intended to host lightweight applications developed to assist with improving Europeana search.

At the moment two are envisaged: **mobsource** will be used for crowdsourcing multilingual queries and ranking them; **rankfiddle** will allow manual manipulation of various search parameters (chiefly weighting and span parameters) for coarse tuning of these.

## Dependencies 

So far ....

* Python >= 3.3 (to run the thing)
* psycopg2 (Postgres support)
* [django-registration](https://github.com/macropin/django-registration) (for one-step registration)

## TODO

### RankFiddle 

1. Build it

### mobsource

1. Style 'forgot password' pages (right now they're just standard Django admin pages)
2. Convert logged queries + nDCG scores and insert into DB
