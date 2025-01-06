import pandas as pd
import random
from faker import Faker

faker = Faker()


Post_Types = {
    "carousel": {"Likes": (500, 1000), "Shares": (200, 500), "Comments": (100, 300), "Views": (1000, 5000)},
    "reels": {"Likes": (1000, 5000), "Shares": (300, 1000), "Comments": (500, 1500), "Views": (5000, 20000)},
    "static_image": {"Likes": (300, 700), "Shares": (100, 300), "Comments": (50, 150), "Views": (500, 3000)},
    "video": {"Likes": (700, 2000), "Shares": (200, 700), "Comments": (300, 800), "Views": (2000, 10000)},
}

# Create a list to store generated data
data = []

# Generate 100 simulated posts
for _ in range(200):
    Post_Type = random.choice(list(Post_Types.keys()))
    metrics = Post_Types[Post_Type]
    
    # Generate random values for each metric
    post_data = {
        "Post_ID": faker.uuid4(),
        "Post_Type": Post_Type,
        "Likes": random.randint(*metrics["Likes"]),
        "Shares": random.randint(*metrics["Shares"]),
        "Comments": random.randint(*metrics["Comments"]),
        "Views": random.randint(*metrics["Views"]),
        "Post_Date": faker.date_between(start_date="-1y", end_date="today"),
    }
    data.append(post_data)

# Convert to a DataFrame
df = pd.DataFrame(data)

# Save to CSV or use directly
df.to_csv("social_media_engagement.csv", index=False)
print(df.head())
