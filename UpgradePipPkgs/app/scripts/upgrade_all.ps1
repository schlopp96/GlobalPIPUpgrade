#!/usr/bin/env pwsh

function UpgradePIP {
    <#
        .SYNOPSIS
            Upgrade all globally installed `pip` packages.

        .NOTES
            Does NOT take in to account version requirements for package dependencies.
    #>
    return pip freeze | ForEach-Object { $_.split('==')[0] } | ForEach-Object { pip install --upgrade $_ };
}

UpgradePIP;