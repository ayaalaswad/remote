@echo off
REM Quick GPU Check for SHARP Training

echo ================================================================================
echo GPU CHECK FOR SHARP TRAINING
echo ================================================================================
echo.

REM Check if nvidia-smi exists
where nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] nvidia-smi not found!
    echo.
    echo NVIDIA drivers may not be installed.
    echo Download from: https://www.nvidia.com/Download/index.aspx
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking NVIDIA GPU with nvidia-smi...
echo.
nvidia-smi
echo.

echo [2/3] Checking PyTorch CUDA support...
echo.
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'); print('VRAM:', round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 1), 'GB' if torch.cuda.is_available() else '')"
echo.

if %errorlevel% neq 0 (
    echo [ERROR] PyTorch not installed or has issues
    echo.
    echo Install PyTorch GPU version:
    echo pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    echo.
    pause
    exit /b 1
)

echo [3/3] Running detailed GPU check...
echo.
python check_gpu.py

echo.
echo ================================================================================
echo CHECK COMPLETE
echo ================================================================================
echo.
pause
