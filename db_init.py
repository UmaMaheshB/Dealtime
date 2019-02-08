from main import db, Item, Category
from datetime import datetime
mobile = Category(name="mobile", user_id="admin")
redmia1 = Item(brand="Redmi",
               name="Redmi A1",
               price=10000,
               description="simple description",
               image='https://images-na.ssl-images-amazon.com/images/I/'
               '81L23OnNA%2BL._SX522_.jpg',
               category_id=1,
               user_id="admin")
db.session.add(mobile)
db.session.add(redmia1)
headset = Category(name="headset", user_id="admin")
bluetooth = Item(brand="samsung",
                 name="Samsung Level U Bluetooth",
                 price=2399,
                 description="The Samsung Level U Wireless Headset offers a"
                 "Comfortable Fit and More Battery Power so that your day "
                 "is filled with your favourite music",
                 image='https://rukminim1.flixcart.com/image/832/832/jhgl5e80/'
                 'headphone/t/9/b/samsung-level-u-eo-bg920bbegin-original-'
                 'imaf5h5qwx37dmca.jpeg?q=70',
                 category_id=2,
                 user_id="admin")
db.session.add(headset)
db.session.add(bluetooth)
db.session.commit()
print("created intialized data")
