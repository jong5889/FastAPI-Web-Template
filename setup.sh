#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Supabase DB project setup...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "❌ Python 3 is not installed. Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "❌ pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating Python virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "\n${YELLOW}⚠️  Please edit the .env file and add your database credentials.${NC}"
else
    echo -e "\n${GREEN}✓ .env file already exists.${NC}"
fi

# Set execute permissions for the script
chmod +x supabase_connect.py

echo -e "\n${GREEN}✅ Setup completed successfully!${NC}"
echo -e "\nTo activate the virtual environment, run: ${YELLOW}source venv/bin/activate${NC}"
echo -e "To run the database connection test: ${YELLOW}python supabase_connect.py${NC}"
echo -e "\n${YELLOW}Don't forget to update your .env file with your database credentials before running the script.${NC}"
