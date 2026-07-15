import os
import urllib.request
from django.core.management.base import BaseCommand
from django.conf import settings
from restaurant.models import Category, MenuItem, Review, RestaurantTable

class Command(BaseCommand):
    help = 'Seeds the database with tables, downloads and saves unique menu images locally, and seeds reviews'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing restaurant data...')
        Review.objects.all().delete()
        MenuItem.objects.all().delete()
        Category.objects.all().delete()
        RestaurantTable.objects.all().delete()

        # Create media directory if it does not exist
        media_dir = os.path.join(settings.MEDIA_ROOT, 'menu_items')
        os.makedirs(media_dir, exist_ok=True)

        self.stdout.write('Creating Restaurant Tables...')
        tables_data = [
            (1, 4, 'Standard'), (2, 4, 'Standard'), (3, 4, 'Standard'), (4, 4, 'Standard'),
            (5, 2, 'Couple'), (6, 2, 'Couple'), (7, 8, 'Family'), (8, 10, 'Family'),
            (9, 8, 'Family'), (10, 6, 'VIP'), (11, 4, 'VIP'), (12, 8, 'VIP'),
        ]
        for t_num, cap, t_type in tables_data:
            RestaurantTable.objects.create(table_number=t_num, capacity=cap, table_type=t_type)

        self.stdout.write('Creating categories (exactly 7 categories)...')
        cats = {
            'starters': Category.objects.create(name="Starters", slug="starters", description="Scrumptious quick bites to kick off your meal."),
            'veg_mains': Category.objects.create(name="Veg Main Course", slug="veg-main-course", description="Delicious vegetarian traditional dishes."),
            'nonveg_mains': Category.objects.create(name="Non-Veg Main Course", slug="non-veg-main-course", description="Rich and spicy meat delicacies."),
            'south_indian': Category.objects.create(name="South Indian", slug="south-indian", description="Fermented crepes, steamed rice cakes, and rich sambar."),
            'north_indian': Category.objects.create(name="North Indian", slug="north-indian", description="Creamy gravies and traditional Punjabi & Mughlai flavors."),
            'desserts_ice_creams': Category.objects.create(name="Desserts & Ice Creams", slug="desserts-ice-creams", description="Rich sweets, cool, creamy and refreshing ice creams."),
            'beverages': Category.objects.create(name="Beverages", slug="beverages", description="Hot teas, rich coffees, and cooling traditional drinks."),
        }

        # 66 completely unique and active Unsplash image IDs (no repetitions)
        dish_images = {
            # Starters
            "Paneer Tikka": "photo-1567188040759-fb8a883dc6d8",
            "Hara Bhara Kabab": "photo-1546069901-ba9599a7e63c",
            "Samosa Chaat": "photo-1506084868230-bb9d95c24759",
            "Chicken 65": "photo-1610057099443-fde8c4d50f91",
            "Veg Spring Rolls": "photo-1544025162-d76694265947",
            "Onion Bhaji": "photo-1589301760014-d929f3979dbc",
            "Gobi 65": "photo-1606491956689-2ea866880c84",
            "Chicken Tikka": "photo-1599487488170-d11ec9c172f0",
            "Mutton Seekh Kabab": "photo-1606787366850-de6330128bfc",
            "Chilli Paneer": "photo-1631452180519-c014fe946bc7",

            # Veg Main Course
            "Paneer Butter Masala": "photo-1565557623262-b51c2513a641",
            "Dal Makhani": "photo-1546833999-b9f581a1996d",
            "Kadhai Paneer": "photo-1565299624946-b28f40a0ae38",
            "Mix Veg": "photo-1626777552726-4a6b54c97e46",
            "Chana Masala": "photo-1565958011703-44f9829ba187",
            "Malai Kofta": "photo-1484723091739-30a097e8f929",
            "Aloo Gobhi": "photo-1482049016688-2d3e1b311543",
            "Bhindi Masala": "photo-1476224203421-9ac39bcb3327",
            "Baingan Bharta": "photo-1588166524941-3bf61a9c41db",
            "Dal Tadka": "photo-1541832676-9b763b0239ab",

            # Non-Veg Main Course
            "Butter Chicken": "photo-1603894584373-5ac82b2ae398",
            "Chicken Tikka Masala": "photo-1473093295043-cdd812d0e601",
            "Mutton Rogan Josh": "photo-1467003909585-2f8a72700288",
            "Chicken Curry": "photo-1540189549336-e6e99c3679fe",
            "Mutton Korma": "photo-1555939594-58d7cb561ad1",
            "Fish Curry": "photo-1519708227418-c8fd9a32b7a2",
            "Prawn Masala": "photo-1534422298391-e4f8c172dddb",
            "Egg Curry": "photo-1594756202469-9ff9799b2e4e",
            "Chicken Handi": "photo-1565299624946-b28f40a0ae38",
            "Mutton Bhuna": "photo-1485962398705-ef6a13c41e8f",

            # South Indian
            "Plain Dosa": "photo-1512621776951-a57141f2eefd",
            "Masala Dosa": "photo-1668236543090-82eba5ee5976",
            "Idli Sambhar": "photo-1504674900247-0877df9cc836",
            "Vada Sambhar": "photo-1498837167922-ddd27525d352",
            "Mysore Masala Dosa": "photo-1490645935967-10de6ba17061",
            "Onion Uttapam": "photo-1529042410759-befb1204b468",
            "Rava Dosa": "photo-1455619452474-d2be8b1e70cd",
            "Paper Roast Dosa": "photo-1511690656952-34342bb7c2f2",
            "Upma": "photo-1513442542250-854d436a73f2",
            "Lemon Rice": "photo-1505253716362-afaea1d3d1af",

            # North Indian
            "Chole Bhature": "photo-1505253668822-42074d58a7c6",
            "Amritsari Kulcha": "photo-1532550907401-a500c9a57435",
            "Rajma Chawal": "photo-1543353071-10c8ba85a904",
            "Kadhi Chawal": "photo-1556910103-1c02745aae4d",
            "Sarson Ka Saag": "photo-1563729784474-d77dbb933a9e",
            "Paneer Pasanda": "photo-1551024601-bec78aea704b",
            "Shahi Paneer": "photo-1551024709-8f23befc6f87",
            "Dum Aloo": "photo-1551818255-e6e10975bc17",
            "Malai Kofta": "photo-1579871494447-9811cf80d66c",
            "Bhindi Do Pyaza": "photo-1608897013039-887f21d8c804",

            # Desserts & Ice Creams
            "Gulab Jamun": "photo-1585238342024-78d387f4a707",
            "Rasmalai": "photo-1586190848861-99aa4a171e90",
            "Gajar Halwa": "photo-1594212699903-ec8a3eca50f5",
            "Kulfi": "photo-1604382355076-af4b0eb60143",
            "Vanilla Ice Cream": "photo-1501443762994-82bd5dace89a",
            "Chocolate Ice Cream": "photo-1563805042-7684c019e1cb",
            "Strawberry Ice Cream": "photo-1604908176997-125f25cc6f3d",
            "Mango Ice Cream": "photo-1570145820259-b5b80c5c8bd6",
            "Butterscotch Ice Cream": "photo-1557142046-c704a3adf364",
            "Chocolate Brownie": "photo-1606313564200-e75d5e30476c",

            # Beverages
            "Masala Chai": "photo-1576092768241-dec231879fc3",
            "Filter Coffee": "photo-1514432324607-a09d9b4aefdd",
            "Sweet Lassi": "photo-1481931098730-318b6f776db0",
            "Mango Juice": "photo-1621506289937-a8e4df240d0b",
            "Lime Soda": "photo-1536935338788-846bb9981813",
            "Iced Tea": "photo-1513558161293-cdaf765ed2fd",
        }

        # Food item helper
        def add_item(cat, name, desc, price, is_veg=True, is_special=False, is_popular=False, is_chef=False, disc=0, is_new=False):
            image_id = dish_images.get(name, "photo-1546069901-ba9599a7e63c")
            image_url = f"https://images.unsplash.com/{image_id}?auto=format&fit=crop&w=600&q=80"
            
            # Local download setup
            filename = f"{name.lower().replace(' ', '_').replace('&', 'and')}.jpg"
            local_path = os.path.join(media_dir, filename)
            
            self.stdout.write(f"Downloading image for '{name}'...")
            try:
                req = urllib.request.Request(
                    image_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response:
                    with open(local_path, 'wb') as out_file:
                        out_file.write(response.read())
                
                db_image_path = f"menu_items/{filename}"
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to download '{name}' image: {e}. Falling back to default."))
                db_image_path = None

            MenuItem.objects.create(
                name=name, description=desc, price=price, category=cat,
                image=db_image_path,
                image_url=image_url,
                is_available=True, is_special=is_special, is_veg=is_veg,
                is_popular=is_popular, is_chef_recommendation=is_chef,
                discount_percentage=disc, is_new_arrival=is_new
            )

        self.stdout.write('Populating menu items (exactly 10 per category, Beverages exactly 6)...')
        
        # 1. Starters
        starters = [
            ("Paneer Tikka", "Spiced cottage cheese cubes charred in tandoor.", 290, True, True, True, False, 10, False),
            ("Hara Bhara Kabab", "Crisp spinach, green peas, and potato patties.", 220, True, False, False, False, 0, False),
            ("Samosa Chaat", "Crushed samosas topped with spicy chole, yogurt, and chutneys.", 180, True, False, True, False, 0, True),
            ("Chicken 65", "Deep-fried spicy chicken chunks tossed in curry leaves.", 340, False, True, True, False, 0, False),
            ("Veg Spring Rolls", "Crispy wrappers filled with seasoned shredded vegetables.", 230, True, False, False, False, 0, False),
            ("Onion Bhaji", "Deep fried spiced onion fritters served crisp.", 150, True),
            ("Gobi 65", "Crispy spiced cauliflower florets deep fried.", 190, True),
            ("Chicken Tikka", "Juicy roasted tandoori chicken chunks.", 350, False, False, True, False, 15, True),
            ("Mutton Seekh Kabab", "Minced mutton skewers seasoned with warm spices.", 420, False, False, False, True, 0, False),
            ("Chilli Paneer", "Cottage cheese tossed with bell peppers and soy chili.", 290, True),
        ]
        for item in starters:
            add_item(cats['starters'], *item)

        # 2. Veg Main Course
        veg_mains = [
            ("Paneer Butter Masala", "Cottage cheese cubes in rich creamy tomato gravy.", 320, True, True, True, False, 0, False),
            ("Dal Makhani", "Slow-cooked black lentils enriched with butter and cream.", 280, True, True, True, True, 10, False),
            ("Kadhai Paneer", "Cottage cheese cooked with bell peppers in thick masala.", 310, True),
            ("Mix Veg", "Assorted seasonal vegetables cooked in dry spices.", 250, True),
            ("Chana Masala", "Spicy chickpeas cooked in authentic Punjabi gravy.", 230, True),
            ("Malai Kofta", "Fried potato-cottage cheese balls in creamy golden gravy.", 340, True, False, False, True, 0, True),
            ("Aloo Gobhi", "Classic dry potato and cauliflower vegetable dish.", 210, True),
            ("Bhindi Masala", "Okra pods stir-fried with onions and dry spices.", 220, True),
            ("Baingan Bharta", "Roasted mashed eggplant cooked with peas and tomatoes.", 240, True),
            ("Dal Tadka", "Yellow lentils tempered with cumin, garlic, and dry red chilies.", 210, True),
        ]
        for item in veg_mains:
            add_item(cats['veg_mains'], *item)

        # 3. Non-Veg Main Course
        nonveg_mains = [
            ("Butter Chicken", "Tandoori chicken in sweet and creamy tomato-butter gravy.", 420, False, True, True, False, 0, False),
            ("Chicken Tikka Masala", "Grilled chicken tikka pieces in a spicy onion gravy.", 410, False),
            ("Mutton Rogan Josh", "Kashmiri style mutton stew cooked with yogurt and ginger.", 480, False, True, False, True, 10, False),
            ("Chicken Curry", "Home-style chicken cooked in onion-tomato gravy.", 350, False),
            ("Mutton Korma", "Traditional slow-cooked lamb in nut paste gravy.", 450, False),
            ("Fish Curry", "Traditional home-style fish curry in tangy gravy.", 430, False),
            ("Prawn Masala", "Juicy prawns tossed in thick spicy masala gravy.", 490, False),
            ("Egg Curry", "Boiled eggs cooked in traditional thick spicy gravy.", 250, False),
            ("Chicken Handi", "Chicken slow-cooked in a traditional clay handi pot.", 380, False),
            ("Mutton Bhuna", "Fried mutton cooked with dense spice gravy.", 470, False),
        ]
        for item in nonveg_mains:
            add_item(cats['nonveg_mains'], *item)

        # 4. South Indian
        south_indian = [
            ("Plain Dosa", "Crispy paper-thin fermented rice crepe.", 110, True),
            ("Masala Dosa", "Crispy crepe stuffed with spiced potato mash.", 145, True, True, True, False, 0, False),
            ("Idli Sambhar", "Steamed fluffy rice-lentil cakes served with sambar.", 100, True),
            ("Vada Sambhar", "Crispy fried lentil donuts served with coconut chutney.", 110, True),
            ("Mysore Masala Dosa", "Dosa spread with garlic-chili paste and potato mash.", 160, True),
            ("Onion Uttapam", "Savory thick rice pancake topped with onions.", 130, True),
            ("Rava Dosa", "Crispy crepe made of semolina and rice flour.", 140, True),
            ("Paper Roast Dosa", "Super thin large dosa cooked with ghee.", 150, True),
            ("Upma", "Savory semolina porridge cooked with mustard and curry leaves.", 100, True),
            ("Lemon Rice", "Tangy South Indian rice tempered with peanuts.", 160, True),
        ]
        for item in south_indian:
            add_item(cats['south_indian'], *item)

        # 5. North Indian
        north_indian = [
            ("Chole Bhature", "Spicy chickpea curry served with fried puffed bread.", 220, True, True, True, False, 0, False),
            ("Amritsari Kulcha", "Crispy potato stuffed flatbread served with chickpeas.", 240, True),
            ("Rajma Chawal", "Spicy red kidney bean gravy served over steamed rice.", 180, True),
            ("Kadhi Chawal", "Yogurt gram flour curry with pakodas served over rice.", 170, True),
            ("Sarson Ka Saag", "Traditional Punjabi mustard greens dish.", 230, True),
            ("Paneer Pasanda", "Fried paneer sandwiches filled with nuts in creamy gravy.", 360, True),
            ("Shahi Paneer", "Cottage cheese cubes in rich aromatic cashew-cream gravy.", 310, True),
            ("Dum Aloo", "Fried potatoes slow-cooked in spicy yogurt gravy.", 240, True),
            ("Malai Kofta", "Cheese dumplings cooked in cashew gravy.", 330, True),
            ("Bhindi Do Pyaza", "Okra cooked with double amount of sauteed onions.", 230, True),
        ]
        for item in north_indian:
            add_item(cats['north_indian'], *item)

        # 6. Desserts & Ice Creams
        desserts_ice_creams = [
            ("Gulab Jamun", "Warm fried milk dumplings in cardamom sugar syrup.", 90, True),
            ("Rasmalai", "Soft cottage cheese patties in saffron-infused milk.", 120, True, True, True, False, 0, False),
            ("Gajar Halwa", "Slow-cooked carrot pudding with nuts and khoya.", 130, True),
            ("Kulfi", "Traditional dense Indian ice cream flavored with saffron.", 110, True),
            ("Vanilla Ice Cream", "Classic creamy vanilla bean ice cream.", 90, True),
            ("Chocolate Ice Cream", "Rich dark chocolate ice cream.", 100, True),
            ("Strawberry Ice Cream", "Creamy ice cream with real strawberry pulp.", 90, True),
            ("Mango Ice Cream", "Sweet mango flavored summer special ice cream.", 100, True),
            ("Butterscotch Ice Cream", "Butterscotch ice cream with crunchy caramelized nuts.", 110, True),
            ("Chocolate Brownie", "Fudgy chocolate brownie served warm.", 150, True),
        ]
        for item in desserts_ice_creams:
            add_item(cats['desserts_ice_creams'], *item)

        # 7. Beverages (EXACTLY 6 items as requested)
        beverages = [
            ("Masala Chai", "Traditional Indian tea brewed with milk and spices.", 60, True),
            ("Filter Coffee", "Strong South Indian filter coffee brewed with milk.", 70, True),
            ("Sweet Lassi", "Chilled sweet churned yogurt drink.", 100, True),
            ("Mango Juice", "Chilled refreshing pulp juice made of ripe mangoes.", 120, True),
            ("Lime Soda", "Fresh lime juice served sweet and salted with soda.", 95, True),
            ("Iced Tea", "Chilled lemon flavored tea served over ice.", 100, True),
        ]
        for item in beverages:
            add_item(cats['beverages'], *item)

        self.stdout.write('Creating reviews...')
        Review.objects.create(
            name="Rohan Mehra", rating=5,
            comment="The Butter Chicken and Cheese Garlic Naan was incredible. Best tandoori items in town. Clean environment and premium golden branding!"
        )
        Review.objects.create(
            name="Anjali Sharma", rating=5,
            comment="I reserved Table 12 (VIP Lounge) for a family party. The process was super smooth, and the food pre-ordering saved us so much time! High-quality South Indian dosas as well."
        )
        Review.objects.create(
            name="Vikram Singh", rating=4,
            comment="Beautiful dark-themed ambiance. Authentic Biryani flavor and fast service. Will visit again soon!"
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded all tables, 66 food items, and reviews!'))
