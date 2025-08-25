import pandas as pd
import pyarrow.parquet as pq
import os

def read_parquet_files(folder, primary_filter = None, primary_filter_id='geneId', secondary_filter=None, secondary_filter_id='studyLocusId',
                       tertiary_filter=None, tertiary_filter_id='isTransQtl'):
    filtered_data = []
    
    # Build the filters for PyArrow
    # The filter format is a list of tuples or a list of lists of tuples (for DNF).
    pyarrow_filters = []
    if primary_filter:
        pyarrow_filters.append((primary_filter_id, 'in', primary_filter))
    if secondary_filter:
        pyarrow_filters.append((secondary_filter_id, 'in', secondary_filter))
    if tertiary_filter:
        pyarrow_filters.append((tertiary_filter_id, 'in', tertiary_filter))
    # If no filters are provided, set filters to None
    if not pyarrow_filters:
        pyarrow_filters = None
        
    for file in os.listdir(folder):
        if file.endswith('.parquet'):
            print(f"Processing file: {file}")
            filepath = os.path.join(folder, file)
            try:
                # Use pq.read_table() directly with the filepath and filters
                table = pq.read_table(filepath, filters=pyarrow_filters)
                df = table.to_pandas()
                if not df.empty:
                    filtered_data.append(df)
            except Exception as e:
                print(f"Error processing {file}: {e}")
            # No need to manually delete objects; Python's garbage collector handles it.

    if not filtered_data:
        return pd.DataFrame()
    
    return pd.concat(filtered_data, ignore_index=True)
