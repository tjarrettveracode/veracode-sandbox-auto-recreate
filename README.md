# Veracode Sandbox Auto-Recreate

## Required Libraries

`veracode-api-signing`, `requests`, and `lxml`, which can be installed using pip:

    pip install -r requirements.txt

## Description

Sets sandboxes to auto-recreate for the requested applications. Can operate on an individual application ID or across an entire portfolio. Only sets sandboxes to auto-recreate that have an expiration time to set (Veracode does not support auto-recreate for non-expiring sandboxes).

API credentials are supplied using the [standard Veracode methods](https://help.veracode.com/go/c_configure_api_cred_file) (either via a `.veracode/credentials` file or via environment variables).

## Parameters

    1. -a --app_id  # Application ID for which you want to set auto-recreate
    2. -l, --all   # If "true", will be applied for all applications in the organization.

## Logging

The script creates a `Vcsandboxrc.log` file. All actions are logged.
