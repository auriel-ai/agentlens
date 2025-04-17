#!/bin/bash
# Helper script to set up and run AgentLens examples

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}     AgentLens Setup & Demo        ${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3 to continue.${NC}"
    exit 1
fi

# Create and activate virtual environment
echo -e "\n${CYAN}Setting up virtual environment...${NC}"
python3 -m venv agentlens_env
source agentlens_env/bin/activate

# Install AgentLens in development mode
echo -e "\n${CYAN}Installing AgentLens in development mode...${NC}"
pip install -e .

# Install example dependencies
echo -e "\n${CYAN}Installing example dependencies...${NC}"
pip install openai langchain

echo -e "\n${GREEN}Setup complete!${NC}"

# Prompt for API key if not set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "\n${YELLOW}OPENAI_API_KEY environment variable not found.${NC}"
    echo -e "The examples require an OpenAI API key to run."
    read -p "Enter your OpenAI API key (or press enter to skip running examples): " API_KEY
    if [ -n "$API_KEY" ]; then
        export OPENAI_API_KEY=$API_KEY
    else
        echo -e "\n${YELLOW}Skipping examples as no API key was provided.${NC}"
        echo -e "You can run examples later by setting OPENAI_API_KEY and running individual example scripts."
        exit 0
    fi
fi

# Menu for running examples
while true; do
    echo -e "\n${BLUE}====================================${NC}"
    echo -e "${BLUE}         Example Selection          ${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo -e "1. Run basic example (no API calls)"
    echo -e "2. Run LangChain basic example (requires API key)"
    echo -e "3. Run LangChain integration example (requires API key)"
    echo -e "4. Run OpenAI integration example (requires API key)"
    echo -e "5. Run CLI example (no API calls)"
    echo -e "6. Exit"
    
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            echo -e "\n${CYAN}Running basic example...${NC}"
            python examples/basic_example.py
            ;;
        2)
            echo -e "\n${CYAN}Running LangChain basic example...${NC}"
            python examples/langchain_example.py
            ;;
        3)
            echo -e "\n${CYAN}Running LangChain integration example...${NC}"
            python examples/langchain_integration_example.py
            ;;
        4)
            echo -e "\n${CYAN}Running OpenAI integration example...${NC}"
            python examples/openai_integration_example.py
            ;;
        5)
            echo -e "\n${CYAN}Running CLI example...${NC}"
            bash examples/cli_example.sh
            ;;
        6)
            echo -e "\n${GREEN}Exiting. Thanks for trying AgentLens!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${YELLOW}Invalid choice. Please enter a number between 1 and 6.${NC}"
            ;;
    esac
done 