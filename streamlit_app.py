import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title='IS 445 HW6: Illinois State Buildings', layout='centered')

url = 'https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/building_inventory.csv'


@st.cache_data
def load_data():
    df = pd.read_csv(url)
    # year 0 means missing so keep real years only
    df = df[df['Year Constructed'] >= 1800].copy()
    df['Decade'] = (df['Year Constructed'] // 10) * 10
    return df


df = load_data()

st.title('Illinois State Buildings')
st.write('Sujit Vellanki | IS 445 HW6')
st.write(
    'This app looks at the Illinois state building inventory. Each row is one building owned by a state agency. '
    'It has when the building was built, how big it is, what it is used for, and which agency owns it. '
    'I dropped rows where the construction year was 0 since that means the year is missing.'
)

# Plot 1
st.header('Plot 1: What the state built each decade')

agencies = ['All agencies'] + df['Agency Name'].value_counts().index.tolist()
agency = st.selectbox('Pick an agency', agencies)
df1 = df if agency == 'All agencies' else df[df['Agency Name'] == agency]

by_decade = df1.groupby(['Decade', 'Usage Description']).size().reset_index(name='Buildings')

pick = alt.selection_point(fields=['Usage Description'], bind='legend')

plot1 = alt.Chart(by_decade).mark_bar().encode(
    x=alt.X('Decade:O', title='Decade built'),
    y=alt.Y('Buildings:Q', title='Number of buildings'),
    color=alt.Color('Usage Description:N', title='Usage (click to highlight)', scale=alt.Scale(scheme='tableau20')),
    opacity=alt.condition(pick, alt.value(1), alt.value(0.15)),
    tooltip=['Decade', 'Usage Description', 'Buildings']
).add_params(pick).properties(height=400, title=f'Buildings built per decade: {agency}')

st.altair_chart(plot1, width='stretch')

st.write(
    'This plot shows how many buildings were built each decade and what they are used for. '
    'The main thing it highlights is the building boom that starts in the 1950s, peaks in the 1970s and stays high until the 2000s. '
    'The 2010s bar is small because the data only goes up to 2019. '
    'You can pick one agency from the dropdown to see its own history. For example Corrections builds a lot in the 1980s and 1990s '
    'while Natural Resources is mostly storage and "unusual" buildings like shelters. '
    'I used a stacked bar chart since decades are ordered groups and the stacks show the mix of usage types inside each decade. '
    'I put decades on an ordinal axis so every bar has the same width and the count on a linear axis starting at zero so bar heights are honest. '
    'Usage type is a category so I used a categorical color scheme with enough colors for all of them. '
    'Clicking a usage type in the legend fades out the others which makes one type easy to follow over time. '
    'If I had more time I would let you switch between counting buildings and adding up square footage '
    'and I would group the small usage types into an Other group so the colors are easier to tell apart.'
)

# Plot 2
st.header('Plot 2: Where the floor space is')

yr_min, yr_max = int(df['Year Constructed'].min()), int(df['Year Constructed'].max())
years = st.slider('Years built', yr_min, yr_max, (1900, yr_max))
top_n = st.slider('How many counties to show', 5, 25, 15)

df2 = df[df['Year Constructed'].between(years[0], years[1])]
by_county = df2.groupby(['County', 'Bldg Status'])['Square Footage'].sum().reset_index()
top = df2.groupby('County')['Square Footage'].sum().nlargest(top_n).index
by_county = by_county[by_county['County'].isin(top)]
by_county['Million sq ft'] = by_county['Square Footage'] / 1e6

plot2 = alt.Chart(by_county).mark_bar().encode(
    x=alt.X('sum(Million sq ft):Q', title='Total floor space (million sq ft)'),
    y=alt.Y('County:N', sort='-x', title='County'),
    color=alt.Color('Bldg Status:N', title='Status',
                    scale=alt.Scale(domain=['In Use', 'In Progress', 'Abandon'], range=['#4c78a8', '#f2a541', '#d62728'])),
    tooltip=['County', 'Bldg Status', alt.Tooltip('Million sq ft:Q', format='.2f')]
).properties(height=alt.Step(22), title=f'Top {top_n} counties by state floor space, built {years[0]} to {years[1]}')

st.altair_chart(plot2, width='stretch')

st.write(
    'This plot shows which counties hold the most state owned floor space. '
    'Cook and Champaign are at the top because of the big university campuses and state offices there. '
    'The year slider lets you pick which buildings count based on when they were built so you can see how the top counties change over time. '
    'The second slider sets how many counties to show. '
    'I used a horizontal bar chart because county names are long and are easier to read on the y axis. '
    'The bars are sorted from largest to smallest so the ranking is clear. '
    'I changed square feet to millions of square feet so the axis labels are short. '
    'The color shows building status. Blue is in use, orange is in progress, and red is abandoned so the red parts stand out as a warning. '
    'If I had more time I would turn this into a county map of Illinois and I would add a per person version so big counties do not always win.'
)

st.header('Overlap with Homework 5')
st.write(
    'There is no overlap with Homework 5. For Homework 5 I used the Bigfoot reports dataset. '
    'This app uses a different dataset (the Illinois building inventory) and both plots and all of the write up are new.'
)
