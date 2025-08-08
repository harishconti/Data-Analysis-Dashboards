import polars as pl

# 1. Create a DataFrame
data = {
    'city': ['Bengaluru', 'Mumbai', 'Bengaluru', 'Delhi', 'Mumbai'],
    'temperature': [28, 31, 29, 34, 32],
    'rainfall_mm': [120, 250, 150, 80, 280]
}
df = pl.DataFrame(data)

# 2. Build a lazy query using the Expression API
lazy_query = (
    df.lazy()  # Start lazy execution mode
    .filter(pl.col('rainfall_mm') > 100)  # Filter rows based on a condition
    .with_columns(
        # Create a new column
        (pl.col('temperature') * 9/5 + 32).alias('temp_fahrenheit')
    )
    .select([
        # Select and reorder columns
        pl.col('city'),
        pl.col('temp_fahrenheit')
    ])
)

# 3. Execute the optimized query plan
result = lazy_query.collect()

print(result)