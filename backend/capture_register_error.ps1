# capture_register_error.ps1
# Run from the backend folder. This will POST to /register and print any server error body.

$body = @{ username = "testuser3"; password = "password123"; email = "you@example.com" } | ConvertTo-Json

try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:8000/register' -Method Post -ContentType 'application/json' -Body $body -Verbose -ErrorAction Stop
    Write-Output "Request succeeded."
} catch {
    $resp = $_.Exception.Response
    if ($resp -ne $null) {
        $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $text = $sr.ReadToEnd()
        $sr.Close()
        Write-Output "---- SERVER ERROR BODY START ----"
        Write-Output $text
        Write-Output "---- SERVER ERROR BODY END ----"
    } else {
        Write-Output "No response stream; exception:"
        $_ | Out-String | Write-Output
    }
}