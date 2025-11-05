param(
  [Parameter(Mandatory=$true)][string]$Username,
  [Parameter(Mandatory=$true)][string]$Token,
  [Parameter(Mandatory=$true)][string]$RemoteUrl,
  [Parameter(Mandatory=$true)][string]$Branch
)

# Build Basic auth header value: base64(username:token)
$pair = "$Username`:$Token"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$b64 = [System.Convert]::ToBase64String($bytes)

& git -c ("http.extraheader=AUTHORIZATION: Basic {0}" -f $b64) push $RemoteUrl $Branch
