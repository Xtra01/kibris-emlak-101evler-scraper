param(
  [Parameter(Mandatory=$true)][string]$Token,
  [Parameter(Mandatory=$true)][string]$RemoteUrl
)

& git -c ("http.extraheader=AUTHORIZATION: bearer {0}" -f $Token) ls-remote $RemoteUrl
