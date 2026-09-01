import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv('C:/HopeAI/Master Program in Applied AI, GenAI and Data Science/08. MCP Week20/Practice/sqlite_mcp_langchain_gemini/.env')
print ("Environment variables loaded from .env file")

'''api_key = os.getenv("GOOGLE_API_KEY")
print("API key loaded:", bool(api_key))
print("API key loaded:", api_key)
print("API key length:", len(api_key) if api_key else 0)
model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=api_key
)'''

# Initialize model and server parameters
model = ChatGoogleGenerativeAI(model="gemini-3.6-flash", api_key=os.environ["GOOGLE_API_KEY"])

server_params = StdioServerParameters(
    command="uv",
    args=[
        "--directory", 
        "C:/HopeAI/Master Program in Applied AI, GenAI and Data Science/08. MCP Week20/Practice/servers/servers-archived/src/sqlite",
        "run", 
        "mcp-server-sqlite",
        "--db-path",
        "C:/HopeAI/Master Program in Applied AI, GenAI and Data Science/08. MCP Week20/Practice/sqlite_mcp_langchain_gemini/database.db",
    ],
)

async def process_query(agent, query):
    response = await agent.ainvoke({"messages": query})
    content = response["messages"][-1].content

    if isinstance(content, list):
        return "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return content

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_agent(model, tools)
            
            print("SQLite Database Assistant (type 'exit' to quit)")
            
            while True:
                query = input("\nEnter your query: ").strip()
                if query.lower() == 'exit':
                    break
                if not query:
                    continue
                    
                print("\nProcessing...\n")
                response = await process_query(agent, query)
                print(f"\nAnswer: {response}")

if __name__ == "__main__":
    asyncio.run(main())