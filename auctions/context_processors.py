def watch_listings_count(request):
    if request.user.is_authenticated:
        watchlisting_count = request.user.watch_listings.filter(closed=False).count()
    else:
        watchlisting_count = 0
    return {'wlistings_count': watchlisting_count} 