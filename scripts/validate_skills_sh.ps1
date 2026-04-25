$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SkillName = "xsoar-development"

function Fail($Message) {
  throw "skills.sh validation failed: $Message"
}

function Remove-Ansi($Text) {
  $Escape = [char]27
  return (($Text -join "`n") -replace "$Escape\[[0-9;?]*[ -/]*[@-~]", "")
}

function Get-Frontmatter($Path) {
  $Text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
  if ($Text -notmatch '(?s)^---\r?\n(.*?)\r?\n---') {
    Fail "missing YAML frontmatter in $Path"
  }
  return $Matches[1]
}

function Assert-SkillCliOutput($Label, $Output) {
  $Output = Remove-Ansi $Output
  if ($Output -notmatch [regex]::Escape($SkillName)) {
    Fail "$Label did not list $SkillName"
  }
  if ($Output -notmatch 'Found\D+1\D+skill') {
    Fail "$Label did not report exactly one discovered skill"
  }
}

function Get-TargetedScanPaths {
  $Paths = @(
    "README.md",
    "SKILL.md",
    "NOTICE.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/docs/index.json"
  )

  if (Test-Path -LiteralPath (Join-Path $RepoRoot "docs")) {
    $Paths += Get-ChildItem -LiteralPath (Join-Path $RepoRoot "docs") -Recurse -File |
      ForEach-Object { Resolve-Path -LiteralPath $_.FullName -Relative }
  }

  $Paths += Get-ChildItem -LiteralPath (Join-Path $RepoRoot "references") -File -Filter *.md |
    ForEach-Object { Resolve-Path -LiteralPath $_.FullName -Relative }

  $Paths += Get-ChildItem -LiteralPath (Join-Path $RepoRoot "references/structures") -Recurse -File |
    ForEach-Object { Resolve-Path -LiteralPath $_.FullName -Relative }

  return $Paths | ForEach-Object { $_ -replace '^\./', '' } | Sort-Object -Unique
}

Push-Location $RepoRoot
try {
  $SkillPath = Join-Path $RepoRoot "SKILL.md"
  $Frontmatter = Get-Frontmatter $SkillPath
  if ($Frontmatter -notmatch "(?m)^name:\s*$([regex]::Escape($SkillName))\s*$") {
    Fail "SKILL.md name does not match $SkillName"
  }
  if ($Frontmatter -notmatch "(?m)^description:\s*\S") {
    Fail "SKILL.md is missing description"
  }
  if ($Frontmatter -notmatch "(?m)^license:\s*MIT\s*$") {
    Fail "SKILL.md is missing MIT license metadata"
  }
  if ($Frontmatter -notmatch "(?m)^compatibility:\s*\S") {
    Fail "SKILL.md is missing compatibility metadata"
  }
  if ($Frontmatter -notmatch "(?ms)^metadata:\s*\r?\n\s+version:\s*`"0\.1\.0`"\s*$") {
    Fail "SKILL.md is missing metadata.version"
  }

  foreach ($RelativePath in Get-TargetedScanPaths) {
    $Path = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $Path)) {
      Fail "targeted scan path is missing: $RelativePath"
    }
    $Lines = Get-Content -LiteralPath $Path -Encoding UTF8
    for ($Index = 0; $Index -lt $Lines.Count; $Index++) {
      $Line = $Lines[$Index]
      if ($Line -match 'Users\\darka|darka-local|T:\\|D:\\|C:\\|%USERPROFILE%|Documents\\Projects\\XSoar|SplunkPy_ES_SPLUNK_SIEM') {
        Fail "machine-specific or private path leaked in $RelativePath line $($Index + 1)"
      }
    }
  }

  $env:DISABLE_TELEMETRY = "1"
  $RemoteOutput = & npx skills add Darkaxt/xsoar-development --list 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) {
    Fail "remote skills CLI discovery failed"
  }
  Assert-SkillCliOutput "remote skills CLI discovery" $RemoteOutput

  $LocalOutput = & npx skills add . --list 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) {
    Fail "local skills CLI discovery failed"
  }
  Assert-SkillCliOutput "local skills CLI discovery" $LocalOutput

  Write-Host "skills.sh validation passed for $SkillName."
} finally {
  Pop-Location
}
