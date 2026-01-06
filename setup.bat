@echo off
echo 🖨️  Printing Price Predictor - Quick Start
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

:: Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

:: Setup Backend
echo 📦 Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo ⚙️  Backend setup complete!
echo.

:: Setup Frontend
echo 📦 Setting up frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing Node dependencies...
    npm install
)

echo.
echo ⚙️  Frontend setup complete!
echo.

:: Create .env files if they don't exist
cd ..

if not exist "backend\.env" (
    echo Creating backend\.env file...
    (
        echo ANTHROPIC_API_KEY=your_api_key_here
        echo PORT=8000
    ) > backend\.env
    echo ⚠️  Please update backend\.env with your Anthropic API key
)

if not exist "frontend\.env" (
    echo Creating frontend\.env file...
    echo REACT_APP_API_URL=http://localhost:8000 > frontend\.env
)

echo.
echo ✅ Setup complete!
echo.
echo To start the application:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm start
echo.
echo 📝 Don't forget to update backend\.env with your Anthropic API key!
echo 🌐 Frontend will be available at http://localhost:3000
echo 🔌 Backend API will be available at http://localhost:8000
echo.
pause
