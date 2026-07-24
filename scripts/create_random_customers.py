import random
from accounts.models import User, Customer_model

# Sample data for random generation
first_names = [
    'John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa',
    'William', 'Emma', 'James', 'Olivia', 'Daniel', 'Sophia', 'Matthew', 'Ava',
    'Christopher', 'Mia', 'Andrew', 'Charlotte', 'Joshua', 'Amelia', 'Kevin', 'Ella',
    'Brian', 'Abigail', 'Jason', 'Emily', 'Ryan', 'Ella', 'Eric', 'Elizabeth',
    'Adam', 'Madison', 'Nathan', 'Chloe', 'Tyler', 'Grace', 'Dylan', 'Victoria',
    'Jonathan', 'Zoe', 'Samuel', 'Lily', 'Alexander', 'Aubrey', 'Brendan', 'Evelyn',
    'Patrick', 'Hannah', 'Gabriel', 'Audrey', 'Isaac', 'Brooklyn', 'Caleb', 'Bella',
    'Dominic', 'Claire', 'Austin', 'Lucy', 'Evan', 'Natalie', 'Cole', 'Samantha',
    'Jose', 'Anna', 'Jesse', 'Katherine', 'Blake', 'Rebecca', 'Adam', 'Hailey',
    'Justin', 'Addison', 'Tanner', 'Sophie', 'Spencer', 'Lydia', 'Tristan', 'Faith',
    'Gavin', 'Nora', 'Hayden', 'Madeline', 'Brady', 'Kylie', 'Grant', 'Naomi'
]

last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill',
    'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell',
    'Mitchell', 'Carter', 'Roberts', 'Turner', 'Phillips', 'Collins', 'Diaz', 'Parker',
    'Evans', 'Edwards', 'Collins', 'Stewart', 'Morris', 'Murphy', 'Cook', 'Rogers',
    'Morgan', 'Peterson', 'Cooper', 'Reed', 'Bailey', 'Bell', 'Howard', 'Ward',
    'Cox', 'Diaz', 'Richardson', 'Wood', 'Watson', 'Brooks', 'Bennett', 'Gray',
    'James', 'Reyes', 'Cruz', 'Hughes', 'Price', 'Myers', 'Long', 'Foster',
    'Sanders', 'Ross', 'Powell', 'Sullivan'
]

street_names = [
    'Main St', 'Oak Ave', 'Pine Rd', 'Maple Dr', 'Cedar Ln', 'Elm Blvd',
    'Washington Ave', 'Lake St', 'Park Rd', 'Hill Dr', 'River Ln', 'Forest Ave',
    'Garden St', 'Meadow Ln', 'Sunset Blvd', 'Highland Ave', 'Church St', 'Market St'
]

cities = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
    'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
    'Fort Worth', 'Columbus', 'San Francisco', 'Charlotte', 'Indianapolis', 'Seattle',
    'Denver', 'Washington', 'Boston', 'Nashville', 'Baltimore', 'Portland',
    'Las Vegas', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno', 'Sacramento',
    'Kansas City', 'Mesa', 'Atlanta', 'Omaha', 'Colorado Springs', 'Raleigh'
]

states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
          'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
          'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
          'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
          'WI', 'WY']

# Create 100 random customers
created = 0
skipped = 0

print("Creating 100 random customers...")

for i in range(100):
    try:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
        
        # Create user
        user = User.objects.create_user(
            email=email,
            password='Test@123456',
            first_name=first_name,
            last_name=last_name,
            role='customer',
            phone_number=f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
        )
        
        # Generate random address
        address = f"{random.randint(100, 9999)} {random.choice(street_names)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"
        
        # Create customer profile
        Customer_model.objects.create(
            user=user,
            phone=user.phone_number,
            address=address
        )
        
        created += 1
        
        if created % 10 == 0:
            print(f"Created {created} customers...")
            
    except Exception as e:
        skipped += 1
        print(f"Error creating customer {i+1}: {e}")

print(f"\n✅ Successfully created {created} random customers!")
if skipped > 0:
    print(f"⚠️ Skipped {skipped} customers due to errors.")