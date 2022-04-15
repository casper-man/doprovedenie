@ECHO on
@CLS

set put=%cd%

::%cd%\venv\Scripts\activate

::%cd%\venv\Scripts\python.exe main.py

cmd /k "cd /d %put%\venv\Scripts & activate & cd /d %put% & python main.py"

pause