import os

from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
import streamlit as st  # Add Streamlit import


os.environ['OPENAI_API_KEY']=st.secrets('OPENAI_API_KEY')
# Set up SerpAPI (or Google Search Results) API key
os.environ["SERPER_API_KEY"] = st.secrets("SERPER_API_KEY")

os.environ["OPENAI_MODEL_NAME"]="gpt-4o-mini"

# Define the search tool
search_tool = SerperDevTool()

# Define the agents
researcher = Agent(
    role="Researcher",
    goal="Collect data on the given topic using search tools.",
    backstory="An expert in data collection and analysis, skilled at finding reliable sources using search engines.",
   
    memory=True,
    allow_delegation=True,
    tools=[search_tool]  # Enable search tools for this agent
)

analyst = Agent(
    role="Analyst",
    goal="Analyze the collected data to identify key insights.",
    backstory="A data scientist with expertise in statistical analysis and trend identification.",
    
    memory=True,
    allow_delegation=True,
    
)

writer = Agent(
    role="Writer",
    goal="Create a comprehensive report in Markdown format based on the analyzed data.",
    backstory="A skilled technical writer with experience in creating clear and concise reports.",
    
    memory=True,
    allow_delegation=False,
    
)

# Define the tasks
def create_tasks(topic):
    research_task = Task(
        description=f"Search and collect data on {topic} using search tools.",
        expected_output=f"A list of recent developments and insights on {topic}",
        agent=researcher,
        tools=[search_tool]
        
    )

    analysis_task = Task(
        description=f"Analyze the collected data on {topic} to identify key insights.",
        expected_output="A summary of key insights from the data",
        agent=analyst,
        tools=[search_tool],  # Ensure tools are provided if required
       
    )

    writing_task = Task(
        description=f"Write a detailed report of 5 paragraphs in Markdown format summarizing the insights on {topic}. Include emojis to make the report engaging.",
        expected_output="A comprehensive Markdown report",
        agent=writer,
        tools=[search_tool],  # Ensure tools are provided if required
        async_execution=False,
        output_file='Report.md' 
       
    )

    return [research_task, analysis_task, writing_task]

# Create the crew
def create_crew(topic):
    tasks = create_tasks(topic)
    return Crew(
        agents=[researcher, analyst, writer],
        tasks=tasks,
        
        memory=True,
        cache=True,
        max_rpm=100,
        share_crew=True
    )

# Run the crew
if __name__ == "__main__":
    # Set up Streamlit interface
    st.title("Research Assistant")  # Add title to the app
    st.write("""
        This app serves as a comprehensive Research Assistant, designed to help users collect, analyze, and report insights on various topics. 
        Simply enter a topic of interest, and the app will utilize advanced AI agents to gather data, analyze it, and generate a detailed report in Markdown format. 
        The report will be displayed directly in the app, making it easy to access and review your findings.
    """)  # Add description to the app
    topic = st.text_input("Enter the topic for research:")  # Input for topic

    if st.button("Start Research"):  # Button to start research
        if topic:  # Check if topic is provided
            # Create the crew
            research_crew = create_crew(topic)

            # Run the crew
            research_crew.kickoff()

            # Read and display the contents of Report.md
            if os.path.exists('Report.md'):
                with open('Report.md', 'r', encoding='utf-8') as file:
                    report_content = file.read()
                st.subheader("Research Report")  # Subheader for report
                st.write(report_content)  # Display the report content
                
                # Delete the Report.md file after displaying its content
                os.remove('Report.md')
            else:
                st.warning("Report.md not found.")  # Warning if the report file is not found
        else:
            st.warning("Please enter a topic.")  # Warning if no topic is entered

    