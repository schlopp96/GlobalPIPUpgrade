#!usr/bin/env pwsh
function UpgradePip {
    return pip freeze | ForEach-Object { $_.split('==')[0] } | ForEach-Object { pip install --upgrade $_ };
}

function prompt {
    $prompt = "Do you wish to update all existing pip-installed packages?`n==========================================================`nEnter `"1`" to continue with update process.`nEnter anything else to exit the process.`n`n>"
    $uchoice = Read-Host -Prompt $prompt
    if ($uchoice -eq "1") {
        Write-Output "Upgrading ALL Pip Packages...`n"
        UpgradePip
        return Write-Output "`nAll eligible pip packages sucessfully upgraded!"
    }
    else {
        return Write-Output "`nExiting window...`n";
        exit;
    }
}

prompt;