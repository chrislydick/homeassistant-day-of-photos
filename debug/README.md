# Debug and Diagnostic Scripts

This directory contains various debug and diagnostic scripts for troubleshooting OneDrive authentication and photo fetching issues.

## Scripts Overview

### Token and Authentication Debugging

- **`diagnose_token.py`** - Basic token file analysis and validation
- **`token_debug.py`** - Comprehensive token lifecycle debugging
- **`debug_token_exchange.py`** - Step-by-step OAuth token exchange debugging
- **`test_oauth_flow.py`** - Test complete OAuth flow and see token responses

### Azure Configuration Debugging

- **`check_azure_config.py`** - Check Azure app registration settings
- **`check_account_permissions.py`** - Test account permissions and API access
- **`test_alternative_scopes.py`** - Test different OAuth scope combinations

### Photo Discovery Debugging

- **`debug_onedrive_photos.py`** - Debug OneDrive photo discovery and search

## Usage

### When to Use Each Script

**Token Issues:**
```bash
# Basic token check
python3 debug/diagnose_token.py

# Comprehensive token analysis
python3 debug/token_debug.py

# Debug OAuth flow step by step
python3 debug/debug_token_exchange.py

# Test complete OAuth flow
python3 debug/test_oauth_flow.py
```

**Azure Configuration Issues:**
```bash
# Check Azure app settings
python3 debug/check_azure_config.py

# Test account permissions
python3 debug/check_account_permissions.py

# Test different scope combinations
python3 debug/test_alternative_scopes.py
```

**Photo Discovery Issues:**
```bash
# Debug photo search and discovery
python3 debug/debug_onedrive_photos.py
```

## Common Debugging Workflow

1. **Start with basic token check:**
   ```bash
   python3 debug/diagnose_token.py
   ```

2. **If token issues persist:**
   ```bash
   python3 debug/token_debug.py
   python3 debug/debug_token_exchange.py
   ```

3. **If Azure configuration issues:**
   ```bash
   python3 debug/check_azure_config.py
   python3 debug/check_account_permissions.py
   ```

4. **If photo discovery issues:**
   ```bash
   python3 debug/debug_onedrive_photos.py
   ```

## Troubleshooting Guide

### "No refresh token received"
- Run `debug_token_exchange.py` to see exact OAuth response
- Check Azure app configuration with `check_azure_config.py`
- Test alternative scopes with `test_alternative_scopes.py`

### "Token expires quickly"
- Run `token_debug.py` to analyze token lifecycle
- Check if refresh tokens are working with `debug_token_exchange.py`

### "No photos found"
- Run `debug_onedrive_photos.py` to explore OneDrive structure
- Check folder paths and date extraction

### "Authentication fails"
- Run `test_oauth_flow.py` to test complete flow
- Check Azure app configuration with `check_azure_config.py`

## Notes

- These scripts are for debugging only and should not be used in production
- Some scripts require manual interaction (browser authentication)
- All scripts use the same `.env` file as the main script
- Scripts are designed to provide detailed output for troubleshooting
