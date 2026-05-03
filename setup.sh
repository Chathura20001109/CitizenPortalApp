#!/bin/bash

# Citizen Portal - Automated Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "=========================================="
echo "  CITIZEN PORTAL - AUTOMATED SETUP"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/10] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.9+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo -e "\n${YELLOW}[2/10] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}[3/10] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}[4/10] Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}[5/10] Installing dependencies...${NC}"
echo "This may take several minutes..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create required directories
echo -e "\n${YELLOW}[6/10] Creating required directories...${NC}"
mkdir -p data logs static/forms static/store static/img uploads
touch data/.gitkeep logs/.gitkeep uploads/.gitkeep
echo -e "${GREEN}✓ Directories created${NC}"

# Setup environment file
echo -e "\n${YELLOW}[7/10] Setting up environment file...${NC}"
if [ -f ".env" ]; then
    echo ".env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
    else
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from template${NC}"
    fi
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
fi

# Configure MongoDB URI
echo -e "\n${YELLOW}[8/10] MongoDB Atlas Configuration${NC}"
echo "Please provide your MongoDB Atlas connection string"
echo "Format: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
echo ""
read -p "Enter MongoDB URI (or press Enter to configure later): " MONGO_URI

if [ ! -z "$MONGO_URI" ]; then
    # Update .env file with MongoDB URI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|MONGO_URI=.*|MONGO_URI=$MONGO_URI|g" .env
    else
        # Linux
        sed -i "s|MONGO_URI=.*|MONGO_URI=$MONGO_URI|g" .env
    fi
    echo -e "${GREEN}✓ MongoDB URI configured${NC}"
else
    echo -e "${YELLOW}⚠ Remember to update MONGO_URI in .env file before running the application${NC}"
fi

# Generate secret key
echo -e "\n${YELLOW}[9/10] Generating Flask secret key...${NC}"
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|FLASK_SECRET=.*|FLASK_SECRET=$SECRET_KEY|g" .env
else
    sed -i "s|FLASK_SECRET=.*|FLASK_SECRET=$SECRET_KEY|g" .env
fi
echo -e "${GREEN}✓ Secret key generated${NC}"

# Create placeholder images
echo -e "\n${YELLOW}[10/10] Creating placeholder images...${NC}"
# Create simple placeholder files
touch static/store/placeholder.jpg
touch static/img/logo.png
echo -e "${GREEN}✓ Placeholder files created${NC}"

# Summary
echo ""
echo "=========================================="
echo "  SETUP COMPLETED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure MongoDB Atlas:"
if [ -z "$MONGO_URI" ]; then
    echo "   - Update MONGO_URI in .env file"
fi
echo "   - Ensure your IP is whitelisted in MongoDB Atlas"
echo ""
echo "2. Seed the database:"
echo "   source venv/bin/activate"
echo "   python seed_data.py"
echo ""
echo "3. Run the application:"
echo "   python app.py"
echo ""
echo "4. Access the portal:"
echo "   - Public Portal: http://localhost:5000"
echo "   - Admin Panel: http://localhost:5000/admin"
echo "   - Store: http://localhost:5000/store"
echo ""
echo "5. Default admin credentials:"
echo "   - Username: admin"
echo "   - Password: (set in .env as ADMIN_PWD)"
echo ""
echo "6. After seeding, build AI index:"
echo "   - Login to admin panel"
echo "   - Click 'Build AI Index' button"
echo ""
echo "=========================================="
echo ""
echo "For detailed documentation, see README.md"
echo ""

# Check if should seed now
if [ ! -z "$MONGO_URI" ]; then
    read -p "Do you want to seed the database now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Seeding database..."
        python seed_data.py
        echo ""
        echo -e "${GREEN}✓ Database seeded successfully${NC}"
        echo ""
        echo "You can now run: python app.py"
    fi
fi

echo -e "${GREEN}Setup complete!${NC}"