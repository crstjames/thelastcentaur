"""
THE LAST CENTAUR - Agent Implementation
Version: 1.0.0

This module implements the agent workflow as specified in agent_design.txt.
The agent handles user input, generates search queries, performs parallel searches,
aggregates data, analyzes results, and generates structured output.
"""

import os
import json
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from termcolor import colored
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

# Define constants for models
GPT4O_MINI = "gpt-4o-mini"
GPT4O = "gpt-4o"
CLAUDE_SONNET = "claude-3-5-sonnet-latest"
GEMINI_FLASH = "google/gemini-flash-1.5-8b"
LLAMA_SONAR = "llama-3.1-sonar-large-128k-online"

# Define file paths
RESULTS_DIR = "results"
SEARCH_RESULTS_FILE = os.path.join(RESULTS_DIR, "search_results.json")
ANALYSIS_OUTPUT_FILE = os.path.join(RESULTS_DIR, "analysis_output.json")
CONVERSATION_HISTORY_FILE = os.path.join(RESULTS_DIR, "conversation_history.json")

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

class Agent:
    """
    Agent class that implements the workflow specified in agent_design.txt.
    """
    
    def __init__(self):
        """Initialize the agent with API clients and context."""
        # Initialize API clients
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.perplexity_client = AsyncOpenAI(
            base_url="https://api.perplexity.ai",
            api_key=os.getenv("PERPLEXITY_API_KEY")
        )
        self.openrouter_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        # Initialize conversation context
        self.conversation_history = []
        self.load_conversation_history()
    
    def load_conversation_history(self) -> None:
        """Load conversation history from file if it exists."""
        try:
            if os.path.exists(CONVERSATION_HISTORY_FILE):
                with open(CONVERSATION_HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
                print(colored("Loaded conversation history.", "green"))
        except Exception as e:
            print(colored(f"Error loading conversation history: {e}", "red"))
            self.conversation_history = []
    
    def save_conversation_history(self) -> None:
        """Save conversation history to file."""
        try:
            with open(CONVERSATION_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, indent=2)
            print(colored("Saved conversation history.", "green"))
        except Exception as e:
            print(colored(f"Error saving conversation history: {e}", "red"))
    
    async def handle_input(self, user_input: str) -> Dict[str, Any]:
        """
        Handle user input by validating, sanitizing, and storing it.
        
        Args:
            user_input: The raw input from the user
            
        Returns:
            Dict containing the processed input
        """
        print(colored("STEP 1: Input Handling", "cyan"))
        
        # Validate and sanitize input
        if not user_input or not user_input.strip():
            return {"error": "Empty input"}
        
        # Remove any potentially harmful characters
        sanitized_input = user_input.strip()
        
        # Store input in conversation history
        input_entry = {
            "role": "user",
            "content": sanitized_input,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(input_entry)
        
        return {"input": sanitized_input, "timestamp": input_entry["timestamp"]}
    
    async def generate_queries(self, user_input: str) -> List[str]:
        """
        Generate search queries from user input using GPT-4o-mini.
        
        Args:
            user_input: The processed user input
            
        Returns:
            List of search queries
        """
        print(colored("STEP 2: Query Generation", "cyan"))
        
        try:
            # Create system prompt for query generation
            system_prompt = """
            Generate 3 distinct search queries based on the user's input.
            Each query should focus on different aspects of the user's question to ensure comprehensive search results.
            Format your response as a JSON array of strings.
            """
            
            # Call GPT-4o-mini to generate queries
            response = await self.openai_client.chat.completions.create(
                model=GPT4O_MINI,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract queries from response
            result = json.loads(response.choices[0].message.content)
            queries = result.get("queries", [])
            
            # Ensure we have exactly 3 queries
            if not queries or len(queries) < 3:
                # Generate default queries if none were returned
                queries = [
                    f"{user_input} facts",
                    f"{user_input} explanation",
                    f"{user_input} examples"
                ]
            
            # Limit to 3 queries
            queries = queries[:3]
            
            print(colored(f"Generated queries: {queries}", "green"))
            return queries
            
        except Exception as e:
            print(colored(f"Error generating queries: {e}", "red"))
            # Fallback to basic queries
            return [
                f"{user_input} facts",
                f"{user_input} explanation",
                f"{user_input} examples"
            ]
    
    async def search_perplexity(self, query: str) -> Dict[str, Any]:
        """
        Search using Perplexity API with llama-3.1-sonar-large-128k-online model.
        
        Args:
            query: The search query
            
        Returns:
            Dict containing search results
        """
        try:
            response = await self.perplexity_client.chat.completions.create(
                model=LLAMA_SONAR,
                messages=[
                    {"role": "system", "content": "You are a helpful search assistant."},
                    {"role": "user", "content": query}
                ]
            )
            
            return {
                "query": query,
                "content": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(colored(f"Error searching Perplexity for '{query}': {e}", "red"))
            return {
                "query": query,
                "content": f"Error retrieving search results: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def perform_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Perform parallel searches using the Perplexity API.
        
        Args:
            queries: List of search queries
            
        Returns:
            List of search results
        """
        print(colored("STEP 3: Parallel Search", "cyan"))
        
        try:
            # Execute searches concurrently
            search_tasks = [self.search_perplexity(query) for query in queries]
            search_results = await asyncio.gather(*search_tasks)
            
            print(colored(f"Completed {len(search_results)} searches", "green"))
            return search_results
            
        except Exception as e:
            print(colored(f"Error performing searches: {e}", "red"))
            return [{"query": q, "content": "Error retrieving results", "error": str(e)} for q in queries]
    
    async def aggregate_data(self, queries: List[str], search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate search results and save to JSON file.
        
        Args:
            queries: The original search queries
            search_results: The results from the searches
            
        Returns:
            Dict containing the aggregated data
        """
        print(colored("STEP 4: Data Aggregation", "cyan"))
        
        try:
            # Create aggregated data structure
            aggregated_data = {
                "queries": queries,
                "results": search_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to JSON file
            with open(SEARCH_RESULTS_FILE, "w", encoding="utf-8") as f:
                json.dump(aggregated_data, f, indent=2)
            
            print(colored(f"Saved search results to {SEARCH_RESULTS_FILE}", "green"))
            return aggregated_data
            
        except Exception as e:
            print(colored(f"Error aggregating data: {e}", "red"))
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def generate_summary(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of search results using Gemini Flash.
        
        Args:
            search_results: The search results to summarize
            
        Returns:
            Summary text
        """
        try:
            # Combine search results into a single text
            combined_results = "\n\n".join([f"Query: {r['query']}\nResults: {r['content']}" 
                                          for r in search_results])
            
            # Call Gemini Flash via OpenRouter
            response = await self.openrouter_client.chat.completions.create(
                model=GEMINI_FLASH,
                messages=[
                    {"role": "system", "content": "Summarize the following search results concisely."},
                    {"role": "user", "content": combined_results}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(colored(f"Error generating summary: {e}", "red"))
            return f"Error generating summary: {str(e)}"
    
    async def generate_bullet_points(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate bullet points from search results using Claude.
        
        Args:
            search_results: The search results to analyze
            
        Returns:
            List of bullet points
        """
        try:
            # Combine search results into a single text
            combined_results = "\n\n".join([f"Query: {r['query']}\nResults: {r['content']}" 
                                          for r in search_results])
            
            # Call Claude to generate bullet points
            response = await self.anthropic_client.messages.create(
                model=CLAUDE_SONNET,
                max_tokens=1000,
                system="Extract the most important points from the search results as a list of bullet points. Format as a JSON array of strings.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": combined_results
                            }
                        ]
                    }
                ]
            )
            
            # Parse the bullet points from the response
            content = response.content[0].text
            
            # Try to extract JSON array
            try:
                # Look for JSON array in the response
                import re
                json_match = re.search(r'\[\s*".*"\s*\]', content, re.DOTALL)
                if json_match:
                    bullet_points = json.loads(json_match.group(0))
                else:
                    # Fall back to splitting by newlines and bullet points
                    bullet_points = [line.strip().lstrip('•-* ') for line in content.split('\n') 
                                    if line.strip() and line.strip()[0] in '•-*']
                    if not bullet_points:
                        bullet_points = [line.strip() for line in content.split('\n') if line.strip()]
            except:
                # If JSON parsing fails, split by newlines
                bullet_points = [line.strip() for line in content.split('\n') 
                                if line.strip() and not line.strip().startswith('```')]
            
            return bullet_points
            
        except Exception as e:
            print(colored(f"Error generating bullet points: {e}", "red"))
            return [f"Error generating bullet points: {str(e)}"]
    
    async def extract_key_takeaway(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract key takeaway from search results using Gemini Flash.
        
        Args:
            search_results: The search results to analyze
            
        Returns:
            Key takeaway text
        """
        try:
            # Combine search results into a single text
            combined_results = "\n\n".join([f"Query: {r['query']}\nResults: {r['content']}" 
                                          for r in search_results])
            
            # Call Gemini Flash via OpenRouter
            response = await self.openrouter_client.chat.completions.create(
                model=GEMINI_FLASH,
                messages=[
                    {"role": "system", "content": "Extract the single most important takeaway from these search results in one concise sentence."},
                    {"role": "user", "content": combined_results}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(colored(f"Error extracting key takeaway: {e}", "red"))
            return f"Error extracting key takeaway: {str(e)}"
    
    async def extract_entities(self, search_results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract entities from search results using GPT-4o.
        
        Args:
            search_results: The search results to analyze
            
        Returns:
            Dict of entity types to lists of entities
        """
        try:
            # Combine search results into a single text
            combined_results = "\n\n".join([f"Query: {r['query']}\nResults: {r['content']}" 
                                          for r in search_results])
            
            # Create system prompt for entity extraction
            system_prompt = """
            Extract named entities from the text into these categories:
            - people: Names of individuals
            - organizations: Names of companies, institutions, etc.
            - locations: Names of places, cities, countries, etc.
            - dates: Temporal references
            - concepts: Key concepts or technical terms
            
            Format your response as a JSON object with these categories as keys and arrays of strings as values.
            """
            
            # Call GPT-4o to extract entities
            response = await self.openai_client.chat.completions.create(
                model=GPT4O,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_results}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract entities from response
            entities = json.loads(response.choices[0].message.content)
            
            return entities
            
        except Exception as e:
            print(colored(f"Error extracting entities: {e}", "red"))
            return {
                "people": [],
                "organizations": [],
                "locations": [],
                "dates": [],
                "concepts": [],
                "error": str(e)
            }
    
    async def analyze_results(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform parallel analysis of search results.
        
        Args:
            search_results: The search results to analyze
            
        Returns:
            Dict containing the analysis results
        """
        print(colored("STEP 5: Parallel Analysis", "cyan"))
        
        try:
            # Execute analyses concurrently
            summary_task = self.generate_summary(search_results)
            bullet_points_task = self.generate_bullet_points(search_results)
            key_takeaway_task = self.extract_key_takeaway(search_results)
            entities_task = self.extract_entities(search_results)
            
            # Gather results
            summary, bullet_points, key_takeaway, entities = await asyncio.gather(
                summary_task, bullet_points_task, key_takeaway_task, entities_task
            )
            
            # Combine results
            analysis = {
                "summary": summary,
                "bullet_points": bullet_points,
                "key_takeaway": key_takeaway,
                "entities": entities,
                "timestamp": datetime.now().isoformat()
            }
            
            print(colored("Completed parallel analysis", "green"))
            return analysis
            
        except Exception as e:
            print(colored(f"Error analyzing results: {e}", "red"))
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def generate_output(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured output and save to file.
        
        Args:
            analysis: The analysis results
            
        Returns:
            Dict containing the structured output
        """
        print(colored("STEP 6: Output Generation", "cyan"))
        
        try:
            # Save analysis to file
            with open(ANALYSIS_OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)
            
            # Add to conversation history
            output_entry = {
                "role": "assistant",
                "content": analysis,
                "timestamp": datetime.now().isoformat()
            }
            self.conversation_history.append(output_entry)
            self.save_conversation_history()
            
            print(colored(f"Saved analysis to {ANALYSIS_OUTPUT_FILE}", "green"))
            return analysis
            
        except Exception as e:
            print(colored(f"Error generating output: {e}", "red"))
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def check_exit_conditions(self, user_input: str) -> bool:
        """
        Check if the user wants to exit.
        
        Args:
            user_input: The user's input
            
        Returns:
            True if should exit, False otherwise
        """
        exit_commands = ["exit", "quit", "bye", "goodbye"]
        return user_input.lower().strip() in exit_commands
    
    async def process_cycle(self, user_input: str) -> Dict[str, Any]:
        """
        Process a complete agent cycle.
        
        Args:
            user_input: The user's input
            
        Returns:
            Dict containing the final output
        """
        try:
            # Step 1: Input Handling
            input_data = await self.handle_input(user_input)
            if "error" in input_data:
                return {"error": input_data["error"]}
            
            # Step 2: Query Generation
            queries = await self.generate_queries(input_data["input"])
            
            # Step 3: Parallel Search
            search_results = await self.perform_searches(queries)
            
            # Step 4: Data Aggregation
            aggregated_data = await self.aggregate_data(queries, search_results)
            
            # Step 5: Parallel Analysis
            analysis = await self.analyze_results(search_results)
            
            # Step 6: Output Generation
            output = await self.generate_output(analysis)
            
            # Step 7: Cycle Control is handled by the main loop
            
            return output
            
        except Exception as e:
            print(colored(f"Error in processing cycle: {e}", "red"))
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

async def main():
    """Main function to run the agent."""
    print(colored("Starting The Last Centaur Agent...", "cyan"))
    
    # Initialize agent
    agent = Agent()
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input(colored("\nEnter your query (or 'exit' to quit): ", "yellow"))
            
            # Check exit conditions
            if agent.check_exit_conditions(user_input):
                print(colored("Exiting agent. Goodbye!", "cyan"))
                break
            
            # Process the cycle
            output = await agent.process_cycle(user_input)
            
            # Display results
            if "error" in output:
                print(colored(f"Error: {output['error']}", "red"))
            else:
                print(colored("\n=== SUMMARY ===", "green"))
                print(output["summary"])
                
                print(colored("\n=== KEY TAKEAWAY ===", "green"))
                print(output["key_takeaway"])
                
                print(colored("\n=== BULLET POINTS ===", "green"))
                for point in output["bullet_points"]:
                    print(f"• {point}")
                
                print(colored("\n=== ENTITIES ===", "green"))
                for entity_type, entities in output["entities"].items():
                    if entity_type != "error" and entities:
                        print(f"{entity_type.capitalize()}: {', '.join(entities)}")
            
        except KeyboardInterrupt:
            print(colored("\nInterrupted by user. Exiting...", "yellow"))
            break
        except Exception as e:
            print(colored(f"Error: {e}", "red"))

if __name__ == "__main__":
    asyncio.run(main()) 