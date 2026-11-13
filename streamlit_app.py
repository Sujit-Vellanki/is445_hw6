import pandas as pd
import altair as alt
import streamlit as st

url = 'https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/building_inventory.csv'
df = pd.read_csv(url)

# a year of 0 means the year is missing
df = df[df['Year Constructed'] > 0]
df['Decade'] = df['Year Constructed'] // 10 * 10

st.title('Illinois State Buildings')
st.write('Sujit Vellanki | IS 445 Homework 6')
st.write(
    'This app uses the Illinois building inventory dataset. Each row is a building owned by the State of Illinois. '
    'It lists the agency that owns it, the county it is in, the year it was built, its square footage, '
    'its status and what it is used for. I removed buildings with a construction year of 0 because that means the year is missing.'
)

# Plot 1
st.header('Plot 1: Buildings Built Each Decade')

agency = st.selectbox('Choose an agency', ['All agencies'] + sorted(df['Agency Name'].unique()))
if agency == 'All agencies':
    df1 = df
else:
    df1 = df[df['Agency Name'] == agency]

decades = df1.groupby(['Decade', 'Usage Description']).size().reset_index(name='Buildings')

legend_click = alt.selection_point(fields=['Usage Description'], bind='legend')

plot1 = alt.Chart(decades).mark_bar().encode(
    x=alt.X('Decade:O', title='Decade Built'),
    y=alt.Y('Buildings:Q', title='Number of Buildings'),
    color=alt.Color('Usage Description:N', title='Usage Type', scale=alt.Scale(scheme='tableau20')),
    opacity=alt.condition(legend_click, alt.value(1), alt.value(0.2)),
    tooltip=['Decade', 'Usage Description', 'Buildings']
).add_params(legend_click).properties(title='Buildings Built per Decade: ' + agency, height=400)

st.altair_chart(plot1, width='stretch')

st.write(
    'This plot shows how many state buildings were built in each decade and what they are used for. '
    'The main feature I wanted to highlight is the building boom that starts in the 1950s, peaks in the 1970s '
    'and stays high until the 2000s. The 2010s bar is small because the data only goes up to 2019. '
    'The dropdown lets you look at one agency at a time. For example, the Department of Corrections built the most in the 1980s, '
    'and the Department of Natural Resources mostly has storage and "Unusual" buildings. '
    'You can also click a usage type in the legend to highlight it and fade out the others. '
    'For the design, I used a stacked bar chart because decades are ordered groups and the stacks show the mix of usage types in each decade. '
    'The decades are on an ordinal axis so every bar is the same width, and the count axis starts at zero so the bar heights are not misleading. '
    'Usage type is a categorical variable, so I used the tableau20 color scheme since it has enough distinct colors for all 13 types. '
    'If I had more time, I would add an option to show total square footage instead of the building count, '
    'and I would combine the small usage types into an "Other" group so the colors are easier to tell apart.'
)

# Plot 2
st.header('Plot 2: State Floor Space by County')

years = st.slider('Select the years the buildings were built', 1750, 2019, (1900, 2019))

df2 = df[(df['Year Constructed'] >= years[0]) & (df['Year Constructed'] <= years[1])]
top15 = df2.groupby('County')['Square Footage'].sum().nlargest(15).index
df2 = df2[df2['County'].isin(top15)]
counties = df2.groupby(['County', 'Bldg Status'])['Square Footage'].sum().reset_index()
counties['Million Sq Ft'] = counties['Square Footage'] / 1000000

plot2 = alt.Chart(counties).mark_bar().encode(
    x=alt.X('sum(Million Sq Ft):Q', title='Total Floor Space (million sq ft)'),
    y=alt.Y('County:N', sort='-x', title='County', axis=alt.Axis(labelOverlap=False)),
    color=alt.Color('Bldg Status:N', title='Building Status',
                    scale=alt.Scale(domain=['In Use', 'In Progress', 'Abandon'], range=['#4c78a8', '#f2a541', '#d62728'])),
    tooltip=['County', 'Bldg Status', alt.Tooltip('Million Sq Ft:Q', format='.2f')]
).properties(title=f'Top 15 Counties by State Floor Space (Built {years[0]} to {years[1]})', height=500)

st.altair_chart(plot2, width='stretch')

st.write(
    'This plot shows the 15 counties with the most state owned floor space. '
    'The main feature I wanted to highlight is that Cook and Champaign are far ahead of every other county. '
    'Most of that space belongs to the University of Illinois campuses in Chicago and Champaign. '
    'Sangamon is third because Springfield is the state capital and has a lot of state offices. '
    'The slider lets you choose which buildings are counted based on the year they were built, '
    'so you can see how the top counties change when you only look at older or newer buildings. '
    'For the design, I used a horizontal bar chart because the county names are easier to read on the y axis. '
    'I sorted the bars from largest to smallest so the ranking is clear, and I converted square feet to millions of square feet '
    'so the axis labels stay short. The color shows building status. I used blue for in use, orange for in progress '
    'and red for abandoned so the abandoned buildings stand out. '
    'If I had more time, I would make this a county map of Illinois, '
    'and I would add an option to adjust for county population so large counties do not always come out on top.'
)

st.header('Overlap with Homework 5')
st.write(
    'There is no overlap between this homework and Homework 5. For Homework 5, I used the Bigfoot reports dataset. '
    'For this homework, I used the Illinois building inventory dataset, which is a different source. '
    'Plot 1 and Plot 2 are both new plots, and none of the write up is reused from Homework 5.'
)
