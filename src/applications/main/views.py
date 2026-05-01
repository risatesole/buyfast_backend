from django.shortcuts import render, redirect

def categories_context_handler():
    categories = [
        {
            "name": "Electronics",
            "slug": "electronics",
            "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
            "count": "2.4K+ products"
        },
        {
            "name": "Grocery",
            "slug": "grocery",
            "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
            "count": "1.8K+ products"
        },
        {
            "name": "Home & Kitchen",
            "slug": "home",
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
            "count": "3.2K+ products"
        },        
        {
            "name": "Shoes",
            "slug": "shoes",
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
            "count": "3.2K+ products"
        },
        {
            "name": "Electronics",
            "slug": "electronics",
            "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
            "count": "2.4K+ products"
        },
        {
            "name": "Grocery",
            "slug": "grocery",
            "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
            "count": "1.8K+ products"
        },
        {
            "name": "Home & Kitchen",
            "slug": "home",
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
            "count": "3.2K+ products"
        },        
        {
            "name": "Shoes",
            "slug": "shoes",
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
            "count": "3.2K+ products"
        },
                {
            "name": "Electronics",
            "slug": "electronics",
            "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
            "count": "2.4K+ products"
        },     
        {
            "name": "Shoes",
            "slug": "shoes",
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
            "count": "3.2K+ products"
        },
        {
            "name": "Electronics",
            "slug": "electronics",
            "image": "https://images.unsplash.com/photo-1593640408182-31c228b78b5b?w=300&h=300&fit=crop",
            "count": "2.4K+ products"
        },
    ]
    # trick i found the [:8] limits the return to just 8 categories... jaja
    return categories


def home_context_handler():
    categories = categories_context_handler()
    hero_section = {
        "text": {
            "main": "Compra a tu manera",
            "eyebrow": "productos que dicen comprame",
            "supporting": "Descubre cientos de productos seleccionados para cada estilo y ocasión"
        }
    }

    context = {
        "storename": "Petal",
        "hero": hero_section,
        "categories": categories[:8] 

    }
    return context


def home_view(request):
    context = home_context_handler()
    return render(request, "pages/home/index.html", context)







def categories_view(request):
    context = {
        "categories": categories_context_handler()
    }
    return render(request, "store/categories/categories_page.html",context)


















mock_products = [
    # --- FRUITS_AND_VEGETABLES ---
    {"name": "Organic Fuji Apples", "description": "Crisp and sweet organic apples.", "category": "FRUITS_AND_VEGETABLES", "status": "ACTIVE", "brand": "Nature's Own", "image": "products/apples.jpg", "metric_unit": "UNIT"},
    {"name": "Baby Spinach", "description": "Fresh pre-washed baby spinach leaves.", "category": "FRUITS_AND_VEGETABLES", "status": "ACTIVE", "brand": "GreenLeaf", "image": "products/spinach.jpg", "metric_unit": "UNIT"},

    # --- LACTEOUS ---
    {"name": "Whole Milk 1L", "description": "Pasteurized whole milk.", "category": "LACTEOUS", "status": "ACTIVE", "brand": "DairyFarm", "image": "products/milk.jpg", "metric_unit": "UNIT"},
    {"name": "Greek Yogurt", "description": "Plain unsweetened greek yogurt.", "category": "LACTEOUS", "status": "ACTIVE", "brand": "Chobani-Style", "image": "products/yogurt.jpg", "metric_unit": "UNIT"},
    {"name": "Cheddar Cheese Block", "description": "Aged sharp cheddar.", "category": "LACTEOUS", "status": "DEACTIVATED", "brand": "OldWorld", "image": "products/cheese.jpg", "metric_unit": "UNIT"},

    # --- GROCERY_AND_GOURMET ---
    {"name": "Extra Virgin Olive Oil", "description": "Cold-pressed mediterranean oil.", "category": "GROCERY_AND_GOURMET", "status": "ACTIVE", "brand": "Pompeian", "image": "products/olive_oil.jpg", "metric_unit": "UNIT"},
    {"name": "Himalayan Pink Salt", "description": "Fine grain mineral salt.", "category": "GROCERY_AND_GOURMET", "status": "ACTIVE", "brand": "SaltCo", "image": "products/salt.jpg", "metric_unit": "UNIT"},
    {"name": "Organic Quinoa", "description": "High-protein white quinoa.", "category": "GROCERY_AND_GOURMET", "status": "ACTIVE", "brand": "AncientGrains", "image": "products/quinoa.jpg", "metric_unit": "UNIT"},

    # --- ELECTRONIC_AND_TECH ---
    {"name": "Wireless Noise Cancelling Headphones", "description": "Over-ear Bluetooth headphones.", "category": "ELECTRONIC_AND_TECH", "status": "ACTIVE", "brand": "SonicFlow", "image": "products/headphones.jpg", "metric_unit": "UNIT"},
    {"name": "Smart Watch Series 5", "description": "Fitness tracking and notifications.", "category": "ELECTRONIC_AND_TECH", "status": "ACTIVE", "brand": "TechTime", "image": "products/watch.jpg", "metric_unit": "UNIT"},
    {"name": "USB-C Hub Multiport", "description": "6-in-1 adapter for laptops.", "category": "ELECTRONIC_AND_TECH", "status": "ACTIVE", "brand": "ConnectIt", "image": "products/hub.jpg", "metric_unit": "UNIT"},
    {"name": "Mechanical Keyboard", "description": "RGB backlit tactile switches.", "category": "ELECTRONIC_AND_TECH", "status": "ACTIVE", "brand": "GamerGear", "image": "products/keyboard.jpg", "metric_unit": "UNIT"},

    # --- CLOTHING ---
    {"name": "Cotton Crewneck T-Shirt", "description": "100% organic cotton tee.", "category": "CLOTHING", "status": "ACTIVE", "brand": "BasicThreads", "image": "products/tshirt.jpg", "metric_unit": "UNIT"},
    {"name": "Slim Fit Denim Jeans", "description": "Classic blue stretch denim.", "category": "CLOTHING", "status": "ACTIVE", "brand": "DenimCo", "image": "products/jeans.jpg", "metric_unit": "UNIT"},
    {"name": "Winter Wool Coat", "description": "Heavyweight wool blend coat.", "category": "CLOTHING", "status": "DEACTIVATED", "brand": "ArcticWear", "image": "products/coat.jpg", "metric_unit": "UNIT"},

    # --- SHOES ---
    {"name": "Running Sneakers", "description": "Lightweight breathable mesh.", "category": "SHOES", "status": "ACTIVE", "brand": "Velocity", "image": "products/sneakers.jpg", "metric_unit": "PAIR"},
    {"name": "Leather Chelsea Boots", "description": "Classic brown leather finish.", "category": "SHOES", "status": "ACTIVE", "brand": "UrbanStep", "image": "products/boots.jpg", "metric_unit": "PAIR"},
    {"name": "Formal Oxford Shoes", "description": "Black polished dress shoes.", "category": "SHOES", "status": "ACTIVE", "brand": "GentleWalk", "image": "products/oxfords.jpg", "metric_unit": "PAIR"},

    # --- JEWELRY ---
    {"name": "Silver Chain Necklace", "description": "925 Sterling silver 20 inch.", "category": "JEWELRY", "status": "ACTIVE", "brand": "LuxeJewels", "image": "products/necklace.jpg", "metric_unit": "UNIT"},
    {"name": "Gold Hoop Earrings", "description": "14k Gold plated hoops.", "category": "JEWELRY", "status": "ACTIVE", "brand": "ShineOn", "image": "products/earrings.jpg", "metric_unit": "PAIR"},

    # --- HOME_AND_KITCHEN ---
    {"name": "Non-Stick Frying Pan", "description": "12-inch ceramic coated pan.", "category": "HOME_AND_KITCHEN", "status": "ACTIVE", "brand": "ChefPro", "image": "products/pan.jpg", "metric_unit": "UNIT"},
    {"name": "Electric Kettle", "description": "1.7L stainless steel kettle.", "category": "HOME_AND_KITCHEN", "status": "ACTIVE", "brand": "QuickBoil", "image": "products/kettle.jpg", "metric_unit": "UNIT"},
    {"name": "Egyptian Cotton Towels", "description": "Set of 2 bath towels.", "category": "HOME_AND_KITCHEN", "status": "ACTIVE", "brand": "SoftTouch", "image": "products/towels.jpg", "metric_unit": "BOX"},

    # --- TOOLS_AND_HOME_IMPROVEMENT ---
    {"name": "Cordless Drill Set", "description": "20V power drill with bits.", "category": "TOOLS_AND_HOME_IMPROVEMENT", "status": "ACTIVE", "brand": "BuildIt", "image": "products/drill.jpg", "metric_unit": "BOX"},
    {"name": "Screwdriver Set (10pc)", "description": "Magnetic tip assorted sizes.", "category": "TOOLS_AND_HOME_IMPROVEMENT", "status": "ACTIVE", "brand": "FixTool", "image": "products/screwdrivers.jpg", "metric_unit": "BOX"},

    # --- FURNITURE ---
    {"name": "Ergonomic Office Chair", "description": "Lumbar support mesh chair.", "category": "FURNITURE", "status": "ACTIVE", "brand": "ComfortSeat", "image": "products/chair.jpg", "metric_unit": "UNIT"},
    {"name": "Oak Coffee Table", "description": "Solid wood minimalist design.", "category": "FURNITURE", "status": "ACTIVE", "brand": "WoodWorks", "image": "products/table.jpg", "metric_unit": "UNIT"},

    # --- BOOKS ---
    {"name": "The Great Gatsby", "description": "Classic novel by F. Scott Fitzgerald.", "category": "BOOKS", "status": "ACTIVE", "brand": "Penguin Classics", "image": "products/gatsby.jpg", "metric_unit": "UNIT"},
    {"name": "Python Crash Course", "description": "A hands-on introduction to programming.", "category": "BOOKS", "status": "ACTIVE", "brand": "No Starch Press", "image": "products/python_book.jpg", "metric_unit": "UNIT"},

    # --- VIDEO_GAMES ---
    {"name": "Legend of Zelda", "description": "Action-adventure game.", "category": "VIDEO_GAMES", "status": "ACTIVE", "brand": "Nintendo", "image": "products/zelda.jpg", "metric_unit": "UNIT"},
    {"name": "Gaming Controller", "description": "Wireless Bluetooth controller.", "category": "VIDEO_GAMES", "status": "ACTIVE", "brand": "PlayPad", "image": "products/controller.jpg", "metric_unit": "UNIT"},

    # --- MUSIC ---
    {"name": "Vinyl Record Player", "description": "3-speed turntable with speakers.", "category": "MUSIC", "status": "ACTIVE", "brand": "RetroSound", "image": "products/vinyl.jpg", "metric_unit": "UNIT"},
    {"name": "Acoustic Guitar Strings", "description": "Medium gauge steel strings.", "category": "MUSIC", "status": "ACTIVE", "brand": "Strummer", "image": "products/strings.jpg", "metric_unit": "UNIT"},

    # --- MOVIES_AND_TV ---
    {"name": "Sci-Fi Movie Box Set", "description": "Ultimate collection of space epics.", "category": "MOVIES_AND_TV", "status": "ACTIVE", "brand": "CinemaHome", "image": "products/scifi.jpg", "metric_unit": "BOX"},

    # --- BEAUTY_AND_PERSONAL_CARE ---
    {"name": "Hydrating Face Cream", "description": "Daily moisturizer with SPF 30.", "category": "BEAUTY_AND_PERSONAL_CARE", "status": "ACTIVE", "brand": "GlowUp", "image": "products/cream.jpg", "metric_unit": "UNIT"},
    {"name": "Electric Toothbrush", "description": "Sonic cleaning technology.", "category": "BEAUTY_AND_PERSONAL_CARE", "status": "ACTIVE", "brand": "CleanSmile", "image": "products/toothbrush.jpg", "metric_unit": "UNIT"},
    {"name": "Lavender Essential Oil", "description": "Pure therapeutic grade oil.", "category": "BEAUTY_AND_PERSONAL_CARE", "status": "ACTIVE", "brand": "AromaLife", "image": "products/lavender.jpg", "metric_unit": "UNIT"},

    # --- HEALTH_AND_HOUSEHOLD ---
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Multivitamin Tablets", "description": "Daily supplement for adults.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "VitaMax", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},
    {"name": "Eco-Friendly Detergent", "description": "Biodegradable laundry soap.", "category": "HEALTH_AND_HOUSEHOLD", "status": "ACTIVE", "brand": "PureClean", "image": "https://fastly.picsum.photos/id/29/4000/2670.jpg?hmac=rCbRAl24FzrSzwlR5tL-Aqzyu5tX_PA95VJtnUXegGU", "metric_unit": "UNIT"},

    # --- TOYS_AND_GAMES ---
    {"name": "Building Block Set", "description": "500-piece creative set.", "category": "TOYS_AND_GAMES", "status": "ACTIVE", "brand": "BrickMaster", "image": "products/blocks.jpg", "metric_unit": "BOX"},
    {"name": "Remote Control Car", "description": "Off-road 4WD high speed.", "category": "TOYS_AND_GAMES", "status": "ACTIVE", "brand": "TurboToys", "image": "products/car.jpg", "metric_unit": "UNIT"},

    # --- BABY_PRODUCTS ---
    {"name": "Baby Diapers Size 3", "description": "Ultra-absorbent soft diapers.", "category": "BABY_PRODUCTS", "status": "ACTIVE", "brand": "Pampers", "image": "products/diapers.jpg", "metric_unit": "BOX"},
    {"name": "Silicone Baby Bibs", "description": "Waterproof easy-clean bibs.", "category": "BABY_PRODUCTS", "status": "ACTIVE", "brand": "BabySafe", "image": "products/bibs.jpg", "metric_unit": "UNIT"},

    # --- SPORTS_AND_OUTDOORS ---
    {"name": "Yoga Mat", "description": "Non-slip 6mm thick mat.", "category": "SPORTS_AND_OUTDOORS", "status": "ACTIVE", "brand": "ZenFlow", "image": "products/yoga.jpg", "metric_unit": "UNIT"},
    {"name": "Aluminum Water Bottle", "description": "Insulated sports bottle 32oz.", "category": "SPORTS_AND_OUTDOORS", "status": "ACTIVE", "brand": "HydroPeak", "image": "products/bottle.jpg", "metric_unit": "UNIT"},
    {"name": "Camping Tent (4-Person)", "description": "Waterproof easy-setup tent.", "category": "SPORTS_AND_OUTDOORS", "status": "DEACTIVATED", "brand": "WildTrack", "image": "products/tent.jpg", "metric_unit": "UNIT"},

    # --- AUTOMOTIVE ---
    {"name": "Car Phone Mount", "description": "Dashboard universal holder.", "category": "AUTOMOTIVE", "status": "ACTIVE", "brand": "DriveSafe", "image": "products/mount.jpg", "metric_unit": "UNIT"},
    {"name": "Microfiber Cleaning Cloths", "description": "Scratch-free car drying.", "category": "AUTOMOTIVE", "status": "ACTIVE", "brand": "AutoShine", "image": "products/cloths.jpg", "metric_unit": "BOX"},

    # --- PET_SUPPLIES ---
    {"name": "Dry Dog Food (15kg)", "description": "Chicken and rice formula.", "category": "PET_SUPPLIES", "status": "ACTIVE", "brand": "PetPals", "image": "products/dogfood.jpg", "metric_unit": "UNIT"},
    {"name": "Cat Scratching Post", "description": "Sisal rope covered post.", "category": "PET_SUPPLIES", "status": "ACTIVE", "brand": "FelineFun", "image": "products/scratchpost.jpg", "metric_unit": "UNIT"},

    # --- OFFICE_PRODUCTS ---
    {"name": "Gel Pen Set (12pc)", "description": "Smooth writing black ink.", "category": "OFFICE_PRODUCTS", "status": "ACTIVE", "brand": "WriteRight", "image": "products/pens.jpg", "metric_unit": "BOX"},
    {"name": "Paper Shredder", "description": "Cross-cut security shredder.", "category": "OFFICE_PRODUCTS", "status": "ACTIVE", "brand": "OfficeShield", "image": "products/shredder.jpg", "metric_unit": "UNIT"},

    # --- INDUSTRIAL_AND_SCIENTIFIC ---
    {"name": "Digital Multimeter", "description": "Voltage and current tester.", "category": "INDUSTRIAL_AND_SCIENTIFIC", "status": "ACTIVE", "brand": "VoltTech", "image": "products/multimeter.jpg", "metric_unit": "UNIT"},
    {"name": "Safety Goggles", "description": "Anti-fog protective eyewear.", "category": "INDUSTRIAL_AND_SCIENTIFIC", "status": "ACTIVE", "brand": "SafeGuard", "image": "products/goggles.jpg", "metric_unit": "UNIT"}
]

def storefront_Health_and_Household_section(request):
    # Filter the list to only include Health and Household items
    health_household_items = [
        product for product in mock_products
        if product["category"] == "HEALTH_AND_HOUSEHOLD"
    ]

    context = {
        "section_title": "Health & Household",
        "section_slogan": "Designed for wellbeing & daily life",
        "section_hero_short_text": "thoughtful essentials",
        "products": health_household_items
    }

    return render(request, "pages/home/store_front_section_template.html", context)

def storefront_product_page(request,product_id):
    return render(request,"pages/home/store_product_page.html")



def storefront_electronic_section(request):
    return render(request,"pages/home/electronic_section.html")
