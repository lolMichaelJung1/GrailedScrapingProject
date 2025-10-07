import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Load CSV
filename = "grailed_listings.csv"
df = pd.read_csv(filename)

#Convert price to numeric and drop invalid rows
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df = df.dropna(subset=["price"])
df = df[df["price"] > 0]

print(f"Analyzing {len(df)} valid listings from '{filename}'...\n")

#Function to print stats and generate plots for a subset
def analyze_subset(subset, label):
    print(f"--- {label} ---")
    stats = subset["price"].describe(percentiles=[0.25, 0.5, 0.75])
    print(stats)
    print(f"Mean price: ${subset['price'].mean():.2f}")
    print(f"Median price: ${subset['price'].median():.2f}")
    print(f"Standard deviation: ${subset['price'].std():.2f}\n")
    
    #Histogram
    plt.figure(figsize=(10,5))
    sns.histplot(subset["price"], bins=30, kde=True)
    plt.title(f"Price Distribution - {label}")
    plt.xlabel("Price (USD)")
    plt.ylabel("Number of Listings")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    #Boxplot by condition if available
    if "condition" in subset.columns and subset["condition"].notna().any():
        plt.figure(figsize=(10,5))
        sns.boxplot(x="condition", y="price", data=subset, palette="Set2")
        plt.title(f"Price by Condition - {label}")
        plt.xlabel("Condition")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

#Overall stats
analyze_subset(df, "All Listings")

#Stats by Brand
brands = df["brand"].unique()
for brand in brands:
    brand_df = df[df["brand"] == brand]
    analyze_subset(brand_df, f"Brand: {brand}")

#Stats by Brand + Category
for brand in brands:
    brand_df = df[df["brand"] == brand]
    categories = brand_df["category"].dropna().unique()
    for cat in categories:
        cat_df = brand_df[brand_df["category"] == cat]
        analyze_subset(cat_df, f"{brand} - {cat}")

#Stats by Brand + Category + Style
for brand in brands:
    brand_df = df[df["brand"] == brand]
    categories = brand_df["category"].dropna().unique()
    for cat in categories:
        cat_df = brand_df[brand_df["category"] == cat]
        styles = cat_df["style"].dropna().unique()
        for style in styles:
            style_df = cat_df[cat_df["style"] == style]
            analyze_subset(style_df, f"{brand} - {cat} - {style}")
