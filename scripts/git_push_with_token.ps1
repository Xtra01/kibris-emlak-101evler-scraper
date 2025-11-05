param(
  [Parameter(Mandatory=$true)][string]$Token,
  [Parameter(Mandatory=$true)][string]$RemoteUrl,
  [Parameter(Mandatory=$true)][string]$Branch
)

& git -c ("http.extraheader=AUTHORIZATION: bearer {0}" -f $Token) push $RemoteUrl $Branch
