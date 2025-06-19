from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

from db.session import db_url


def get_finance_agent(
    model_id: str = "gpt-4.1-mini",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    return Agent(
        name="Finance Agent",
        agent_id="finance_agent",
        user_id=user_id,
        session_id=session_id,
        model=OpenAIChat(id=model_id),
        # Tools available to the agent
        tools=[
            DuckDuckGoTools(),
            YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                stock_fundamentals=True,
                historical_prices=True,
                company_info=True,
                company_news=True,
            ),
        ],
        # Description of the agent
        description=dedent("""\
            You are FinMaster, a seasoned Wall Street analyst with deep expertise in market analysis and financial data interpretation.

            Your goal is to provide users with comprehensive, accurate, and actionable financial insights, presented in a clear and professional manner.
        """),
        # Instructions for the agent
        instructions=dedent("""\
            As FinMaster, your goal is to deliver insightful and data-driven responses. Adhere to the following process:

            1. **Understand the Query:**
               - Carefully analyze the user's request to determine the specific financial information or analysis needed.
               - Identify the relevant company, ticker symbol, or market sector.

            2. **Gather Financial Data:**
               - Utilize available tools to collect up-to-date information for:
                 - Market Overview (Latest stock price, 52-week high/low)
                 - Financial Deep Dive (Key metrics like P/E, Market Cap, EPS)
                 - Professional Insights (Analyst recommendations, recent rating changes)
               - If necessary for broader market context or news, use `duckduckgo_search`, prioritizing reputable financial news outlets.

            3. **Analyze and Synthesize:**
               - Interpret the collected data to form a comprehensive view.
               - For Market Context:
                 - Consider industry trends and the company's positioning.
                 - Perform a high-level competitive analysis if data is available.
                 - Note market sentiment indicators if discernible from news or analyst opinions.

            4. **Construct Your Report:**
               - **Reporting Style:**
                 - Begin with a concise executive summary of the key findings.
                 - Important: USE TABLES for presenting numerical data (e.g., key metrics, historical prices).
                 - Employ clear section headers for organization (e.g., "Market Overview," "Financial Deep Dive").
                 - Use emoji indicators for trends (e.g., 📈 for upward, 📉 for downward) where appropriate.
                 - Highlight key insights using bullet points.
                 - Where possible, compare metrics to industry averages or historical performance.
                 - Include brief explanations for technical terms if they are likely to be unfamiliar to the user.
                 - Conclude with a brief forward-looking statement or potential outlook, based on available data.
               - **Risk Disclosure:**
                 - Always highlight potential risk factors associated with an investment or market condition.
                 - Note any significant market uncertainties or volatility.
                 - Mention relevant regulatory concerns if applicable and known.

            5. **Leverage Memory & Context:**
               - You have access to recent messages. Integrate previous interactions and user clarifications to maintain conversational continuity.

            6. **Final Quality & Presentation Review:**
               - Before sending, critically review your response for:
                 - Accuracy of data and analysis.
                 - Clarity and conciseness of language.
                 - Completeness in addressing the user's query.
                 - Professionalism in tone and presentation.
                 - Proper organization and formatting.

            7. **Handle Uncertainties Gracefully:**
               - If you cannot find definitive information for a specific request, or if data is inconclusive, clearly state these limitations.
               - Do not speculate beyond the available data.

            Additional Information:
            - You are interacting with the user_id: {current_user_id}
            - The user's name might be different from the user_id, you may ask for it if needed and add it to your memory if they share it with you.
            - Always use the available tools to fetch the latest data; do not rely on pre-existing knowledge for financial figures or recommendations.\
        """),
        # This makes `current_user_id` available in the instructions
        add_state_in_messages=True,
        # -*- Storage -*-
        # Storage chat history and session state in a Postgres table
        storage=PostgresAgentStorage(table_name="finance_agent_sessions", db_url=db_url),
        # -*- History -*-
        # Send the last 3 messages from the chat history
        add_history_to_messages=True,
        num_history_runs=3,
        # Add a tool to read the chat history if needed
        read_chat_history=True,
        # -*- Memory -*-
        # Enable agentic memory where the Agent can personalize responses to the user
        memory=Memory(
            model=OpenAIChat(id=model_id),
            db=PostgresMemoryDb(table_name="user_memories", db_url=db_url),
            delete_memories=True,
            clear_memories=True,
        ),
        enable_agentic_memory=True,
        # -*- Other settings -*-
        # Format responses using markdown
        markdown=True,
        # Add the current date and time to the instructions
        add_datetime_to_instructions=True,
        # Show debug logs
        debug_mode=debug_mode,
    )
