Set-Location .\profile
Remove-Item -Force ..\profile.zip
&"c:\program files (x86)\7-zip\7z.exe" a -tzip ..\profile.zip * 
Set-Location ..
