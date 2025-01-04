import pandas as pd
import random
from faker import Faker

faker = Faker()


post_types = {
    "carousel": {"likes": (500, 1000), "shares": (200, 500), "comments": (100, 300), "views": (1000, 5000)},
    "reels": {"likes": (1000, 5000), "shares": (300, 1000), "comments": (500, 1500), "views": (5000, 20000)},
    "static_image": {"likes": (300, 700), "shares": (100, 300), "comments": (50, 150), "views": (500, 3000)},
    "video": {"likes": (700, 2000), "shares": (200, 700), "comments": (300, 800), "views": (2000, 10000)},
}

# Create a list to store generated data
data = []

# Generate 100 simulated posts
for _ in range(200):
    post_type = random.choice(list(post_types.keys()))
    metrics = post_types[post_type]
    
    # Generate random values for each metric
    post_data = {
        "Post_ID": faker.uuid4(),
        "Post_Type": post_type,
        "Likes": random.randint(*metrics["likes"]),
        "Shares": random.randint(*metrics["shares"]),
        "Comments": random.randint(*metrics["comments"]),
        "Views": random.randint(*metrics["views"]),
        "Post_Date": faker.date_between(start_date="-1y", end_date="today"),
    }
    data.append(post_data)

# Convert to a DataFrame
df = pd.DataFrame(data)

# Save to CSV or use directly
df.to_csv("social_media_engagement.csv", index=False)
print(df.head())
