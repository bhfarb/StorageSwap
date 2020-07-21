We modeled our project on the Problem Set 8 Finance framework. We formatted our HTML pages using a Bootswatch theme and
Bootstrap templates.

On the home page, you can register as a buyer or seller. The registration inputs get added to a SQL data table
called "users," with an entry called "role" that is set as "buyer" if the user is registering as a buyer and "seller" if the
user is registering as a seller. Once you register, you are redirected to login.

If you're logged in as a buyer, the interface extends "layout_buyer.html" with options for "Profile,"
"Search," and "Messages" in the navigation bar. If you're logged in as a seller, the interface extends
"layout_seller.html" with options for "Profile," "Make a Listing," and "Messages" in the navigation bar.

As a seller, when you make a listing, the required inputs entered in the "Make a Listing" page are added to a SQL data table called
"listings" along with an automatically generated unique "listing_id" for each listing to keep track of each listing.

Buyers search for listings on the page designed as "search.html." The buyers input their location and range in miles. In the "helpers.py" file,
you will find the function used to calculate the distance between two locations. Specifically, "find_distance()" accesses the
Google Maps API to do so, using an API key for which we obtained a free trial. Within "application.py", the listings SQL table is
traversed, checking for listings that fall within the physical range of the search parameters and for listings with dates that encompass the
dates of the search parameters. The latter is accomplished using a function in "helpers.py", which accesses the datetime module. The
resulting listings are then sorted by price in "application.py" and displayed in the "search_results.html" page in a table
that is generated using Jinja. The resulting listings and seller profiles are presented as unique hyperlinks to the
corresponding listing page and seller profile, respectively.

To generate users' profiles, data is retrieved from the "users" SQL data table. For buyers, the "buyerprofile.html"
page is rendered and for sellers, the "sellerprofile.html" page is rendered. The only difference between the two profiles
is that the seller profile includes a list of their current listings. Each displayed listing is presented
as a unique hyperlink. When a listing hyperlink is clicked, the listing page is rendered either as "listing_buyer.html" if the logged in user
is a buyer or "listing_seller.html" if the logged in user is a seller. The unique "listing_id" is passed along to the page so that
the resulting page displays the selected listing's unique information retrieved from the "listings" SQL data table.

On each listing page, the buyer can message the listing's seller by clicking the message button, which links to a form in "new_message.html."
When the user submits the form, the message is passed into a SQL table called "messages" along with their username, the username
of the user they're sending it to, and a timestamp. Then, when a user wants to view their messages, they click on "Messages" in the nav bar.
This page is formatted by "messages.html," and displays the user's messages from the SQL table. They can reply to a message via the
"Reply" button,which is a hyperlink to the /new_message route in "application.py" that again renders the "new_message.html" page.
