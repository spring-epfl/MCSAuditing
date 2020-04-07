"""
"""

def compute_prior_x(locations):
    """Compute the probability of a user being at a certain location."""

    df['Latitude'] = df['Latitude'].apply(lambda x: round(x, 3))
    df['Longitude'] = df['Longitude'].apply(lambda x: round(x, 3))
    dfprob = df.groupby(['Latitude', 'Longitude']).size().reset_index().rename(columns={0: 'PriorX'})
    dfprob['PriorX'] = dfprob['PriorX'] / dfprob['PriorX'].sum()
    dfprob = dfprob.drop_duplicates()

    return dfprob