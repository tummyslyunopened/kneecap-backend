try {
    $uri = "http://localhost/api/opml/import/"
    $filePath = $args[0]  # Get file path from command line argument
    
    # Check if file path was provided
    if (-not $filePath) {
        Write-Error "Please provide the path to your OPML file as an argument."
        Write-Host "Usage: .\import-opml.ps1 example.opml"
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
