# NOTE: When using STREAMLIT, comments inside """ """ are rendered on the User Interface
# Which is why # is being used instead for multi-line comments here



#----------------------------------------------------------------------------------------
# 1) Import the necessary libraries for calculations and visualization.
# Plotly is used for creating interactive charts and can run even without Streamlit.
#----------------------------------------------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import csv
from PIL import Image
import plotly
import plotly.express as px
import plotly.graph_objects as go



#-----------------------------------------------------------------------------------------
# 2) VARIABLES: The following variables pertain to the file names, questions,
# options (and their corresponding scores for risk profiling), portfolio volatilities,
# and risk profile descriptions. You may change these variables as necessary
# without having to change the rest of the code.
#-----------------------------------------------------------------------------------------

## 2.1) NAMES: File names for CSV files of investment universe, risk profiles,
## asset weights for taxable and retirement accounts, portfolio returns,
## portfolio advanced statistics, photo of table for Question 7,
## as well as name of the robo-advisor and title of page
investment_universe = 'investment_universe.csv'
all_risk_profiles = 'risk_profiles.csv'
asset_weights_taxable = 'asset_weights_taxable.csv'
asset_weights_retirement = 'asset_weights_retirement.csv'
portfolio_returns_taxable = 'portfolio_returns_taxable.csv'
portfolio_returns_retirement = 'portfolio_returns_retirement.csv'
portfolio_advanced_statistics_taxable = 'portfolio_advanced_statistics_taxable.csv'
portfolio_advanced_statistics_retirement= 'portfolio_advanced_statistics_retirement.csv'
Q7_photo = 'Q7.png'
roboadvisor = 'Monero'	# change the name of roboadvisor here if necessary
page_title = f'{roboadvisor} Robo-Advisor by Portfolio Constructs, LLC' # title of page to be shown on browser tab

## 2.2) Question about investment value and setting of minimum investment value (in US Dollars)
minimum_investment = 500	# change the minimum investment value here if necessary
investment_value_text = f'How much would you like to invest (in US Dollars)? The amount must be at least USD {minimum_investment}.'

## 2.3) Question about investment account type
account_type_text = 'Select the type of account where your investment will be placed.'
account_type_options = ['Taxable Account', 'Retirement Account']

## 2.4) Risk profiling questions and options with corresponding scores

### 2.4.1) Risk Capacity (Investment Goal/Objective)
Q1_text = 'What is your primary goal for this investment?'
Q1_dict =   {
			'Generate income to cover ongoing expense':0,
			'Build an emergency fund':0,
			'Build your retirement fund':9,
			'Fund major expenditure in the future (business, education, house, etc.)':4,
			'Save for something special to reward yourself (car, vacation, wedding celebration, etc.)':9,
			'Build long-term wealth (provide an inheritance, future charitable giving, etc.)':14
			}
Q1_options = list(Q1_dict.keys())

### 2.4.2) Risk Capacity (Investment Time Horizon)
Q2_text = 'When do you plan to begin withdrawing money from this investment?'
Q2_dict = {'In less than 2 years':0, 'In 2-4 years':2, 'In 5-7 years':5, 'In 8-10 years':8, 'In more than 10 years':10}
Q2_options = list(Q2_dict.keys())

### 2.4.3) Risk Capacity (Liquid Net Worth)
Q3_text = 'What is the percentage of your liquid net worth to be used for this investment? Please refer to the notes below on how to determine your liquid net worth.'
Q3_caption_1 = '\* **Liquid Net Worth** = Cash + Other Investments* ‒ Total Liabilities'
Q3_caption_2 = '\* **Exclude** real estate or the value of businesses you own; "Other Investments" must be money that is **quickly accessible**'
Q3_dict = {'Less than 10%':6, 'Within 10% to 25%':5, 'Within 26% to 40%':2, 'Within 41% to 50%':1, 'More than 50%':0}
Q3_options = list(Q3_dict.keys())

### 2.4.4) Risk Capacity (Stability of Current and Future Income Sources)
Q4_text = 'Your current and future income sources (such as salary, own business, other investments, pension) are'
Q4_dict = {'Very unstable':0, 'Unstable':1, 'Stable':5, 'Very stable':6}
Q4_options = list(Q4_dict.keys())

### 2.4.5) Risk Tolerance (Investment Knowledge Level)
Q5_text = 'How knowledgeable are you about investments?'
Q5_dict =   {
			'Not Familiar: You have little or no knowledge of investments.':0,
			'Moderately Familiar: You have general awareness of the risks involved in investments.':6,
			'Very Familiar: With your extensive knowledge of investments, you are capable of recognizing different factors affecting investment performance and making your own investment decisions.':10
			}
Q5_options = list(Q5_dict.keys())

### 2.4.6) Risk Tolerance (Qualitative)
Q6_text = 'When investing your money, you are'
Q6_dict =   {
			'Always concerned about the potential losses of your investment':0,
			'Always considering the potential gains of your investment':10,
			'Equally thinking about the potential losses and the potential gains of your investment':6
			}
Q6_options = list(Q6_dict.keys())

### 2.4.7) Risk Tolerance (Quantitative)
Q7_text = 'The table below shows the possible best-case and worst-case annual returns of five hypothetical investment portfolios. Considering the information below, where would you invest your money?'
Q7_image = Image.open(Q7_photo)
Q7_dict = {'Investment Portfolio A':0, 'Investment Portfolio B':3, 'Investment Portfolio C':7, 'Investment Portfolio D':10, 'Investment Portfolio E':12}
Q7_options = list(Q7_dict.keys())

### 2.4.8) Risk Tolerance (Hypothetical Situation)
Q8_text = 'Suppose you own a stock investment that lost 25% of its value in three months. What would you do to this stock investment?'
Q8_dict = {'Sell all of your shares':0, 'Sell some of your shares':2, 'Do nothing':5, 'Buy more shares':8}
Q8_options = list(Q8_dict.keys())

## 2.5) Recommended portfolios and corresponding volatilities
volatilities_dict = {1:'6.0%', 2:'7.0%', 3:'8.0%', 4:'9.0%', 5:'10.0%', 6:'11.0%', 7:'12.0%', 8:'13.0%', 9:'14.0%', 10:'15.0%'}

## 2.6) Recommended portfolios and corresponding risk profile names
profiles_dict = {
				1:'Cash Sentinel', 2:'Asset Keeper', 3:'Guarded Explorer', 4:'Cautious Explorer', 5:'Prepared Explorer',
				6:'Trained Explorer', 7:'Active Explorer', 8:'Spirited Explorer', 9:'Adventurous Explorer', 10:'Fearless Explorer'
				}

## 2.7) Risk profile names and corresponding descriptions
descriptions_dict = {
					'Cash Sentinel':'You find peace in your comfort zone. You are a **safety-oriented** investor who values financial security. Your goal is the preservation of wealth above anything else.',
					'Asset Keeper':'You prefer traveling the status quo journey. You are a **conservative** investor whose priority is protecting your invested capital against potential losses as much as possible.',
					'Guarded Explorer':'You are wary of taking an unfamiliar path alone. You are a **moderately conservative** investor who likes stability, aiming to minimize fluctuations in investment value.',
					'Cautious Explorer':'You can trek an easy, well-maintained trail. You are a **passive** investor who prefers low-volatility assets whose potential gains are generally low but still a bit higher than regular savings accounts\'.', 
					'Prepared Explorer':'You are willing to go on a bit extended but guided trek. You are a **balanced** investor. You aim to strike a balance between financial security and capital gains as much as possible.',
					'Trained Explorer':'You are well-equipped to take moderate hikes. With a general awareness of investment markets, you are a **progressive** investor who recognizes investment risk and return trade-off.', 
					'Active Explorer':'You are capable of independent trekking. You are an **assertive** investor who is not afraid to take calculated risks to maximize the growth potential of your investment in the long run.',
					'Spirited Explorer':'You are comfortable to lead challenging trails. You are a **moderately aggressive** investor who seeks good investment growth despite a fair level of volatility that comes with it.',
					'Adventurous Explorer':'You are willing to cross complicated trails. You are an **aggressive** investor who is willing to accept high volatility of investment value for higher potential capital gains in the long run.',
					'Fearless Explorer':'You brave long, dangerous routes to reach breathtaking views. You are an **extremely aggressive** investor who bears high risk for high returns, thanks to your investment knowledge and experience.'
					}

## 2.8) Time frame options (in years) to months (as model uses monthly data) for cumulative returns
timeframe_dict = {'1 Year':12, '3 Years':36, '5 Years':60, '10 Years':120}
timeframe_options = list(timeframe_dict.keys())



#---------------------------------------------------------------------------------------------------------------
# 3) STREAMLIT: Set page title and layout. Set empty questionnaire and portfolio options (to be filled later).
# The empty elements are crucial to the flow; without them, STREAMLIT will result in an error.
# HTML code is a workaround to automatically scroll page to the top by default when a new element is loaded
# Source: https://discuss.streamlit.io/t/no-way-to-set-focus-at-top-of-screen-on-page-reload-really/15474/14
#---------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title=page_title, layout='wide')
questionnaire = st.empty()
portfolio_options = st.empty()

if "counter" not in st.session_state:
    st.session_state.counter = 1

components.html(
    f"""
        <p>{st.session_state.counter}</p>
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """,
    height=0
)



#----------------------------------------------------------------------------------------------------------------------
# 4) CALLBACK TO CALCULATE RISK PROFILES: This function will calculate the user's risk profiles based on answers to
# the Investor Profile Questionnaire. This will determine the 3 risk profiles that the user may choose from.
#----------------------------------------------------------------------------------------------------------------------

def calculate_risk_profiles():

	st.session_state.counter += 1	# for HTML code to refocus page to the top

	## 4.1) Declare the following as global variables because they will be used in other callbacks
	global risk_capacity
	global risk_tolerance
	global portfolio
	global portfolio_down
	global portfolio_up
	global profile
	global profile_down
	global profile_up
	global profile_desc
	global profile_down_desc
	global profile_up_desc
	global profile_plotly

	## 4.2) Check investment value: STREAMLIT numeric input widget automatically displays an error if investment value is less than minimum.
	## If the tool/platform to be used does not have such functionality, then insert code here to check minimum investment.
	
	#-------insert code here to validate the investment value if needed
	#-------if investment value is less than the minimum, then the user must be asked to revise input before scores can be calculated

	## 4.3) Check completeness of answers: If STREAMLIT allows disabling the default/pre-selected options for input widgets in the future,
	## there must be a code to check that the user has answered all the questions.
	
	#-------insert code here to check completeness of answers
	#-------if there are unanswered questions, then the user must be asked to complete the questionnaire before scores can be calculated
	
	## 4.4) Calculate risk capacity and risk tolerance: Map user's answers to corresponding scores and then add the scores
	risk_capacity = Q1_dict.get(Q1_answer) + Q2_dict.get(Q2_answer) + Q3_dict.get(Q3_answer) + Q4_dict.get(Q4_answer)
	risk_tolerance = Q5_dict.get(Q5_answer) + Q6_dict.get(Q6_answer) + Q7_dict.get(Q7_answer) + Q8_dict.get(Q8_answer)

	## 4.5) Load risk profiles from CSV file and create a multi-index dataframe (risk capacity and risk tolerance)
	risk_profiles = pd.DataFrame(pd.read_csv(all_risk_profiles)).set_index(['Risk_Capacity','Risk_Tolerance'])

	## 4.6) Index lookup for the 3 recommended portfolios based on risk capacity score and risk tolerance score
	portfolio = risk_profiles.at[(risk_capacity,risk_tolerance), 'Risk_Profile']
	portfolio_down = portfolio - 1
	portfolio_up = portfolio + 1

	## 4.7) Get risk profiles and descriptions corresponding to the 3 recommended portfolios
	profile = profiles_dict.get(portfolio)
	profile_down = profiles_dict.get(portfolio_down)
	profile_up = profiles_dict.get(portfolio_up)
	profile_desc = descriptions_dict.get(profile)
	profile_down_desc = descriptions_dict.get(profile_down)
	profile_up_desc = descriptions_dict.get(profile_up)	

	## 4.8) Create dataframe of representative points (close to maximum points) of risk capacity, risk tolerance per portfolio
	## Slice the dataframe to obtain only the data for 3 recommended risk profiles
	## Replace data for the most recommended risk profile with actual risk capacity and risk tolerance scores 
	data = [[1,'Cash Sentinel - Portfolio 1',4,14], [2,'Asset Keeper - Portfolio 2',9,18],
			[3,'Guarded Explorer - Portfolio 3',12,19], [4,'Cautious Explorer - Portfolio 4',16,24],
			[5,'Prepared Explorer - Portfolio 5',19,24], [6,'Trained Explorer - Portfolio 6',22,28],
			[7,'Active Explorer - Portfolio 7',25,30], [8,'Spirited Explorer - Portfolio 8',28,34],
			[9,'Adventurous Explorer - Portfolio 9',32,35], [10,'Fearless Explorer - Portfolio 10',34,38]]
	profiling_data = pd.DataFrame(data, columns=['Portfolio_Number', 'Portfolio', 'Risk Capacity', 'Risk Tolerance'])
	profiling_data['Size'] = len(profiling_data)*[30]	# this will be used as the dot size for better visibility in the scatter chart
	profiling_table = profiling_data[((profiling_data.Portfolio_Number==portfolio_down) |
									(profiling_data.Portfolio_Number==portfolio) |
									(profiling_data.Portfolio_Number==portfolio_up))]
	profiling_table.iloc[1,2] = risk_capacity 	# record the actual risk capacity score for the recommended portfolio
	profiling_table.iloc[1,3] = risk_tolerance 	# record the actual risk tolerance score for the recommended portfolio

	## 4.9) Create table of risk capacity and risk tolerance scores, along with recommended portfolio name for chart hover name and dot size
	## Use the created table as source data for Plotly scatter chart  
	profile_plotly = go.Figure(data=go.Scatter(x=profiling_table['Risk Capacity'], y=profiling_table['Risk Tolerance'],
												mode='markers',
												marker=dict(size=profiling_table['Size'],
															color=['#636EFA','#00CC96','#636EFA']),
												text=profiling_table['Portfolio'],
												hovertemplate='%{text} <br>Risk Capacity: %{x} <br>Risk Tolerance: %{y} <extra></extra>'
												)
								)
	profile_plotly.update_layout(title_text=f'Your Profile: {profile} - Portfolio {portfolio}',
								xaxis_title='Risk Capacity', yaxis_title='Risk Tolerance')
	profile_plotly.update_xaxes(range=[0.01, 38])  # maximum risk capacity score = 36, add 2 for some space allowance 
	profile_plotly.update_yaxes(range=[0.01, 43])  # maximum risk tolerance score = 40, add 3 for some space allowance
	profile_plotly.update_xaxes(showspikes=True)
	profile_plotly.update_yaxes(showspikes=True)



#----------------------------------------------------------------------------------------------------------
# 5) STREAMLIT Function to Show the Recommended Risk Profiles: This function will be called after the user
# has completed the Investor Profile Questionnaire.
#----------------------------------------------------------------------------------------------------------

def show_profiles():

	st.session_state.counter += 1	# for HTML code to refocus page to the top

	## 5.1) STREAMLIT: Inform the user about risk capacity and risk tolerance scores along with recommended portfolio.
	## Also, inform the user about the option to move one level down or up the recommended portfolio.

	with portfolio_options.container():

		st.title('Recommended Portfolio')

		# Call the function to calculate risk profiles
		calculate_risk_profiles()

		# If the user already has the most conservative portfolio, there will be only 2 portfolio options
		if portfolio_down < 1:
			col1, col2, col3 = st.columns([1.5,2,0.5])
			with col1:
				st.write('')
				st.write('')
				st.write('Thank you for answering the Investor Profile Questionnaire.')
				st.write(f'{roboadvisor} believes that you are **{profile}** best suited for **Portfolio {portfolio}**, based on your risk capacity score of {risk_capacity} and your risk tolerance score of {risk_tolerance}.')
				st.write('Your recommended portfolio already represents the most conservative point in the risk profile spectrum.')
				st.write(f'If you would like to have a somewhat more aggressive portfolio, please select **{profile_up} - Portfolio {portfolio_up}**.')
				st.write('You may refer to the scatter chart on the right for the relative positions of these risk profiles. You can also see the risk profile descriptions below.')
				st.write(f'Whenever you are ready, please let {roboadvisor} know of your selected portfolio via the confirmation box at the bottom of this page.')
			with col2:
				st.plotly_chart(profile_plotly, use_container_width=True)

		# If the user already has the most aggressive portfolio, there will be only 2 portfolio options
		elif portfolio_up > 10:
			col1, col2, col3 = st.columns([1.5,2,0.5])
			with col1:
				st.write('')
				st.write('')
				st.write('Thank you for answering the Investor Profile Questionnaire.')
				st.write(f'{roboadvisor} believes that you are **{profile}** best suited for **Portfolio {portfolio}**, based on your risk capacity score of {risk_capacity} and your risk tolerance score of {risk_tolerance}.')
				st.write('Your recommended portfolio already represents the most aggressive point in the risk profile spectrum.')
				st.write(f'If you would like to have a somewhat more conservative portfolio, please select **{profile_down} - Portfolio {portfolio_down}**.')	
				st.write('You may refer to the scatter chart on the right for the relative positions of these risk profiles. You can also see the risk profile descriptions below.')
				st.write(f'Whenever you are ready, please let {roboadvisor} know of your selected portfolio via the confirmation box at the bottom of this page.')
			with col2:
				st.plotly_chart(profile_plotly, use_container_width=True)

		else:
			col1, col2, col3 = st.columns([1.5,2,0.5])
			with col1:
				st.write('')
				st.write('')
				st.write('Thank you for answering the Investor Profile Questionnaire.')
				st.write(f'{roboadvisor} believes that you are **{profile}** best suited for **Portfolio {portfolio}**, based on your risk capacity score of {risk_capacity} and your risk tolerance score of {risk_tolerance}.')
				st.write(f'If you would like to have a somewhat more conservative portfolio, please select **{profile_down} - Portfolio {portfolio_down}**.')
				st.write(f'If you would like to have a somewhat more aggressive portfolio, please select **{profile_up} - Portfolio {portfolio_up}**.')
				st.write('You may refer to the scatter chart on the right for the relative positions of these risk profiles. You can also see the risk profile descriptions below.')
				st.write(f'Whenever you are ready, please let {roboadvisor} know of your selected portfolio via the confirmation box at the bottom of this page.')
			with col2:
				st.plotly_chart(profile_plotly, use_container_width=True)

		### 5.1.1) STREAMLIT: Use 3 columns to present the recommended risk profiles and their descriptions

		col1, col2, col3 = st.columns(3)

		with col1:
			if portfolio_down < 1:
				st.header('Your recommended portfolio is already the most conservative one.')
			else:
				st.header(profile_down)
				st.subheader(f'Portfolio {portfolio_down}')
				st.write(profile_down_desc)	
				
		with col2:
			st.header(profile)
			st.subheader(f'Portfolio {portfolio}')
			st.write(profile_desc)
						
		with col3:
			if portfolio_up > 10:
				st.header('Your recommended portfolio is already the most aggressive one.')
			else:
				st.header(profile_up)
				st.subheader(f'Portfolio {portfolio_up}')
				st.write(profile_up_desc)

		### 5.1.2) STREAMLIT: Create a form for portfolio selection. The default selected option (index) is the "RECOMMENDED" portfolio.
		
		st.write('')		
		form = st.form('Profiling')
		form.subheader('What is your preferred risk profile?')

		# If the user already has the most conservative portfolio, there will be only 2 portfolio options
		if portfolio_down < 1:
			user_portfolio = form.radio('Select one portfolio.',
										[f'{profile} - Portfolio {portfolio} (RECOMMENDED)',
										f'{profile_up} - Portfolio {portfolio_up} (Somewhat More Aggressive)'],
										index=0, key='portfolio_selection')

		# If the user already has the most aggressive portfolio, there will be only 2 portfolio options
		elif portfolio_up > 10:
			user_portfolio = form.radio('Select one portfolio.',
										[f'{profile_down} - Portfolio {portfolio_down} (Somewhat More Conservative)',
										f'{profile} - Portfolio {portfolio} (RECOMMENDED)'],
										index=1, key='portfolio_selection')

		else:
			user_portfolio = form.radio('Select one portfolio.',
										[f'{profile_down} - Portfolio {portfolio_down} (Somewhat More Conservative)',
										f'{profile} - Portfolio {portfolio} (RECOMMENDED)',
										f'{profile_up} - Portfolio {portfolio_up} (Somewhat More Aggressive)'],
										index=1, key='portfolio_selection')

		# After the user clicked "Confirm", the callback for showing portfolio details must be executed
		confirm = form.form_submit_button('Confirm', on_click=show_portfolio_details)

		# After the callback for showing portfolio details is referred to, hide the questionnaire and portfolio options
		if confirm:
			questionnaire.empty()
			portfolio_options.empty()	



#------------------------------------------------------------------------------------------------------------
# 6) CALLBACK TO SHOW DETAILS OF SELECTED PORTFOLIO: This function will be called after the user confirmed
# the selected portfolio.
#------------------------------------------------------------------------------------------------------------

def show_portfolio_details():

	st.session_state.counter += 1	# for HTML code to refocus page to the top

	## 6.1) Use the function to show the 3 portfolio options and set the session state for variables
	show_profiles()

	### 6.1.1) Store the user's selected portfolio
	st.session_state['user_portfolio']=st.session_state['portfolio_selection']

	### 6.1.2) Store the volatility corresponding to the user's selected portfolio

	if st.session_state['user_portfolio']==f'{profile_down} - Portfolio {portfolio_down} (Somewhat More Conservative)':
		volatility = volatilities_dict.get(portfolio_down)
	elif st.session_state['user_portfolio']==f'{profile} - Portfolio {portfolio} (RECOMMENDED)':
		volatility = volatilities_dict.get(portfolio)
	else:
		volatility = volatilities_dict.get(portfolio_up)

	### 6.1.3) Store the timeframe for cumulative returns line chart

	if 'user_timeframe' not in st.session_state:
		st.session_state['user_timeframe'] = '5 Years'						# default timeframe is 5 Years
	if st.session_state['user_timeframe']:
		st.session_state['timeframe']=st.session_state['user_timeframe']	# override the default with the user's selected timeframe
 
	## 6.2) ASSET WEIGHTS: Load asset weights depending on account type.
	## Select row for volatility corresponding to user's selected portfolio, drop zero weights, and sort in descending order

	if account_type=='Taxable Account':
		df_weights = pd.read_csv(asset_weights_taxable, index_col=0)	
	else:
		df_weights = pd.read_csv(asset_weights_retirement, index_col=0)
	
	df_weights = df_weights.loc[[volatility]]
	df_weights = df_weights.loc[:,(df_weights!=0).any(axis=0)]
	df_weights.sort_values(volatility, axis=1, ascending=False, inplace=True)	

	### 6.2.1) Create asset weights table and insert columns for calculated investment value per ETF, ETF name, ETF ticker, and Expense Ratio	

	weights_table = df_weights.copy().T
	weights_table.rename(columns={volatility:'ETF Weight'}, inplace=True)
	weights_table.insert(len(weights_table.columns),
						'Investment Value (in US Dollars)',
						weights_table['ETF Weight']*investment_value,
						allow_duplicates=True)
	asset_details = pd.read_csv(investment_universe, index_col=0)
	weights_table = pd.merge(pd.DataFrame(asset_details), pd.DataFrame(weights_table), how='right', left_index=True, right_index=True)
	weights_table['Expense Ratio'] = pd.to_numeric(weights_table['Expense Ratio'].str.replace('%', ''))/100
	weights_table['No. of Shares'] = len(weights_table)*[0]
	weights_table = weights_table.reset_index().rename(columns={'index': 'Asset Class'})

	## 6.3) PORTFOLIO CUMULATIVE RETURNS: Load portfolio returns depending on account type.
	## Select column for volatility corresponding to user's selected portfolio

	if account_type=='Taxable Account':	
		df_returns = pd.read_csv(portfolio_returns_taxable, index_col=0)
	else:
		df_returns = pd.read_csv(portfolio_returns_retirement, index_col=0)
	
	df_returns = df_returns[[volatility]]
	df_returns.rename(columns={volatility:'Portfolio Returns'}, inplace=True)

	## 6.4) PORTFOLIO ADVANCED STATISTICS: Load portfolio advanced statistics based on selected portfolio and account type.
	## Delect row for volatility corresponding to user's selected portfolio and convert percent to decimal.
	
	selected_portfolio = list(volatilities_dict.keys())[list(volatilities_dict.values()).index(volatility)]
	selected_profile = profiles_dict.get(selected_portfolio)

	if account_type=='Taxable Account':
		df_advanced_stats = pd.read_csv(portfolio_advanced_statistics_taxable, index_col=0)
		
	else:
		df_advanced_stats = pd.read_csv(portfolio_advanced_statistics_retirement, index_col=0)

	df_advanced_stats = df_advanced_stats.loc[[volatility]]
	df_advanced_stats['Alpha'] = df_advanced_stats['Alpha']/100
	df_advanced_stats['Historical Volatility'] = df_advanced_stats['Historical Volatility']/100
	df_advanced_stats['Historical Return'] = df_advanced_stats['Historical Return']/100
	df_advanced_stats['Expected Return(CAPM)'] = df_advanced_stats['Expected Return(CAPM)']/100
	df_advanced_stats['MDD'] = df_advanced_stats['MDD']/100
	wave_expense_ratio = np.dot(weights_table['Expense Ratio'],weights_table['ETF Weight'])		# portfolio's weighted average expense ratio
	df_advanced_stats.insert(2, 'Weighted Average Expense Ratio', wave_expense_ratio)
	df_advanced_stats.index.names = ['Portfolio']
	df_advanced_stats.rename(index={df_advanced_stats.index[0]: selected_profile}, inplace=True)
		
	## 6.5) STREAMLIT: Charts and tables for portfolio details to be displayed

	stats = st.empty()

	with stats.container():

		st.subheader('')
		st.title(f'About {selected_profile} (Portfolio {selected_portfolio})')

		col1, col2 = st.columns(2)
		
		### 6.5.1) STREAMLIT: First column contains Plotly horizontal bar chart showing investment value allocated per asset
		### and table showing portfolio details (ETF weight, name, ticker, and investment value)

		with col1:		

			st.subheader('Portfolio Composition')
			st.write(f'Portfolio Target Volatility: {volatility}')
			df_investment = df_weights.copy().T*investment_value
			df_investment.rename(columns={volatility:'Investment Value (in USD)'}, inplace=True)
			df_investment.index.names=['Asset Class']
			allocation_plotly = go.Figure(data=[go.Pie(labels=df_investment.index, values=df_investment['Investment Value (in USD)'], hole=.5,
										hovertemplate='%{label} <br>Allocation Weight: %{percent:.2%} <br>Allocated Value (in USD): %{value:$,.2f} <extra></extra>')])
			allocation_plotly.update_layout(title_text=f'Portfolio Allocation with Total Investment Value of USD {"{:,.0f}".format(investment_value)}')
			allocation_plotly.update_traces(textinfo='none')
			st.plotly_chart(allocation_plotly, use_container_width=True)

			color_even_rows = 'whitesmoke'
			color_odd_rows = 'white'
			details_plotly = go.Figure(
										data=[go.Table(
														columnwidth=[3.3,3,1.3,1.8,1.4,2.3,1.3],
														header=dict(
																	values=list(f'<b>{x}<b>' for x in weights_table.columns),
																	line_color='white',
																	fill_color='cornflowerblue',
																	align='center',
																	font=dict(color='white', size=16)),
														cells=dict(
																	values=[weights_table.iloc[:,x] for x in range(len(weights_table.columns))],
																	line_color='white',
																	fill_color=[[color_odd_rows,color_even_rows]*len(weights_table)],
																	align=['left','left','left','right','right','right'],
																	font_size=16,
																	format=['','','','.2%','.2%','$,.2f','.0f'])
													   )
										 ])
			details_plotly.update_layout(margin=dict(l=30, r=30, b=0, t=0))

			def get_table_height(df, header_height=85, row_height=54,
								char_limit_a=27, char_limit_b=40, char_limit_c=48,
								height_padding_a=27, height_padding_b=54, height_padding_c=81):		
				
				# Currently, Plotly Table does not have a functionality for dataframes with dynamic data.
				# This is a workaround. Default values must be changed if font size and margins are changed (trial and error).  
				# Explanation of args:
					# df: The dataframe with only the columns you want to plot
					# header_height: The height of the table header only (without any rows)
					# row_height: The height that one row requires
					# char_limit_a: If the length of a value crosses this limit, the row's height needs to be expanded to fit the value
					# char_limit_b: If the length of a value crosses this limit, the row's height needs to be further expanded
					# char_limit_c: If the length of a value crosses this limit, the row's height needs to be further expanded
					# height_padding_a: Extra height in a row when a length of value exceeds char_limit_a
					# height_padding_b: Extra height in a row when a length of value exceeds char_limit_b
					# height_padding_c: Extra height in a row when a length of value exceeds char_limit_c
				
				total_height = 0 + header_height
				for x in range(len(df)):
					total_height += row_height				# default row height: for ETF Names wrapped in 2 lines
					if len(str(df.iloc[x,1])) > char_limit_a and len(str(df.iloc[x,1])) < char_limit_b:
						total_height += height_padding_a	# for ETF Names wrapped in 3 lines 
					elif len(str(df.iloc[x,1])) > char_limit_b and len(str(df.iloc[x,1])) < char_limit_c:
						total_height += height_padding_b	# for ETF Names wrapped in 4 lines 
					elif len(str(df.iloc[x,1])) > char_limit_c:
						total_height += height_padding_c	# for ETF Names wrapped in 5 lines 
				return total_height
			
			details_plotly.update_layout(height=get_table_height(weights_table))
			st.plotly_chart(details_plotly, use_container_width=True)

		### 6.5.2) STREAMLIT: Second column contains Plotly line chart showing investment value hypothetical growth based on cumulative returns
		### according to the time frame selected by the user and Plotly vertical bar chart for portfolio returns across different time frames.

		with col2:

			st.subheader('Portfolio Performance')

			timeframe = st.selectbox('Select time frame.', timeframe_options, on_change=show_portfolio_details, key='user_timeframe')
			selected_timeframe = timeframe_dict.get(timeframe)
			df_returns_subset = df_returns.copy().tail(selected_timeframe)
			df_cumulative_returns = (1 + df_returns_subset).cumprod()
			df_cumulative_returns.rename(columns={'Portfolio Returns':'Portfolio Cumulative Returns'}, inplace=True)
			df_cumulative_returns.insert(len(df_cumulative_returns.columns), 'Investment Value (in US Dollars)',
										df_cumulative_returns['Portfolio Cumulative Returns']*investment_value, allow_duplicates=True)
			df_cumulative_returns.index.names = ['Month']
			current_value = df_cumulative_returns['Investment Value (in US Dollars)'].iloc[-1]
			current_month = pd.to_datetime(df_cumulative_returns.index[-1]).strftime('%B %d, %Y')
			
			returns_table = pd.DataFrame([[1,1,1,1]], columns=list(timeframe_dict.keys()))		# just to initialize dataframe
			months = list(timeframe_dict.values())
			for i in range(len(months)):
				returns_table.iloc[0,i] = ((1 + df_returns.copy().tail(months[i])).cumprod().tail(1))-1		# calculate portfolio return across horizons
			returns_table.rename(index={returns_table.index[0]: f'Portfolio Return as of {current_month}'}, inplace=True)
			
			cumulative_returns_plotly = px.line(df_cumulative_returns, x=df_cumulative_returns.index, y=df_cumulative_returns['Investment Value (in US Dollars)'],
												title=f'Hypothetical Growth of USD {"{:,.0f}".format(investment_value)} for the Past {timeframe}',
												hover_data={'Investment Value (in US Dollars)':':$,.2f'})
			st.plotly_chart(cumulative_returns_plotly, use_container_width=True)
			st.write(f'If **USD {"{:,.0f}".format(investment_value)}** had been invested in this portfolio **{timeframe} Ago**, then the portfolio value would have been approximately **USD {"{:,.0f}".format(current_value)} as of {current_month}**.')
			st.write('')
			st.write('')
			st.write('')
			st.write(f'The chart below shows the portfolio performance across different investment horizons.')

			returns_plotly = go.Figure(data=[go.Bar(x=returns_table.columns, y=[returns_table.iloc[0,x] for x in range(len(returns_table.columns))],
													hovertemplate='Investment Horizon: %{x} <br>Portfolio Return: %{y} <extra></extra>')])
			returns_plotly.update_layout(title_text=f'Portfolio Return as of {current_month}',
										xaxis_title='Investment Horizon', yaxis_title='Portfolio Return')
			returns_plotly.update_yaxes(tickformat='.0%')
			returns_plotly.update_yaxes(hoverformat='.2%')
			st.plotly_chart(returns_plotly, use_container_width=True)

		### 6.5.3) STREAMLIT: Toggle for showing portfolio advanced statistics

		with st.expander('Show More Details', expanded=False):
		
			st.subheader('Other Portfolio Statistics')
			st.write(f'Portfolio Target Volatility: {volatility}')
			
			col1, col2 = st.columns([2,1])
			 
			with col1:
				fig1 = px.bar(df_advanced_stats, x=['Historical Volatility','Expected Return(CAPM)','Historical Return'], y=df_advanced_stats.index,
								orientation='h', barmode='group', title='Portfolio Volatility and Return',
				 				color_discrete_sequence=['#EF553B','#636EFA','#00CC96'])
				fig1.update_xaxes(tickformat='.0%')
				fig1.update_xaxes(hoverformat='.2%')
				st.plotly_chart(fig1, use_container_width=True)

			with col2:
				fig2 = px.bar(df_advanced_stats, x=df_advanced_stats.index, y=['Sharpe Ratio','MDD'], title='Portfolio Sharpe Ratio and Maximum Drawdown')
				fig2.update_yaxes(hoverformat='.4f')
				st.plotly_chart(fig2, use_container_width=True)

			stats_plotly = go.Figure(
									data=[go.Table(
													header=dict(
																values=list(f'<b>{x}<b>' for x in df_advanced_stats.columns),
																line_color='white',
																fill_color='cornflowerblue',
																align='center',
																font=dict(color='white', size=16)),
													cells=dict(
																values=[df_advanced_stats.iloc[:,x] for x in range(len(df_advanced_stats.columns))],
																line_color='white',
																fill_color='white',
																align='center',
																font_size=16,
																format=['.4f','.4f','.2%','.2%','.2%','.2%','.4f','.4f'])
													)
									])
			stats_plotly.update_layout(margin=dict(l=30, r=30, b=0, t=0))
			st.plotly_chart(stats_plotly, use_container_width=True)

	# After the portfolio details are shown, hide the portfolio options
	portfolio_options.empty()

	# This must be the last stage of the robo-advisor
	# Calling this STREAMLIT function will prevent the questionnaire and recommended portfolios from reappearing
	st.stop()



#-----------------------------------------------------------------
# 7) STREAMLIT: Create form for Investor Profile Questionnaire
#-----------------------------------------------------------------

with questionnaire.container():

	## 7.1) STREAMLIT: Page title and description along with form title
	st.title(f'{roboadvisor}')
	st.subheader(f"{roboadvisor} is here to help you by suggesting a long-term investment portfolio that's just right for you.")
	st.subheader("Let's start by building your risk profile. Please accomplish the following Investor Profile Questionnaire.")
	st.subheader('')
	form = st.form('IPQ')
	form.title('Investor Profile Questionnaire')

	## 7.2) STREAMLIT: Questions and input widgets (radio buttons) for options

	form.text('')
	form.text('')
	form.subheader(investment_value_text)
	investment_value = form.number_input('Enter the investment value as a number (without any letters or symbols).',
										min_value=minimum_investment, key='value')

	form.text('')
	form.text('')
	form.subheader(account_type_text)
	account_type = form.radio('Select one answer.', account_type_options, key='type')

	form.text('')
	form.text('')
	form.subheader(Q1_text)
	Q1_answer = form.radio('Select one answer.', Q1_options, key='Q1')

	form.text('')
	form.text('')
	form.subheader(Q2_text)
	Q2_answer = form.radio('Select one answer.', Q2_options, key='Q2')

	form.text('')
	form.text('')
	form.subheader(Q3_text)
	form.caption(Q3_caption_1)
	form.caption(Q3_caption_2)
	Q3_answer = form.radio('Select one answer.', Q3_options, key='Q3')

	form.text('')
	form.text('')
	form.subheader(Q4_text)
	Q4_answer = form.radio('Select one answer.', Q4_options, key='Q4')

	form.text('')
	form.text('')
	form.subheader(Q5_text)
	Q5_answer = form.radio('Select one answer.', Q5_options, key='Q5')

	form.text('')
	form.text('')
	form.subheader(Q6_text)
	Q6_answer = form.radio('Select one answer.', Q6_options, key='Q6')

	form.text('')
	form.text('')
	form.subheader(Q7_text)
	Q7_answer = form.radio('Select one answer.', Q7_options, key='Q7')
	form.image(Q7_image)

	form.text('')
	form.text('')
	form.subheader(Q8_text)
	Q8_answer = form.radio('Select one answer.', Q8_options, key='Q8')

	## 7.3) STREAMLIT: Form submit button to record the user's answers
	## After the user clicked "Submit", the callback for calculating risk profiles will be executed
	form.title('')
	col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = form.columns(11)	# workaround to align the Submit button in the center
	submit = col6.form_submit_button('Submit', on_click=calculate_risk_profiles)
	if submit:
		questionnaire.empty()	# After the callback for calculating risk profiles is referred to, hide the questionnaire
		show_profiles()			# After hiding the questionnaire, show the recommended risk profiles