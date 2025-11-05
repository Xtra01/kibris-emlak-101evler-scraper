param(
  [string]$RemoteName = 'origin',
  [Parameter(Mandatory=$true)][string]$RemoteUrl
)

# Check if remote exists
$existing = (& git remote) -split "\r?\n" | Where-Object { $_ -eq $RemoteName }
if ($existing) {
  Write-Output "Updating remote '$RemoteName' to $RemoteUrl"
  & git remote set-url $RemoteName $RemoteUrl
} else {
  Write-Output "Adding remote '$RemoteName' => $RemoteUrl"
  & git remote add $RemoteName $RemoteUrl
}

Write-Output ((& git remote -v) -join "`n")
