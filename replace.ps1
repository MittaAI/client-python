Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
>>   (Get-Content $_.FullName) -replace 'from mistralai', 'from mitta_mistralai' | Set-Content $_.FullName
>> }
