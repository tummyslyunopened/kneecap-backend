try {
    # Accept URI and file path from arguments
    $target = $args[1]
    $filePath = $args[0]  # Get file path from command line argument

    # Map target argument to URI
    switch ($target) {
        "local"   { $uri = "http://localhost/api/opml/import/" }
        "kneecap" { $uri = "http://kneecap.2wu.me/api/opml/import/" }
        default   { $uri = $target }
    }

    # Check if file path and target were provided
    if (-not $filePath -or -not $target) {
        Write-Error "Please provide the path to your OPML file and the target (local|kneecap|custom URI) as arguments."
        Write-Host "Usage: .\import-opml.ps1 example.opml local"
        Write-Host "   or: .\import-opml.ps1 example.opml kneecap"
        Write-Host "   or: .\import-opml.ps1 example.opml http://custom/api/opml/import/"
        exit 1
    }

    # Verify file exists
    if (-not (Test-Path $filePath)) {
        Write-Error "File not found: $filePath"
        exit 1
    }

    $form = @{
        file = Get-Item -Path $filePath
    }

    # Make the request
    Write-Host "Uploading OPML file to $uri..."
    $response = Invoke-WebRequest -Uri $uri -Method Post -Form $form

    # Display the response
    Write-Host "`nStatus Code: $($response.StatusCode)"
    Write-Host "`nResponse Body:"
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "`nError occurred: $_"
    
    # Better error handling
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $statusDescription = $_.Exception.Response.StatusDescription
        
        Write-Host "Status Code: $statusCode"
        Write-Host "Status Description: $statusDescription"
        
        try {
            $rawResponse = $_.ErrorDetails.Message
            if ($rawResponse) {
                Write-Host "`nError Details:"
                $rawResponse
            }
        }
        catch {
            Write-Host "Could not retrieve detailed error message"
        }
    }
    else {
        Write-Host "No response details available"
    }
} 
