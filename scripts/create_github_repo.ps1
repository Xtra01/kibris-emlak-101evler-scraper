param(
  [Parameter(Mandatory=$true)][string]$Token,
  [Parameter(Mandatory=$true)][string]$RepoName,
  [string]$Private = 'false'
)

$headers = @{
  Authorization = "token $Token"
  Accept        = 'application/vnd.github+json'
}
$body = @{
  name    = $RepoName
  private = [System.Convert]::ToBoolean($Private)
} | ConvertTo-Json

try {
  $resp = Invoke-RestMethod -Method Post -Uri 'https://api.github.com/user/repos' -Headers $headers -ContentType 'application/json' -Body $body
  Write-Output "Created: $($resp.html_url)"
} catch {
  if ($_.Exception.Response.StatusCode.Value__ -eq 422) {
    Write-Output 'Repo already exists or name taken. Continuing.'
    exit 0
  } else {
    throw $_
  }
}
