# ECommerce
eBay-like e-commerce auction site that will allow users to post auction listings, place bids on listings, comment on those listings, and add listings to a watchlist.

## Getting started

1. Clone the repo

```
git clone git@github.com:kershik/ECommerce.git
```

2. Go to ECommerce directory.

```
cd ECommerce
```

2. Make migrations for auctions app.

```
python manage.py makemigrations auctions
```

3. Apply migrations to your database.

```
python manage.py migrate
```
