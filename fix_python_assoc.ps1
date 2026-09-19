$exe = "C:\Users\haroon traders\AppData\Local\Programs\Python\Python313\python.exe"
cmd /c "assoc .py=Python.File"
cmd /c "ftype Python.File=`"$exe`" `"%1`" %*"
Write-Host "Done. Test with: python app.py"
